import pandas as pd
from typing import Dict, Any


def evaluate_trend(df: pd.DataFrame, symbol: str = "") -> Dict[str, Any]:
    """
    Trend Screener:
    Rule:
      MA20 > MA50 > MA200 (Golden / Perfect Bullish Alignment)
    
    Score: 0 - 100
    """
    if df.empty or "Close" not in df.columns:
        return {
            "passed": False,
            "score": 0.0,
            "ma20": None,
            "ma50": None,
            "ma200": None,
            "alignment": "Insufficient Data",
            "details": "Insufficient price data to compute moving averages."
        }

    close = df["Close"]
    current_close = float(close.iloc[-1])

    # Moving averages
    ma20 = close.rolling(window=20, min_periods=1).mean().iloc[-1]
    ma50 = close.rolling(window=50, min_periods=1).mean().iloc[-1]
    ma200 = close.rolling(window=200, min_periods=1).mean().iloc[-1]

    ma20_val = round(float(ma20), 2)
    ma50_val = round(float(ma50), 2)
    ma200_val = round(float(ma200), 2)

    # Check the Golden Alignment rule: MA20 > MA50 > MA200
    perfect_bullish_alignment = (ma20_val > ma50_val) and (ma50_val > ma200_val)
    passed = perfect_bullish_alignment

    # Scoring (0 - 100)
    score = 0.0

    if perfect_bullish_alignment:
        if current_close > ma20_val:
            # 100 pts: Full uptrend + price trading above MA20
            score = 100.0
            alignment = "MA20 > MA50 > MA200 (Strong Bullish)"
            details = (
                f"STRONG UPTREND: Perfect Moving Average alignment "
                f"(MA20: {ma20_val:,.0f} > MA50: {ma50_val:,.0f} > MA200: {ma200_val:,.0f}) "
                f"and Price (Rp {current_close:,.0f}) is above MA20."
            )
        else:
            # 85 pts: MA alignment holds, but price is pulling back near MA20/50
            score = 85.0
            alignment = "MA20 > MA50 > MA200 (Bullish Pullback)"
            details = (
                f"BULLISH PULLBACK: Trend alignment is intact (MA20 > MA50 > MA200), "
                f"with Price (Rp {current_close:,.0f}) currently testing support."
            )
    elif ma20_val > ma50_val:
        if current_close > ma20_val:
            score = 65.0
            alignment = "MA20 > MA50 (Early Stage Bullish)"
            details = "Early Bullish: Short-term MA20 is above MA50, building upward momentum."
        else:
            score = 50.0
            alignment = "MA20 > MA50 (Consolidation)"
            details = "Neutral-Bullish: MA20 is above MA50, but consolidation is in progress."
    elif ma50_val > ma20_val and ma20_val > ma200_val:
        score = 40.0
        alignment = "Mixed / Correction"
        details = "Correction Mode: Price and short-term MA20 have dipped below MA50."
    elif ma20_val < ma50_val and ma50_val < ma200_val:
        score = 10.0
        alignment = "MA20 < MA50 < MA200 (Bearish Alignment)"
        details = "DOWNTREND: Bearish alignment across all major moving averages."
    else:
        score = 25.0
        alignment = "Sideways / Choppy"
        details = "Choppy / Mixed moving averages without clear trend direction."

    return {
        "passed": passed,
        "score": score,
        "ma20": ma20_val,
        "ma50": ma50_val,
        "ma200": ma200_val,
        "alignment": alignment,
        "details": details
    }
