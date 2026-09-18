# Schemas package init
from .stock import StockInfo, OHLCVData, IndicatorData, StockDetailResponse
from .recommendation import (
    RuleBreakdown,
    TradingPlan,
    RecommendationResponse,
    ScreenerFilter,
    ScreenerResultItem,
)

# Legacy aliases for backward compatibility
StockInfoSchema = StockInfo
OHLCVSchema = OHLCVData
RecommendationSchema = RecommendationResponse

__all__ = [
    "StockInfo",
    "OHLCVData",
    "IndicatorData",
    "StockDetailResponse",
    "RuleBreakdown",
    "TradingPlan",
    "RecommendationResponse",
    "ScreenerFilter",
    "ScreenerResultItem",
    "StockInfoSchema",
    "OHLCVSchema",
    "RecommendationSchema",
]
