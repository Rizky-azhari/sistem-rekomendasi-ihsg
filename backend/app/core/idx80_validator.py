"""
IDX80 Validation Layer
=======================
Centralized gatekeeper that every ticker request must pass through
before reaching Yahoo Finance API.

Flow:
    User Request → IDX80 Validation → Approved Ticker → Yahoo Finance → Data Processing
"""

from typing import List
from fastapi import HTTPException

from app.config.idx80_tickers import is_idx80, normalize_ticker, get_all_idx80_tickers


class IDX80ValidationError(Exception):
    """Raised when a ticker is not part of the IDX80 universe."""

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = symbol
        self.message = f"Ticker '{symbol}' is not included in IDX80 universe. Only IDX80 constituents are supported."
        super().__init__(self.message)


def validate_ticker(symbol: str) -> str:
    """
    Validates that a ticker is in the IDX80 whitelist.

    Args:
        symbol: Raw ticker input (e.g. "BBCA", "BBCA.JK", "bbca")

    Returns:
        Normalized ticker string (e.g. "BBCA.JK")

    Raises:
        IDX80ValidationError: If ticker is not in IDX80 whitelist or is empty.
    """
    if not symbol or not symbol.strip():
        raise IDX80ValidationError("(empty)")
    normalized = normalize_ticker(symbol)
    if not is_idx80(normalized):
        raise IDX80ValidationError(normalized)
    return normalized



def validate_tickers(symbols: List[str]) -> List[str]:
    """
    Validates a list of tickers against the IDX80 whitelist.

    Returns:
        List of normalized, validated tickers.

    Raises:
        IDX80ValidationError: On the first invalid ticker encountered.
    """
    validated = []
    for sym in symbols:
        validated.append(validate_ticker(sym))
    return validated


def validate_ticker_safe(symbol: str) -> tuple:
    """
    Non-raising validation. Returns (normalized_ticker, is_valid).
    Useful for batch operations where you want to skip invalid tickers
    instead of aborting.
    """
    if not symbol or not symbol.strip():
        return "", False
    normalized = normalize_ticker(symbol)
    return normalized, is_idx80(normalized)


def validate_ticker_optional(symbol: str = None) -> str:
    """Validates ticker if provided; returns None if None or empty string."""
    if not symbol or not str(symbol).strip():
        return None
    return validate_ticker(symbol)


def is_valid_idx80(symbol: str) -> bool:
    """Boolean check if a symbol is in IDX80 whitelist."""
    if not symbol or not str(symbol).strip():
        return False
    return is_idx80(symbol)


def get_validated_idx80_list() -> List[str]:

    """Returns the complete validated IDX80 ticker list."""
    return get_all_idx80_tickers()


def idx80_validation_exception_handler(request, exc: IDX80ValidationError):
    """
    FastAPI exception handler for IDX80ValidationError.
    Register this in your FastAPI app to auto-convert validation errors to HTTP 400.
    """
    return {
        "status_code": 400,
        "detail": exc.message,
        "ticker": exc.symbol,
        "allowed_universe": "IDX80"
    }
