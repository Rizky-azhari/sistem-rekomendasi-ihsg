"""
IDX80 Data Cache
=================
Thread-safe, TTL-based in-memory cache for Yahoo Finance data.
Prevents repeated API calls for the same stock within the cache window.

Cache targets:
  - Historical OHLCV DataFrames (keyed by symbol + period)
  - Stock info dicts (keyed by symbol)
  - Batch download results (keyed by batch timestamp)
"""

import time
import threading
from typing import Dict, Any, Optional, Tuple, Union
import pandas as pd

from app.config.idx80_tickers import normalize_ticker


class IDX80DataCache:
    """
    Thread-safe TTL cache for IDX80 stock data.

    Usage:
        cache = IDX80DataCache(ttl_seconds=3600)
        cache.set_history("BBCA.JK", "1y", df)
        df = cache.get_history("BBCA.JK", "1y")  # returns df or None if expired
    """

    DEFAULT_TTL = 3600  # 1 hour

    def __init__(self, ttl_seconds: int = DEFAULT_TTL):
        self.ttl = ttl_seconds
        self._lock = threading.Lock()

        # {(symbol, period): (DataFrame, timestamp)}
        self._history_cache: Dict[Tuple[str, str], Tuple[pd.DataFrame, float]] = {}

        # {symbol: (info_dict, timestamp)}
        self._info_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}

        # Batch download cache: {cache_key: (Dict[str, DataFrame], timestamp)}
        self._batch_cache: Dict[str, Tuple[Dict[str, pd.DataFrame], float]] = {}

    def _is_valid(self, timestamp: float) -> bool:
        """Check if a cached entry is still within TTL."""
        return (time.time() - timestamp) < self.ttl

    # -------------------------------------------------------------------------
    # Historical Price Data Cache
    # -------------------------------------------------------------------------
    def get_history(self, symbol: str, period: str = "1y", *args) -> Optional[pd.DataFrame]:
        """Returns cached DataFrame or None if expired/missing."""
        key = (normalize_ticker(symbol), period)
        with self._lock:
            entry = self._history_cache.get(key)
            if entry and self._is_valid(entry[1]):
                return entry[0].copy()
        return None

    def set_history(self, symbol: str, period: str, *args, **kwargs) -> None:
        """
        Stores a DataFrame in the history cache.
        Supports:
          set_history(symbol, period, df)
          set_history(symbol, period, interval, df)
        """
        df = None
        if len(args) == 1 and isinstance(args[0], pd.DataFrame):
            df = args[0]
        elif len(args) >= 2 and isinstance(args[1], pd.DataFrame):
            df = args[1]
        elif "df" in kwargs and isinstance(kwargs["df"], pd.DataFrame):
            df = kwargs["df"]

        if df is None:
            return

        key = (normalize_ticker(symbol), period)
        with self._lock:
            self._history_cache[key] = (df.copy(), time.time())

    # -------------------------------------------------------------------------
    # Stock Info Cache
    # -------------------------------------------------------------------------
    def get_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Returns cached stock info dict or None if expired/missing."""
        sym = normalize_ticker(symbol)
        with self._lock:
            entry = self._info_cache.get(sym)
            if entry and self._is_valid(entry[1]):
                return dict(entry[0])
        return None

    def set_info(self, symbol: str, data: Dict[str, Any]) -> None:
        """Stores stock info in the cache."""
        sym = normalize_ticker(symbol)
        with self._lock:
            self._info_cache[sym] = (dict(data), time.time())


    # -------------------------------------------------------------------------
    # Batch Download Cache
    # -------------------------------------------------------------------------
    def get_batch(self, cache_key: str) -> Optional[Dict[str, pd.DataFrame]]:
        """Returns cached batch download result or None if expired/missing."""
        with self._lock:
            entry = self._batch_cache.get(cache_key)
            if entry and self._is_valid(entry[1]):
                return entry[0]
        return None

    def set_batch(self, cache_key: str, data: Dict[str, pd.DataFrame]) -> None:
        """Stores batch download result in cache."""
        with self._lock:
            self._batch_cache[cache_key] = (data, time.time())

    # -------------------------------------------------------------------------
    # Cache Management
    # -------------------------------------------------------------------------
    def invalidate(self, symbol: str) -> None:
        """Removes all cached data for a specific symbol."""
        sym = normalize_ticker(symbol)
        with self._lock:
            keys_to_remove = [k for k in self._history_cache if k[0] == sym]
            for k in keys_to_remove:
                del self._history_cache[k]
            self._info_cache.pop(sym, None)

    def invalidate_all(self) -> None:
        """Clears the entire cache."""
        with self._lock:
            self._history_cache.clear()
            self._info_cache.clear()
            self._batch_cache.clear()

    def clear_all(self) -> None:
        """Alias for invalidate_all."""
        self.invalidate_all()


    def get_stats(self) -> Dict[str, Any]:
        """Returns cache statistics."""
        with self._lock:
            valid_history = sum(1 for v in self._history_cache.values() if self._is_valid(v[1]))
            valid_info = sum(1 for v in self._info_cache.values() if self._is_valid(v[1]))
            return {
                "history_entries": len(self._history_cache),
                "history_valid": valid_history,
                "info_entries": len(self._info_cache),
                "info_valid": valid_info,
                "batch_entries": len(self._batch_cache),
                "ttl_seconds": self.ttl
            }

    def cleanup_expired(self) -> int:
        """Removes expired entries. Returns number of entries removed."""
        removed = 0
        with self._lock:
            expired_history = [k for k, v in self._history_cache.items() if not self._is_valid(v[1])]
            for k in expired_history:
                del self._history_cache[k]
                removed += 1

            expired_info = [k for k, v in self._info_cache.items() if not self._is_valid(v[1])]
            for k in expired_info:
                del self._info_cache[k]
                removed += 1

            expired_batch = [k for k, v in self._batch_cache.items() if not self._is_valid(v[1])]
            for k in expired_batch:
                del self._batch_cache[k]
                removed += 1

        return removed


# ==============================================================================
# Global singleton cache instance
# ==============================================================================
idx80_cache = IDX80DataCache(ttl_seconds=3600)
