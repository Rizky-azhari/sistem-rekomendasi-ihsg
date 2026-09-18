"""
Universe Scheduler — IDX80 Only
==================================
Daily background scheduler for IDX80 stock universe.
Syncs IDX80 data to database (no external API calls).
"""

import datetime
import threading
import time
from typing import Optional
from app.universe.stock_universe_manager import StockUniverseManager


class UniverseScheduler:
    """
    Daily background scheduler for IDX80 Stock Universe.
    - Synchronizes idx80_stocks table
    - Refreshes cache
    """

    _thread: Optional[threading.Thread] = None
    _is_running: bool = False
    _last_run: Optional[datetime.datetime] = None

    @classmethod
    def run_daily_job(cls):
        """Executes the daily IDX80 universe sync task."""
        print(f"[Scheduler] Running daily IDX80 universe synchronization at {datetime.datetime.now()}...")
        try:
            res = StockUniverseManager.sync_to_database()
            cls._last_run = datetime.datetime.now()
            print(f"[Scheduler] Daily sync success: {res['total_universe']} IDX80 stocks synced.")
        except Exception as e:
            print(f"[Scheduler] Error during daily sync: {e}")

    @classmethod
    def _worker_loop(cls):
        """Background thread loop running once daily."""
        while cls._is_running:
            now = datetime.datetime.now()
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
        cls._thread = threading.Thread(target=cls._worker_loop, daemon=True, name="IDX80DailyScheduler")
        cls._thread.start()
        print("[Scheduler] IDX80DailyScheduler started successfully in background.")

    @classmethod
    def stop(cls):
        """Stops the scheduler."""
        cls._is_running = False
        if cls._thread:
            cls._thread = None
            print("[Scheduler] IDX80DailyScheduler stopped.")


def start_universe_scheduler():
    """Helper entry point to start the scheduler."""
    UniverseScheduler.start()
