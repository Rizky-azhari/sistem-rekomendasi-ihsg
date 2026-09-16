import asyncio
import datetime
import threading
import time
from typing import Optional
from app.universe.stock_universe_manager import StockUniverseManager


class UniverseScheduler:
    """
    Daily background scheduler for IDX Stock Universe.
    - Synchronizes active stocks
    - Detects new IPOs
    - Updates delisted stocks
    """

    _thread: Optional[threading.Thread] = None
    _is_running: bool = False
    _last_run: Optional[datetime.datetime] = None

    @classmethod
    def run_daily_job(cls):
        """Executes the daily universe update task."""
        print(f"[Scheduler] Running daily IDX stock universe synchronization at {datetime.datetime.now()}...")
        try:
            res = StockUniverseManager.sync_to_database()
            cls._last_run = datetime.datetime.now()
            print(f"[Scheduler] Daily sync success: {res['total_universe']} total, {res['inserted_new_ipos']} new IPOs.")
        except Exception as e:
            print(f"[Scheduler] Error during daily sync: {e}")

    @classmethod
    def _worker_loop(cls):
        """Background thread loop running once daily."""
        while cls._is_running:
            now = datetime.datetime.now()
            # If never run or past midnight (or last run was previous day)
            if not cls._last_run or cls._last_run.date() < now.date():
                cls.run_daily_job()
            
            # Sleep for 1 hour before checking again
            for _ in range(3600):
                if not cls._is_running:
                    break
                time.sleep(1)

    @classmethod
    def start(cls):
        """Starts the background scheduler thread."""
        if cls._thread and cls._thread.is_alive():
            return
        cls._is_running = True
        cls._thread = threading.Thread(target=cls._worker_loop, daemon=True, name="UniverseDailyScheduler")
        cls._thread.start()
        print("[Scheduler] UniverseDailyScheduler started successfully in background.")

    @classmethod
    def stop(cls):
        """Stops the scheduler."""
        cls._is_running = False
        if cls._thread:
            cls._thread = None
            print("[Scheduler] UniverseDailyScheduler stopped.")


def start_universe_scheduler():
    """Helper entry point to start the scheduler."""
    UniverseScheduler.start()
