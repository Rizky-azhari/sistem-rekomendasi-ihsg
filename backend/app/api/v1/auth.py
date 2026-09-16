from typing import Optional, Dict, Any
import time
import random
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from app.database.connection import get_supabase, get_supabase_admin, engine
from app.core.security import get_current_user, log_activity_event
from app.services.email_sender import send_verification_email, is_smtp_configured
from sqlalchemy import text

router = APIRouter()

# In-memory storage for reset verification codes (demo / verification support)
RESET_VERIFICATION_CODES: Dict[str, Dict[str, Any]] = {}


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
    Mendukung akun Google terdaftar dan akun Supabase.
    """
    email = payload.email.strip().lower()
    password = payload.password

    sb = get_supabase_admin() or get_supabase()
    if not sb:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Koneksi Supabase belum terkonfigurasi."
        )

    # 1. Cek apakah email terdaftar di profiles
    user_profile = None
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

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Akun dengan email {email} belum terdaftar di sistem. Silakan gunakan Google Login terlebih dahulu."
        )

    # 2. Autentikasi menggunakan Supabase Auth
    try:
        login_res = sb.auth.sign_in_with_password({"email": email, "password": password})
        token = login_res.session.access_token
        user_id = str(login_res.user.id)
    except Exception as e:
        err_msg = str(e)
        print(f"[Auth] Supabase sign_in_with_password notice: {err_msg}")
        # Jika akun Google belum memiliki kata sandi atau password salah
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password salah atau akun belum menyetel kata sandi. Silakan gunakan fitur 'Lupa password?' atau masuk langsung dengan tombol 'Login dengan Google'."
        )

    # Log activity
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
    Kode digenerate secara random dan dikirim via SMTP.
    """
    email = payload.email.strip().lower()

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, email, full_name, role FROM public.profiles WHERE LOWER(email) = :email"),
            {"email": email}
        ).first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email {email} tidak ditemukan dalam daftar akun pengguna. Pastikan email sesuai dengan akun Google Anda."
        )

    # Generate random 6-digit verification code
    code = str(random.randint(100000, 999999))
    RESET_VERIFICATION_CODES[email] = {
        "code": code,
        "user_id": str(row[0]),
        "expires_at": time.time() + 900  # 15 menit
    }

    # Send verification code via SMTP email
    email_sent = send_verification_email(email, code)

    # Fallback: also try Supabase reset_password_for_email
    if not email_sent:
        sb = get_supabase()
        if sb:
            try:
                sb.auth.reset_password_for_email(email)
            except Exception as e:
                print(f"[Auth] reset_password_for_email notice: {e}")

    log_activity_event(
        user_id=str(row[0]),
        user_email=email,
        role=row[3] or "user",
        action="REQUEST_PASSWORD_RESET",
        details={"email": email, "method": "smtp" if email_sent else "fallback"},
        request=request
    )

    return {
        "message": f"Kode verifikasi 6-digit telah dikirim ke {email}. Periksa inbox dan folder spam Anda.",
        "email": email,
        "email_sent": email_sent,
        "expires_in_minutes": 15
    }


@router.post("/verify-reset")
def verify_password_reset(payload: VerifyResetRequest, request: Request):
    """
    Memverifikasi kode reset dan memperbarui password pengguna di Supabase.
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
        # Code expired
        del RESET_VERIFICATION_CODES[email]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode verifikasi telah kedaluwarsa. Silakan minta kode baru."
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode verifikasi tidak valid. Periksa kembali kode yang dikirim ke email Anda."
        )

    # Update password di Supabase Auth using isolated admin client
    sb = get_supabase_admin() or get_supabase()
    if not sb:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client tidak tersedia."
        )

    try:
        sb.auth.admin.update_user_by_id(user_id, {"password": new_password})
    except Exception as e:
        print(f"[Auth] Error updating password via admin client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memperbarui password di Supabase: {e}"
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
    Returns profile and role of currently authenticated Google user.
    Reads from public.profiles: {id, email, full_name, avatar_url, role}.
    """
    return current_user


@router.post("/callback-sync")
def sync_google_login(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Called after successful Google OAuth redirect to record LOGIN audit event
    and return confirmed role ('admin' or 'user').
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
        details={"status": "User initiated Google logout"},
        request=request
    )
    return {"message": "Berhasil logout."}

