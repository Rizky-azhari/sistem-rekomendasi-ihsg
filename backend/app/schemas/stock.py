from pydantic import BaseModel
from typing import List, Optional

class StockInfo(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = "N/A"
    industry: Optional[str] = "N/A"
    current_price: float
    previous_close: float
    change_amount: float
    change_percentage: float
    volume: int
    market_cap: Optional[float] = None

class OHLCVData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class IndicatorData(BaseModel):
    date: str
    close: float
    sma20: Optional[float] = None
    sma50: Optional[float] = None
    sma200: Optional[float] = None
    ema12: Optional[float] = None
    ema26: Optional[float] = None
    rsi14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    atr14: Optional[float] = None
    vol_sma20: Optional[float] = None

class StockDetailResponse(BaseModel):
    info: StockInfo
    ohlcv: List[OHLCVData]
    indicators: List[IndicatorData]
