"""
Tests for IDX80 Ticker Configuration and Whitelist.
"""

import sys
from pathlib import Path
import unittest

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
from app.config.idx80_tickers import (
    IDX80_TICKERS,
    IDX80_EXPECTED_COUNT,
    IDX80_METADATA,
    is_idx80,
    normalize_ticker,
    get_all_idx80_tickers,
    get_idx80_metadata,
    get_idx80_stocks_for_db,
)


class TestIDX80Config(unittest.TestCase):
    def test_ticker_count(self):
        """Verify exactly 80 tickers are defined."""
        self.assertEqual(len(IDX80_TICKERS), 80)
        self.assertEqual(IDX80_EXPECTED_COUNT, 80)
        self.assertEqual(len(IDX80_METADATA), 80)

    def test_ticker_format(self):
        """All tickers must end with .JK and be uppercase."""
        for ticker in IDX80_TICKERS:
            self.assertTrue(ticker.endswith(".JK"), f"{ticker} does not end with .JK")
            self.assertEqual(ticker, ticker.upper())
            self.assertTrue(ticker in IDX80_METADATA, f"{ticker} missing from IDX80_METADATA")

    def test_metadata_fields(self):
        """All metadata entries must have company_name, sector, and market."""
        for ticker, meta in IDX80_METADATA.items():
            self.assertIn("company_name", meta)
            self.assertIn("sector", meta)
            self.assertEqual(meta["market"], "IDX80")
            self.assertTrue(len(meta["company_name"]) > 0)
            self.assertTrue(len(meta["sector"]) > 0)

    def test_normalize_ticker(self):
        """Normalization should handle tickers with or without .JK suffix."""
        self.assertEqual(normalize_ticker("bbca"), "BBCA.JK")
        self.assertEqual(normalize_ticker("BBCA"), "BBCA.JK")
        self.assertEqual(normalize_ticker("BBCA.JK"), "BBCA.JK")
        self.assertEqual(normalize_ticker("  tlkm  "), "TLKM.JK")
        self.assertEqual(normalize_ticker("bmri.jk"), "BMRI.JK")

    def test_is_idx80(self):
        """Whitelist check should correctly classify tickers."""
        # Valid IDX80 tickers
        self.assertTrue(is_idx80("BBCA"))
        self.assertTrue(is_idx80("BBCA.JK"))
        self.assertTrue(is_idx80("bbri"))
        self.assertTrue(is_idx80("TLKM.JK"))
        self.assertTrue(is_idx80("ASII"))
        self.assertTrue(is_idx80("GOTO"))

        # Non-IDX80 tickers
        self.assertFalse(is_idx80("AAPL"))
        self.assertFalse(is_idx80("TSLA.JK"))
        self.assertFalse(is_idx80("NONEXISTENT"))
        self.assertFalse(is_idx80("ZZZZ.JK"))

    def test_get_all_idx80_tickers(self):
        """Returns a copy of the 80 tickers."""
        tickers = get_all_idx80_tickers()
        self.assertEqual(len(tickers), 80)
        self.assertEqual(tickers, IDX80_TICKERS)
        # Ensure returned list is a copy
        tickers.append("FAKE.JK")
        self.assertEqual(len(IDX80_TICKERS), 80)

    def test_get_idx80_metadata(self):
        """Metadata retrieval works with normalized and unnormalized tickers."""
        meta = get_idx80_metadata("bbca")
        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertIn("Bank Central Asia", meta["company_name"])

        meta_none = get_idx80_metadata("INVALID")
        self.assertIsNone(meta_none)

    def test_get_idx80_stocks_for_db(self):
        """Database seeding list contains 80 items with required keys."""
        db_stocks = get_idx80_stocks_for_db()
        self.assertEqual(len(db_stocks), 80)
        for item in db_stocks:
            self.assertIn("ticker", item)
            self.assertIn("company_name", item)
            self.assertIn("sector", item)
            self.assertEqual(item["market"], "IDX80")
            self.assertTrue(item["is_active"])


if __name__ == "__main__":
    unittest.main()
