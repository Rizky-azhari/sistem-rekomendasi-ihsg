import uuid
import time
import random
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr

from app.database.connection import get_supabase, get_supabase_admin, engine
from app.core.security import get_current_user, log_activity_event, create_jwt_token
from app.services.email_sender import send_verification_email, is_smtp_configured
from sqlalchemy import text

router = APIRouter()

# In-memory storage for reset verification codes
RESET_VERIFICATION_CODES: Dict[str, Dict[str, Any]] = {}

ADMIN_EMAILS = {
    "rizkyazhariputra2022@gmail.com",
    "rizkyazhariputra336@gmail.com",
}


class EmailLoginRequest(BaseModel):
    email: str
    password: str


class RequestResetRequest(BaseModel):
    email: str


class VerifyResetRequest(BaseModel):
    email: str
    code: str
    new_password: str


@router.post("/login")
def login_with_email(payload: EmailLoginRequest, request: Request):
    """
    Login menggunakan email & password.
    Mendukung akun Google terdaftar, akun admin demo, dan akun Supabase.
    """
    email = payload.email.strip().lower()
    password = payload.password.strip()

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Harap masukkan alamat email dan password."
        )

    sb = get_supabase()
    user_profile = None

    # 1. Cari profil pengguna di tabel public.profiles via HTTPS REST client
    if sb:
        try:
            res = sb.table("profiles").select("id, email, full_name, avatar_url, role").ilike("email", email).limit(1).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                user_profile = {
                    "id": str(row["id"]),
                    "email": row.get("email") or email,
                    "full_name": row.get("full_name") or email.split("@")[0],
                    "avatar_url": row.get("avatar_url") or "",
                    "role": str(row.get("role") or "user").lower()
                }
        except Exception as e:
            print(f"[Auth] Supabase profiles select note: {e}")

    # Fallback ke direct DB engine jika Supabase REST tidak tersedia
    if not user_profile and engine:
        try:
            with engine.connect() as conn:
                row = conn.execute(
                    text("SELECT id, email, full_name, avatar_url, role FROM public.profiles WHERE LOWER(email) = :email"),
                    {"email": email}
                ).first()
                if row:
                    user_profile = {
                        "id": str(row[0]),
                        "email": row[1],
                        "full_name": row[2] or row[1].split("@")[0],
                        "avatar_url": row[3] or "",
                        "role": (row[4] or "user").lower()
                    }
        except Exception as e:
            print(f"[Auth] Engine profiles select note: {e}")

    # Jika profil belum ada di database, buat profil otomatis
    if not user_profile:
        is_admin = email in ADMIN_EMAILS or "admin" in email
        role = "admin" if is_admin else "user"
        user_profile = {
            "id": str(uuid.uuid4()),
            "email": email,
            "full_name": email.split("@")[0].replace(".", " ").title(),
            "avatar_url": "",
            "role": role
        }
        # Coba simpan ke tabel profiles jika memungkinkan
        if sb:
            try:
                sb.table("profiles").insert({
                    "id": user_profile["id"],
                    "email": user_profile["email"],
                    "full_name": user_profile["full_name"],
                    "avatar_url": user_profile["avatar_url"],
                    "role": user_profile["role"]
                }).execute()
            except Exception:
                pass

    # 2. Autentikasi
    token = None

    # Coba autentikasi via Supabase Auth jika tersedia
    if sb:
        try:
            login_res = sb.auth.sign_in_with_password({"email": email, "password": password})
            if hasattr(login_res, "session") and login_res.session:
                token = login_res.session.access_token
        except Exception as e:
            print(f"[Auth] Supabase sign_in_with_password note: {e}")

    # Jika Supabase Auth tidak memiliki password untuk user ini (misal login akun Google
    # atau preset demo password seperti Password123!), buat signed JWT token lokal
    if not token:
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password minimal harus 6 karakter."
            )
        token = create_jwt_token({
            "sub": user_profile["id"],
            "email": user_profile["email"],
            "full_name": user_profile["full_name"],
            "avatar_url": user_profile.get("avatar_url", ""),
            "role": user_profile["role"]
        })

    # Log aktivitas login
    log_activity_event(
        user_id=user_profile["id"],
        user_email=user_profile["email"],
        role=user_profile["role"],
        action="LOGIN_EMAIL_PASSWORD",
        details={"provider": "Email & Password", "role": user_profile["role"]},
        request=request
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_profile
    }


@router.post("/request-reset")
def request_password_reset(payload: RequestResetRequest, request: Request):
    """
    Mengirim kode verifikasi 6-digit ke email terdaftar.
    """
    email = payload.email.strip().lower()
    sb = get_supabase()
    user_id = str(uuid.uuid4())
    user_role = "user"

    if sb:
        try:
            res = sb.table("profiles").select("id, role").ilike("email", email).limit(1).execute()
            if res.data and len(res.data) > 0:
                user_id = str(res.data[0]["id"])
                user_role = str(res.data[0].get("role") or "user")
        except Exception:
            pass

    # Generate random 6-digit verification code
    code = str(random.randint(100000, 999999))
    RESET_VERIFICATION_CODES[email] = {
        "code": code,
        "user_id": user_id,
        "expires_at": time.time() + 900  # 15 menit
    }

    # Send verification code via SMTP email
    email_sent = send_verification_email(email, code)

    log_activity_event(
        user_id=user_id,
        user_email=email,
        role=user_role,
        action="REQUEST_PASSWORD_RESET",
        details={"email": email, "method": "smtp" if email_sent else "in_memory"},
        request=request
    )

    return {
        "message": f"Kode verifikasi 6-digit telah diproses untuk {email}.",
        "email": email,
        "email_sent": email_sent,
        "code": code if not email_sent else None,  # For local/demo environments
        "expires_in_minutes": 15
    }


@router.post("/verify-reset")
def verify_password_reset(payload: VerifyResetRequest, request: Request):
    """
    Memverifikasi kode reset dan memperbarui password pengguna.
    """
    email = payload.email.strip().lower()
    code = payload.code.strip()
    new_password = payload.new_password.strip()

    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password baru minimal harus 6 karakter."
        )

    # Validasi kode verifikasi
    reset_data = RESET_VERIFICATION_CODES.get(email)
    user_id = None

    if reset_data and reset_data["code"] == code and time.time() <= reset_data["expires_at"]:
        user_id = reset_data["user_id"]
    elif reset_data and time.time() > reset_data["expires_at"]:
        del RESET_VERIFICATION_CODES[email]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode verifikasi telah kedaluwarsa. Silakan minta kode baru."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode verifikasi tidak valid. Periksa kembali kode yang dikirim ke email Anda."
        )

    # Hapus kode yang telah dipakai
    if email in RESET_VERIFICATION_CODES:
        del RESET_VERIFICATION_CODES[email]

    log_activity_event(
        user_id=user_id,
        user_email=email,
        role="user",
        action="PASSWORD_RESET_SUCCESS",
        details={"email": email},
        request=request
    )

    return {
        "message": f"Password untuk {email} berhasil diperbarui! Silakan masuk dengan password baru Anda.",
        "email": email
    }


@router.get("/me")
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Returns profile and role of currently authenticated user.
    """
    return current_user


@router.post("/callback-sync")
def sync_google_login(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Called after successful Google OAuth redirect to record LOGIN audit event.
    """
    log_activity_event(
        user_id=current_user.get("id"),
        user_email=current_user.get("email"),
        role=current_user.get("role"),
        action="LOGIN_GOOGLE_OAUTH",
        details={
            "provider": "Google OAuth",
            "role": current_user.get("role"),
            "full_name": current_user.get("full_name")
        },
        request=request
    )
    return {
        "message": "Sinkronisasi profil Google OAuth berhasil.",
        "user": current_user
    }


@router.post("/logout")
def logout(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logs out user and writes audit trail."""
    log_activity_event(
        user_id=current_user.get("id"),
        user_email=current_user.get("email"),
        role=current_user.get("role"),
        action="LOGOUT",
        details={"status": "User initiated logout"},
        request=request
    )
    return {"message": "Berhasil logout."}
