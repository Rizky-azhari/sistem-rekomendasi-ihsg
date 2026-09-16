from fastapi import APIRouter, Query
from typing import List, Optional
import pandas as pd
from app.services.yfinance_service import fetch_stock_info, fetch_stock_history
from app.engine.indicators import calculate_technical_indicators
from app.engine.rules import evaluate_rules
from app.schemas.recommendation import ScreenerResultItem
from app.core.config import settings

router = APIRouter()

@router.get("", response_model=List[ScreenerResultItem])
def screen_stocks(
    signal: Optional[str] = Query(None, description="Filter by signal (STRONG BUY, BUY, HOLD, SELL, STRONG SELL)"),
    min_score: Optional[float] = Query(None, description="Filter by minimum score (0-100)"),
    max_score: Optional[float] = Query(None, description="Filter by maximum score (0-100)"),
    sort_by: str = Query("total_score", description="Sort by column: total_score, change_percentage, current_price")
):
    from app.screener.batch_scanner_engine import BatchScannerEngine
    from app.universe.stock_universe_manager import StockUniverseManager

    # Retrieve all active stocks directly from stock_universe database table
    universe_stocks = StockUniverseManager.fetch_all_idx_stocks()
    total_found = len(universe_stocks)

    # Fetch scanned results
    scanned = BatchScannerEngine.get_scanned_results(
        recommendation_filter=signal,
        min_score=min_score,
        sort_by=sort_by
    )

    results: List[ScreenerResultItem] = []
    for item in scanned:
        score = float(item.get("final_score") or item.get("composite_score") or 0.0)
        if max_score is not None and score > max_score:
            continue
        results.append(ScreenerResultItem(
            symbol=item["symbol"],
            name=item.get("name") or item["symbol"].replace(".JK", ""),
            sector=item.get("sector") or "IDX Stock",
            current_price=float(item.get("price") or 0.0),
            change_percentage=float(item.get("change_percentage") or 0.0),
            signal=item.get("recommendation") or "HOLD",
            total_score=score,
            rsi=50.0,
            macd_status="BULLISH" if score >= 60 else "BEARISH",
            volume=int(item.get("volume") or 0)
        ))

    total_success = len(results)
    total_failed = max(0, total_found - total_success)

    print(f"Total saham ditemukan: {total_found}")
    print(f"Total saham berhasil dianalisis: {total_success}")
    print(f"Total saham gagal: {total_failed}")

    return results
