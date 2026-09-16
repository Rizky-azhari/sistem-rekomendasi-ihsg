from pydantic import BaseModel
from typing import List, Optional

class RuleBreakdown(BaseModel):
    rule_name: str
    category: str  # Trend, Momentum, Volatility, Volume
    score: float   # e.g., -25 to +25
    weight: float
    description: str
    status: str    # BULLISH, BEARISH, NEUTRAL

class TradingPlan(BaseModel):
    entry_price: float
    entry_range: str
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    risk_reward_ratio: float
    recommended_risk_percent: float = 2.0  # Max risk allocation %
    notes: str

class RecommendationResponse(BaseModel):
    symbol: str
    name: str
    current_price: float
    signal: str      # STRONG BUY, BUY, HOLD, SELL, STRONG SELL
    total_score: float # 0 to 100
    confidence_level: str # HIGH, MEDIUM, LOW
    summary: str
    rule_breakdowns: List[RuleBreakdown]
    trading_plan: TradingPlan
    updated_at: str

class ScreenerFilter(BaseModel):
    signal: Optional[str] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    sector: Optional[str] = None

class ScreenerResultItem(BaseModel):
    symbol: str
    name: str
    sector: str
    current_price: float
    change_percentage: float
    signal: str
    total_score: float
    rsi: Optional[float] = None
    macd_status: Optional[str] = None
    volume: int
