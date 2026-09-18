# Services package init
from .yahoo import (
    get_stock_info,
    get_all_stocks,
    get_historical_data,
    normalize_ticker as normalize_symbol,  # backward compatibility alias
    DEFAULT_IHSG_SYMBOLS
)
from .indicator import (
    calculate_ma,
    calculate_rsi,
    calculate_indicators,
    extract_latest_indicators
)
from .analysis import (
    determine_trend,
    perform_stock_analysis
)

# Compatibility classes / aliases
from .stock_service import StockService
from .yfinance_service import YFinanceService, fetch_stock_info, fetch_stock_history

__all__ = [
    # Yahoo service
    "get_stock_info",
    "get_all_stocks",
    "get_historical_data",
    "normalize_symbol",
    "DEFAULT_IHSG_SYMBOLS",
    # Indicator service
    "calculate_ma",
    "calculate_rsi",
    "calculate_indicators",
    "extract_latest_indicators",
    # Analysis service
    "determine_trend",
    "perform_stock_analysis",
    # Backward compatibility
    "StockService",
    "YFinanceService",
    "fetch_stock_info",
    "fetch_stock_history"
]
