import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def calculate_ma(series: pd.Series, window: int) -> pd.Series:
    """Calculate Simple Moving Average (SMA/MA) for a given window."""
    return pd.Series(series.rolling(window=window, min_periods=1).mean().round(2))


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate the Relative Strength Index (RSI) using standard Wilder's smoothing.
    Returns values bounded between 0.0 and 100.0.
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Wilder's exponential smoothing
    for i in range(period, len(series)):
        if pd.notna(gain.iloc[i]) and pd.notna(avg_gain.iloc[i - 1]):
            avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
        if pd.notna(loss.iloc[i]) and pd.notna(avg_loss.iloc[i - 1]):
            avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = pd.Series(100.0 - (100.0 / (1.0 + rs)))

    # Fill NaN values with neutral 50.0
    return pd.Series(rsi.fillna(50.0).round(2))


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate MA20, MA50, MA200, and RSI for a historical price DataFrame.
    Appends the calculated columns to the DataFrame.
    """
    if df.empty or "Close" not in df.columns:
        return df

    df = df.copy()
    close = pd.Series(df["Close"])

    # Calculate Moving Averages
    df["MA20"] = calculate_ma(close, window=20)
    df["MA50"] = calculate_ma(close, window=50)
    df["MA200"] = calculate_ma(close, window=200)

    # Calculate RSI (14)
    df["RSI"] = calculate_rsi(close, period=14)

    # Calculate 20-day annualized volatility
    pct_change = close.pct_change()
    df["volatility"] = (pct_change.rolling(window=20, min_periods=5).std() * np.sqrt(252)).fillna(0.0).round(4)

    return df


def extract_latest_indicators(df_with_indicators: pd.DataFrame) -> Dict[str, Optional[float]]:
    """Extract the most recent indicator values from the calculated DataFrame."""
    if df_with_indicators.empty:
        return {
            "harga_terakhir": None,
            "MA20": None,
            "MA50": None,
            "MA200": None,
            "RSI": None,
            "volatility": None
        }

    latest = df_with_indicators.iloc[-1]
    return {
        "harga_terakhir": float(latest["Close"]),
        "MA20": float(latest["MA20"]) if pd.notna(latest.get("MA20")) else None,
        "MA50": float(latest["MA50"]) if pd.notna(latest.get("MA50")) else None,
        "MA200": float(latest["MA200"]) if pd.notna(latest.get("MA200")) else None,
        "RSI": float(latest["RSI"]) if pd.notna(latest.get("RSI")) else 50.0,
        "volatility": float(latest["volatility"]) if pd.notna(latest.get("volatility")) else 0.0
    }


def get_technical_summary(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """Calculate and return standardized technical indicator JSON."""
    from app.indicators.technical_indicator import TechnicalIndicators
    return TechnicalIndicators.get_summary(df, symbol)

