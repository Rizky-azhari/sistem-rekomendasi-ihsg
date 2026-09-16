from fastapi import APIRouter

router = APIRouter(prefix="/screener", tags=["screener"])

@router.get("")
def screen_stocks(signal: str = None, min_score: float = None):
    """Placeholder endpoint for IHSG stock screener."""
    return []
