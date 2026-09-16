from fastapi import APIRouter
from app.universe.stock_universe_manager import StockUniverseManager

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("/search")
def search_stocks(q: str = ""):
    """Search stock tickers across the stock_universe database."""
    all_stocks = StockUniverseManager.fetch_all_idx_stocks()
    q = q.strip().upper()
    if not q:
        return all_stocks[:50]
    return [
        s for s in all_stocks
        if q in s["symbol"].upper() or q in s.get("company_name", "").upper()
    ]

@router.get("/{symbol}")
def get_stock_detail(symbol: str):
    """Retrieve stock information from universe database."""
    item = StockUniverseManager.get_stock_by_symbol(symbol)
    return item or {"symbol": symbol, "status": "not_found"}
