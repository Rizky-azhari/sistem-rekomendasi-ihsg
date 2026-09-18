import json
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from app.database.connection import engine
from app.core.security import get_current_user, require_role, log_activity_event
from sqlalchemy import text

router = APIRouter(dependencies=[Depends(require_role(["user", "admin"]))])


class CreateReportRequest(BaseModel):
    title: str
    symbol: str
    report_type: Optional[str] = "TECHNICAL_ANALYSIS"
    recommendation: Optional[str] = "BUY"
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    content: str
    summary: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = True


@router.get("")
def list_reports(
    symbol: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_role(["user", "admin"]))
):
    """
    [USER & ADMIN] Melihat Laporan: Menampilkan daftar laporan analisis saham.
    """
    reports = []
    try:
        query = """
            SELECT id, user_id, author_name, author_email, symbol, title, report_type,
                   recommendation, target_price, stop_loss, content, summary, is_public, created_at
            FROM public.reports
        """
        params: Dict[str, Any] = {}
        conditions = []

        if symbol:
            conditions.append("symbol = :symbol")
            params["symbol"] = symbol.upper()

        # Non-admin only sees public or own reports
        if str(current_user.get("role", "")).lower() != "admin":
            conditions.append("(is_public = TRUE OR user_id = :uid)")
            params["uid"] = current_user.get("id")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC"

        if not engine:
            return []

        with engine.connect() as conn:
            rows = conn.execute(text(query), params).fetchall()
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
        print(f"[Reports] Error fetching reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil laporan: {e}"
        )

    return {
        "total": len(reports),
        "reports": reports
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_report(
    payload: CreateReportRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(require_role(["USER", "ADMIN"]))
):
    """
    [USER & ADMIN] Membuat Laporan: Pengguna dapat membuat laporan analisis saham baru.
    """
    if not payload.title.strip():
        raise HTTPException(status_code=400, detail="Judul laporan tidak boleh kosong.")
    if not payload.symbol.strip():
        raise HTTPException(status_code=400, detail="Ticker saham tidak boleh kosong.")

    sym = payload.symbol.upper()
    if not sym.endswith(".JK") and len(sym) == 4:
        sym = f"{sym}.JK"

    if not engine:
        raise HTTPException(status_code=503, detail="Database engine tidak tersedia.")

    try:
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            res = conn.execute(
                text("""
                    INSERT INTO public.reports (
                        user_id, author_name, author_email, symbol, title, report_type,
                        recommendation, target_price, stop_loss, content, summary, is_public, created_at, updated_at
                    )
                    VALUES (
                        :uid, :author_name, :author_email, :symbol, :title, :report_type,
                        :rec, :target, :stop, :content, CAST(:summary AS jsonb), :is_public, NOW(), NOW()
                    )
                    RETURNING id, created_at
                """),
                {
                    "uid": current_user.get("id"),
                    "author_name": current_user.get("full_name") or current_user.get("email", "").split("@")[0],
                    "author_email": current_user.get("email"),
                    "symbol": sym,
                    "title": payload.title,
                    "report_type": payload.report_type or "TECHNICAL_ANALYSIS",
                    "rec": payload.recommendation or "BUY",
                    "target": payload.target_price,
                    "stop": payload.stop_loss,
                    "content": payload.content,
                    "summary": json.dumps(payload.summary or {}),
                    "is_public": payload.is_public if payload.is_public is not None else True
                }
            ).first()

            if res is None:
                raise HTTPException(status_code=500, detail="Gagal membuat laporan analisis saham.")

            report_id = str(res[0])
            created_at = res[1].isoformat()

        # Log activity
        log_activity_event(
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            role=current_user.get("role"),
            action="CREATE_REPORT",
            details={"report_id": report_id, "symbol": sym, "title": payload.title},
            request=request
        )

        return {
            "message": "Laporan analisis saham berhasil dibuat.",
            "report": {
                "id": report_id,
                "symbol": sym,
                "title": payload.title,
                "recommendation": payload.recommendation,
                "created_at": created_at
            }
        }
    except Exception as e:
        print(f"[Reports] Error creating report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat laporan: {e}"
        )


@router.delete("/{report_id}")
def delete_report(
    report_id: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(require_role(["USER", "ADMIN"]))
):
    """
    Menghapus laporan. Hanya pemilik laporan atau ADMIN yang diizinkan.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Database engine tidak tersedia.")

    try:
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            row = conn.execute(
                text("SELECT user_id, title, symbol FROM public.reports WHERE id = :id"),
                {"id": report_id}
            ).first()

            if not row:
                raise HTTPException(status_code=404, detail="Laporan tidak ditemukan.")

            owner_id = str(row[0]) if row[0] else None
            # Check permission: admin or owner
            if str(current_user.get("role", "")).lower() != "admin" and owner_id != current_user.get("id"):
                raise HTTPException(status_code=403, detail="Access Denied: Anda tidak memiliki hak untuk menghapus laporan ini.")

            conn.execute(text("DELETE FROM public.reports WHERE id = :id"), {"id": report_id})

        log_activity_event(
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            role=current_user.get("role"),
            action="DELETE_REPORT",
            details={"report_id": report_id, "title": row[1], "symbol": row[2]},
            request=request
        )

        return {"message": "Laporan berhasil dihapus."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Reports] Error deleting report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menghapus laporan: {e}"
        )
