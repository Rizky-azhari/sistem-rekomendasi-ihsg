import pandas as pd
from typing import Dict, Any


def evaluate_breakout(df: pd.DataFrame, symbol: str = "") -> Dict[str, Any]:
    """
    Breakout Screener:
    Rule:
      Close > Highest High 20 hari (Donchian 20-day High Breakout)
    
    Score: 0 - 100
    """
    if df.empty or "Close" not in df.columns or len(df) < 20:
        return {
            "passed": False,
            "score": 0.0,
            "close": None,
            "highest_high_20": None,
            "breakout_pct": 0.0,
            "volume_surge": False,
            "details": "Insufficient historical data for 20-day high calculation."
        }

    close = df["Close"]
    high = df["High"] if "High" in df.columns else close
    volume = df["Volume"] if "Volume" in df.columns else None

    current_close = float(close.iloc[-1])

    # 20-day Highest High EXCLUDING today's bar
    prior_20_highs = high.iloc[-21:-1] if len(high) > 21 else high.iloc[:-1]
    highest_high_20 = round(float(prior_20_highs.max()), 2)

    # Check breakout
    is_breakout = current_close > highest_high_20
    passed = is_breakout

    # Breakout percentage relative to 20-day high
    breakout_pct = round(((current_close - highest_high_20) / highest_high_20) * 100, 2)

    # Check if accompanied by volume surge (Volume > 1.5x 20-day avg)
    volume_surge = False
    vol_ratio = 1.0
    if volume is not None and len(volume) >= 20:
        vol_sma20 = float(volume.iloc[-21:-1].mean())
        cur_vol = float(volume.iloc[-1])
        vol_ratio = round((cur_vol / vol_sma20), 2) if vol_sma20 > 0 else 1.0
        volume_surge = vol_ratio >= 1.5

    # Scoring (0 - 100)
    score = 0.0

    if is_breakout:
        if volume_surge:
            # 100 pts: Confirmed breakout with massive volume surge
            score = 100.0
            details = (
                f"CONFIRMED HIGH-VOLUME BREAKOUT: Close (Rp {current_close:,.0f}) has broken above "
                f"20-day Highest High (Rp {highest_high_20:,.0f}) by +{breakout_pct}% with heavy volume surge ({vol_ratio}x avg)."
            )
        else:
            # 85 pts: Clean breakout, but normal volume
            score = 85.0
            details = (
                f"PRICE BREAKOUT: Close (Rp {current_close:,.0f}) broke above 20-day Highest High "
                f"(Rp {highest_high_20:,.0f}) by +{breakout_pct}%. Watch for volume follow-through."
            )
    elif -1.0 <= breakout_pct < 0.0:
        # 70 pts: Right at the resistance brink (within 1% of breakout)
        score = 70.0
        details = (
            f"TESTING BREAKOUT LEVEL: Close (Rp {current_close:,.0f}) is testing 20-day high "
            f"(Rp {highest_high_20:,.0f}), just {abs(breakout_pct)}% below resistance."
        )
    elif -3.0 <= breakout_pct < -1.0:
        # 50 pts: Consolidating closely near the high
        score = 50.0
        details = (
            f"Consolidating near 20-day high (Rp {highest_high_20:,.0f}), {abs(breakout_pct)}% away."
        )
    else:
        # Scaled down based on distance from 20-day high
        score = max(0.0, round(40.0 - abs(breakout_pct) * 2, 1))
        details = f"Below Breakout: Price is {abs(breakout_pct)}% below 20-day highest high (Rp {highest_high_20:,.0f})."

    return {
        "passed": passed,
        "score": score,
        "close": current_close,
        "highest_high_20": highest_high_20,
        "breakout_pct": breakout_pct,
        "volume_surge": volume_surge,
        "details": details
    }
