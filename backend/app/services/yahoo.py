"""
Yahoo Finance Service — IDX80 Optimized
=========================================
All data fetching is restricted to IDX80 constituents only.
Uses batch download (yf.download) and in-memory caching to minimize API calls.
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.config.idx80_tickers import (
    IDX80_TICKERS,
    IDX80_METADATA,
    normalize_ticker,
    is_idx80,
    get_all_idx80_tickers,
)
from app.core.idx80_validator import validate_ticker, IDX80ValidationError
from app.services.data_cache import idx80_cache


# Backward compatibility — now returns only IDX80 tickers
DEFAULT_IHSG_SYMBOLS = list(IDX80_TICKERS)
normalize_symbol = normalize_ticker



def get_all_idx_symbols(limit: Optional[int] = None) -> List[str]:
    """Returns IDX80 tickers only."""
    tickers = get_all_idx80_tickers()
    if limit:
        return tickers[:limit]
    return tickers


def get_stock_metadata(symbol: str) -> Dict[str, str]:
    """Retrieves company name and sector from IDX80 metadata."""
    sym = normalize_ticker(symbol)
    meta = IDX80_METADATA.get(sym)
    if meta:
        return {
            "name": meta["company_name"],
            "sector": meta["sector"],
            "exchange": "IDX"
        }
    return {
        "name": sym.replace(".JK", ""),
        "sector": "IDX Equities",
        "exchange": "IDX"
    }


def get_stock_info(symbol: str) -> Dict[str, Any]:
    """
    Fetch current info and price for a single IDX80 stock.
    Uses cache to avoid redundant API calls.
    """
    sym = validate_ticker(symbol)  # IDX80 validation gate

    # Check cache first
    cached = idx80_cache.get_info(sym)
    if cached:
        return cached

    meta = get_stock_metadata(sym)

    current_price = 0.0
    previous_close = 0.0
    change = 0.0
    change_pct = 0.0
    volume = 0

    try:
        ticker = yf.Ticker(sym)
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
            info = ticker.info or {}
            current_price = float(info.get("currentPrice") or info.get("regularMarketPrice") or 0.0)
            previous_close = float(info.get("previousClose") or current_price)
            change = round(current_price - previous_close, 2)
            change_pct = round((change / previous_close * 100), 2) if previous_close > 0 else 0.0
            volume = int(info.get("regularMarketVolume") or info.get("volume") or 0)
    except Exception as e:
        print(f"[YahooService] Warning fetching info for {sym}: {e}")

    data = {
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

    # Store in cache
    idx80_cache.set_info(sym, data)
    return data


def get_all_stocks(symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Fetch overview list of IDX80 stocks."""
    if symbols:
        results = []
        for sym in symbols:
            normalized = normalize_ticker(sym)
            if is_idx80(normalized):
                results.append(get_stock_info(normalized))
        return results

    # Return full IDX80 universe with metadata
    from app.screener.batch_scanner_engine import BatchScannerEngine
    cached_prices = {r["symbol"]: r for r in BatchScannerEngine._RESULTS}

    results = []
    for ticker in IDX80_TICKERS:
        meta = IDX80_METADATA.get(ticker, {})
        cached = cached_prices.get(ticker)
        results.append({
            "symbol": ticker,
            "company_name": meta.get("company_name", ticker.replace(".JK", "")),
            "sector": meta.get("sector", "IDX Equities"),
            "board": "Utama",
            "exchange": "IDX",
            "market": "IDX80",
            "current_price": cached["price"] if cached else 0.0,
            "change_percentage": cached.get("change_percentage", 0.0) if cached else 0.0,
            "volume": cached.get("volume", 0) if cached else 0,
            "final_score": cached.get("final_score") if cached else None,
            "recommendation": cached.get("recommendation") if cached else None,
            "is_active": True,
            "updated_at": datetime.now().isoformat()
        })
    return results


def get_historical_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical OHLCV data for an IDX80 symbol.
    Uses cache to avoid redundant downloads.
    """
    sym = validate_ticker(symbol)  # IDX80 validation gate

    # Check cache first
    cached_df = idx80_cache.get_history(sym, period)
    if cached_df is not None and not cached_df.empty:
        return cached_df

    try:
        ticker = yf.Ticker(sym)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            df = ticker.history(period="6mo", interval=interval)

        if df.empty:
            return pd.DataFrame()

        df = df.reset_index()

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        elif "Datetime" in df.columns:
            df["Date"] = pd.to_datetime(df["Datetime"]).dt.strftime("%Y-%m-%d")

        core_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
        df = df[[c for c in core_cols if c in df.columns]]
        df["Open"] = df["Open"].round(2)
        df["High"] = df["High"].round(2)
        df["Low"] = df["Low"].round(2)
        df["Close"] = df["Close"].round(2)
        df["Volume"] = df["Volume"].astype(int)

        # Store in cache
        idx80_cache.set_history(sym, period, df)
        return pd.DataFrame(df)

    except IDX80ValidationError:
        raise
    except Exception as e:
        print(f"[YahooService] Error fetching history for {sym}: {e}")
        return pd.DataFrame()


def batch_download_idx80(
    tickers: Optional[List[str]] = None,
    period: str = "1y",
    interval: str = "1d"
) -> Dict[str, pd.DataFrame]:
    """
    Batch download historical data for multiple IDX80 tickers using yf.download().
    This is dramatically more efficient than individual downloads.

    Args:
        tickers: List of tickers to download. Defaults to all IDX80.
        period: Time period (e.g. "1y", "6mo").
        interval: Data interval (e.g. "1d", "1wk").

    Returns:
        Dict mapping each ticker to its OHLCV DataFrame.
    """
    target_tickers = tickers or IDX80_TICKERS

    # Only download tickers that are not already cached
    uncached_tickers = []
    cached_results: Dict[str, pd.DataFrame] = {}

    for t in target_tickers:
        cached_df = idx80_cache.get_history(t, period)
        if cached_df is not None and not cached_df.empty:
            cached_results[t] = cached_df
        else:
            uncached_tickers.append(t)

    results = dict(cached_results)

    if not uncached_tickers:
        print(f"[YahooService] All {len(target_tickers)} IDX80 tickers served from cache.")
        return results

    print(f"[YahooService] Batch downloading {len(uncached_tickers)} IDX80 tickers via yf.download()...")

    try:
        raw = yf.download(
            tickers=uncached_tickers,
            period=period,
            interval=interval,
            group_by="ticker",
            threads=True,
            progress=False
        )

        if raw is None or raw.empty:
            print("[YahooService] Batch download returned empty DataFrame.")
            return results

        for ticker in uncached_tickers:
            try:
                if len(uncached_tickers) == 1:
                    ticker_df = pd.DataFrame(raw).copy()
                else:
                    if hasattr(raw, "columns") and ticker in raw.columns.get_level_values(0):
                        ticker_df = pd.DataFrame(raw[ticker]).copy()
                    else:
                        continue

                ticker_df = ticker_df.dropna(how="all")
                if ticker_df.empty:
                    continue

                ticker_df = ticker_df.reset_index()

                if "Date" in ticker_df.columns:
                    ticker_df["Date"] = pd.to_datetime(ticker_df["Date"]).dt.strftime("%Y-%m-%d")
                elif "Datetime" in ticker_df.columns:
                    ticker_df["Date"] = pd.to_datetime(ticker_df["Datetime"]).dt.strftime("%Y-%m-%d")

                core_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
                ticker_df = ticker_df[[c for c in core_cols if c in ticker_df.columns]]

                for col in ["Open", "High", "Low", "Close"]:
                    if col in ticker_df.columns:
                        ticker_df[col] = ticker_df[col].round(2)
                if "Volume" in ticker_df.columns:
                    ticker_df["Volume"] = ticker_df["Volume"].fillna(0).astype(int)

                results[ticker] = pd.DataFrame(ticker_df)
                idx80_cache.set_history(ticker, period, results[ticker])

            except Exception as e:
                print(f"[YahooService] Error processing batch data for {ticker}: {e}")
                continue

        print(f"[YahooService] Batch download complete: {len(results)}/{len(target_tickers)} tickers retrieved.")

    except Exception as e:
        print(f"[YahooService] Batch download error: {e}")
        # Fallback: download individually for any remaining tickers
        for ticker in uncached_tickers:
            if ticker not in results:
                try:
                    t = yf.Ticker(ticker)
                    df = t.history(period=period, interval=interval)
                    if not df.empty:
                        df = df.reset_index()
                        if "Date" in df.columns:
                            df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
                        core_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
                        df = df[[c for c in core_cols if c in df.columns]]
                        df["Open"] = df["Open"].round(2)
                        df["High"] = df["High"].round(2)
                        df["Low"] = df["Low"].round(2)
                        df["Close"] = df["Close"].round(2)
                        df["Volume"] = df["Volume"].astype(int)
                        results[ticker] = pd.DataFrame(df)
                        idx80_cache.set_history(ticker, period, df)
                except Exception:
                    pass

    return results
