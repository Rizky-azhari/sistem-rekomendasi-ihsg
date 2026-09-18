"""
Tests for IDX80 Validation Layer.
"""

import unittest
from app.core.idx80_validator import (
    validate_ticker,
    validate_tickers,
    validate_ticker_optional,
    is_valid_idx80,
    IDX80ValidationError,
)


class TestIDX80Validator(unittest.TestCase):
    def test_validate_valid_tickers(self):
        """Valid IDX80 tickers pass validation and are normalized."""
        self.assertEqual(validate_ticker("BBCA"), "BBCA.JK")
        self.assertEqual(validate_ticker("bbca.jk"), "BBCA.JK")
        self.assertEqual(validate_ticker("  BBRI  "), "BBRI.JK")
        self.assertEqual(validate_ticker("TLKM.JK"), "TLKM.JK")
        self.assertEqual(validate_ticker("bmri"), "BMRI.JK")

    def test_validate_invalid_ticker_raises(self):
        """Invalid tickers raise IDX80ValidationError with descriptive message."""
        with self.assertRaises(IDX80ValidationError) as ctx:
            validate_ticker("AAPL")
        self.assertIn("AAPL.JK", ctx.exception.message)
        self.assertIn("IDX80", ctx.exception.message)

        with self.assertRaises(IDX80ValidationError) as ctx:
            validate_ticker("UNKNOWN_TICKER")
        self.assertEqual(ctx.exception.ticker, "UNKNOWN_TICKER.JK")

    def test_validate_empty_ticker_raises(self):
        """Empty or whitespace ticker raises IDX80ValidationError."""
        with self.assertRaises(IDX80ValidationError):
            validate_ticker("")
        with self.assertRaises(IDX80ValidationError):
            validate_ticker("   ")

    def test_validate_tickers_batch(self):
        """Batch validation succeeds if all tickers are in IDX80."""
        inputs = ["BBCA", "BBRI.JK", "BMRI", "TLKM"]
        expected = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK"]
        self.assertEqual(validate_tickers(inputs), expected)

    def test_validate_tickers_batch_fails_on_any_invalid(self):
        """Batch validation raises if even one ticker is invalid."""
        inputs = ["BBCA", "INVALID_STOCK", "BMRI"]
        with self.assertRaises(IDX80ValidationError):
            validate_tickers(inputs)

    def test_validate_tickers_batch_empty(self):
        """Empty batch returns empty list."""
        self.assertEqual(validate_tickers([]), [])

    def test_validate_ticker_optional(self):
        """Optional validation returns None for None/empty, validates otherwise."""
        self.assertIsNone(validate_ticker_optional(None))
        self.assertIsNone(validate_ticker_optional(""))
        self.assertEqual(validate_ticker_optional("bbca"), "BBCA.JK")

        with self.assertRaises(IDX80ValidationError):
            validate_ticker_optional("INVALID")

    def test_is_valid_idx80(self):
        """Boolean check without exceptions."""
        self.assertTrue(is_valid_idx80("BBCA"))
        self.assertTrue(is_valid_idx80("BBCA.JK"))
        self.assertFalse(is_valid_idx80("INVALID"))
        self.assertFalse(is_valid_idx80(""))


if __name__ == "__main__":
    unittest.main()
