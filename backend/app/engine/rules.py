import pandas as pd
from typing import Dict, Any, List
from app.schemas.recommendation import RuleBreakdown

def evaluate_rules(df_indicators: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluates rule-based technical signals on the latest indicator data point.
    Returns score, recommendation signal, confidence level, and rule breakdowns.
    """
    if df_indicators.empty:
        raise ValueError("Indicator DataFrame is empty")
        
    latest = df_indicators.iloc[-1]
    prev = df_indicators.iloc[-2] if len(df_indicators) > 1 else latest
    
    close = latest['Close']
    rsi = latest['RSI14']
    macd = latest['MACD']
    macd_sig = latest['MACD_Signal']
    macd_hist = latest['MACD_Hist']
    prev_macd = prev['MACD']
    prev_macd_sig = prev['MACD_Signal']
    
    ema12 = latest['EMA12']
    ema26 = latest['EMA26']
    sma20 = latest['SMA20']
    sma50 = latest['SMA50']
    
    bb_upper = latest['BB_Upper']
    bb_lower = latest['BB_Lower']
    bb_middle = latest['BB_Middle']
    
    volume = latest['Volume']
    vol_sma20 = latest['Vol_SMA20']
    
    rule_breakdowns: List[RuleBreakdown] = []
    total_score = 50.0  # Base neutral score
    
    # 1. RSI Indicator Rules
    rsi_score = 0.0
    rsi_status = "NEUTRAL"
    if rsi < 30:
        rsi_score = 25.0
        rsi_status = "BULLISH"
        rsi_desc = f"RSI is Oversold ({rsi:.1f} < 30). High potential for bullish reversal."
    elif 30 <= rsi <= 50:
        rsi_score = 15.0
        rsi_status = "BULLISH"
        rsi_desc = f"RSI is in Bullish Recovery Zone ({rsi:.1f})."
    elif 50 < rsi < 70:
        rsi_score = 5.0
        rsi_status = "NEUTRAL"
        rsi_desc = f"RSI is Moderate Bullish ({rsi:.1f})."
    else: # rsi >= 70
        rsi_score = -25.0
        rsi_status = "BEARISH"
        rsi_desc = f"RSI is Overbought ({rsi:.1f} > 70). Risk of short-term pullback."
    
    total_score += rsi_score
    rule_breakdowns.append(RuleBreakdown(
        rule_name="RSI Momentum Rule",
        category="Momentum",
        score=rsi_score,
        weight=25.0,
        description=rsi_desc,
        status=rsi_status
    ))
    
    # 2. MACD Crossover & Trend Rules
    macd_score = 0.0
    macd_status = "NEUTRAL"
    is_golden_cross = (prev_macd < prev_macd_sig) and (macd >= macd_sig)
    is_death_cross = (prev_macd > prev_macd_sig) and (macd <= macd_sig)
    
    if is_golden_cross:
        macd_score = 25.0
        macd_status = "BULLISH"
        macd_desc = "MACD Golden Cross detected! Strong bullish buy signal."
    elif macd > macd_sig and macd_hist > 0:
        macd_score = 15.0
        macd_status = "BULLISH"
        macd_desc = f"MACD is above signal line with positive histogram ({macd_hist:.2f})."
    elif is_death_cross:
        macd_score = -25.0
        macd_status = "BEARISH"
        macd_desc = "MACD Death Cross detected! Strong bearish sell signal."
    else:
        macd_score = -10.0
        macd_status = "BEARISH"
        macd_desc = "MACD is below signal line. Downward momentum."
        
    total_score += macd_score
    rule_breakdowns.append(RuleBreakdown(
        rule_name="MACD Signal & Crossover Rule",
        category="Momentum",
        score=macd_score,
        weight=25.0,
        description=macd_desc,
        status=macd_status
    ))
    
    # 3. Moving Average Trend Rules
    ma_score = 0.0
    ma_status = "NEUTRAL"
    if close > sma20 > sma50:
        ma_score = 25.0
        ma_status = "BULLISH"
        ma_desc = "Strong Uptrend: Price is above SMA20 and SMA50."
    elif close > sma20:
        ma_score = 15.0
        ma_status = "BULLISH"
        ma_desc = "Short-term Uptrend: Price is above SMA20."
    elif close < sma20 < sma50:
        ma_score = -25.0
        ma_status = "BEARISH"
        ma_desc = "Downtrend: Price is below SMA20 and SMA50."
    else:
        ma_score = -10.0
        ma_status = "NEUTRAL"
        ma_desc = "Consolidation / Mixed Moving Average alignment."
        
    total_score += ma_score
    rule_breakdowns.append(RuleBreakdown(
        rule_name="Moving Average Alignment Rule",
        category="Trend",
        score=ma_score,
        weight=25.0,
        description=ma_desc,
        status=ma_status
    ))
    
    # 4. Bollinger Bands Volatility Rule
    bb_score = 0.0
    bb_status = "NEUTRAL"
    bb_desc = "Bollinger Bands data unavailable or price in tight compression."
    bb_range = bb_upper - bb_lower
    if bb_range > 0:
        pct_b = (close - bb_lower) / bb_range
        if pct_b < 0.15:
            bb_score = 15.0
            bb_status = "BULLISH"
            bb_desc = f"Price near lower Bollinger Band ({pct_b*100:.0f}% %B). Oversold bounce opportunity."
        elif pct_b > 0.85:
            bb_score = -15.0
            bb_status = "BEARISH"
            bb_desc = f"Price near upper Bollinger Band ({pct_b*100:.0f}% %B). Resistance pressure."
        else:
            bb_score = 5.0
            bb_status = "NEUTRAL"
            bb_desc = "Price oscillating within normal Bollinger Bands range."
            
    total_score += bb_score
    rule_breakdowns.append(RuleBreakdown(
        rule_name="Bollinger Band Position Rule",
        category="Volatility",
        score=bb_score,
        weight=15.0,
        description=bb_desc,
        status=bb_status
    ))
    
    # 5. Volume Confirmation Rule
    vol_score = 0.0
    vol_status = "NEUTRAL"
    if vol_sma20 > 0 and volume > (1.5 * vol_sma20):
        if total_score >= 50:
            vol_score = 10.0
            vol_status = "BULLISH"
            vol_desc = f"High Volume Surge ({volume:,} vs avg {int(vol_sma20):,}) confirming bullish interest."
        else:
            vol_score = -10.0
            vol_status = "BEARISH"
            vol_desc = f"High Volume Pressure on downtrend."
    else:
        vol_score = 0.0
        vol_status = "NEUTRAL"
        vol_desc = "Volume is within normal 20-day average."
        
    total_score += vol_score
    rule_breakdowns.append(RuleBreakdown(
        rule_name="Volume Confirmation Rule",
        category="Volume",
        score=vol_score,
        weight=10.0,
        description=vol_desc,
        status=vol_status
    ))
    
    # Clamp score to [0, 100]
    final_score = max(0.0, min(100.0, round(total_score, 1)))
    
    # Determine Final Signal Recommendation
    if final_score >= 75:
        signal = "STRONG BUY"
        confidence = "HIGH"
        summary = "Multi-indicator strong bullish alignment. High probability entry setup."
    elif final_score >= 60:
        signal = "BUY"
        confidence = "MEDIUM"
        summary = "Positive technical indicators outweigh bearish risks. Good buy setup."
    elif final_score >= 40:
        signal = "HOLD"
        confidence = "MEDIUM"
        summary = "Market is in consolidation or mixed signals. Wait for clearer breakout."
    elif final_score >= 25:
        signal = "SELL"
        confidence = "MEDIUM"
        summary = "Bearish technical indicators dominating. Recommend reducing position."
    else:
        signal = "STRONG SELL"
        confidence = "HIGH"
        summary = "Severe downward momentum across indicators. Protect capital."
        
    return {
        "total_score": final_score,
        "signal": signal,
        "confidence_level": confidence,
        "summary": summary,
        "rule_breakdowns": rule_breakdowns
    }
