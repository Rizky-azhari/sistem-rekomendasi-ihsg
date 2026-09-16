from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import pandas as pd
from app.services.yfinance_service import fetch_stock_info, fetch_stock_history, normalize_symbol
from app.engine.indicators import calculate_technical_indicators
from app.schemas.stock import StockDetailResponse, StockInfo, OHLCVData, IndicatorData
from app.core.config import settings

router = APIRouter()

def get_all_universe_stocks() -> List[Dict[str, Any]]:
    """Fetches all active IDX stocks from stock_universe database table."""
    try:
        from app.universe.stock_universe_manager import StockUniverseManager
        universe = StockUniverseManager.fetch_all_idx_stocks()
        return [
            {
                "symbol": s["symbol"],
                "name": s.get("company_name") or s["symbol"].replace(".JK", ""),
                "sector": s.get("sector") or "IDX Equities",
                "board": s.get("board") or "Utama",
                "is_active": s.get("is_active", True)
            }
            for s in universe if s.get("is_active", True)
        ]
    except Exception as e:
        print(f"[StocksAPI] Warning loading stock_universe database: {e}")
        return []

@router.get("", response_model=List[Dict[str, Any]])
def list_all_stocks():
    """List all available IHSG stocks from stock_universe database."""
    from app.services.yahoo import get_all_stocks
    return get_all_stocks()


@router.get("/search", response_model=List[Dict[str, Any]])
def search_stocks(q: str = Query("", description="Search term for ticker symbol or name")):
    all_stocks = get_all_universe_stocks()
    q = q.strip().upper()
    if not q:
        return all_stocks[:50]
    
    results = [
        item for item in all_stocks
        if q in item["symbol"].upper() or q in item["name"].upper()
    ]
    if not results and len(q) >= 3:
        sym = normalize_symbol(q)
        results = [{"symbol": sym, "name": sym.replace(".JK", ""), "sector": "IDX Stock", "board": "Utama", "is_active": True}]
    return results

@router.get("/{symbol}", response_model=StockDetailResponse)
def get_stock_detail(symbol: str, period: str = Query("1y", description="Time period e.g. 1mo, 3mo, 6mo, 1y")):
    sym = normalize_symbol(symbol)
    info_raw = fetch_stock_info(sym)
    df_raw = fetch_stock_history(sym, period=period)
    
    if df_raw.empty:
        raise HTTPException(status_code=404, detail=f"No price history found for symbol {sym}")
        
    df_ind = calculate_technical_indicators(df_raw)
    
    info = StockInfo(**info_raw)
    
    ohlcv_list = [
        OHLCVData(
            date=row['Date'],
            open=float(row['Open']),
            high=float(row['High']),
            low=float(row['Low']),
            close=float(row['Close']),
            volume=int(row['Volume'])
        ) for _, row in df_raw.iterrows()
    ]
    
    indicators_list = [
        IndicatorData(
            date=row['Date'],
            close=float(row['Close']),
            sma20=float(row['SMA20']) if not pd.isna(row['SMA20']) else None,
            sma50=float(row['SMA50']) if not pd.isna(row['SMA50']) else None,
            sma200=float(row['SMA200']) if not pd.isna(row['SMA200']) else None,
            ema12=float(row['EMA12']) if not pd.isna(row['EMA12']) else None,
            ema26=float(row['EMA26']) if not pd.isna(row['EMA26']) else None,
            rsi14=float(row['RSI14']) if not pd.isna(row['RSI14']) else None,
            macd=float(row['MACD']) if not pd.isna(row['MACD']) else None,
            macd_signal=float(row['MACD_Signal']) if not pd.isna(row['MACD_Signal']) else None,
            macd_hist=float(row['MACD_Hist']) if not pd.isna(row['MACD_Hist']) else None,
            bb_upper=float(row['BB_Upper']) if not pd.isna(row['BB_Upper']) else None,
            bb_middle=float(row['BB_Middle']) if not pd.isna(row['BB_Middle']) else None,
            bb_lower=float(row['BB_Lower']) if not pd.isna(row['BB_Lower']) else None,
            atr14=float(row['ATR14']) if not pd.isna(row['ATR14']) else None,
            vol_sma20=float(row['Vol_SMA20']) if not pd.isna(row['Vol_SMA20']) else None,
        ) for _, row in df_ind.iterrows()
    ]
    
    return StockDetailResponse(info=info, ohlcv=ohlcv_list, indicators=indicators_list)

@router.get("/{symbol}/info", response_model=StockInfo)
def get_stock_info(symbol: str):
    sym = normalize_symbol(symbol)
    info_dict = fetch_stock_info(sym)
    return StockInfo(**info_dict)
