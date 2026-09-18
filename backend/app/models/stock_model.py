from sqlalchemy import Column, Integer, BigInteger, String, Float, Numeric, Date, DateTime, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


# ==============================================================================
# 1. STOCKS TABLE
# ==============================================================================
class Stock(Base):
    """Master stock metadata table."""
    __tablename__ = "stocks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True, index=True)
    exchange = Column(String(20), default="IDX", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    prices = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    indicators = relationship("Indicator", back_populates="stock", cascade="all, delete-orphan")
    screener_results = relationship("ScreenerResult", back_populates="stock", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="stock", cascade="all, delete-orphan")
    trading_plans = relationship("TradingPlan", back_populates="stock", cascade="all, delete-orphan")


# ==============================================================================
# 2. STOCK_PRICES TABLE
# ==============================================================================
class StockPrice(Base):
    """Historical and daily OHLCV stock prices."""
    __tablename__ = "stock_prices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(14, 2), nullable=False)
    high = Column(Numeric(14, 2), nullable=False)
    low = Column(Numeric(14, 2), nullable=False)
    close = Column(Numeric(14, 2), nullable=False)
    volume = Column(BigInteger, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_stock_prices_symbol_date"),
    )

    stock = relationship("Stock", back_populates="prices")


# ==============================================================================
# 3. INDICATORS TABLE
# ==============================================================================
class Indicator(Base):
    """Calculated technical indicators (MA20, MA50, MA200, RSI, Volatility)."""
    __tablename__ = "indicators"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, default=func.current_date(), nullable=False)
    ma20 = Column(Numeric(14, 2), nullable=True)
    ma50 = Column(Numeric(14, 2), nullable=True)
    ma200 = Column(Numeric(14, 2), nullable=True)
    rsi = Column(Numeric(6, 2), nullable=True)
    volatility = Column(Numeric(10, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uq_indicators_symbol_date"),
    )

    stock = relationship("Stock", back_populates="indicators")


# ==============================================================================
# 4. SCREENER_RESULT TABLE
# ==============================================================================
class ScreenerResult(Base):
    """Screener factor scores and setup rankings."""
    __tablename__ = "screener_result"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False, index=True)
    momentum_score = Column(Numeric(6, 2), default=0.0, nullable=False)
    trend_score = Column(Numeric(6, 2), default=0.0, nullable=False)
    breakout_score = Column(Numeric(6, 2), default=0.0, nullable=False)
    oversold_score = Column(Numeric(6, 2), default=0.0, nullable=False)
    trading_setup_score = Column(Numeric(6, 2), default=0.0, nullable=False, index=True)
    screened_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    stock = relationship("Stock", back_populates="screener_results")


# ==============================================================================
# 5. RECOMMENDATION TABLE
# ==============================================================================
class Recommendation(Base):
    """Final decision recommendation output."""
    __tablename__ = "recommendation"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False, index=True)
    final_score = Column(Numeric(6, 2), nullable=False, index=True)
    recommendation = Column(String(20), nullable=False)  # STRONG BUY, BUY, HOLD, SELL
    upside = Column(Numeric(6, 2), nullable=True)
    risk = Column(String(20), nullable=True)             # LOW, MEDIUM, HIGH
    liquidity = Column(String(20), nullable=True)        # HIGH, MEDIUM, LOW
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    stock = relationship("Stock", back_populates="recommendations")


# ==============================================================================
# 6. TRADING_PLAN TABLE
# ==============================================================================
class TradingPlan(Base):
    """Automated execution plan: Buy Area, Stop Loss, Target Profits, RR."""
    __tablename__ = "trading_plan"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("stocks.symbol", ondelete="CASCADE"), nullable=False, index=True)
    buy_area = Column(String(100), nullable=False)
    stop_loss = Column(Numeric(14, 2), nullable=False)
    tp1 = Column(Numeric(14, 2), nullable=False)
    tp2 = Column(Numeric(14, 2), nullable=True)
    tp3 = Column(Numeric(14, 2), nullable=True)
    risk_reward = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    stock = relationship("Stock", back_populates="trading_plans")


# ==============================================================================
# 7. STOCK_UNIVERSE TABLE (Comprehensive All-IDX Issuers Universe)
# ==============================================================================
class StockUniverse(Base):
    """Full IDX Stock Universe table tracking all Indonesian listed issuers."""
    __tablename__ = "stock_universe"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True, index=True)
    board = Column(String(50), default="Utama", index=True)
    market_cap = Column(Numeric(20, 2), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ==============================================================================
# 8. IDX80_STOCKS TABLE (IDX80 Index Constituents — Performance Optimized)
# ==============================================================================
class IDX80Stock(Base):
    """IDX80 Index constituent reference table. 80 constituent stocks."""
    __tablename__ = "idx80_stocks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True, index=True)
    market = Column(String(20), default="IDX80", index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ==============================================================================
# BACKWARD COMPATIBILITY ALIASES & CACHE
# ==============================================================================
class StockCache(Base):
    __tablename__ = "stock_cache"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    current_price = Column(Float, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


RecommendationLog = Recommendation
StockModel = Stock

