import pandas as pd
import numpy as np
from typing import Dict, Any


def evaluate_oversold(df: pd.DataFrame, symbol: str = "") -> Dict[str, Any]:
    """
    Oversold Screener:
    Rule:
      1. RSI < 35
      2. Harga mendekati support (within 3% of 20-day swing low or lower Bollinger Band)
    
    Score: 0 - 100
    """
    if df.empty or "Close" not in df.columns or len(df) < 14:
        return {
            "passed": False,
            "score": 0.0,
            "rsi": None,
            "support_level": None,
            "distance_to_support_pct": None,
            "details": "Insufficient data to compute RSI and support."
        }

    close = df["Close"]
    low = df["Low"] if "Low" in df.columns else close
    current_close = float(close.iloc[-1])

    # 1. Calculate RSI 14 (Wilder's method)
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()

    for i in range(14, len(close)):
        if pd.notna(gain.iloc[i]) and pd.notna(avg_gain.iloc[i - 1]):
            avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * 13 + gain.iloc[i]) / 14
        if pd.notna(loss.iloc[i]) and pd.notna(avg_loss.iloc[i - 1]):
            avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * 13 + loss.iloc[i]) / 14

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_series = 100.0 - (100.0 / (1.0 + rs))
    rsi = float(rsi_series.iloc[-1]) if pd.notna(rsi_series.iloc[-1]) else 50.0
    rsi = round(rsi, 2)

    # 2. Support Level Identification
    # Support = lowest low of the last 20 days (excluding today) or lower Bollinger Band
    recent_lows = low.iloc[-21:-1] if len(low) > 21 else low.iloc[:-1]
    swing_support = float(recent_lows.min()) if not recent_lows.empty else current_close * 0.95
    
    # Also check lower Bollinger band (20, 2)
    bb_mean = close.rolling(window=20, min_periods=1).mean().iloc[-1]
    bb_std = close.rolling(window=20, min_periods=1).std().iloc[-1]
    bb_lower = float(bb_mean - (2 * bb_std)) if pd.notna(bb_std) else swing_support

    key_support = round(max(swing_support, bb_lower), 2)

    # Distance to support in percentage
    # If price is at or just slightly above support (0% to 3%), it's "near support"
    distance_to_support_pct = round(((current_close - key_support) / key_support) * 100, 2)
    is_near_support = -1.5 <= distance_to_support_pct <= 3.0

    is_oversold_rsi = rsi < 35.0
    passed = is_oversold_rsi and is_near_support

    # Scoring (0 - 100)
    score = 0.0

    # RSI Component (Max 55 pts)
    if rsi <= 25.0:
        score += 55.0  # Extreme oversold
    elif rsi < 30.0:
        score += 48.0
    elif rsi < 35.0:
        score += 40.0
    elif rsi < 40.0:
        score += 25.0
    elif rsi < 50.0:
        score += 15.0
    else:
        score += 5.0

    # Support Proximity Component (Max 45 pts)
    if 0.0 <= distance_to_support_pct <= 1.5:
        score += 45.0  # Right on top of strong support
    elif 1.5 < distance_to_support_pct <= 3.0:
        score += 38.0
    elif -1.5 <= distance_to_support_pct < 0.0:
        score += 35.0  # Testing slightly below support (shakeout zone)
    elif 3.0 < distance_to_support_pct <= 5.0:
        score += 20.0
    else:
        score += max(0.0, 15.0 - (distance_to_support_pct * 1.5))

    score = round(max(0.0, min(100.0, score)), 1)

    if passed:
        details = (
            f"HIGH-PROBABILITY OVERSOLD BOUNCE: RSI ({rsi}) is in deep oversold territory (< 35) "
            f"and Price (Rp {current_close:,.0f}) is hovering right near support (Rp {key_support:,.0f}, {distance_to_support_pct}% away)."
        )
    elif is_oversold_rsi:
        details = f"Oversold RSI ({rsi} < 35), but price is still {distance_to_support_pct}% above nearest key support."
    elif is_near_support:
        details = f"Price is testing key support (Rp {key_support:,.0f}), but RSI ({rsi}) has not reached oversold levels."
    else:
        details = f"Normal Zone: RSI is at {rsi} and price is {distance_to_support_pct}% away from support."

    return {
        "passed": passed,
        "score": score,
        "rsi": rsi,
        "support_level": key_support,
        "distance_to_support_pct": distance_to_support_pct,
        "details": details
    }
