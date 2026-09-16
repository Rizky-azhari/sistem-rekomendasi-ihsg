-- ==============================================================================
-- IHSG Smart Stock Recommendation System - PostgreSQL Schema Migration
-- Designed according to Supabase Postgres Best Practices:
-- 1. BIGINT GENERATED ALWAYS AS IDENTITY for primary keys
-- 2. Lowercase snake_case identifiers for multi-tool/ORM compatibility
-- 3. Indexed Foreign Keys (ON DELETE CASCADE) for optimal JOINs and CASCADE speed
-- 4. Composite unique constraints to prevent duplicate timeseries/price rows
-- 5. Row-Level Security (RLS) enabled with public read policies
-- ==============================================================================

-- 1. STOCKS TABLE (Master Data)
CREATE TABLE IF NOT EXISTS public.stocks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    exchange VARCHAR(20) NOT NULL DEFAULT 'IDX',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index on symbol and sector for fast lookup and filtering
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON public.stocks(symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_sector ON public.stocks(sector);

-- ------------------------------------------------------------------------------
-- 2. STOCK_PRICES TABLE (OHLCV Historical & Daily Prices)
CREATE TABLE IF NOT EXISTS public.stock_prices (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES public.stocks(symbol) ON DELETE CASCADE,
    date DATE NOT NULL,
    open NUMERIC(14, 2) NOT NULL,
    high NUMERIC(14, 2) NOT NULL,
    low NUMERIC(14, 2) NOT NULL,
    close NUMERIC(14, 2) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_stock_prices_symbol_date UNIQUE (symbol, date)
);

-- Fast lookup for ticker history ordered by date
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON public.stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON public.stock_prices(date DESC);
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date ON public.stock_prices(symbol, date DESC);

-- ------------------------------------------------------------------------------
-- 3. INDICATORS TABLE (Technical Indicators: MA, RSI, Volatility)
CREATE TABLE IF NOT EXISTS public.indicators (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES public.stocks(symbol) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    ma20 NUMERIC(14, 2),
    ma50 NUMERIC(14, 2),
    ma200 NUMERIC(14, 2),
    rsi NUMERIC(6, 2),
    volatility NUMERIC(10, 4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_indicators_symbol_date UNIQUE (symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_indicators_symbol ON public.indicators(symbol);
CREATE INDEX IF NOT EXISTS idx_indicators_date ON public.indicators(date DESC);

-- ------------------------------------------------------------------------------
-- 4. SCREENER_RESULT TABLE (Multi-factor Screener Scores)
CREATE TABLE IF NOT EXISTS public.screener_result (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES public.stocks(symbol) ON DELETE CASCADE,
    momentum_score NUMERIC(6, 2) NOT NULL DEFAULT 0,
    trend_score NUMERIC(6, 2) NOT NULL DEFAULT 0,
    breakout_score NUMERIC(6, 2) NOT NULL DEFAULT 0,
    oversold_score NUMERIC(6, 2) NOT NULL DEFAULT 0,
    trading_setup_score NUMERIC(6, 2) NOT NULL DEFAULT 0,
    screened_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_screener_result_symbol ON public.screener_result(symbol);
CREATE INDEX IF NOT EXISTS idx_screener_result_setup_score ON public.screener_result(trading_setup_score DESC);
CREATE INDEX IF NOT EXISTS idx_screener_result_screened_at ON public.screener_result(screened_at DESC);

-- ------------------------------------------------------------------------------
-- 5. RECOMMENDATION TABLE (Decision Support System Output)
CREATE TABLE IF NOT EXISTS public.recommendation (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES public.stocks(symbol) ON DELETE CASCADE,
    final_score NUMERIC(6, 2) NOT NULL,
    recommendation VARCHAR(20) NOT NULL, -- e.g. STRONG BUY, BUY, HOLD, SELL
    upside NUMERIC(6, 2),                -- Expected percentage upside (%)
    risk VARCHAR(20),                    -- LOW, MEDIUM, HIGH
    liquidity VARCHAR(20),               -- HIGH, MEDIUM, LOW
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommendation_symbol ON public.recommendation(symbol);
CREATE INDEX IF NOT EXISTS idx_recommendation_final_score ON public.recommendation(final_score DESC);
CREATE INDEX IF NOT EXISTS idx_recommendation_created_at ON public.recommendation(created_at DESC);

-- ------------------------------------------------------------------------------
-- 6. TRADING_PLAN TABLE (Automated Entry, SL, TP1, TP2, TP3, RR)
CREATE TABLE IF NOT EXISTS public.trading_plan (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES public.stocks(symbol) ON DELETE CASCADE,
    buy_area VARCHAR(100) NOT NULL,
    stop_loss NUMERIC(14, 2) NOT NULL,
    tp1 NUMERIC(14, 2) NOT NULL,
    tp2 NUMERIC(14, 2),
    tp3 NUMERIC(14, 2),
    risk_reward VARCHAR(20),            -- e.g. 1:2.5
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trading_plan_symbol ON public.trading_plan(symbol);
CREATE INDEX IF NOT EXISTS idx_trading_plan_created_at ON public.trading_plan(created_at DESC);

-- ------------------------------------------------------------------------------
-- 7. ENABLE ROW-LEVEL SECURITY (RLS) FOR ALL TABLES
ALTER TABLE public.stocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.stock_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.screener_result ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendation ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trading_plan ENABLE ROW LEVEL SECURITY;

-- Read policies for public access (anon & authenticated)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'stocks' AND policyname = 'Allow public read access on stocks') THEN
        CREATE POLICY "Allow public read access on stocks" ON public.stocks FOR SELECT TO anon, authenticated USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'stock_prices' AND policyname = 'Allow public read access on stock_prices') THEN
        CREATE POLICY "Allow public read access on stock_prices" ON public.stock_prices FOR SELECT TO anon, authenticated USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'indicators' AND policyname = 'Allow public read access on indicators') THEN
        CREATE POLICY "Allow public read access on indicators" ON public.indicators FOR SELECT TO anon, authenticated USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'screener_result' AND policyname = 'Allow public read access on screener_result') THEN
        CREATE POLICY "Allow public read access on screener_result" ON public.screener_result FOR SELECT TO anon, authenticated USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'recommendation' AND policyname = 'Allow public read access on recommendation') THEN
        CREATE POLICY "Allow public read access on recommendation" ON public.recommendation FOR SELECT TO anon, authenticated USING (true);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'trading_plan' AND policyname = 'Allow public read access on trading_plan') THEN
        CREATE POLICY "Allow public read access on trading_plan" ON public.trading_plan FOR SELECT TO anon, authenticated USING (true);
    END IF;
END $$;

-- ------------------------------------------------------------------------------
-- 8. INITIAL SEED DATA FOR TOP IHSG BLUECHIP & POPULAR STOCKS
INSERT INTO public.stocks (symbol, company_name, sector, exchange)
VALUES 
    ('BBCA.JK', 'Bank Central Asia Tbk', 'Financials', 'IDX'),
    ('BBRI.JK', 'Bank Rakyat Indonesia (Persero) Tbk', 'Financials', 'IDX'),
    ('BMRI.JK', 'Bank Mandiri (Persero) Tbk', 'Financials', 'IDX'),
    ('BBNI.JK', 'Bank Negara Indonesia (Persero) Tbk', 'Financials', 'IDX'),
    ('TLKM.JK', 'Telkom Indonesia (Persero) Tbk', 'Telecommunication', 'IDX'),
    ('ASII.JK', 'Astra International Tbk', 'Industrials', 'IDX'),
    ('GOTO.JK', 'GoTo Gojek Tokopedia Tbk', 'Technology', 'IDX'),
    ('ICBP.JK', 'Indofood CBP Sukses Makmur Tbk', 'Consumer Non-Cyclicals', 'IDX'),
    ('UNVR.JK', 'Unilever Indonesia Tbk', 'Consumer Non-Cyclicals', 'IDX'),
    ('AMRT.JK', 'Sumber Alfaria Trijaya Tbk', 'Consumer Non-Cyclicals', 'IDX'),
    ('ADRO.JK', 'Alamtri Resources Indonesia Tbk', 'Energy', 'IDX'),
    ('PTBA.JK', 'Bukit Asam Tbk', 'Energy', 'IDX'),
    ('PGAS.JK', 'Perusahaan Gas Negara Tbk', 'Utilities', 'IDX'),
    ('INDF.JK', 'Indofood Sukses Makmur Tbk', 'Consumer Non-Cyclicals', 'IDX'),
    ('CPIN.JK', 'Charoen Pokphand Indonesia Tbk', 'Consumer Non-Cyclicals', 'IDX'),
    ('KLBF.JK', 'Kalbe Farma Tbk', 'Healthcare', 'IDX')
ON CONFLICT (symbol) DO UPDATE SET 
    company_name = EXCLUDED.company_name,
    sector = EXCLUDED.sector,
    exchange = EXCLUDED.exchange,
    updated_at = NOW();
