"""
Tests for IDX80 Data Cache.
"""

import unittest
import pandas as pd
import time
from app.services.data_cache import IDX80DataCache


class TestDataCache(unittest.TestCase):
    def setUp(self):
        self.cache = IDX80DataCache(ttl_seconds=2)

    def test_info_cache_set_and_get(self):
        """Cache stores and retrieves info correctly."""
        data = {"company_name": "Test Company", "price": 5000}
        self.cache.set_info("BBCA.JK", data)
        retrieved = self.cache.get_info("BBCA.JK")
        self.assertEqual(retrieved, data)

    def test_info_cache_normalization(self):
        """Cache lookup normalizes symbols automatically."""
        data = {"company_name": "Test Company", "price": 5000}
        self.cache.set_info("BBCA", data)
        self.assertEqual(self.cache.get_info("bbca.jk"), data)
        self.assertEqual(self.cache.get_info("BBCA"), data)

    def test_history_cache_set_and_get(self):
        """Cache stores and retrieves historical DataFrame correctly."""
        df = pd.DataFrame({"Close": [100, 200, 300], "Volume": [10, 20, 30]})
        self.cache.set_history("BBCA.JK", "1y", df)
        retrieved = self.cache.get_history("BBCA.JK", "1y")
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved), 3)

    def test_history_cache_normalization(self):
        """History cache lookup normalizes symbols automatically."""
        df = pd.DataFrame({"Close": [100, 200, 300]})
        self.cache.set_history("BBCA", "1y", df)
        retrieved = self.cache.get_history("bbca.jk", "1y")
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved), 3)

    def test_cache_miss(self):
        """Cache returns None for missing keys."""
        self.assertIsNone(self.cache.get_info("NONEXISTENT.JK"))
        self.assertIsNone(self.cache.get_history("NONEXISTENT.JK", "1y"))

    def test_cache_ttl_expiry(self):
        """Cached data expires after TTL."""
        cache_fast = IDX80DataCache(ttl_seconds=1)
        cache_fast.set_info("BBCA.JK", {"price": 1000})
        self.assertIsNotNone(cache_fast.get_info("BBCA.JK"))
        time.sleep(1.1)
        self.assertIsNone(cache_fast.get_info("BBCA.JK"))

    def test_invalidation(self):
        """Invalidating a symbol removes both info and history."""
        self.cache.set_info("BBCA.JK", {"price": 1000})
        df = pd.DataFrame({"Close": [100]})
        self.cache.set_history("BBCA.JK", "1y", df)

        self.cache.invalidate("BBCA")
        self.assertIsNone(self.cache.get_info("BBCA.JK"))
        self.assertIsNone(self.cache.get_history("BBCA.JK", "1y"))

    def test_clear_all(self):
        """clear_all empties all cache stores."""
        self.cache.set_info("BBCA.JK", {"price": 1000})
        self.cache.set_info("BBRI.JK", {"price": 2000})
        self.cache.clear_all()
        stats = self.cache.get_stats()
        self.assertEqual(stats["info_entries"], 0)
        self.assertEqual(stats["history_entries"], 0)


if __name__ == "__main__":
    unittest.main()
