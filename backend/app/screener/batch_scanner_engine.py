"""
IDX80 Batch Scanner Engine
============================
Optimized stock scanner that processes ONLY IDX80 constituents (80 stocks).
Uses batch yf.download() for efficient data retrieval.

Key improvements over the original full-universe scanner:
  - 80 stocks instead of 900+ → completes in 15-30 seconds
  - Single batch API call instead of 900+ individual calls
  - No timeout risk on serverless platforms
  - Minimal RAM usage (~50 MB)
"""

import time
import math
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

from app.config.idx80_tickers import IDX80_TICKERS, IDX80_METADATA, get_all_idx80_tickers
from app.services.yahoo import batch_download_idx80, get_historical_data, normalize_ticker
from app.screener.stock_screener import screen_stock_rules
from app.recommendation.recommendation_engine import RecommendationEngine


class BatchScannerEngine:
    """
    IDX80-Only Batch Stock Scanner Engine.

    Features:
    - Scans exactly IDX80 constituents (80 active tickers)
    - Uses yf.download() batch API for single-call data retrieval
    - Multi-threaded analysis (ThreadPoolExecutor) for indicator calculation
    - Real-time progress tracking
    - 5 core screener rules (Momentum, Trend, Oversold, Breakout, Trading Setup)
    - Recommendation Engine final score & reasons
    """

    BATCH_SIZE: int = 20   # 80 stocks / 20 = 4 batches
    MAX_WORKERS: int = 5   # Reduced from 8 — less concurrent load needed

    # State tracking
    _lock = threading.Lock()
    _is_running: bool = False
    _current_index: int = 0
    _total_stocks: int = 0
    _current_batch: int = 0
    _total_batches: int = 0
    _start_time: Optional[datetime.datetime] = None
    _end_time: Optional[datetime.datetime] = None
    _progress_message: str = "Scanner Siap"
    _thread: Optional[threading.Thread] = None

    # Cached results (sorted by score descending)
    _RESULTS: List[Dict[str, Any]] = []

    @classmethod
    def get_progress(cls) -> Dict[str, Any]:
        """Returns current scanning progress state with exact counts."""
        with cls._lock:
            percent = (
                round((cls._current_index / cls._total_stocks * 100), 1)
                if cls._total_stocks > 0
                else 0.0
            )
            total_berhasil = len(cls._RESULTS)
            total_gagal = max(0, cls._current_index - total_berhasil)
            return {
                "is_running": cls._is_running,
                "current_index": cls._current_index,
                "total_stocks": cls._total_stocks,
                "current_batch": cls._current_batch,
                "total_batches": cls._total_batches,
                "percent": percent,
                "progress_message": cls._progress_message,
                "total_saham_ditemukan": cls._total_stocks,
                "total_saham_berhasil": total_berhasil,
                "total_saham_gagal": total_gagal,
                "total_scanned_results": total_berhasil,
                "universe": "IDX80",
                "start_time": cls._start_time.strftime("%Y-%m-%d %H:%M:%S") if cls._start_time else None,
                "end_time": cls._end_time.strftime("%Y-%m-%d %H:%M:%S") if cls._end_time else None
            }

    @staticmethod
    def _sanitize_value(val):
        """Replace NaN/Inf float values with 0.0 for JSON compliance."""
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return 0.0
        if isinstance(val, dict):
            return {k: BatchScannerEngine._sanitize_value(v) for k, v in val.items()}
        if isinstance(val, list):
            return [BatchScannerEngine._sanitize_value(v) for v in val]
        return val

    @classmethod
    def _analyze_single_stock(cls, ticker: str, df) -> Optional[Dict[str, Any]]:
        """
        Analyzes a single stock's pre-downloaded DataFrame through the 5-factor screener.
        Note: Data is already downloaded via batch — this only does indicator calculation.
        """
        try:
            if df is None or df.empty or len(df) < 14:
                return None

            meta = IDX80_METADATA.get(ticker, {})
            screen_res = screen_stock_rules(df, ticker)
            price = screen_res["price"]
            final_score = screen_res["final_score"]
            recommendation = screen_res["recommendation"]
            reasons = screen_res["reasons"]
            alasan = screen_res["alasan_rekomendasi"]

            # Calculate daily change
            change_pct = 0.0
            if len(df) >= 2:
                last_c = float(df["Close"].iloc[-1])
                prev_c = float(df["Close"].iloc[-2])
                change_pct = round(((last_c - prev_c) / prev_c) * 100, 2) if prev_c > 0 else 0.0

            volume = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0

            result = {
                "symbol": ticker,
                "name": meta.get("company_name", ticker.replace(".JK", "")),
                "sector": meta.get("sector", "IDX Equities"),
                "board": "Utama",
                "market": "IDX80",
                "price": price,
                "change_percentage": change_pct,
                "volume": volume,
                "composite_score": final_score,
                "final_score": final_score,
                "recommendation": recommendation,
                "overall_signal": recommendation,
                "reasons": reasons,
                "alasan_rekomendasi": alasan,
                "momentum_score": screen_res["scores"]["momentum_score"],
                "trend_score": screen_res["scores"]["trend_score"],
                "breakout_score": screen_res["scores"]["breakout_score"],
                "oversold_score": screen_res["scores"]["oversold_score"],
                "trading_setup_score": screen_res["scores"]["trading_setup_score"],
                "rules_passed": screen_res["rules_passed"],
                "details": {
                    "stop_loss": screen_res["breakdowns"]["trading_setup"].get("stop_loss"),
                    "target_price": screen_res["breakdowns"]["trading_setup"].get("target_price"),
                    "risk_reward": screen_res["breakdowns"]["trading_setup"].get("risk_reward_formatted")
                }
            }

            return cls._sanitize_value(result)
        except Exception as e:
            print(f"[BatchScanner] Error analyzing {ticker}: {e}")
            return None

    @classmethod
    def _execute_scan_loop(cls, tickers: List[str]):
        """
        Internal worker: batch-downloads all IDX80 data, then analyzes each stock.
        """
        total = len(tickers)
        total_batches = math.ceil(total / cls.BATCH_SIZE)

        with cls._lock:
            cls._is_running = True
            cls._current_index = 0
            cls._total_stocks = total
            cls._current_batch = 0
            cls._total_batches = total_batches
            cls._start_time = datetime.datetime.now()
            cls._end_time = None
            cls._progress_message = f"Downloading IDX80 data... 0 / {total} saham"

        print(f"[BatchScanner] Starting IDX80 universe scan ({total} stocks)...")

        # Step 1: Batch download ALL IDX80 data in one call
        print(f"[BatchScanner] Batch downloading {total} IDX80 tickers via yf.download()...")
        all_data = batch_download_idx80(tickers=tickers, period="1y")
        print(f"[BatchScanner] Batch download complete: {len(all_data)} tickers retrieved.")

        with cls._lock:
            cls._progress_message = f"Analyzing IDX80 stocks... 0 / {total} saham selesai"

        # Step 2: Analyze each stock using thread pool (CPU-bound indicator calc)
        scanned_results: List[Dict[str, Any]] = []

        for batch_num in range(total_batches):
            if not cls._is_running:
                print("[BatchScanner] Scan stopped prematurely.")
                break

            batch_start = batch_num * cls.BATCH_SIZE
            batch_end = min(batch_start + cls.BATCH_SIZE, total)
            batch_tickers = tickers[batch_start:batch_end]

            with cls._lock:
                cls._current_batch = batch_num + 1

            with ThreadPoolExecutor(max_workers=cls.MAX_WORKERS) as executor:
                future_to_ticker = {
                    executor.submit(
                        cls._analyze_single_stock,
                        t,
                        all_data.get(t)
                    ): t for t in batch_tickers
                }

                for future in as_completed(future_to_ticker):
                    res = future.result()
                    if res:
                        scanned_results.append(res)

                    with cls._lock:
                        cls._current_index += 1
                        cls._progress_message = f"Analyzing IDX80: {cls._current_index} / {total} saham selesai"

            print(f"[BatchScanner] Completed Batch {batch_num + 1}/{total_batches} ({cls._current_index}/{total}).")

            # Update live results cache after each batch
            with cls._lock:
                cls._RESULTS = sorted(
                    scanned_results,
                    key=lambda x: x["final_score"],
                    reverse=True
                )

        total_berhasil = len(scanned_results)
        total_gagal = max(0, total - total_berhasil)

        with cls._lock:
            cls._is_running = False
            cls._end_time = datetime.datetime.now()
            cls._progress_message = f"Selesai: {total_berhasil} / {total} saham IDX80 dianalisis"
            cls._RESULTS = sorted(
                scanned_results,
                key=lambda x: x["final_score"],
                reverse=True
            )

        elapsed = (cls._end_time - cls._start_time).total_seconds()
        print(f"[BatchScanner] [DONE] IDX80 scan complete in {elapsed:.1f}s!")
        print(f"  Total saham IDX80: {total}")
        print(f"  Berhasil dianalisis: {total_berhasil}")
        print(f"  Gagal: {total_gagal}")

    @classmethod
    def start_universe_scan(cls, max_stocks: Optional[int] = None) -> Dict[str, Any]:
        """
        Triggers IDX80 stock scanning in background.
        """
        with cls._lock:
            if cls._is_running:
                return {
                    "status": "already_running",
                    "progress": cls.get_progress()
                }

        tickers = get_all_idx80_tickers()
        if max_stocks:
            tickers = tickers[:max_stocks]

        print(f"[BatchScanner] Initiating IDX80 scan ({len(tickers)} stocks)...")

        cls._thread = threading.Thread(
            target=cls._execute_scan_loop,
            args=(tickers,),
            daemon=True,
            name="IDX80ScannerWorker"
        )
        cls._thread.start()

        return {
            "status": "started",
            "universe": "IDX80",
            "total_stocks_to_scan": len(tickers),
            "total_batches": math.ceil(len(tickers) / cls.BATCH_SIZE),
            "progress_message": f"Starting IDX80 scan: 0 / {len(tickers)} saham"
        }

    @classmethod
    def get_scanned_results(
        cls,
        rule_filter: Optional[str] = None,
        recommendation_filter: Optional[str] = None,
        min_score: Optional[float] = None,
        sort_by: str = "score",
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Returns sorted and filtered IDX80 screener results."""
        with cls._lock:
            results = list(cls._RESULTS)

        # If no results cached yet, run quick initialization
        if not results:
            cls._initialize_quick_top_universe()
            with cls._lock:
                results = list(cls._RESULTS)

        # 1. Filter by recommendation
        if recommendation_filter and recommendation_filter.upper() != "ALL":
            rf = recommendation_filter.upper()
            results = [r for r in results if r.get("recommendation") == rf]

        # 2. Filter by specific rule passed
        if rule_filter:
            rule_key = rule_filter.lower()
            results = [r for r in results if r.get("rules_passed", {}).get(rule_key, False)]

        # 3. Filter by minimum score
        if min_score is not None:
            results = [r for r in results if r["final_score"] >= min_score]

        # 4. Sorting
        if sort_by == "price":
            results.sort(key=lambda x: x["price"], reverse=True)
        elif sort_by == "change":
            results.sort(key=lambda x: x.get("change_percentage", 0.0), reverse=True)
        elif sort_by in ["momentum_score", "momentum"]:
            results.sort(key=lambda x: x.get("momentum_score", 0.0), reverse=True)
        elif sort_by in ["trend_score", "trend"]:
            results.sort(key=lambda x: x.get("trend_score", 0.0), reverse=True)
        elif sort_by in ["breakout_score", "breakout"]:
            results.sort(key=lambda x: x.get("breakout_score", 0.0), reverse=True)
        elif sort_by in ["oversold_score", "oversold"]:
            results.sort(key=lambda x: x.get("oversold_score", 0.0), reverse=True)
        elif sort_by in ["trading_setup_score", "trading_setup"]:
            results.sort(key=lambda x: x.get("trading_setup_score", 0.0), reverse=True)
        else:
            results.sort(key=lambda x: x["final_score"], reverse=True)

        if limit:
            return results[:limit]
        return results

    @classmethod
    def _initialize_quick_top_universe(cls):
        """
        Quick initialization: batch-downloads and analyzes all IDX80 stocks.
        Since there are only 80 tickers, this is fast enough to run synchronously.
        """
        try:
            tickers = get_all_idx80_tickers()
            total = len(tickers)
            print(f"[BatchScanner] Quick init: batch downloading {total} IDX80 tickers...")

            all_data = batch_download_idx80(tickers=tickers, period="1y")
            print(f"[BatchScanner] Quick init: {len(all_data)} tickers downloaded, analyzing...")

            quick_results = []
            with ThreadPoolExecutor(max_workers=cls.MAX_WORKERS) as executor:
                future_to_ticker = {
                    executor.submit(cls._analyze_single_stock, t, all_data.get(t)): t
                    for t in tickers
                }
                for future in as_completed(future_to_ticker):
                    try:
                        res = future.result()
                        if res:
                            quick_results.append(res)
                    except Exception as e:
                        print(f"[BatchScanner] Error in quick init: {e}")

            total_berhasil = len(quick_results)
            total_gagal = max(0, total - total_berhasil)
            print(f"[BatchScanner] Quick init complete: {total_berhasil}/{total} IDX80 stocks analyzed.")
            if total_gagal > 0:
                print(f"[BatchScanner] {total_gagal} stocks failed (no data from Yahoo Finance).")

            with cls._lock:
                cls._RESULTS = sorted(quick_results, key=lambda x: x["final_score"], reverse=True)
                cls._total_stocks = total
                cls._current_index = total
                cls._progress_message = f"IDX80 Ready: {total_berhasil} / {total} saham"

        except Exception as e:
            print(f"[BatchScanner] ❌ Error during quick initialization: {e}")
            with cls._lock:
                cls._RESULTS = []
                cls._total_stocks = 0
                cls._progress_message = f"Gagal inisialisasi scanner: {str(e)[:100]}"
