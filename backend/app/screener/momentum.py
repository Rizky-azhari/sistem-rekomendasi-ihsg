import pandas as pd
from typing import Dict, Any


def evaluate_momentum(df: pd.DataFrame, symbol: str = "") -> Dict[str, Any]:
    """
    Momentum Screener:
    Rule:
      1. Close > MA20
      2. Volume > average volume 20 hari (Vol_SMA20)
    
    Score: 0 - 100
    """
    if df.empty or "Close" not in df.columns or "Volume" not in df.columns:
        return {
            "passed": False,
            "score": 0.0,
            "close": None,
            "ma20": None,
            "volume": None,
            "avg_volume_20": None,
            "volume_ratio": 0.0,
            "details": "Insufficient price/volume data."
        }

    close = df["Close"]
    volume = df["Volume"]

    # 20-day Moving Averages
    ma20 = close.rolling(window=20, min_periods=1).mean().iloc[-1]
    vol_sma20 = volume.rolling(window=20, min_periods=1).mean().iloc[-1]

    current_close = float(close.iloc[-1])
    current_vol = float(volume.iloc[-1])
    ma20_val = round(float(ma20), 2)
    vol_sma20_val = round(float(vol_sma20), 2)

    vol_ratio = round((current_vol / vol_sma20_val), 2) if vol_sma20_val > 0 else 1.0

    # Check conditions
    cond_price_above_ma20 = current_close > ma20_val
    cond_volume_above_avg = current_vol > vol_sma20_val
    passed = cond_price_above_ma20 and cond_volume_above_avg

    # Calculate Score (0 - 100)
    score = 0.0

    # 1. Price vs MA20 Component (Max 50 pts)
    if cond_price_above_ma20:
        pct_above_ma20 = ((current_close - ma20_val) / ma20_val) * 100
        # 40 base + up to 10 bonus for healthy cushion (1% - 5% above MA20)
        score += min(50.0, 40.0 + min(10.0, pct_above_ma20 * 2))
    else:
        # Penalty if below MA20
        pct_below = ((ma20_val - current_close) / ma20_val) * 100
        score += max(0.0, 30.0 - (pct_below * 5))

    # 2. Volume Component (Max 50 pts)
    if cond_volume_above_avg:
        # Base 35 pts + scaled bonus up to 15 pts for strong volume ratio
        score += min(50.0, 35.0 + min(15.0, (vol_ratio - 1.0) * 15))
    else:
        score += max(0.0, vol_ratio * 25.0)

    score = round(max(0.0, min(100.0, score)), 1)

    if passed:
        details = (
            f"BULLISH MOMENTUM: Close (Rp {current_close:,.0f}) is above MA20 (Rp {ma20_val:,.0f}) "
            f"with above-average volume surge ({vol_ratio}x vs 20-day avg)."
        )
    elif cond_price_above_ma20:
        details = f"Moderate Momentum: Close is above MA20, but volume is below 20-day average ({vol_ratio}x)."
    elif cond_volume_above_avg:
        details = f"Weak Momentum: High volume ({vol_ratio}x), but Close is below MA20."
    else:
        details = "Negative Momentum: Close is below MA20 and volume is below average."

    return {
        "passed": passed,
        "score": score,
        "close": current_close,
        "ma20": ma20_val,
        "volume": int(current_vol),
        "avg_volume_20": int(vol_sma20_val),
        "volume_ratio": vol_ratio,
        "details": details
    }
