/**
 * IDX80 Constituents Universe
 * Single source of truth for the 80 stocks in the IDX80 Index (Bursa Efek Indonesia).
 */

export const IDX80_SYMBOLS = [
  'ACES', 'ADMR', 'ADRO', 'AKRA', 'AMMN', 'AMRT', 'ANTM', 'ARTO',
  'ASII', 'AUTO', 'AVIA', 'BBCA', 'BBNI', 'BBRI', 'BBTN', 'BDMN',
  'BFIN', 'BMRI', 'BRIS', 'BRPT', 'BSDE', 'BTPS', 'BUKA', 'BUMI',
  'CLEO', 'CMRY', 'CPIN', 'CTRA', 'EMTK', 'ENRG', 'ERAA', 'ESSA',
  'EXCL', 'GGRM', 'GOTO', 'HEAL', 'HRUM', 'ICBP', 'INCO', 'INDF',
  'INDY', 'INKP', 'INTP', 'ISAT', 'ITMG', 'JPFA', 'JSMR', 'KLBF',
  'MAPA', 'MAPI', 'MBMA', 'MDKA', 'MEDC', 'MIKA', 'MNCN', 'MTEL',
  'MYOR', 'NCKL', 'PGAS', 'PGEO', 'PNBN', 'PTBA', 'PTPP', 'PTRO',
  'PWON', 'RAJA', 'SCMA', 'SIDO', 'SMGR', 'SMRA', 'SRTG', 'SSIA',
  'TBIG', 'TINS', 'TKIM', 'TLKM', 'TOWR', 'TPIA', 'UNTR', 'UNVR'
] as const;

export const IDX80_SYMBOLS_SET = new Set<string>(IDX80_SYMBOLS);

/**
 * Check whether a symbol or ticker (e.g., 'BBCA' or 'BBCA.JK') belongs to the IDX80 Index.
 */
export function isIDX80Stock(symbol: string): boolean {
  if (!symbol) return false;
  const clean = symbol.replace('.JK', '').trim().toUpperCase();
  return IDX80_SYMBOLS_SET.has(clean);
}

/**
 * Complete catalog of all 80 IDX80 stocks with company names and sectors.
 */
export const IDX80_DEFAULT_CATALOG: Array<{ symbol: string; name: string; sector: string }> = [
  { symbol: 'ACES.JK', name: 'Aspirasi Hidup Indonesia Tbk', sector: 'Consumer Cyclicals' },
  { symbol: 'ADMR.JK', name: 'Adaro Minerals Indonesia Tbk', sector: 'Energy' },
  { symbol: 'ADRO.JK', name: 'Alamtri Resources Indonesia Tbk', sector: 'Energy' },
  { symbol: 'AKRA.JK', name: 'AKR Corporindo Tbk', sector: 'Energy' },
  { symbol: 'AMMN.JK', name: 'Amman Mineral Internasional Tbk', sector: 'Basic Materials' },
  { symbol: 'AMRT.JK', name: 'Sumber Alfaria Trijaya Tbk', sector: 'Consumer Non-Cyclicals' },
  { symbol: 'ANTM.JK', name: 'Aneka Tambang Tbk', sector: 'Basic Materials' },
  { symbol: 'ARTO.JK', name: 'Bank Jago Tbk', sector: 'Financials' },
  { symbol: 'ASII.JK', name: 'Astra International Tbk', sector: 'Industrials' },
  { symbol: 'AUTO.JK', name: 'Astra Otoparts Tbk', sector: 'Consumer Cyclicals' },
  { symbol: 'AVIA.JK', name: 'Avia Avian Tbk', sector: 'Basic Materials' },
  { symbol: 'BBCA.JK', name: 'Bank Central Asia Tbk', sector: 'Financials' },
  { symbol: 'BBNI.JK', name: 'Bank Negara Indonesia Tbk', sector: 'Financials' },
  { symbol: 'BBRI.JK', name: 'Bank Rakyat Indonesia Tbk', sector: 'Financials' },
  { symbol: 'BBTN.JK', name: 'Bank Tabungan Negara Tbk', sector: 'Financials' },
  { symbol: 'BDMN.JK', name: 'Bank Danamon Indonesia Tbk', sector: 'Financials' },
  { symbol: 'BFIN.JK', name: 'BFI Finance Indonesia Tbk', sector: 'Financials' },
  { symbol: 'BMRI.JK', name: 'Bank Mandiri Tbk', sector: 'Financials' },
  { symbol: 'BRIS.JK', name: 'Bank Syariah Indonesia Tbk', sector: 'Financials' },
  { symbol: 'BRPT.JK', name: 'Barito Pacific Tbk', sector: 'Basic Materials' },
  { symbol: 'BSDE.JK', name: 'Bumi Serpong Damai Tbk', sector: 'Properties & Real Estate' },
  { symbol: 'BTPS.JK', name: 'Bank BTPN Syariah Tbk', sector: 'Financials' },
  { symbol: 'BUKA.JK', name: 'Bukalapak.com Tbk', sector: 'Technology' },
  { symbol: 'BUMI.JK', name: 'Bumi Resources Tbk', sector: 'Energy' },
  { symbol: 'CLEO.JK', name: 'Sariguna Primatirta Tbk', sector: 'Consumer Non-Cyclicals' },
  { symbol: 'CMRY.JK', name: 'Cisarua Mountain Dairy Tbk', sector: 'Consumer Non-Cyclicals' },
  { symbol: 'CPIN.JK', name: 'Charoen Pokphand Indonesia Tbk', sector: 'Consumer Non-Cyclicals' },
  { symbol: 'CTRA.JK', name: 'Ciputra Development Tbk', sector: 'Properties & Real Estate' },
  { symbol: 'EMTK.JK', name: 'Elang Mahkota Teknologi Tbk', sector: 'Technology' },
  { symbol: 'ENRG.JK', name: 'Energi Mega Persada Tbk', sector: 'Energy' },
  { symbol: 'ERAA.JK', name: 'Erajaya Swasembada Tbk', sector: 'Consumer Cyclicals' },
  { symbol: 'ESSA.JK', name: 'ESSA Industries Indonesia Tbk', sector: 'Basic Materials' },
  { symbol: 'EXCL.JK', name: 'XL Axiata Tbk', sector: 'Infrastructures' },
  { symbol: 'GGRM.JK', name: 'Gudang Garam Tbk', sector: 'Consumer Non-Cyclicals' },
  { symbol: 'GOTO.JK', name: 'GoTo Gojek Tokopedia Tbk', sector: 'Technology' },
  { symbol: 'HEAL.JK', name: 'Medikaloka Hermina Tbk', sector: 'Healthcare' },
  { symbol: 'HRUM.JK', name: 'Harum Energy Tbk', sector: 'Energy' },
  { symbol: 'ICBP.JK', name: 'Indofood CBP Sukses Makmur Tbk', sector: 'Consumer Non-Cyclicals' },
  { symbol: 'INCO.JK', name: 'Vale Indonesia Tbk', sector: 'Basic Materials' },
  { symbol: 'INDF.JK', name: 'Indofood Sukses Makmur Tbk', sector: 'Consumer Non-Cyclicals' },
  { symbol: 'INDY.JK', name: 'Indika Energy Tbk', sector: 'Energy' },
  { symbol: 'INKP.JK', name: 'Indah Kiat Pulp & Paper Tbk', sector: 'Basic Materials' },
  { symbol: 'INTP.JK', name: 'Indocement Tunggal Prakarsa Tbk', sector: 'Basic Materials' },
  { symbol: 'ISAT.JK', name: 'Indosat Tbk', sector: 'Infrastructures' },
  { symbol: 'ITMG.JK', name: 'Indo Tambangraya Megah Tbk', sector: 'Energy' },
  { symbol: 'JPFA.JK', name: 'Japfa Comfeed Indonesia Tbk', sector: 'Consumer Non-Cyclicals' },
  { symbol: 'JSMR.JK', name: 'Jasa Marga Tbk', sector: 'Infrastructures' },
  { symbol: 'KLBF.JK', name: 'Kalbe Farma Tbk', sector: 'Healthcare' },
  { symbol: 'MAPA.JK', name: 'Map Aktif Adiperkasa Tbk', sector: 'Consumer Cyclicals' },
  { symbol: 'MAPI.JK', name: 'Mitra Adiperkasa Tbk', sector: 'Consumer Cyclicals' },
  { symbol: 'MBMA.JK', name: 'Merdeka Battery Materials Tbk', sector: 'Basic Materials' },
  { symbol: 'MDKA.JK', name: 'Merdeka Copper Gold Tbk', sector: 'Basic Materials' },
  { symbol: 'MEDC.JK', name: 'Medco Energi Internasional Tbk', sector: 'Energy' },
  { symbol: 'MIKA.JK', name: 'Mitra Keluarga Karyasehat Tbk', sector: 'Healthcare' },
  { symbol: 'MNCN.JK', name: 'Media Nusantara Citra Tbk', sector: 'Consumer Cyclicals' },
  { symbol: 'MTEL.JK', name: 'Dayamitra Telekomunikasi Tbk', sector: 'Infrastructures' },
  { symbol: 'MYOR.JK', name: 'Mayora Indah Tbk', sector: 'Consumer Non-Cyclicals' },
  { symbol: 'NCKL.JK', name: 'Trimegah Bangun Persada Tbk', sector: 'Basic Materials' },
  { symbol: 'PGAS.JK', name: 'Perusahaan Gas Negara Tbk', sector: 'Energy' },
  { symbol: 'PGEO.JK', name: 'Pertamina Geothermal Energy Tbk', sector: 'Infrastructures' },
  { symbol: 'PNBN.JK', name: 'Bank Pan Indonesia Tbk', sector: 'Financials' },
  { symbol: 'PTBA.JK', name: 'Bukit Asam Tbk', sector: 'Energy' },
  { symbol: 'PTPP.JK', name: 'PP (Persero) Tbk', sector: 'Infrastructures' },
  { symbol: 'PTRO.JK', name: 'Petrosea Tbk', sector: 'Energy' },
  { symbol: 'PWON.JK', name: 'Pakuwon Jati Tbk', sector: 'Properties & Real Estate' },
  { symbol: 'RAJA.JK', name: 'Rukun Raharja Tbk', sector: 'Energy' },
  { symbol: 'SCMA.JK', name: 'Surya Citra Media Tbk', sector: 'Consumer Cyclicals' },
  { symbol: 'SIDO.JK', name: 'Industri Jamu dan Farmasi Sido Muncul Tbk', sector: 'Healthcare' },
  { symbol: 'SMGR.JK', name: 'Semen Indonesia Tbk', sector: 'Basic Materials' },
  { symbol: 'SMRA.JK', name: 'Summarecon Agung Tbk', sector: 'Properties & Real Estate' },
  { symbol: 'SRTG.JK', name: 'Saratoga Investama Sedaya Tbk', sector: 'Financials' },
  { symbol: 'SSIA.JK', name: 'Surya Semesta Internusa Tbk', sector: 'Infrastructures' },
  { symbol: 'TBIG.JK', name: 'Tower Bersama Infrastructure Tbk', sector: 'Infrastructures' },
  { symbol: 'TINS.JK', name: 'Timah Tbk', sector: 'Basic Materials' },
  { symbol: 'TKIM.JK', name: 'Pabrik Kertas Tjiwi Kimia Tbk', sector: 'Basic Materials' },
  { symbol: 'TLKM.JK', name: 'Telkom Indonesia Tbk', sector: 'Infrastructures' },
  { symbol: 'TOWR.JK', name: 'Sarana Menara Nusantara Tbk', sector: 'Infrastructures' },
  { symbol: 'TPIA.JK', name: 'Chandra Asri Pacific Tbk', sector: 'Basic Materials' },
  { symbol: 'UNTR.JK', name: 'United Tractors Tbk', sector: 'Industrials' },
  { symbol: 'UNVR.JK', name: 'Unilever Indonesia Tbk', sector: 'Consumer Non-Cyclicals' }
];

/**
 * Intelligent IDX80 stock search with relevance ranking.
 * Prioritizes ticker symbol matches before company name matches, and ignores generic corporate stopwords.
 */
export function searchIDX80Stocks(
  stocks: Array<{ symbol: string; name: string }>,
  query: string
): Array<{ symbol: string; name: string }> {
  const q = query.trim().toLowerCase();
  if (!q) return [];

  // Stopwords to avoid false-positive matches on common Indonesian corporate terms
  const STOPWORDS = new Set(['indonesia', 'tbk', 'persero', 'pt', 'dan']);

  type ScoredStock = {
    stock: { symbol: string; name: string };
    score: number;
  };

  const matches: ScoredStock[] = [];

  for (const s of stocks) {
    const rawSymbol = s.symbol.toUpperCase();
    const cleanSymbol = rawSymbol.replace('.JK', '').toLowerCase();
    const nameLower = (s.name || '').toLowerCase();

    // 1. Exact match on ticker code
    if (cleanSymbol === q) {
      matches.push({ stock: s, score: 100 });
      continue;
    }

    // 2. Ticker code starts with query (e.g., 's' -> SCMA, SIDO, SMGR, SMRA, SRTG, SSIA)
    if (cleanSymbol.startsWith(q)) {
      matches.push({ stock: s, score: 80 - cleanSymbol.length });
      continue;
    }

    // 3. Ticker code contains query (e.g., 's' -> ASII, BSDE, ISAT, JSMR)
    if (cleanSymbol.includes(q)) {
      matches.push({ stock: s, score: 50 });
      continue;
    }

    // 4. Company words start with query (e.g., 's' -> Semen Indonesia, Surya Citra)
    const words = nameLower.split(/[\s,()\-]+/).filter(w => w.length > 0 && !STOPWORDS.has(w));
    const wordStartsWith = words.some(w => w.startsWith(q));
    if (wordStartsWith) {
      matches.push({ stock: s, score: 30 });
      continue;
    }

    // 5. Company name includes query (only for queries with length >= 3 to avoid noise)
    if (q.length >= 3 && nameLower.includes(q)) {
      matches.push({ stock: s, score: 10 });
      continue;
    }
  }

  // Sort descending by score, then alphabetically by ticker
  matches.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    return a.stock.symbol.localeCompare(b.stock.symbol);
  });

  return matches.map(m => m.stock);
}
