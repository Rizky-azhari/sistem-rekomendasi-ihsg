"""
YFinance Service — IDX80 Optimized
====================================
Wrapper service for Yahoo Finance with IDX80 validation and caching.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import datetime

from app.config.idx80_tickers import normalize_ticker, is_idx80, IDX80_METADATA
from app.core.idx80_validator import validate_ticker, IDX80ValidationError
from app.services.data_cache import idx80_cache

normalize_symbol = normalize_ticker


# Cache dict for ticker info to avoid excessive rate limiting
_INFO_CACHE: Dict[str, Dict[str, Any]] = {}


def fetch_stock_info(symbol: str) -> Dict[str, Any]:
    """Fetch stock info with IDX80 validation and caching."""
    symbol = validate_ticker(symbol)  # IDX80 validation gate

    # Check IDX80 data cache first
    cached = idx80_cache.get_info(symbol)
    if cached:
        return cached

    # Check local info cache
    if symbol in _INFO_CACHE:
        return _INFO_CACHE[symbol]

    # Get metadata from IDX80 config
    meta = IDX80_METADATA.get(symbol, {})

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or 0.0
        prev_close = info.get("previousClose") or current_price
        change_amt = current_price - prev_close
        change_pct = (change_amt / prev_close * 100) if prev_close > 0 else 0.0

        data = {
            "symbol": symbol,
            "name": meta.get("company_name") or info.get("longName") or info.get("shortName") or symbol.replace(".JK", ""),
            "sector": meta.get("sector") or info.get("sector", "IDX Equities"),
            "industry": info.get("industry", "Indonesian Market"),
            "current_price": float(current_price),
            "previous_close": float(prev_close),
            "change_amount": round(float(change_amt), 2),
            "change_percentage": round(float(change_pct), 2),
            "volume": int(info.get("regularMarketVolume") or info.get("volume") or 0),
            "market_cap": info.get("marketCap")
        }
        _INFO_CACHE[symbol] = data
        idx80_cache.set_info(symbol, data)
        return data
    except IDX80ValidationError:
        raise
    except Exception as e:
        print(f"Error fetching info for {symbol}: {e}")
        return {
            "symbol": symbol,
            "name": meta.get("company_name") or symbol.replace(".JK", ""),
            "sector": meta.get("sector") or "IDX Equities",
            "industry": "Indonesian Market",
            "current_price": 0.0,
            "previous_close": 0.0,
            "change_amount": 0.0,
            "change_percentage": 0.0,
            "volume": 0,
            "market_cap": None
        }


def fetch_stock_history(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch stock history with IDX80 validation and caching."""
    symbol = validate_ticker(symbol)  # IDX80 validation gate

    # Check cache first
    cached_df = idx80_cache.get_history(symbol, period)
    if cached_df is not None and not cached_df.empty:
        return cached_df

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            df = generate_mock_history(symbol)
        else:
            df.reset_index(inplace=True)
            if 'Date' in df.columns:
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            elif 'Datetime' in df.columns:
                df['Date'] = df['Datetime'].dt.strftime('%Y-%m-%d')

        # Cache the result
        if not df.empty:
            idx80_cache.set_history(symbol, period, df)

    except IDX80ValidationError:
        raise
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        df = generate_mock_history(symbol)
    return df


def generate_mock_history(symbol: str, days: int = 250) -> pd.DataFrame:
    """Generates realistic synthetic stock data for testing or offline fallbacks."""
    end_date = datetime.date.today()
    dates = [(end_date - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in reversed(range(days))]

    np.random.seed(abs(hash(symbol)) % (2**32))
    base_price = 5000.0 if "BBCA" in symbol else (3000.0 if "TLKM" in symbol else 1000.0)

    returns = np.random.normal(0.0005, 0.015, days)
    price_series = base_price * np.exp(np.cumsum(returns))

    records = []
    for date, close in zip(dates, price_series):
        high = close * (1 + abs(np.random.normal(0, 0.008)))
        low = close * (1 - abs(np.random.normal(0, 0.008)))
        open_price = low + (high - low) * np.random.random()
        volume = int(np.random.uniform(500000, 10000000))
        records.append({
            "Date": date,
            "Open": round(float(open_price), 2),
            "High": round(float(high), 2),
            "Low": round(float(low), 2),
            "Close": round(float(close), 2),
            "Volume": volume
        })
    return pd.DataFrame(records)


class YFinanceService:
    @staticmethod
    def get_info(symbol: str):
        return fetch_stock_info(symbol)

    @staticmethod
    def get_history(symbol: str, period: str = "1y", interval: str = "1d"):
        return fetch_stock_history(symbol, period=period, interval=interval)

    @staticmethod
    def normalize(symbol: str):
        return normalize_ticker(symbol)
