import os
import json
import datetime
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy import text

from app.database.connection import get_supabase, engine
from app.core.config import settings

security_scheme = HTTPBearer(auto_error=False)


def create_jwt_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Generates a signed JWT token for email/password and demo login sessions."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


def decode_jwt_token(token: str) -> Optional[dict]:
    """Decodes a locally issued JWT token."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Dict[str, Any]:
    """
    Extracts and validates Auth token from Authorization header.
    Supports:
    1. Locally signed JWT tokens (issued by Email/Password login)
    2. Supabase Auth OAuth JWT tokens (issued by Google OAuth)
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Otentikasi diperlukan. Header Authorization Bearer token tidak ditemukan.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # 1. Check if token is a locally issued JWT (Email / Password login)
    local_payload = decode_jwt_token(token)
    if local_payload and "sub" in local_payload:
        email = str(local_payload.get("email", ""))
        return {
            "id": str(local_payload["sub"]),
            "email": email,
            "full_name": str(local_payload.get("full_name") or email.split("@")[0]),
            "avatar_url": str(local_payload.get("avatar_url", "")),
            "role": str(local_payload.get("role", "user")).lower()
        }

    # 2. Check token with Supabase Auth (Google OAuth)
    sb = get_supabase()
    user_id = None
    email = None

    if sb:
        try:
            user_response = sb.auth.get_user(token)
            user = getattr(user_response, "user", None) or user_response
            if user and getattr(user, "id", None):
                user_id = str(user.id)
                email = str(getattr(user, "email", "") or "")
        except Exception as e:
            print(f"[Security] Supabase get_user note: {e}")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesi login tidak valid atau telah kadaluarsa. Silakan login kembali.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Fetch user profile from Supabase profiles table via REST API
    profile = None
    if sb:
        try:
            res = sb.table("profiles").select("id, email, full_name, avatar_url, role").eq("id", user_id).limit(1).execute()
            if res.data:
                row = res.data[0]
                profile = {
                    "id": str(row["id"]),
                    "email": row.get("email") or email,
                    "full_name": row.get("full_name") or email.split("@")[0],
                    "avatar_url": row.get("avatar_url") or "",
                    "role": str(row.get("role") or "user").lower()
                }
        except Exception as e:
            print(f"[Security] Supabase REST profile fetch notice: {e}")

    # Fallback to direct DB engine if Supabase REST had an issue
    if not profile and engine:
        try:
            with engine.connect() as conn:
                row = conn.execute(
                    text("SELECT id, email, full_name, avatar_url, role FROM public.profiles WHERE id = :id"),
                    {"id": user_id}
                ).first()
                if row:
                    profile = {
                        "id": str(row[0]),
                        "email": row[1],
                        "full_name": row[2] or row[1].split("@")[0],
                        "avatar_url": row[3] or "",
                        "role": (row[4] or "user").lower()
                    }
        except Exception:
            pass

    MASTER_ADMIN_EMAILS = [
        "rizkyazhariputra2022@gmail.com",
        "rizkyazhariputra336@gmail.com"
    ]

    if not profile:
        profile = {
            "id": user_id,
            "email": email or "",
            "full_name": (email or "").split("@")[0] if email else "User",
            "avatar_url": "",
            "role": "user"
        }

    # Permanent admin enforcement for designated master admins
    resolved_email = (profile.get("email") or email or "").lower().strip()
    if resolved_email in MASTER_ADMIN_EMAILS:
        profile["role"] = "admin"

    return profile


def require_role(allowed_roles: List[str]):
    """
    Middleware / Dependency Factory for Role Protection:
    Ensures the authenticated user has one of the allowed_roles (e.g. ['admin'] or ['user', 'admin']).
    Returns 403 Forbidden with 'Access Denied' message if unauthorized.
    """
    normalized_allowed = [r.lower() for r in allowed_roles]

    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = str(current_user.get("role", "user")).lower()
        if user_role not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Akses hanya diizinkan untuk peran {', '.join(allowed_roles)}. Peran Anda saat ini: {user_role}."
            )
        return current_user
    return role_checker


def log_activity_event(
    user_id: Optional[str],
    user_email: Optional[str],
    role: Optional[str],
    action: str,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
):
    """Logs user activity for audit trail. Fails gracefully without raising errors."""
    ip_addr = None
    if request:
        client_host = request.client.host if request.client else None
        forwarded = request.headers.get("x-forwarded-for")
        ip_addr = forwarded.split(",")[0].strip() if forwarded else client_host

    sb = get_supabase()
    if sb:
        try:
            sb.table("activity_logs").insert({
                "user_id": user_id,
                "user_email": user_email,
                "role": role or "user",
                "action": action,
                "details": details or {},
                "ip_address": ip_addr or "127.0.0.1"
            }).execute()
            return
        except Exception:
            pass

    if engine:
        try:
            with engine.connect() as conn:
                conn.execution_options(isolation_level="AUTOCOMMIT")
                conn.execute(
                    text("""
                        INSERT INTO public.activity_logs (user_id, user_email, role, action, details, ip_address, created_at)
                        VALUES (:uid, :email, :role, :action, CAST(:details AS jsonb), :ip, NOW())
                    """),
                    {
                        "uid": user_id,
                        "email": user_email,
                        "role": role,
                        "action": action,
                        "details": json.dumps(details or {}),
                        "ip": ip_addr or "127.0.0.1"
                    }
                )
        except Exception:
            pass
