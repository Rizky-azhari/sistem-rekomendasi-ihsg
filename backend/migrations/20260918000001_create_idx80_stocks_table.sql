-- ==============================================================================
-- Migration: 20260918000001_create_idx80_stocks_table.sql
-- Description: Create idx80_stocks reference table for IDX80 Index constituents (80 Stocks)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS public.idx80_stocks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    market VARCHAR(20) DEFAULT 'IDX80',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Optimized indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_idx80_stocks_ticker ON public.idx80_stocks(ticker);
CREATE INDEX IF NOT EXISTS idx_idx80_stocks_is_active ON public.idx80_stocks(is_active);
CREATE INDEX IF NOT EXISTS idx_idx80_stocks_sector ON public.idx80_stocks(sector);
CREATE INDEX IF NOT EXISTS idx_idx80_stocks_market ON public.idx80_stocks(market);

-- Enable Row-Level Security (RLS) with Public Read Policy
ALTER TABLE public.idx80_stocks ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'idx80_stocks' 
        AND policyname = 'Allow public read access on idx80_stocks'
    ) THEN
        CREATE POLICY "Allow public read access on idx80_stocks" 
        ON public.idx80_stocks FOR SELECT 
        TO anon, authenticated 
        USING (true);
    END IF;
END $$;

-- ==============================================================================
-- Seed IDX80 constituent data (80 Stocks)
-- ==============================================================================
INSERT INTO public.idx80_stocks (ticker, company_name, sector, market, is_active) VALUES
    ('ACES.JK', 'Aspirasi Hidup Indonesia Tbk.', 'Consumer Cyclicals', 'IDX80', true),
    ('ADMR.JK', 'Adaro Minerals Indonesia Tbk.', 'Energy', 'IDX80', true),
    ('ADRO.JK', 'Alamtri Resources Indonesia Tb', 'Energy', 'IDX80', true),
    ('AKRA.JK', 'AKR Corporindo Tbk.', 'Energy', 'IDX80', true),
    ('AMMN.JK', 'Amman Mineral Internasional Tb', 'Basic Materials', 'IDX80', true),
    ('AMRT.JK', 'Sumber Alfaria Trijaya Tbk.', 'Consumer Non-Cyclicals', 'IDX80', true),
    ('ANTM.JK', 'Aneka Tambang Tbk.', 'Basic Materials', 'IDX80', true),
    ('ARTO.JK', 'Bank Jago Tbk.', 'Financials', 'IDX80', true),
    ('ASII.JK', 'Astra International Tbk.', 'Industrials', 'IDX80', true),
    ('AUTO.JK', 'Astra Otoparts Tbk.', 'Consumer Cyclicals', 'IDX80', true),
    ('AVIA.JK', 'Avia Avian Tbk.', 'Basic Materials', 'IDX80', true),
    ('BBCA.JK', 'Bank Central Asia Tbk.', 'Financials', 'IDX80', true),
    ('BBNI.JK', 'Bank Negara Indonesia (Persero', 'Financials', 'IDX80', true),
    ('BBRI.JK', 'Bank Rakyat Indonesia (Persero', 'Financials', 'IDX80', true),
    ('BBTN.JK', 'Bank Tabungan Negara (Persero)', 'Financials', 'IDX80', true),
    ('BDMN.JK', 'Bank Danamon Indonesia Tbk.', 'Financials', 'IDX80', true),
    ('BFIN.JK', 'BFI Finance  Indonesia Tbk.', 'Financials', 'IDX80', true),
    ('BMRI.JK', 'Bank Mandiri (Persero) Tbk.', 'Financials', 'IDX80', true),
    ('BRIS.JK', 'Bank Syariah Indonesia Tbk.', 'Financials', 'IDX80', true),
    ('BRPT.JK', 'Barito Pacific Tbk.', 'Basic Materials', 'IDX80', true),
    ('BSDE.JK', 'Bumi Serpong Damai Tbk.', 'Properties & Real Estate', 'IDX80', true),
    ('BTPS.JK', 'Bank BTPN Syariah Tbk.', 'Financials', 'IDX80', true),
    ('BUKA.JK', 'Bukalapak.com Tbk.', 'Technology', 'IDX80', true),
    ('BUMI.JK', 'Bumi Resources Tbk.', 'Energy', 'IDX80', true),
    ('CLEO.JK', 'Sariguna Primatirta Tbk.', 'Consumer Non-Cyclicals', 'IDX80', true),
    ('CMRY.JK', 'Cisarua Mountain Dairy Tbk.', 'Consumer Non-Cyclicals', 'IDX80', true),
    ('CPIN.JK', 'Charoen Pokphand Indonesia Tbk', 'Consumer Non-Cyclicals', 'IDX80', true),
    ('CTRA.JK', 'Ciputra Development Tbk.', 'Properties & Real Estate', 'IDX80', true),
    ('EMTK.JK', 'Elang Mahkota Teknologi Tbk.', 'Technology', 'IDX80', true),
    ('ENRG.JK', 'Energi Mega Persada Tbk.', 'Energy', 'IDX80', true),
    ('ERAA.JK', 'Erajaya Swasembada Tbk.', 'Consumer Cyclicals', 'IDX80', true),
    ('ESSA.JK', 'ESSA Industries Indonesia Tbk.', 'Basic Materials', 'IDX80', true),
    ('EXCL.JK', 'XL Axiata Tbk.', 'Infrastructures', 'IDX80', true),
    ('GGRM.JK', 'Gudang Garam Tbk.', 'Consumer Non-Cyclicals', 'IDX80', true),
    ('GOTO.JK', 'GoTo Gojek Tokopedia Tbk.', 'Technology', 'IDX80', true),
    ('HEAL.JK', 'Medikaloka Hermina Tbk.', 'Healthcare', 'IDX80', true),
    ('HRUM.JK', 'Harum Energy Tbk.', 'Energy', 'IDX80', true),
    ('ICBP.JK', 'Indofood CBP Sukses Makmur Tbk', 'Consumer Non-Cyclicals', 'IDX80', true),
    ('INCO.JK', 'Vale Indonesia Tbk.', 'Basic Materials', 'IDX80', true),
    ('INDF.JK', 'Indofood Sukses Makmur Tbk.', 'Consumer Non-Cyclicals', 'IDX80', true),
    ('INDY.JK', 'Indika Energy Tbk.', 'Energy', 'IDX80', true),
    ('INKP.JK', 'Indah Kiat Pulp & Paper Tbk.', 'Basic Materials', 'IDX80', true),
    ('INTP.JK', 'Indocement Tunggal Prakarsa Tb', 'Basic Materials', 'IDX80', true),
    ('ISAT.JK', 'Indosat Tbk.', 'Infrastructures', 'IDX80', true),
    ('ITMG.JK', 'Indo Tambangraya Megah Tbk.', 'Energy', 'IDX80', true),
    ('JPFA.JK', 'Japfa Comfeed Indonesia Tbk.', 'Consumer Non-Cyclicals', 'IDX80', true),
    ('JSMR.JK', 'Jasa Marga (Persero) Tbk.', 'Infrastructures', 'IDX80', true),
    ('KLBF.JK', 'Kalbe Farma Tbk.', 'Healthcare', 'IDX80', true),
    ('MAPA.JK', 'Map Aktif Adiperkasa Tbk.', 'Consumer Cyclicals', 'IDX80', true),
    ('MAPI.JK', 'Mitra Adiperkasa Tbk.', 'Consumer Cyclicals', 'IDX80', true),
    ('MBMA.JK', 'Merdeka Battery Materials Tbk.', 'Basic Materials', 'IDX80', true),
    ('MDKA.JK', 'Merdeka Copper Gold Tbk.', 'Basic Materials', 'IDX80', true),
    ('MEDC.JK', 'Medco Energi Internasional Tbk', 'Energy', 'IDX80', true),
    ('MIKA.JK', 'Mitra Keluarga Karyasehat Tbk.', 'Healthcare', 'IDX80', true),
    ('MNCN.JK', 'Media Nusantara Citra Tbk.', 'Consumer Cyclicals', 'IDX80', true),
    ('MTEL.JK', 'Dayamitra Telekomunikasi Tbk.', 'Infrastructures', 'IDX80', true),
    ('MYOR.JK', 'Mayora Indah Tbk.', 'Consumer Non-Cyclicals', 'IDX80', true),
    ('NCKL.JK', 'Trimegah Bangun Persada Tbk.', 'Basic Materials', 'IDX80', true),
    ('PGAS.JK', 'Perusahaan Gas Negara Tbk.', 'Energy', 'IDX80', true),
    ('PGEO.JK', 'Pertamina Geothermal Energy Tb', 'Infrastructures', 'IDX80', true),
    ('PNBN.JK', 'Bank Pan Indonesia Tbk', 'Financials', 'IDX80', true),
    ('PTBA.JK', 'Bukit Asam Tbk.', 'Energy', 'IDX80', true),
    ('PTPP.JK', 'PP (Persero) Tbk.', 'Infrastructures', 'IDX80', true),
    ('PTRO.JK', 'Petrosea Tbk.', 'Energy', 'IDX80', true),
    ('PWON.JK', 'Pakuwon Jati Tbk.', 'Properties & Real Estate', 'IDX80', true),
    ('RAJA.JK', 'Rukun Raharja Tbk.', 'Energy', 'IDX80', true),
    ('SCMA.JK', 'Surya Citra Media Tbk.', 'Consumer Cyclicals', 'IDX80', true),
    ('SIDO.JK', 'Industri Jamu dan Farmasi Sido', 'Healthcare', 'IDX80', true),
    ('SMGR.JK', 'Semen Indonesia (Persero) Tbk.', 'Basic Materials', 'IDX80', true),
    ('SMRA.JK', 'Summarecon Agung Tbk.', 'Properties & Real Estate', 'IDX80', true),
    ('SRTG.JK', 'Saratoga Investama Sedaya Tbk.', 'Financials', 'IDX80', true),
    ('SSIA.JK', 'Surya Semesta Internusa Tbk.', 'Infrastructures', 'IDX80', true),
    ('TBIG.JK', 'Tower Bersama Infrastructure T', 'Infrastructures', 'IDX80', true),
    ('TINS.JK', 'Timah Tbk.', 'Basic Materials', 'IDX80', true),
    ('TKIM.JK', 'Pabrik Kertas Tjiwi Kimia Tbk.', 'Basic Materials', 'IDX80', true),
    ('TLKM.JK', 'Telkom Indonesia (Persero) Tbk', 'Infrastructures', 'IDX80', true),
    ('TOWR.JK', 'Sarana Menara Nusantara Tbk.', 'Infrastructures', 'IDX80', true),
    ('TPIA.JK', 'Chandra Asri Pacific Tbk.', 'Basic Materials', 'IDX80', true),
    ('UNTR.JK', 'United Tractors Tbk.', 'Industrials', 'IDX80', true),
    ('UNVR.JK', 'Unilever Indonesia Tbk.', 'Consumer Non-Cyclicals', 'IDX80', true)
ON CONFLICT (ticker) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    sector = EXCLUDED.sector,
    market = EXCLUDED.market,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();
