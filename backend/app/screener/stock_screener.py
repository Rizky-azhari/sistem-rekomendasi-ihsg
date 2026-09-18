"""
Stock Screener — IDX80 Only
==============================
5-Factor Rule Based Screener restricted to IDX80 universe.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from app.services.yahoo import get_historical_data, get_stock_info, DEFAULT_IHSG_SYMBOLS
from app.screener.momentum import evaluate_momentum
from app.screener.trend import evaluate_trend
from app.screener.oversold import evaluate_oversold
from app.screener.breakout import evaluate_breakout
from app.screener.trading_setup import evaluate_trading_setup
from app.recommendation.recommendation_engine import RecommendationEngine


def screen_stock_rules(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """
    Evaluates all 5 rule-based screeners for a single stock DataFrame:
    1. Momentum (Close > MA20 & Volume > Vol_SMA20)
    2. Trend (MA20 > MA50 > MA200)
    3. Oversold (RSI < 35 & Price near support)
    4. Breakout (Close > Highest High 20 days)
    5. Trading Setup (Risk Reward >= 1:2)
    """
    momentum = evaluate_momentum(df, symbol)
    trend = evaluate_trend(df, symbol)
    oversold = evaluate_oversold(df, symbol)
    breakout = evaluate_breakout(df, symbol)
    setup = evaluate_trading_setup(df, symbol)

    # Calculate recommendation using Recommendation Engine
    scores = {
        "trend": trend["score"],
        "momentum": momentum["score"],
        "breakout": breakout["score"],
        "oversold": oversold["score"],
        "trading_setup": setup["score"]
    }
    rec_result = RecommendationEngine.evaluate(
        scores=scores,
        symbol=symbol,
        details={
            "momentum": momentum,
            "trend": trend,
            "breakout": breakout,
            "oversold": oversold,
            "trading_setup": setup
        }
    )

    final_score = rec_result["final_score"]
    recommendation = rec_result["recommendation"]
    reasons = rec_result["reasons"]
    alasan = rec_result["alasan_rekomendasi"]

    price = float(df["Close"].iloc[-1]) if not df.empty and "Close" in df.columns else 0.0

    return {
        "symbol": symbol,
        "price": price,
        "final_score": final_score,
        "composite_score": final_score,
        "recommendation": recommendation,
        "overall_signal": recommendation,
        "reasons": reasons,
        "alasan_rekomendasi": alasan,
        "scores": {
            "momentum_score": momentum["score"],
            "trend_score": trend["score"],
            "breakout_score": breakout["score"],
            "oversold_score": oversold["score"],
            "trading_setup_score": setup["score"]
        },
        "rules_passed": {
            "momentum": momentum["passed"],
            "trend": trend["passed"],
            "breakout": breakout["passed"],
            "oversold": oversold["passed"],
            "trading_setup": setup["passed"]
        },
        "breakdowns": {
            "momentum": momentum,
            "trend": trend,
            "oversold": oversold,
            "breakout": breakout,
            "trading_setup": setup
        }
    }


def run_screener(
    symbols: Optional[List[str]] = None,
    rule_filter: Optional[str] = None,
    min_score: Optional[float] = None,
    sort_by: str = "composite_score"
) -> List[Dict[str, Any]]:
    """
    Runs the 5-Factor Rule Based Screener on IDX80 stocks.
    """
    from app.config.idx80_tickers import IDX80_TICKERS, is_idx80
    from app.screener.batch_scanner_engine import BatchScannerEngine

    if not symbols:
        # Use batched IDX80 scanned results
        results = BatchScannerEngine.get_scanned_results(
            rule_filter=rule_filter,
            min_score=min_score,
            sort_by=sort_by
        )
        total_found = len(IDX80_TICKERS)
        total_success = len(results)
        total_failed = max(0, total_found - total_success)

        print(f"[Screener] IDX80 Universe: {total_found} saham")
        print(f"[Screener] Berhasil dianalisis: {total_success}")
        print(f"[Screener] Gagal: {total_failed}")
        return results

    # If specific symbols provided — validate against IDX80
    target_symbols = [s for s in symbols if is_idx80(s)]
    total_found = len(target_symbols)
    results: List[Dict[str, Any]] = []

    for sym in target_symbols:
        try:
            df = get_historical_data(sym, period="1y")
            if df.empty or len(df) < 20:
                continue

            info = get_stock_info(sym)
            screen_res = screen_stock_rules(df, sym)

            item = {
                "symbol": sym,
                "name": info.get("company_name", sym.replace(".JK", "")),
                "sector": info.get("sector", "IDX Equities"),
                "price": screen_res["price"],
                "change_percentage": info.get("change_percentage", 0.0),
                "volume": info.get("volume", 0),
                "composite_score": screen_res["composite_score"],
                "final_score": screen_res["final_score"],
                "overall_signal": screen_res["overall_signal"],
                "recommendation": screen_res["recommendation"],
                "reasons": screen_res["reasons"],
                "alasan_rekomendasi": screen_res["alasan_rekomendasi"],
                "momentum_score": screen_res["scores"]["momentum_score"],
                "trend_score": screen_res["scores"]["trend_score"],
                "breakout_score": screen_res["scores"]["breakout_score"],
                "oversold_score": screen_res["scores"]["oversold_score"],
                "trading_setup_score": screen_res["scores"]["trading_setup_score"],
                "rules_passed": screen_res["rules_passed"],
                "details": {
                    "trend_desc": screen_res["breakdowns"]["trend"]["details"],
                    "momentum_desc": screen_res["breakdowns"]["momentum"]["details"],
                    "breakout_desc": screen_res["breakdowns"]["breakout"]["details"],
                    "oversold_desc": screen_res["breakdowns"]["oversold"]["details"],
                    "setup_desc": screen_res["breakdowns"]["trading_setup"]["details"],
                    "risk_reward": screen_res["breakdowns"]["trading_setup"]["risk_reward_formatted"],
                    "stop_loss": screen_res["breakdowns"]["trading_setup"]["stop_loss"],
                    "target_price": screen_res["breakdowns"]["trading_setup"]["target_price"]
                }
            }
            results.append(item)
        except Exception as e:
            print(f"[RuleScreener] Error screening {sym}: {e}")
            continue

    # Filter by specific rule pass
    if rule_filter:
        rf = rule_filter.lower()
        results = [r for r in results if r["rules_passed"].get(rf, False)]

    # Filter by min score
    if min_score is not None:
        results = [r for r in results if r["composite_score"] >= min_score]

    # Sort results
    if sort_by in ["momentum_score", "trend_score", "breakout_score", "oversold_score", "trading_setup_score"]:
        results.sort(key=lambda x: x[sort_by], reverse=True)
    elif sort_by == "change_percentage":
        results.sort(key=lambda x: x["change_percentage"], reverse=True)
    else:
        results.sort(key=lambda x: x["composite_score"], reverse=True)

    total_success = len(results)
    total_failed = max(0, total_found - total_success)

    print(f"[Screener] IDX80 Universe: {total_found} saham")
    print(f"[Screener] Berhasil dianalisis: {total_success}")
    print(f"[Screener] Gagal: {total_failed}")

    return results
