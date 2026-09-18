from fastapi import APIRouter

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/{symbol}")
def get_recommendation(symbol: str):
    """Placeholder endpoint for rule-based recommendation & trading plan."""
    return {"symbol": symbol, "recommendation": "HOLD", "score": 50.0}
