from typing import Optional
from fastapi import APIRouter

router = APIRouter(prefix="/screener", tags=["screener"])

@router.get("")
def screen_stocks(signal: Optional[str] = None, min_score: Optional[float] = None):
    """Placeholder endpoint for IHSG stock screener."""
    return []
