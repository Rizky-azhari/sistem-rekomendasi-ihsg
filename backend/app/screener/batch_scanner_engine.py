import time
import math
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

from app.universe.stock_universe_manager import StockUniverseManager
from app.services.yahoo import get_historical_data, get_stock_info, normalize_symbol
from app.screener.stock_screener import screen_stock_rules
from app.recommendation.recommendation_engine import RecommendationEngine


class BatchScannerEngine:
    """
    Asynchronous Full-Universe Stock Scanner Engine for Indonesia Stock Exchange (IDX).
    
    Features:
    - Scans 800 - 950+ stocks in the IDX Stock Universe
    - Batched processing: 50 stocks per batch
    - Multi-threaded concurrent execution per batch (ThreadPoolExecutor)
    - Real-time progress tracking: 'Scanning Progress: 245 / 900 saham selesai'
    - Preserves all 5 core rules (Momentum, Trend, Oversold, Breakout, Trading Setup)
    - Automatically computes Recommendation Engine final score & reasons
    """

    BATCH_SIZE: int = 50
    MAX_WORKERS: int = 8

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
    def _scan_single_stock(cls, stock_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Worker function to process 1 stock through the 5-factor screener and recommendation engine."""
        sym = stock_item["symbol"]
        try:
            df = get_historical_data(sym, period="1y")
            if df.empty or len(df) < 14:
                return None

            screen_res = screen_stock_rules(df, sym)
            price = screen_res["price"]
            final_score = screen_res["final_score"]
            recommendation = screen_res["recommendation"]
            reasons = screen_res["reasons"]
            alasan = screen_res["alasan_rekomendasi"]

            # Calculate daily change if available
            change_pct = 0.0
            if len(df) >= 2:
                last_c = float(df["Close"].iloc[-1])
                prev_c = float(df["Close"].iloc[-2])
                change_pct = round(((last_c - prev_c) / prev_c) * 100, 2) if prev_c > 0 else 0.0

            volume = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0

            result = {
                "symbol": sym,
                "name": stock_item.get("company_name") or sym.replace(".JK", ""),
                "sector": stock_item.get("sector") or "IDX Equities",
                "board": stock_item.get("board") or "Utama",
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

            # Sanitize all NaN/Inf values to prevent JSON serialization errors
            return cls._sanitize_value(result)
        except Exception as e:
            return None


    @classmethod
    def _execute_scan_loop(cls, symbols_data: List[Dict[str, Any]]):
        """Internal worker executing batches of 50 stocks with progress updates."""
        total = len(symbols_data)
        total_batches = math.ceil(total / cls.BATCH_SIZE)

        with cls._lock:
            cls._is_running = True
            cls._current_index = 0
            cls._total_stocks = total
            cls._current_batch = 0
            cls._total_batches = total_batches
            cls._start_time = datetime.datetime.now()
            cls._end_time = None
            cls._progress_message = f"Scanning Progress: 0 / {total} saham selesai"

        print(f"[BatchScanner] Starting universe scan from stock_universe database...")
        print(f"Total saham ditemukan: {total}")
        scanned_results: List[Dict[str, Any]] = []

        for batch_num in range(total_batches):
            if not cls._is_running:
                print("[BatchScanner] Scan stopped prematurely.")
                break

            batch_start = batch_num * cls.BATCH_SIZE
            batch_end = min(batch_start + cls.BATCH_SIZE, total)
            batch_items = symbols_data[batch_start:batch_end]

            with cls._lock:
                cls._current_batch = batch_num + 1

            # Process 50 stocks concurrently using thread pool
            with ThreadPoolExecutor(max_workers=cls.MAX_WORKERS) as executor:
                future_to_stock = {
                    executor.submit(cls._scan_single_stock, item): item for item in batch_items
                }

                for future in as_completed(future_to_stock):
                    res = future.result()
                    if res:
                        scanned_results.append(res)

                    with cls._lock:
                        cls._current_index += 1
                        cls._progress_message = f"Scanning Progress: {cls._current_index} / {total} saham selesai"

            print(f"[BatchScanner] Completed Batch {batch_num + 1}/{total_batches} ({cls._current_index}/{total} stocks).")
            # Update live results cache periodically after each batch
            with cls._lock:
                cls._RESULTS = sorted(
                    scanned_results,
                    key=lambda x: x["final_score"],
                    reverse=True
                )

        total_ditemukan = total
        total_berhasil = len(scanned_results)
        total_gagal = max(0, total_ditemukan - total_berhasil)

        with cls._lock:
            cls._is_running = False
            cls._end_time = datetime.datetime.now()
            cls._progress_message = f"Scanning Selesai: {cls._current_index} / {total} saham diproses"
            cls._RESULTS = sorted(
                scanned_results,
                key=lambda x: x["final_score"],
                reverse=True
            )

        print(f"[BatchScanner] Finished universe scan!")
        print(f"Total saham ditemukan: {total_ditemukan}")
        print(f"Total saham berhasil dianalisis: {total_berhasil}")
        print(f"Total saham gagal: {total_gagal}")

    @classmethod
    def start_universe_scan(cls, max_stocks: Optional[int] = None) -> Dict[str, Any]:
        """
        Triggers full IDX stock universe scanning in background from stock_universe database table.
        """
        with cls._lock:
            if cls._is_running:
                return {
                    "status": "already_running",
                    "progress": cls.get_progress()
                }

        # Query all active stocks from stock_universe database
        universe = StockUniverseManager.fetch_all_idx_stocks()
        if max_stocks:
            universe = universe[:max_stocks]

        print(f"[BatchScanner] Initiating universe scan from stock_universe database...")
        print(f"Total saham ditemukan: {len(universe)}")

        cls._thread = threading.Thread(
            target=cls._execute_scan_loop,
            args=(universe,),
            daemon=True,
            name="BatchScannerWorker"
        )
        cls._thread.start()

        return {
            "status": "started",
            "total_stocks_to_scan": len(universe),
            "total_batches": math.ceil(len(universe) / cls.BATCH_SIZE),
            "progress_message": f"Scanning Progress: 0 / {len(universe)} saham selesai"
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
        """Returns sorted and filtered universe screener results."""
        with cls._lock:
            results = list(cls._RESULTS)

        # If no results cached yet, run a fast initial subset or fallback
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
        """Populates quick subset from stock_universe database and logs exact status."""
        try:
            all_universe = StockUniverseManager.fetch_all_idx_stocks()
            total_ditemukan = len(all_universe)
            print(f"[BatchScanner] Initializing from stock_universe database table...")
            print(f"Total saham ditemukan: {total_ditemukan}")

            if total_ditemukan == 0:
                print("[BatchScanner] No stocks found in universe. Returning empty results.")
                with cls._lock:
                    cls._RESULTS = []
                    cls._total_stocks = 0
                    cls._progress_message = "Belum ada data saham. Jalankan 'Sync Emiten' terlebih dahulu."
                return

            # Scan initial batch of 50 active stocks for immediate rendering
            initial_items = all_universe[:50]
            quick_results = []
            with ThreadPoolExecutor(max_workers=cls.MAX_WORKERS) as executor:
                future_to_stock = {
                    executor.submit(cls._scan_single_stock, item): item for item in initial_items
                }
                for future in as_completed(future_to_stock):
                    try:
                        res = future.result()
                        if res:
                            quick_results.append(res)
                    except Exception as e:
                        print(f"[BatchScanner] Error processing stock in quick init: {e}")

            total_berhasil = len(quick_results)
            total_gagal = max(0, len(initial_items) - total_berhasil)
            print(f"Total saham berhasil dianalisis: {total_berhasil}")
            print(f"Total saham gagal: {total_gagal}")

            with cls._lock:
                cls._RESULTS = sorted(quick_results, key=lambda x: x["final_score"], reverse=True)
                cls._total_stocks = total_ditemukan
                cls._current_index = len(initial_items)
                cls._progress_message = f"Scanning Progress: {len(initial_items)} / {total_ditemukan} saham selesai"

        except Exception as e:
            print(f"[BatchScanner] ❌ Error during quick initialization: {e}")
            with cls._lock:
                cls._RESULTS = []
                cls._total_stocks = 0
                cls._progress_message = f"Gagal inisialisasi scanner: {str(e)[:100]}"

