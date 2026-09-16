import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

# Dynamic stock retrieval from StockUniverseManager
def get_all_idx_symbols(limit: Optional[int] = None) -> List[str]:
    """Dynamically retrieves active IDX tickers from StockUniverseManager."""
    try:
        from app.universe.stock_universe_manager import StockUniverseManager
        return StockUniverseManager.get_active_symbols(limit=limit)
    except Exception:
        # Emergency fallback if module is loading
        return [
            "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK",
            "TLKM.JK", "ASII.JK", "GOTO.JK", "ICBP.JK"
        ]


# Backward compatibility dynamic symbol list
DEFAULT_IHSG_SYMBOLS = get_all_idx_symbols()


def get_stock_metadata(symbol: str) -> Dict[str, str]:
    """Dynamically retrieves company name and sector from Stock Universe."""
    sym = normalize_symbol(symbol)
    try:
        from app.universe.stock_universe_manager import StockUniverseManager
        item = StockUniverseManager.get_stock_by_symbol(sym)
        if item:
            return {
                "name": item.get("company_name") or sym.replace(".JK", ""),
                "sector": item.get("sector") or "IDX Equities",
                "exchange": "IDX"
            }
    except Exception:
        pass

    return {
        "name": sym.replace(".JK", ""),
        "sector": "IDX Equities",
        "exchange": "IDX"
    }



def normalize_symbol(symbol: str) -> str:
    """Normalize user input to standard IDX ticker format (e.g. BBCA -> BBCA.JK)."""
    cleaned = symbol.strip().upper()
    if not cleaned.endswith(".JK") and "." not in cleaned:
        cleaned += ".JK"
    return cleaned


def get_stock_info(symbol: str) -> Dict[str, Any]:
    """Fetch current info and price for a single stock from Yahoo Finance."""
    sym = normalize_symbol(symbol)
    meta = get_stock_metadata(sym)
    
    current_price = 0.0
    previous_close = 0.0
    change = 0.0
    change_pct = 0.0
    volume = 0

    try:
        ticker = yf.Ticker(sym)
        # Fetch fast history for the last 5 days to guarantee valid close and previous close
        hist = ticker.history(period="5d")
        if not hist.empty:
            current_price = float(hist["Close"].iloc[-1])
            if len(hist) > 1:
                previous_close = float(hist["Close"].iloc[-2])
            else:
                previous_close = current_price

            change = round(current_price - previous_close, 2)
            change_pct = round((change / previous_close * 100), 2) if previous_close > 0 else 0.0
            volume = int(hist["Volume"].iloc[-1])
        else:
            # Fallback to info dict
            info = ticker.info or {}
            current_price = float(info.get("currentPrice") or info.get("regularMarketPrice") or 0.0)
            previous_close = float(info.get("previousClose") or current_price)
            change = round(current_price - previous_close, 2)
            change_pct = round((change / previous_close * 100), 2) if previous_close > 0 else 0.0
            volume = int(info.get("regularMarketVolume") or info.get("volume") or 0)
    except Exception as e:
        print(f"[YahooService] Warning fetching info for {sym}: {e}")

    return {
        "symbol": sym,
        "company_name": meta["name"],
        "sector": meta["sector"],
        "exchange": meta["exchange"],
        "current_price": current_price,
        "previous_close": previous_close,
        "change": change,
        "change_percentage": change_pct,
        "volume": volume,
        "updated_at": datetime.now().isoformat()
    }


def get_all_stocks(symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Fetch overview list of stocks."""
    if symbols:
        results = []
        for sym in symbols:
            results.append(get_stock_info(sym))
        return results

    # Return full universe with cached prices if available
    try:
        from app.universe.stock_universe_manager import StockUniverseManager
        from app.screener.batch_scanner_engine import BatchScannerEngine
        universe = StockUniverseManager.fetch_all_idx_stocks()
        cached_prices = {r["symbol"]: r for r in BatchScannerEngine._RESULTS}

        results = []
        for s in universe:
            sym = s["symbol"]
            cached = cached_prices.get(sym)
            results.append({
                "symbol": sym,
                "company_name": s.get("company_name") or sym.replace(".JK", ""),
                "sector": s.get("sector") or "IDX Equities",
                "board": s.get("board") or "Utama",
                "exchange": "IDX",
                "current_price": cached["price"] if cached else 0.0,
                "change_percentage": cached.get("change_percentage", 0.0) if cached else 0.0,
                "volume": cached.get("volume", 0) if cached else 0,
                "final_score": cached.get("final_score") if cached else None,
                "recommendation": cached.get("recommendation") if cached else None,
                "is_active": s.get("is_active", True),
                "updated_at": datetime.now().isoformat()
            })
        return results
    except Exception as e:
        print(f"[YahooService] Fallback in get_all_stocks: {e}")
        return [get_stock_info(s) for s in ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK"]]


def get_historical_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a symbol from Yahoo Finance as a pandas DataFrame.
    Guarantees standard columns: Date, Open, High, Low, Close, Volume.
    """
    sym = normalize_symbol(symbol)
    ticker = yf.Ticker(sym)
    df = ticker.history(period=period, interval=interval)

    if df.empty:
        # Fallback period if 1y is empty
        df = ticker.history(period="6mo", interval=interval)

    if df.empty:
        return pd.DataFrame()

    df = df.reset_index()

    # Normalize Date column
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    elif "Datetime" in df.columns:
        df["Date"] = pd.to_datetime(df["Datetime"]).dt.strftime("%Y-%m-%d")

    # Keep and round core OHLCV columns
    core_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
    df = df[[c for c in core_cols if c in df.columns]]
    df["Open"] = df["Open"].round(2)
    df["High"] = df["High"].round(2)
    df["Low"] = df["Low"].round(2)
    df["Close"] = df["Close"].round(2)
    df["Volume"] = df["Volume"].astype(int)

    return df
