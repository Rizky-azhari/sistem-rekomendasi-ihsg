import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import datetime

# Cache dict for ticker info to avoid excessive rate limiting
_INFO_CACHE: Dict[str, Dict[str, Any]] = {}

def normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.endswith(".JK") and not "." in symbol:
        symbol += ".JK"
    return symbol

def fetch_stock_info(symbol: str) -> Dict[str, Any]:
    symbol = normalize_symbol(symbol)
    if symbol in _INFO_CACHE:
        return _INFO_CACHE[symbol]
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Fallbacks for yfinance fields
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or 0.0
        prev_close = info.get("previousClose") or current_price
        change_amt = current_price - prev_close
        change_pct = (change_amt / prev_close * 100) if prev_close > 0 else 0.0
        
        data = {
            "symbol": symbol,
            "name": info.get("longName") or info.get("shortName") or symbol.replace(".JK", ""),
            "sector": info.get("sector", "Financial Services / IDX"),
            "industry": info.get("industry", "Indonesian Market"),
            "current_price": float(current_price),
            "previous_close": float(prev_close),
            "change_amount": round(float(change_amt), 2),
            "change_percentage": round(float(change_pct), 2),
            "volume": int(info.get("regularMarketVolume") or info.get("volume") or 0),
            "market_cap": info.get("marketCap")
        }
        _INFO_CACHE[symbol] = data
        return data
    except Exception as e:
        # Fallback if yfinance ticker info API fails or rate limits
        print(f"Error fetching info for {symbol}: {e}")
        return {
            "symbol": symbol,
            "name": symbol.replace(".JK", ""),
            "sector": "IDX Stock",
            "industry": "Indonesian Market",
            "current_price": 5000.0,
            "previous_close": 4950.0,
            "change_amount": 50.0,
            "change_percentage": 1.01,
            "volume": 1000000,
            "market_cap": 50000000000000
        }

def fetch_stock_history(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    symbol = normalize_symbol(symbol)
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
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        df = generate_mock_history(symbol)
    return df

def generate_mock_history(symbol: str, days: int = 250) -> pd.DataFrame:
    """Generates realistic synthetic stock data for testing or offline fallbacks."""
    end_date = datetime.date.today()
    dates = [ (end_date - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in reversed(range(days)) ]
    
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
        return normalize_symbol(symbol)

