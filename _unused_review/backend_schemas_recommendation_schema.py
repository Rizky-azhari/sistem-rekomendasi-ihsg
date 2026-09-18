from pydantic import BaseModel
from typing import List, Optional

class TradingPlanSchema(BaseModel):
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    risk_reward_ratio: float

class RecommendationSchema(BaseModel):
    symbol: str
    signal: str
    total_score: float
    trading_plan: TradingPlanSchema
