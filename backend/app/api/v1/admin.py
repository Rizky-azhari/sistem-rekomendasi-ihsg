from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from app.database.connection import get_supabase, engine
from app.core.security import require_role, log_activity_event
from sqlalchemy import text

router = APIRouter(dependencies=[Depends(require_role(["admin"]))])


class UpdateRoleRequest(BaseModel):
    role: str


@router.get("/users")
def list_users(current_admin: Dict[str, Any] = Depends(require_role(["admin"]))):
    """
    [ADMIN ONLY] Kelola User: Melihat daftar seluruh pengguna terdaftar, peran (role), dan avatar.
    """
    users = []
    sb = get_supabase()
    if sb:
        try:
            res = sb.table("profiles").select("id, email, full_name, avatar_url, role, created_at").order("created_at", desc=True).execute()
            if res.data:
                for r in res.data:
                    users.append({
                        "id": str(r.get("id")),
                        "email": r.get("email"),
                        "full_name": r.get("full_name") or "",
                        "avatar_url": r.get("avatar_url") or "",
                        "role": str(r.get("role") or "user").lower(),
                        "created_at": r.get("created_at")
                    })
                return {
                    "total": len(users),
                    "users": users
                }
        except Exception as e:
            print(f"[Admin] Supabase REST list_users note: {e}")

    if engine:
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                        SELECT id, email, full_name, avatar_url, role, created_at
                        FROM public.profiles
                        ORDER BY created_at DESC
                    """)
                ).fetchall()
                for r in rows:
                    users.append({
                        "id": str(r[0]),
                        "email": r[1],
                        "full_name": r[2] or "",
                        "avatar_url": r[3] or "",
                        "role": (r[4] or "user").lower(),
                        "created_at": r[5].isoformat() if r[5] else None
                    })
        except Exception as e:
            print(f"[Admin] Engine list_users note: {e}")

    return {
        "total": len(users),
        "users": users
    }



@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: str,
    payload: UpdateRoleRequest,
    request: Request,
    current_admin: Dict[str, Any] = Depends(require_role(["admin"]))
):
    """
    [ADMIN ONLY] Kelola User: Mengubah role pengguna (admin atau user).
    """
    target_role = payload.role.lower()
    if target_role not in ["admin", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role harus 'admin' atau 'user'."
        )

    MASTER_ADMIN_EMAILS = [
        "rizkyazhariputra2022@gmail.com",
        "rizkyazhariputra336@gmail.com"
    ]

    sb = get_supabase()
    target_email = ""
    updated = False

    try:
        # Step 1: Resolve target user email via Supabase REST or Engine
        if sb:
            try:
                res = sb.table("profiles").select("email, role").eq("id", user_id).limit(1).execute()
                if res.data:
                    target_email = res.data[0].get("email") or ""
            except Exception as e:
                print(f"[Admin] Supabase fetch user email note: {e}")

        if not target_email and engine:
            try:
                with engine.connect() as conn:
                    row = conn.execute(
                        text("SELECT email FROM public.profiles WHERE id = :id"),
                        {"id": user_id}
                    ).first()
                    if row:
                        target_email = row[0]
            except Exception as e:
                print(f"[Admin] Engine fetch user email note: {e}")

        if not target_email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pengguna tidak ditemukan."
            )

        # Protect permanent master admins from demotion
        if target_email.lower() in MASTER_ADMIN_EMAILS and target_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Akun Master Administrator ({target_email}) permanen dan tidak dapat diturunkan perannya."
            )

        # Protect self-demotion
        if user_id == current_admin.get("id") and target_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Anda tidak dapat menurunkan role akun admin Anda sendiri."
            )

        # Step 2: Update role via Direct SQL Engine
        if engine:
            try:
                with engine.connect() as conn:
                    conn.execution_options(isolation_level="AUTOCOMMIT")
                    conn.execute(
                        text("""
                            UPDATE public.profiles
                            SET role = :role
                            WHERE id = :id
                        """),
                        {"id": user_id, "role": target_role}
                    )
                    updated = True
            except Exception as e:
                print(f"[Admin] Engine update role note: {e}")

        # Step 3: Update role via Supabase REST API (HTTPS, bypasses network port limitations)
        if sb:
            try:
                sb.table("profiles").update({"role": target_role}).eq("id", user_id).execute()
                updated = True
            except Exception as e:
                print(f"[Admin] Supabase REST update role note: {e}")

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal memperbarui role: database tidak dapat dijangkau."
            )

        # Log admin activity
        log_activity_event(
            user_id=current_admin.get("id"),
            user_email=current_admin.get("email"),
            role=current_admin.get("role"),
            action="UPDATE_USER_ROLE",
            details={"target_user_id": user_id, "target_email": target_email, "new_role": target_role},
            request=request
        )

        return {
            "message": f"Role pengguna {target_email} berhasil diubah menjadi {target_role}.",
            "user_id": user_id,
            "role": target_role
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Admin] Error updating role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memperbarui role user: {e}"
        )


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    request: Request,
    current_admin: Dict[str, Any] = Depends(require_role(["admin"]))
):
    """
    [ADMIN ONLY] Kelola User: Menghapus pengguna dari sistem.
    """
    MASTER_ADMIN_EMAILS = [
        "rizkyazhariputra2022@gmail.com",
        "rizkyazhariputra336@gmail.com"
    ]

    if user_id == current_admin.get("id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak dapat menghapus akun Anda sendiri."
        )

    sb = get_supabase()
    target_email = ""
    deleted = False

    try:
        # Step 1: Find email first
        if sb:
            try:
                res = sb.table("profiles").select("email").eq("id", user_id).limit(1).execute()
                if res.data:
                    target_email = res.data[0].get("email") or ""
            except Exception as e:
                print(f"[Admin] Supabase fetch user for delete note: {e}")

        if not target_email and engine:
            try:
                with engine.connect() as conn:
                    row = conn.execute(
                        text("SELECT email FROM public.profiles WHERE id = :id"),
                        {"id": user_id}
                    ).first()
                    if row:
                        target_email = row[0]
            except Exception as e:
                print(f"[Admin] Engine fetch user for delete note: {e}")

        if target_email and target_email.lower() in MASTER_ADMIN_EMAILS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Akun Master Administrator ({target_email}) permanen dan tidak dapat dihapus."
            )

        # Step 2: Delete via Engine
        if engine:
            try:
                with engine.connect() as conn:
                    conn.execution_options(isolation_level="AUTOCOMMIT")
                    conn.execute(
                        text("DELETE FROM public.profiles WHERE id = :id"),
                        {"id": user_id}
                    )
                    deleted = True
            except Exception as e:
                print(f"[Admin] Engine delete user note: {e}")

        # Step 3: Delete via Supabase REST API
        if sb:
            try:
                sb.table("profiles").delete().eq("id", user_id).execute()
                deleted = True
            except Exception as e:
                print(f"[Admin] Supabase REST delete profile note: {e}")

            try:
                sb.auth.admin.delete_user(user_id)
            except Exception as e:
                print(f"[Admin] Supabase auth.admin.delete_user notice: {e}")

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal menghapus pengguna: database tidak dapat dijangkau."
            )

        # Log admin activity
        log_activity_event(
            user_id=current_admin.get("id"),
            user_email=current_admin.get("email"),
            role=current_admin.get("role"),
            action="DELETE_USER",
            details={"target_user_id": user_id, "target_email": target_email},
            request=request
        )

        return {"message": f"Pengguna {target_email or user_id} berhasil dihapus."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Admin] Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menghapus user: {e}"
        )


@router.get("/activities")
def list_activities(
    limit: int = 50,
    action: Optional[str] = None,
    current_admin: Dict[str, Any] = Depends(require_role(["admin"]))
):
    """
    [ADMIN ONLY] Melihat Aktivitas: Audit trail / log aktivitas seluruh pengguna sistem.
    """
    activities = []
    try:
        query_sql = """
            SELECT id, user_id, user_email, role, action, details, ip_address, created_at
            FROM public.activity_logs
        """
        params: Dict[str, Any] = {"limit": limit}
        if action:
            query_sql += " WHERE action = :action"
            params["action"] = action
        query_sql += " ORDER BY created_at DESC LIMIT :limit"

        with engine.connect() as conn:
            rows = conn.execute(text(query_sql), params).fetchall()
            for r in rows:
                activities.append({
                    "id": str(r[0]),
                    "user_id": str(r[1]) if r[1] else None,
                    "user_email": r[2] or "Anonim / Sistem",
                    "role": r[3] or "GUEST",
                    "action": r[4],
                    "details": r[5] or {},
                    "ip_address": r[6],
                    "created_at": r[7].isoformat() if r[7] else None
                })
    except Exception as e:
        print(f"[Admin] Error fetching activity logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil log aktivitas: {e}"
        )

    return {
        "total": len(activities),
        "activities": activities
    }


@router.get("/reports")
def list_all_reports_for_admin(current_admin: Dict[str, Any] = Depends(require_role(["admin"]))):
    """
    [ADMIN ONLY] Melihat Laporan: Menampilkan seluruh laporan yang dibuat oleh semua pengguna.
    """
    reports = []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id, user_id, author_name, author_email, symbol, title, report_type,
                           recommendation, target_price, stop_loss, content, summary, is_public, created_at
                    FROM public.reports
                    ORDER BY created_at DESC
                """)
            ).fetchall()
            for r in rows:
                reports.append({
                    "id": str(r[0]),
                    "user_id": str(r[1]) if r[1] else None,
                    "author_name": r[2] or "Trader",
                    "author_email": r[3] or "",
                    "symbol": r[4],
                    "title": r[5],
                    "report_type": r[6],
                    "recommendation": r[7],
                    "target_price": float(r[8]) if r[8] is not None else None,
                    "stop_loss": float(r[9]) if r[9] is not None else None,
                    "content": r[10],
                    "summary": r[11] or {},
                    "is_public": bool(r[12]),
                    "created_at": r[13].isoformat() if r[13] else None
                })
    except Exception as e:
        print(f"[Admin] Error fetching all reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil laporan admin: {e}"
        )

    return {
        "total": len(reports),
        "reports": reports
    }
