import pandas as pd
from typing import Dict, Any


def evaluate_trading_setup(df: pd.DataFrame, symbol: str = "") -> Dict[str, Any]:
    """
    Trading Setup Screener:
    Rule:
      Risk Reward Ratio >= 1:2 (Potential Reward / Risk >= 2.0)
    
    Score: 0 - 100
    """
    if df.empty or "Close" not in df.columns or len(df) < 14:
        return {
            "passed": False,
            "score": 0.0,
            "entry_price": None,
            "stop_loss": None,
            "target_price": None,
            "risk": 0.0,
            "reward": 0.0,
            "risk_reward_ratio": 0.0,
            "risk_reward_formatted": "N/A",
            "details": "Insufficient data to compute trading setup."
        }

    close = df["Close"]
    high = df["High"] if "High" in df.columns else close
    low = df["Low"] if "Low" in df.columns else close

    current_price = float(close.iloc[-1])

    # 1. Estimate ATR (14-day) for dynamic volatility stop
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    atr = float(tr.rolling(window=14, min_periods=1).mean().iloc[-1])
    if pd.isna(atr) or atr <= 0:
        atr = current_price * 0.025  # Fallback 2.5%

    # 2. Stop Loss calculation:
    # Nearest 20-day swing low or 1.5x ATR below current price
    recent_low = float(low.iloc[-20:].min()) if len(low) >= 20 else current_price * 0.96
    atr_stop = current_price - (1.5 * atr)
    
    # Take the safer (higher) stop loss, but at least 2% and at most 8% below entry
    stop_loss = max(recent_low, atr_stop)
    if (current_price - stop_loss) < (current_price * 0.02):
        stop_loss = current_price * 0.98  # minimum 2% risk buffer
    elif (current_price - stop_loss) > (current_price * 0.08):
        stop_loss = current_price * 0.92  # cap risk at 8%

    stop_loss = round(stop_loss, 2)
    risk = round(current_price - stop_loss, 2)

    # 3. Target Price (Resistance) calculation:
    # Target 1 = Recent 20-day / 50-day swing high or multiple of risk
    recent_high = float(high.iloc[-50:].max()) if len(high) >= 50 else float(high.max())
    
    # If recent high is above current price by a healthy margin, use it, else project 2x to 3x risk
    if recent_high > current_price and (recent_high - current_price) >= (risk * 1.5):
        target_price = round(recent_high, 2)
    else:
        target_price = round(current_price + (2.5 * risk), 2)

    reward = round(target_price - current_price, 2)
    rr_ratio = round((reward / risk), 2) if risk > 0 else 0.0
    rr_formatted = f"1:{rr_ratio}"

    # Check Rule: Risk Reward >= 1:2
    passed = rr_ratio >= 2.0

    # Scoring (0 - 100)
    score = 0.0
    if rr_ratio >= 3.0:
        score = 100.0
        details = (
            f"EXCEPTIONAL SETUP (R:R {rr_formatted} >= 1:2): Entry at Rp {current_price:,.0f}, "
            f"Stop Loss at Rp {stop_loss:,.0f} (-{round((risk/current_price)*100, 1)}%), "
            f"Target at Rp {target_price:,.0f} (+{round((reward/current_price)*100, 1)}%)."
        )
    elif rr_ratio >= 2.5:
        score = 92.0
        details = (
            f"STRONG SETUP (R:R {rr_formatted} >= 1:2): Entry at Rp {current_price:,.0f}, "
            f"Stop Loss Rp {stop_loss:,.0f}, Target Rp {target_price:,.0f}."
        )
    elif rr_ratio >= 2.0:
        score = 85.0
        details = (
            f"VALID SETUP (R:R {rr_formatted} >= 1:2): Risk/Reward meets the minimum 1:2 requirement."
        )
    elif rr_ratio >= 1.5:
        score = 60.0
        details = (
            f"Suboptimal Setup (R:R {rr_formatted} < 1:2): Reward does not offer the full 2x risk compensation."
        )
    elif rr_ratio >= 1.0:
        score = 40.0
        details = f"Poor Setup (R:R {rr_formatted}): 1:1 risk to reward ratio is not recommended for entry."
    else:
        score = 15.0
        details = f"Unfavorable Setup (R:R {rr_formatted}): Risk outweighs expected upside potential."

    return {
        "passed": passed,
        "score": score,
        "entry_price": current_price,
        "stop_loss": stop_loss,
        "target_price": target_price,
        "risk": risk,
        "reward": reward,
        "risk_reward_ratio": rr_ratio,
        "risk_reward_formatted": rr_formatted,
        "details": details
    }
