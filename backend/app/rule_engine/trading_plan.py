import pandas as pd
from typing import Dict, Any


def generate_trading_plan(df_indicators: pd.DataFrame, signal: str) -> Dict[str, Any]:
    """
    Generates an automated Trading Plan with entry target, Stop Loss,
    Take Profit 1, Take Profit 2, and Risk-to-Reward Ratio based on ATR.
    """
    if df_indicators.empty:
        raise ValueError("Indicator DataFrame is empty")

    latest = df_indicators.iloc[-1]
    current_price = float(latest['Close'])
    atr = float(latest['ATR14']) if latest['ATR14'] > 0 else current_price * 0.02
    sma20 = float(latest['SMA20'])
    bb_lower = float(latest['BB_Lower'])
    bb_upper = float(latest['BB_Upper'])

    # Calculate Stop Loss distance (1.5 * ATR or dynamic support)
    risk_distance = max(1.5 * atr, current_price * 0.02)

    if signal in ["STRONG BUY", "BUY"]:
        entry_price = current_price
        entry_min = round(min(current_price * 0.995, sma20 if sma20 < current_price else current_price * 0.99), 0)
        entry_max = round(current_price * 1.005, 0)
        entry_range = f"Rp {int(entry_min):,} - Rp {int(entry_max):,}"

        stop_loss = round(current_price - risk_distance, 0)
        risk_per_share = current_price - stop_loss

        tp1 = round(current_price + (1.5 * risk_per_share), 0)
        tp2 = round(current_price + (3.0 * risk_per_share), 0)

        rr_ratio = round((tp1 - current_price) / risk_per_share, 2)
        notes = "Buy setup active. Maintain strict risk management of max 2% total portfolio per trade."

    elif signal == "HOLD":
        entry_price = current_price
        entry_range = f"Wait for Breakout above Rp {int(bb_upper):,}"
        stop_loss = round(current_price - risk_distance, 0)
        risk_per_share = current_price - stop_loss
        tp1 = round(current_price + (1.2 * risk_per_share), 0)
        tp2 = round(current_price + (2.5 * risk_per_share), 0)
        rr_ratio = 1.2
        notes = "Consolidation phase. Wait for price confirmation before adding new positions."

    else:  # SELL / STRONG SELL
        entry_price = current_price
        entry_range = "Exit / Avoid New Position"
        stop_loss = round(current_price + risk_distance, 0)
        tp1 = round(current_price - (1.5 * risk_distance), 0)
        tp2 = round(current_price - (3.0 * risk_distance), 0)
        rr_ratio = 1.5
        notes = "Bearish signal active. Cut loss or take profits immediately to safeguard capital."

    return {
        "entry_price": round(entry_price, 0),
        "entry_range": entry_range,
        "stop_loss": max(1.0, stop_loss),
        "take_profit_1": tp1,
        "take_profit_2": tp2,
        "risk_reward_ratio": rr_ratio,
        "recommended_risk_percent": 2.0,
        "notes": notes
    }
