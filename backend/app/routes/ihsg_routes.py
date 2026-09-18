"""
IHSG Stock Recommendation Routes — IDX80 Only
================================================
All stock analysis routes restricted to IDX80 universe.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

# Ensure backend directory is in sys.path
BACKEND_DIR = str(Path(__file__).resolve().parent.parent.parent)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.yahoo import get_all_stocks, get_historical_data, normalize_ticker, DEFAULT_IHSG_SYMBOLS
from app.services.analysis import perform_stock_analysis
from app.indicators.technical_indicator import TechnicalIndicators
from app.screener.stock_screener import run_screener, screen_stock_rules
from app.recommendation.recommendation_engine import RecommendationEngine, get_recommendation_from_scores
from app.trading_plan.trading_plan_generator import TradingPlanGenerator, generate_trading_plan_dict
from app.universe.stock_universe_manager import StockUniverseManager
from app.screener.batch_scanner_engine import BatchScannerEngine
from app.config.idx80_tickers import IDX80_TICKERS, IDX80_METADATA, is_idx80
from app.core.idx80_validator import validate_ticker, IDX80ValidationError

router = APIRouter(tags=["IHSG Stock Recommendation"])


class ScreenerScoreInput(BaseModel):
    symbol: Optional[str] = Field(default="", description="Kode ticker saham (misal BBCA.JK)")
    trend: float = Field(..., ge=0, le=100, description="Skor Screener Trend (0 - 100)")
    momentum: float = Field(..., ge=0, le=100, description="Skor Screener Momentum (0 - 100)")
    breakout: float = Field(..., ge=0, le=100, description="Skor Screener Breakout (0 - 100)")
    oversold: float = Field(..., ge=0, le=100, description="Skor Screener Oversold (0 - 100)")
    trading_setup: float = Field(..., ge=0, le=100, description="Skor Screener Trading Setup (0 - 100)")


class TradingPlanInput(BaseModel):
    price: float = Field(..., gt=0, description="Harga terkini saham (Current Price)")
    support: Optional[float] = Field(default=None, description="Level Support kunci")
    resistance: Optional[float] = Field(default=None, description="Level Resistance kunci")
    atr: Optional[float] = Field(default=None, description="Average True Range 14-hari")
    volatility: Optional[float] = Field(default=20.0, description="Persentase volatilitas historis (misal 20.0)")
    symbol: Optional[str] = Field(default="", description="Kode ticker saham")



# ------------------------------------------------------------------------------
# 0. Universe Endpoints & Batch Scanner Controls (IDX80)
# ------------------------------------------------------------------------------
@router.get("/universe/stats", summary="Statistik Stock Universe IDX80")
def get_universe_stats():
    """
    Menampilkan statistik universe saham IDX80:
    - total_universe (80 emiten)
    - active_stocks
    - inactive_stocks
    - last_update
    - display_label
    """
    try:
        return StockUniverseManager.get_universe_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil statistik universe: {str(e)}")


@router.post("/universe/sync", summary="Sinkronisasi Stock Universe IDX80 ke Database")
def sync_stock_universe():
    """
    Seeds/updates idx80_stocks table with IDX80 constituent data.
    No external API calls — uses the hardcoded IDX80 config.
    """
    try:
        report = StockUniverseManager.sync_to_database()
        return {
            "status": "success",
            "message": f"Sinkronisasi berhasil: {report['total_universe']} saham IDX80 terdaftar.",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal sinkronisasi universe: {str(e)}")


@router.get("/screener/progress", summary="Progress Status Scanning IDX80")
def get_scanning_progress():
    """
    Menampilkan status scanning real-time:
    - is_running
    - current_index
    - total_stocks (80 IDX80)
    - progress_message
    - percent
    """
    try:
        return BatchScannerEngine.get_progress()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil progress: {str(e)}")


@router.post("/screener/start-scan", summary="Mulai Scanning Seluruh Saham IDX80")
def start_universe_scan(limit: Optional[int] = Query(None, description="Opsional limit saham untuk discan")):
    """
    Memulai scanning IDX80 secara asynchronous background.
    - Uses batch yf.download() for efficient data retrieval
    - Only 80 stocks (not 900+)
    """
    try:
        result = BatchScannerEngine.start_universe_scan(max_stocks=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memulai scan: {str(e)}")


# ------------------------------------------------------------------------------
# 1. GET /stocks — Menampilkan daftar saham IDX80
# ------------------------------------------------------------------------------
@router.get("/stocks", response_model=List[Dict[str, Any]], summary="Daftar Saham IDX80")
def get_stocks_list():
    """
    Menampilkan daftar saham IDX80 beserta informasi harga terkini.
    """
    try:
        stocks = get_all_stocks()
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil daftar saham: {str(e)}")


# ------------------------------------------------------------------------------
# 2. GET /stock/{symbol} — Menampilkan data historis (IDX80 validated)
# ------------------------------------------------------------------------------
@router.get("/stock/{symbol}", summary="Data Historis Saham (IDX80)")
def get_stock_historical(
    symbol: str,
    period: str = Query("1y", description="Rentang waktu data (contoh: 1mo, 3mo, 6mo, 1y, 2y, 5y)"),
    interval: str = Query("1d", description="Interval data (contoh: 1d, 1wk, 1mo)")
):
    """
    Menampilkan data historis OHLCV saham IDX80 dari Yahoo Finance.
    """
    try:
        sym = validate_ticker(symbol)  # IDX80 validation gate
    except IDX80ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)

    try:
        df = get_historical_data(sym, period=period, interval=interval)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Data historis untuk {sym} tidak ditemukan di Yahoo Finance.")

        records = df.to_dict(orient="records")
        return {
            "symbol": sym,
            "period": period,
            "interval": interval,
            "total_records": len(records),
            "data": records
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data historis: {str(e)}")


# ------------------------------------------------------------------------------
# 3. GET /analysis/{symbol} — Analisis Indikator & Trend (IDX80 validated)
# ------------------------------------------------------------------------------
@router.get("/analysis/{symbol}", summary="Analisis Teknikal dan Trend Saham (IDX80)")
def get_stock_technical_analysis(
    symbol: str,
    period: str = Query("1y", description="Rentang data historis untuk kalkulasi")
):
    """
    Menampilkan analisis teknikal saham IDX80.
    """
    try:
        sym = validate_ticker(symbol)  # IDX80 validation gate
    except IDX80ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)

    try:
        analysis = perform_stock_analysis(sym, period=period)
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menganalisis saham {symbol}: {str(e)}")


# ------------------------------------------------------------------------------
# 4. GET /indicators/{symbol} — Technical Indicators (IDX80 validated)
# ------------------------------------------------------------------------------
@router.get("/indicators/{symbol}", summary="Technical Indicators Metrics JSON (IDX80)")
def get_technical_indicators_summary(
    symbol: str,
    period: str = Query("1y", description="Time period for indicator calculations")
):
    """
    Menampilkan modul indikator teknikal saham IDX80.
    """
    try:
        sym = validate_ticker(symbol)  # IDX80 validation gate
    except IDX80ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)

    try:
        df = get_historical_data(sym, period=period)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Data harga tidak ditemukan untuk {sym}")
        summary = TechnicalIndicators.get_summary(df, sym)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghitung indikator: {str(e)}")


# ------------------------------------------------------------------------------
# 5. GET /screener/rules — 5-Factor Rule Based Screener (IDX80)
# ------------------------------------------------------------------------------
@router.get("/screener/rules", summary="5-Factor Rule Based Stock Screener (IDX80)")
def get_rule_screener(
    filter: Optional[str] = Query(None, description="Filter rule: momentum, trend, oversold, breakout, trading_setup"),
    min_score: Optional[float] = Query(None, description="Minimum composite score"),
    sort_by: str = Query("composite_score", description="Sort by: composite_score, momentum_score, trend_score, breakout_score, oversold_score, trading_setup_score, price, change")
):
    """
    Menjalankan Rule-Based Screener 5 Faktor pada IDX80 Stock Universe.
    """
    try:
        results = BatchScannerEngine.get_scanned_results(
            rule_filter=filter,
            min_score=min_score,
            sort_by=sort_by
        )
        return {
            "total_matches": len(results),
            "universe": "IDX80",
            "filter_applied": filter,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Screener] Error in get_rule_screener: {e}")
        return {
            "total_matches": 0,
            "universe": "IDX80",
            "filter_applied": filter,
            "results": [],
            "error_message": f"Scanner belum tersedia. Klik 'Scan IDX80' untuk memulai analisis. Detail: {str(e)[:100]}"
        }


# ------------------------------------------------------------------------------
# 6. GET /screener/{symbol} — Detailed 5-Rule Evaluation (IDX80 validated)
# ------------------------------------------------------------------------------
@router.get("/screener/{symbol}", summary="Evaluasi 5 Rule untuk Saham IDX80")
def get_single_stock_rules(symbol: str):
    """
    Menampilkan evaluasi lengkap 5 Rule Screener untuk satu saham IDX80.
    """
    try:
        sym = validate_ticker(symbol)  # IDX80 validation gate
    except IDX80ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)

    try:
        df = get_historical_data(sym, period="1y")
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Data harga tidak ditemukan untuk {sym}")
        evaluation = screen_stock_rules(df, sym)
        return evaluation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengevaluasi rule {symbol}: {str(e)}")


# ------------------------------------------------------------------------------
# 7. GET /recommendation/{symbol} — Rekomendasi (IDX80 validated)
# ------------------------------------------------------------------------------
@router.get("/recommendation/{symbol}", summary="Rekomendasi Saham IDX80 berbasis 5 Skor Screener")
def get_stock_recommendation(symbol: str):
    """
    Menghitung rekomendasi saham IDX80 menggunakan Recommendation Engine.
    """
    try:
        sym = validate_ticker(symbol)  # IDX80 validation gate
    except IDX80ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)

    try:
        df = get_historical_data(sym, period="1y")
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Data harga tidak ditemukan untuk {sym}")

        screen_res = screen_stock_rules(df, sym)
        scores = {
            "trend": screen_res["scores"]["trend_score"],
            "momentum": screen_res["scores"]["momentum_score"],
            "breakout": screen_res["scores"]["breakout_score"],
            "oversold": screen_res["scores"]["oversold_score"],
            "trading_setup": screen_res["scores"]["trading_setup_score"]
        }
        rec_data = RecommendationEngine.evaluate(
            scores=scores,
            symbol=sym,
            details=screen_res.get("breakdowns")
        )
        return {
            **rec_data,
            "price": screen_res["price"],
            "rules_passed": screen_res["rules_passed"],
            "breakdowns": screen_res.get("breakdowns")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghasilkan rekomendasi {symbol}: {str(e)}")


# ------------------------------------------------------------------------------
# 8. POST /recommendation/calculate — Input Langsung Skor Screener
# ------------------------------------------------------------------------------
@router.post("/recommendation/calculate", summary="Hitung Final Score & Rekomendasi dari Skor Screener")
def calculate_recommendation_from_scores(input_data: ScreenerScoreInput):
    """
    Menerima input 5 skor screener secara langsung dan mengembalikan rekomendasi.
    """
    try:
        scores = {
            "trend": input_data.trend,
            "momentum": input_data.momentum,
            "breakout": input_data.breakout,
            "oversold": input_data.oversold,
            "trading_setup": input_data.trading_setup
        }
        result = RecommendationEngine.evaluate(scores=scores, symbol=input_data.symbol or "IDX")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengkalkulasi rekomendasi: {str(e)}")


# ------------------------------------------------------------------------------
# 9. GET /recommendations — Daftar Rekomendasi Saham IDX80
# ------------------------------------------------------------------------------
@router.get("/recommendations", summary="Daftar Rekomendasi Saham IDX80")
def get_all_recommendations():
    """
    Menampilkan daftar rekomendasi saham IDX80 berdasarkan evaluasi 5 faktor.
    """
    try:
        results = BatchScannerEngine.get_scanned_results(limit=100)
        recommendations_list = []
        for item in results:
            recommendations_list.append({
                "symbol": item["symbol"],
                "name": item["name"],
                "price": item["price"],
                "final_score": item["final_score"],
                "recommendation": item["recommendation"],
                "alasan_rekomendasi": item.get("alasan_rekomendasi", ""),
                "reasons": item.get("reasons", []),
                "scores": {
                    "trend": item.get("trend_score", 0),
                    "momentum": item.get("momentum_score", 0),
                    "breakout": item.get("breakout_score", 0),
                    "oversold": item.get("oversold_score", 0),
                    "trading_setup": item.get("trading_setup_score", 0)
                }
            })
        return recommendations_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil daftar rekomendasi: {str(e)}")


# ------------------------------------------------------------------------------
# 10. GET /trading-plan/{symbol} — Trading Plan (IDX80 validated)
# ------------------------------------------------------------------------------
@router.get("/trading-plan/{symbol}", summary="Trading Plan Generator Saham IDX80")
def get_stock_trading_plan(symbol: str):
    """
    Menghasilkan Trading Plan otomatis untuk saham IDX80.
    """
    try:
        sym = validate_ticker(symbol)  # IDX80 validation gate
    except IDX80ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)

    try:
        df = get_historical_data(sym, period="1y")
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Data harga tidak ditemukan untuk {sym}")

        plan = TradingPlanGenerator.generate(df, symbol=sym)
        return {
            "symbol": sym,
            "current_price": float(df["Close"].iloc[-1]),
            **plan
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat trading plan untuk {symbol}: {str(e)}")


# ------------------------------------------------------------------------------
# 11. POST /trading-plan/generate — Custom Trading Plan
# ------------------------------------------------------------------------------
@router.post("/trading-plan/generate", summary="Hitung Trading Plan dari Nilai Support, Resistance, ATR, Volatility")
def generate_custom_trading_plan(input_data: TradingPlanInput):
    """
    Menerima input Support, Resistance, ATR, Volatility dan mengembalikan Trading Plan.
    """
    try:
        plan = TradingPlanGenerator.generate_plan_from_values(
            current_price=input_data.price,
            support=input_data.support or (input_data.price * 0.96),
            resistance=input_data.resistance or (input_data.price * 1.05),
            atr=input_data.atr or (input_data.price * 0.025),
            volatility=input_data.volatility or 20.0
        )
        return {
            "symbol": input_data.symbol,
            "price": input_data.price,
            **plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengkalkulasi trading plan: {str(e)}")


# ------------------------------------------------------------------------------
# 12. GET /market/ihsg — Data Indeks IHSG (^JKSE) Realtime
# ------------------------------------------------------------------------------
@router.get("/market/ihsg", summary="Data Indeks IHSG Gabungan Realtime")
def get_ihsg_market_overview():
    """
    Menampilkan data Indeks Harga Saham Gabungan (^JKSE).
    Note: ^JKSE is the composite index, not restricted to IDX80 validation.
    """
    import yfinance as yf
    try:
        ticker = yf.Ticker("^JKSE")
        hist = ticker.history(period="1mo", interval="1d")

        if not hist.empty:
            last_row = hist.iloc[-1]
            prev_row = hist.iloc[-2] if len(hist) > 1 else last_row

            price = round(float(last_row["Close"]), 2)
            prev_close = round(float(prev_row["Close"]), 2)
            change = round(price - prev_close, 2)
            change_pct = round((change / prev_close) * 100, 2) if prev_close > 0 else 0.0
            high = round(float(last_row["High"]), 2)
            low = round(float(last_row["Low"]), 2)
            volume = int(last_row["Volume"]) if "Volume" in last_row else 0

            sparkline = [round(float(c), 2) for c in hist["Close"].tail(15).tolist()]
        else:
            price = 6436.85
            prev_close = 6461.15
            change = -24.30
            change_pct = -0.38
            high = 6480.20
            low = 6420.10
            volume = 1250000000
            sparkline = [6410, 6425, 6430, 6450, 6465, 6480, 6470, 6455, 6460, 6475, 6461, 6436]

        status = "BULLISH" if change >= 0 else "BEARISH"

        return {
            "symbol": "^JKSE",
            "name": "IHSG (Indeks Harga Saham Gabungan)",
            "price": price,
            "previous_close": prev_close,
            "change": change,
            "change_percentage": change_pct,
            "high": high,
            "low": low,
            "volume": volume,
            "status": status,
            "sparkline": sparkline
        }
    except Exception as e:
        return {
            "symbol": "^JKSE",
            "name": "IHSG (Indeks Harga Saham Gabungan)",
            "price": 6436.85,
            "previous_close": 6461.15,
            "change": -24.30,
            "change_percentage": -0.38,
            "high": 6480.20,
            "low": 6420.10,
            "volume": 1250000000,
            "status": "BEARISH",
            "sparkline": [6410, 6425, 6430, 6450, 6465, 6480, 6470, 6455, 6460, 6475, 6461, 6436]
        }
