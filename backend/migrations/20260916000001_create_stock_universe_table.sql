-- ==============================================================================
-- Migration: 20260916000001_create_stock_universe_table.sql
-- Description: Create stock_universe table for all Indonesia Stock Exchange (IDX) issuers
-- ==============================================================================

CREATE TABLE IF NOT EXISTS public.stock_universe (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    board VARCHAR(50) DEFAULT 'Utama',
    market_cap NUMERIC(20, 2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_update TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Optimized B-Tree indexes for fast queries, filters, and symbol lookups
CREATE INDEX IF NOT EXISTS idx_stock_universe_symbol ON public.stock_universe(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_universe_is_active ON public.stock_universe(is_active);
CREATE INDEX IF NOT EXISTS idx_stock_universe_sector ON public.stock_universe(sector);
CREATE INDEX IF NOT EXISTS idx_stock_universe_board ON public.stock_universe(board);

-- Enable Row-Level Security (RLS) with Public Read Policy
ALTER TABLE public.stock_universe ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'stock_universe' 
        AND policyname = 'Allow public read access on stock_universe'
    ) THEN
        CREATE POLICY "Allow public read access on stock_universe" 
        ON public.stock_universe FOR SELECT 
        TO anon, authenticated 
        USING (true);
    END IF;
END $$;
