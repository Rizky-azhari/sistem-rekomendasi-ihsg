from pydantic import BaseModel
from typing import Optional, List

class StockInfoSchema(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    current_price: float
    change_percentage: float

class OHLCVSchema(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
