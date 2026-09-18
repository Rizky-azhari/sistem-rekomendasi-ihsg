"""
IDX80 Stock Ticker Configuration
=================================
Single source of truth for the IDX80 Index constituent tickers.
Contains all 80 constituent stocks of the IDX80 Index (Bursa Efek Indonesia).

This whitelist gates every Yahoo Finance API request in the system.
No stock outside this list will be fetched or processed.
"""

from typing import List, Dict, Optional

# ==============================================================================
# IDX80 TICKER LIST (80 Tickers in Yahoo Finance format: CODE.JK)
# ==============================================================================
IDX80_TICKERS: List[str] = [
    "ACES.JK",   # Aspirasi Hidup Indonesia Tbk.
    "ADMR.JK",   # Adaro Minerals Indonesia Tbk.
    "ADRO.JK",   # Alamtri Resources Indonesia Tb
    "AKRA.JK",   # AKR Corporindo Tbk.
    "AMMN.JK",   # Amman Mineral Internasional Tb
    "AMRT.JK",   # Sumber Alfaria Trijaya Tbk.
    "ANTM.JK",   # Aneka Tambang Tbk.
    "ARTO.JK",   # Bank Jago Tbk.
    "ASII.JK",   # Astra International Tbk.
    "AUTO.JK",   # Astra Otoparts Tbk.
    "AVIA.JK",   # Avia Avian Tbk.
    "BBCA.JK",   # Bank Central Asia Tbk.
    "BBNI.JK",   # Bank Negara Indonesia (Persero
    "BBRI.JK",   # Bank Rakyat Indonesia (Persero
    "BBTN.JK",   # Bank Tabungan Negara (Persero)
    "BDMN.JK",   # Bank Danamon Indonesia Tbk.
    "BFIN.JK",   # BFI Finance  Indonesia Tbk.
    "BMRI.JK",   # Bank Mandiri (Persero) Tbk.
    "BRIS.JK",   # Bank Syariah Indonesia Tbk.
    "BRPT.JK",   # Barito Pacific Tbk.
    "BSDE.JK",   # Bumi Serpong Damai Tbk.
    "BTPS.JK",   # Bank BTPN Syariah Tbk.
    "BUKA.JK",   # Bukalapak.com Tbk.
    "BUMI.JK",   # Bumi Resources Tbk.
    "CLEO.JK",   # Sariguna Primatirta Tbk.
    "CMRY.JK",   # Cisarua Mountain Dairy Tbk.
    "CPIN.JK",   # Charoen Pokphand Indonesia Tbk
    "CTRA.JK",   # Ciputra Development Tbk.
    "EMTK.JK",   # Elang Mahkota Teknologi Tbk.
    "ENRG.JK",   # Energi Mega Persada Tbk.
    "ERAA.JK",   # Erajaya Swasembada Tbk.
    "ESSA.JK",   # ESSA Industries Indonesia Tbk.
    "EXCL.JK",   # XL Axiata Tbk.
    "GGRM.JK",   # Gudang Garam Tbk.
    "GOTO.JK",   # GoTo Gojek Tokopedia Tbk.
    "HEAL.JK",   # Medikaloka Hermina Tbk.
    "HRUM.JK",   # Harum Energy Tbk.
    "ICBP.JK",   # Indofood CBP Sukses Makmur Tbk
    "INCO.JK",   # Vale Indonesia Tbk.
    "INDF.JK",   # Indofood Sukses Makmur Tbk.
    "INDY.JK",   # Indika Energy Tbk.
    "INKP.JK",   # Indah Kiat Pulp & Paper Tbk.
    "INTP.JK",   # Indocement Tunggal Prakarsa Tb
    "ISAT.JK",   # Indosat Tbk.
    "ITMG.JK",   # Indo Tambangraya Megah Tbk.
    "JPFA.JK",   # Japfa Comfeed Indonesia Tbk.
    "JSMR.JK",   # Jasa Marga (Persero) Tbk.
    "KLBF.JK",   # Kalbe Farma Tbk.
    "MAPA.JK",   # Map Aktif Adiperkasa Tbk.
    "MAPI.JK",   # Mitra Adiperkasa Tbk.
    "MBMA.JK",   # Merdeka Battery Materials Tbk.
    "MDKA.JK",   # Merdeka Copper Gold Tbk.
    "MEDC.JK",   # Medco Energi Internasional Tbk
    "MIKA.JK",   # Mitra Keluarga Karyasehat Tbk.
    "MNCN.JK",   # Media Nusantara Citra Tbk.
    "MTEL.JK",   # Dayamitra Telekomunikasi Tbk.
    "MYOR.JK",   # Mayora Indah Tbk.
    "NCKL.JK",   # Trimegah Bangun Persada Tbk.
    "PGAS.JK",   # Perusahaan Gas Negara Tbk.
    "PGEO.JK",   # Pertamina Geothermal Energy Tb
    "PNBN.JK",   # Bank Pan Indonesia Tbk
    "PTBA.JK",   # Bukit Asam Tbk.
    "PTPP.JK",   # PP (Persero) Tbk.
    "PTRO.JK",   # Petrosea Tbk.
    "PWON.JK",   # Pakuwon Jati Tbk.
    "RAJA.JK",   # Rukun Raharja Tbk.
    "SCMA.JK",   # Surya Citra Media Tbk.
    "SIDO.JK",   # Industri Jamu dan Farmasi Sido
    "SMGR.JK",   # Semen Indonesia (Persero) Tbk.
    "SMRA.JK",   # Summarecon Agung Tbk.
    "SRTG.JK",   # Saratoga Investama Sedaya Tbk.
    "SSIA.JK",   # Surya Semesta Internusa Tbk.
    "TBIG.JK",   # Tower Bersama Infrastructure T
    "TINS.JK",   # Timah Tbk.
    "TKIM.JK",   # Pabrik Kertas Tjiwi Kimia Tbk.
    "TLKM.JK",   # Telkom Indonesia (Persero) Tbk
    "TOWR.JK",   # Sarana Menara Nusantara Tbk.
    "TPIA.JK",   # Chandra Asri Pacific Tbk.
    "UNTR.JK",   # United Tractors Tbk.
    "UNVR.JK",   # Unilever Indonesia Tbk.
]

IDX80_EXPECTED_COUNT: int = 80

# ==============================================================================
# IDX80 METADATA DICTIONARY
# ==============================================================================
IDX80_METADATA: Dict[str, Dict[str, str]] = {
    "ACES.JK": {"company_name": "Aspirasi Hidup Indonesia Tbk.", "sector": "Consumer Cyclicals", "market": "IDX80"},
    "ADMR.JK": {"company_name": "Adaro Minerals Indonesia Tbk.", "sector": "Energy", "market": "IDX80"},
    "ADRO.JK": {"company_name": "Alamtri Resources Indonesia Tb", "sector": "Energy", "market": "IDX80"},
    "AKRA.JK": {"company_name": "AKR Corporindo Tbk.", "sector": "Energy", "market": "IDX80"},
    "AMMN.JK": {"company_name": "Amman Mineral Internasional Tb", "sector": "Basic Materials", "market": "IDX80"},
    "AMRT.JK": {"company_name": "Sumber Alfaria Trijaya Tbk.", "sector": "Consumer Non-Cyclicals", "market": "IDX80"},
    "ANTM.JK": {"company_name": "Aneka Tambang Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "ARTO.JK": {"company_name": "Bank Jago Tbk.", "sector": "Financials", "market": "IDX80"},
    "ASII.JK": {"company_name": "Astra International Tbk.", "sector": "Industrials", "market": "IDX80"},
    "AUTO.JK": {"company_name": "Astra Otoparts Tbk.", "sector": "Consumer Cyclicals", "market": "IDX80"},
    "AVIA.JK": {"company_name": "Avia Avian Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "BBCA.JK": {"company_name": "Bank Central Asia Tbk.", "sector": "Financials", "market": "IDX80"},
    "BBNI.JK": {"company_name": "Bank Negara Indonesia (Persero", "sector": "Financials", "market": "IDX80"},
    "BBRI.JK": {"company_name": "Bank Rakyat Indonesia (Persero", "sector": "Financials", "market": "IDX80"},
    "BBTN.JK": {"company_name": "Bank Tabungan Negara (Persero)", "sector": "Financials", "market": "IDX80"},
    "BDMN.JK": {"company_name": "Bank Danamon Indonesia Tbk.", "sector": "Financials", "market": "IDX80"},
    "BFIN.JK": {"company_name": "BFI Finance  Indonesia Tbk.", "sector": "Financials", "market": "IDX80"},
    "BMRI.JK": {"company_name": "Bank Mandiri (Persero) Tbk.", "sector": "Financials", "market": "IDX80"},
    "BRIS.JK": {"company_name": "Bank Syariah Indonesia Tbk.", "sector": "Financials", "market": "IDX80"},
    "BRPT.JK": {"company_name": "Barito Pacific Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "BSDE.JK": {"company_name": "Bumi Serpong Damai Tbk.", "sector": "Properties & Real Estate", "market": "IDX80"},
    "BTPS.JK": {"company_name": "Bank BTPN Syariah Tbk.", "sector": "Financials", "market": "IDX80"},
    "BUKA.JK": {"company_name": "Bukalapak.com Tbk.", "sector": "Technology", "market": "IDX80"},
    "BUMI.JK": {"company_name": "Bumi Resources Tbk.", "sector": "Energy", "market": "IDX80"},
    "CLEO.JK": {"company_name": "Sariguna Primatirta Tbk.", "sector": "Consumer Non-Cyclicals", "market": "IDX80"},
    "CMRY.JK": {"company_name": "Cisarua Mountain Dairy Tbk.", "sector": "Consumer Non-Cyclicals", "market": "IDX80"},
    "CPIN.JK": {"company_name": "Charoen Pokphand Indonesia Tbk", "sector": "Consumer Non-Cyclicals", "market": "IDX80"},
    "CTRA.JK": {"company_name": "Ciputra Development Tbk.", "sector": "Properties & Real Estate", "market": "IDX80"},
    "EMTK.JK": {"company_name": "Elang Mahkota Teknologi Tbk.", "sector": "Technology", "market": "IDX80"},
    "ENRG.JK": {"company_name": "Energi Mega Persada Tbk.", "sector": "Energy", "market": "IDX80"},
    "ERAA.JK": {"company_name": "Erajaya Swasembada Tbk.", "sector": "Consumer Cyclicals", "market": "IDX80"},
    "ESSA.JK": {"company_name": "ESSA Industries Indonesia Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "EXCL.JK": {"company_name": "XL Axiata Tbk.", "sector": "Infrastructures", "market": "IDX80"},
    "GGRM.JK": {"company_name": "Gudang Garam Tbk.", "sector": "Consumer Non-Cyclicals", "market": "IDX80"},
    "GOTO.JK": {"company_name": "GoTo Gojek Tokopedia Tbk.", "sector": "Technology", "market": "IDX80"},
    "HEAL.JK": {"company_name": "Medikaloka Hermina Tbk.", "sector": "Healthcare", "market": "IDX80"},
    "HRUM.JK": {"company_name": "Harum Energy Tbk.", "sector": "Energy", "market": "IDX80"},
    "ICBP.JK": {"company_name": "Indofood CBP Sukses Makmur Tbk", "sector": "Consumer Non-Cyclicals", "market": "IDX80"},
    "INCO.JK": {"company_name": "Vale Indonesia Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "INDF.JK": {"company_name": "Indofood Sukses Makmur Tbk.", "sector": "Consumer Non-Cyclicals", "market": "IDX80"},
    "INDY.JK": {"company_name": "Indika Energy Tbk.", "sector": "Energy", "market": "IDX80"},
    "INKP.JK": {"company_name": "Indah Kiat Pulp & Paper Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "INTP.JK": {"company_name": "Indocement Tunggal Prakarsa Tb", "sector": "Basic Materials", "market": "IDX80"},
    "ISAT.JK": {"company_name": "Indosat Tbk.", "sector": "Infrastructures", "market": "IDX80"},
    "ITMG.JK": {"company_name": "Indo Tambangraya Megah Tbk.", "sector": "Energy", "market": "IDX80"},
    "JPFA.JK": {"company_name": "Japfa Comfeed Indonesia Tbk.", "sector": "Consumer Non-Cyclicals", "market": "IDX80"},
    "JSMR.JK": {"company_name": "Jasa Marga (Persero) Tbk.", "sector": "Infrastructures", "market": "IDX80"},
    "KLBF.JK": {"company_name": "Kalbe Farma Tbk.", "sector": "Healthcare", "market": "IDX80"},
    "MAPA.JK": {"company_name": "Map Aktif Adiperkasa Tbk.", "sector": "Consumer Cyclicals", "market": "IDX80"},
    "MAPI.JK": {"company_name": "Mitra Adiperkasa Tbk.", "sector": "Consumer Cyclicals", "market": "IDX80"},
    "MBMA.JK": {"company_name": "Merdeka Battery Materials Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "MDKA.JK": {"company_name": "Merdeka Copper Gold Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "MEDC.JK": {"company_name": "Medco Energi Internasional Tbk", "sector": "Energy", "market": "IDX80"},
    "MIKA.JK": {"company_name": "Mitra Keluarga Karyasehat Tbk.", "sector": "Healthcare", "market": "IDX80"},
    "MNCN.JK": {"company_name": "Media Nusantara Citra Tbk.", "sector": "Consumer Cyclicals", "market": "IDX80"},
    "MTEL.JK": {"company_name": "Dayamitra Telekomunikasi Tbk.", "sector": "Infrastructures", "market": "IDX80"},
    "MYOR.JK": {"company_name": "Mayora Indah Tbk.", "sector": "Consumer Non-Cyclicals", "market": "IDX80"},
    "NCKL.JK": {"company_name": "Trimegah Bangun Persada Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "PGAS.JK": {"company_name": "Perusahaan Gas Negara Tbk.", "sector": "Energy", "market": "IDX80"},
    "PGEO.JK": {"company_name": "Pertamina Geothermal Energy Tb", "sector": "Infrastructures", "market": "IDX80"},
    "PNBN.JK": {"company_name": "Bank Pan Indonesia Tbk", "sector": "Financials", "market": "IDX80"},
    "PTBA.JK": {"company_name": "Bukit Asam Tbk.", "sector": "Energy", "market": "IDX80"},
    "PTPP.JK": {"company_name": "PP (Persero) Tbk.", "sector": "Infrastructures", "market": "IDX80"},
    "PTRO.JK": {"company_name": "Petrosea Tbk.", "sector": "Energy", "market": "IDX80"},
    "PWON.JK": {"company_name": "Pakuwon Jati Tbk.", "sector": "Properties & Real Estate", "market": "IDX80"},
    "RAJA.JK": {"company_name": "Rukun Raharja Tbk.", "sector": "Energy", "market": "IDX80"},
    "SCMA.JK": {"company_name": "Surya Citra Media Tbk.", "sector": "Consumer Cyclicals", "market": "IDX80"},
    "SIDO.JK": {"company_name": "Industri Jamu dan Farmasi Sido", "sector": "Healthcare", "market": "IDX80"},
    "SMGR.JK": {"company_name": "Semen Indonesia (Persero) Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "SMRA.JK": {"company_name": "Summarecon Agung Tbk.", "sector": "Properties & Real Estate", "market": "IDX80"},
    "SRTG.JK": {"company_name": "Saratoga Investama Sedaya Tbk.", "sector": "Financials", "market": "IDX80"},
    "SSIA.JK": {"company_name": "Surya Semesta Internusa Tbk.", "sector": "Infrastructures", "market": "IDX80"},
    "TBIG.JK": {"company_name": "Tower Bersama Infrastructure T", "sector": "Infrastructures", "market": "IDX80"},
    "TINS.JK": {"company_name": "Timah Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "TKIM.JK": {"company_name": "Pabrik Kertas Tjiwi Kimia Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "TLKM.JK": {"company_name": "Telkom Indonesia (Persero) Tbk", "sector": "Infrastructures", "market": "IDX80"},
    "TOWR.JK": {"company_name": "Sarana Menara Nusantara Tbk.", "sector": "Infrastructures", "market": "IDX80"},
    "TPIA.JK": {"company_name": "Chandra Asri Pacific Tbk.", "sector": "Basic Materials", "market": "IDX80"},
    "UNTR.JK": {"company_name": "United Tractors Tbk.", "sector": "Industrials", "market": "IDX80"},
    "UNVR.JK": {"company_name": "Unilever Indonesia Tbk.", "sector": "Consumer Non-Cyclicals", "market": "IDX80"},
}

_IDX80_SET = frozenset(IDX80_TICKERS)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def normalize_ticker(symbol: str) -> str:
    """Normalize user input to standard Yahoo Finance IDX format (e.g. BBCA -> BBCA.JK)."""
    sym = symbol.strip().upper()
    if not sym.endswith(".JK") and "." not in sym:
        sym += ".JK"
    return sym

def is_idx80(symbol: str) -> bool:
    """Returns True if the given symbol is in the IDX80 whitelist."""
    return normalize_ticker(symbol) in _IDX80_SET

def get_all_idx80_tickers() -> List[str]:
    """Returns the full list of 80 IDX80 tickers."""
    return list(IDX80_TICKERS)

def get_idx80_metadata(symbol: str) -> Optional[Dict[str, str]]:
    """Returns metadata dict for an IDX80 ticker, or None if not found."""
    return IDX80_METADATA.get(normalize_ticker(symbol))

def get_idx80_stocks_for_db() -> List[Dict[str, str]]:
    """Returns a list of dicts suitable for database seeding."""
    results = []
    for ticker in IDX80_TICKERS:
        meta = IDX80_METADATA.get(ticker, {})
        results.append({
            "ticker": ticker,
            "symbol": ticker,
            "code": ticker.replace(".JK", ""),
            "company_name": meta.get("company_name", ticker.replace(".JK", "")),
            "sector": meta.get("sector", "IDX Equities"),
            "market": "IDX80",
            "is_active": True,
        })
    return results
