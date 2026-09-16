import os
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database.connection import get_supabase, engine
from sqlalchemy import text

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Dict[str, Any]:
    """
    Extracts and validates Supabase Auth JWT token from Authorization header.
    Returns the authenticated user dict including role from public.user_profiles.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Otentikasi diperlukan. Header Authorization Bearer token tidak ditemukan.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    sb = get_supabase()
    if not sb:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client tidak tersedia di server."
        )

    try:
        # Validate token with Supabase Auth
        user_response = sb.auth.get_user(token)
        user = getattr(user_response, "user", None) or user_response
        if not user or not getattr(user, "id", None):
            raise ValueError("Invalid user token")
        
        user_id = str(user.id)
        email = str(getattr(user, "email", "") or "")
    except Exception as e:
        print(f"[Security] Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesi login tidak valid atau telah kadaluarsa. Silakan login kembali.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user role and profile from public.profiles
    profile = None
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
                    "full_name": row[2] or "",
                    "avatar_url": row[3] or "",
                    "role": (row[4] or "user").lower()
                }
            else:
                # First time login fallback if trigger was skipped:
                # Check if any admin exists in profiles
                admin_count = conn.execute(text("SELECT count(*) FROM public.profiles WHERE role = 'admin'")).scalar() or 0
                assigned_role = "admin" if admin_count == 0 else "user"
                
                meta = getattr(user, "user_metadata", {}) or {}
                full_name = meta.get("full_name") or meta.get("name") or email.split("@")[0]
                avatar_url = meta.get("avatar_url") or meta.get("picture") or ""
                
                conn.execution_options(isolation_level="AUTOCOMMIT")
                conn.execute(
                    text("""
                        INSERT INTO public.profiles (id, email, full_name, avatar_url, role, created_at)
                        VALUES (:id, :email, :full_name, :avatar, :role, NOW())
                        ON CONFLICT (id) DO UPDATE SET email = :email, full_name = :full_name, avatar_url = :avatar
                    """),
                    {"id": user_id, "email": email, "full_name": full_name, "avatar": avatar_url, "role": assigned_role}
                )
                profile = {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "avatar_url": avatar_url,
                    "role": assigned_role
                }
    except Exception as e:
        print(f"[Security] Database fetch profile error: {e}")
        profile = {
            "id": user_id,
            "email": email,
            "full_name": email.split("@")[0],
            "avatar_url": "",
            "role": "user"
        }

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
    """Logs user activity to public.activity_logs table for audit trail."""
    import json
    ip_addr = None
    if request:
        client_host = request.client.host if request.client else None
        forwarded = request.headers.get("x-forwarded-for")
        ip_addr = forwarded.split(",")[0].strip() if forwarded else client_host

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
    except Exception as e:
        print(f"[Security] Failed to write activity log: {e}")
