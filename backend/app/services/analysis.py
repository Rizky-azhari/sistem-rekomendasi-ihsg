from typing import Dict, Any, Optional
from app.services.yahoo import get_historical_data, get_stock_info, normalize_symbol
from app.services.indicator import calculate_indicators, extract_latest_indicators


def determine_trend(price: Optional[float], ma20: Optional[float], ma50: Optional[float], ma200: Optional[float]) -> str:
    """
    Determine the technical market trend based on price and moving average alignments.
    """
    if price is None:
        return "Unknown"

    if ma20 and ma50 and ma200:
        if price > ma20 > ma50 > ma200:
            return "Strong Uptrend (Bullish)"
        elif price > ma20 > ma50:
            return "Uptrend (Bullish)"
        elif price < ma20 < ma50 < ma200:
            return "Strong Downtrend (Bearish)"
        elif price < ma20 < ma50:
            return "Downtrend (Bearish)"
        elif price > ma20 and price < ma50:
            return "Consolidation / Pullback"
        else:
            return "Sideways / Neutral"
    elif ma20 and ma50:
        if price > ma20 > ma50:
            return "Uptrend"
        elif price < ma20 < ma50:
            return "Downtrend"
        else:
            return "Consolidation"
    elif ma20:
        return "Short-term Uptrend" if price > ma20 else "Short-term Downtrend"

    return "Neutral"


def perform_stock_analysis(symbol: str, period: str = "1y") -> Dict[str, Any]:
    """
    Perform end-to-end technical analysis for a given stock symbol.
    Returns:
    - symbol
    - company_name
    - harga_terakhir
    - MA20
    - MA50
    - MA200
    - RSI
    - trend
    - recommendation / signal
    """
    sym = normalize_symbol(symbol)
    stock_info = get_stock_info(sym)
    
    # 1. Fetch OHLCV data via Yahoo service
    df = get_historical_data(sym, period=period)
    if df.empty:
        return {
            "symbol": sym,
            "company_name": stock_info["company_name"],
            "harga_terakhir": stock_info["current_price"],
            "MA20": None,
            "MA50": None,
            "MA200": None,
            "RSI": None,
            "trend": "Insufficient Data",
            "signal": "HOLD",
            "message": "Historical price data is currently unavailable on Yahoo Finance."
        }

    # 2. Calculate Indicators via Indicator service
    df_indicators = calculate_indicators(df)
    latest = extract_latest_indicators(df_indicators)

    price = latest["harga_terakhir"] or stock_info["current_price"]
    ma20 = latest["MA20"]
    ma50 = latest["MA50"]
    ma200 = latest["MA200"]
    rsi = latest["RSI"]

    # 3. Determine Trend
    trend = determine_trend(price, ma20, ma50, ma200)

    # 4. Determine Simple Recommendation Signal
    signal = "HOLD"
    if "Uptrend" in trend and rsi is not None and rsi < 70:
        signal = "BUY" if rsi > 45 else "STRONG BUY"
    elif "Downtrend" in trend or (rsi is not None and rsi > 80):
        signal = "SELL" if (rsi is not None and rsi > 70) else "STRONG SELL"
    elif rsi is not None and rsi < 30:
        signal = "OVERSOLD (Potential Reversal)"

    return {
        "symbol": sym,
        "company_name": stock_info["company_name"],
        "sector": stock_info["sector"],
        "harga_terakhir": price,
        "MA20": ma20,
        "MA50": ma50,
        "MA200": ma200,
        "RSI": rsi,
        "volatility": latest["volatility"],
        "trend": trend,
        "signal": signal,
        "change_percentage": stock_info["change_percentage"]
    }
