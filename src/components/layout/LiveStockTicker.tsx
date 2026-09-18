import React, { useMemo } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Flame
} from 'lucide-react';
import type { IHSGMarketData, ScreenerRuleItem } from '../../types/stock';

interface LiveStockTickerProps {
  ihsg?: IHSGMarketData | null;
  stocks: ScreenerRuleItem[];
  onSelectStock: (symbol: string) => void;
}

// Fallback IDX stock items if live scanner list is still loading
const DEFAULT_TICKER_DATA: Array<{
  symbol: string;
  price: number;
  change: number;
  change_percentage: number;
  bandar_status?: string;
}> = [
  { symbol: 'BBCA', price: 10150, change: 125, change_percentage: 1.25, bandar_status: 'AKUMULASI MASIF' },
  { symbol: 'BBRI', price: 5450, change: -50, change_percentage: -0.91 },
  { symbol: 'BMRI', price: 7100, change: 100, change_percentage: 1.43, bandar_status: 'AKUMULASI NORMAL' },
  { symbol: 'BBNI', price: 5800, change: 75, change_percentage: 1.31 },
  { symbol: 'TLKM', price: 3820, change: -30, change_percentage: -0.78 },
  { symbol: 'ASII', price: 5225, change: 50, change_percentage: 0.97 },
  { symbol: 'BUMI', price: 193, change: -9, change_percentage: -4.46 },
  { symbol: 'SRSN', price: 129, change: 13, change_percentage: 11.21, bandar_status: 'AKUMULASI MASIF' },
  { symbol: 'SINI', price: 16900, change: 100, change_percentage: 0.60, bandar_status: 'AKUMULASI NORMAL' },
  { symbol: 'CUAN', price: 925, change: -20, change_percentage: -2.12 },
  { symbol: 'AMMN', price: 4680, change: -220, change_percentage: -4.49 },
  { symbol: 'GOTO', price: 78, change: 2, change_percentage: 2.63, bandar_status: 'AKUMULASI NORMAL' },
  { symbol: 'ADRO', price: 2850, change: 60, change_percentage: 2.15, bandar_status: 'AKUMULASI MASIF' },
  { symbol: 'MDKA', price: 2430, change: -40, change_percentage: -1.62 },
  { symbol: 'BRIS', price: 2620, change: 80, change_percentage: 3.15, bandar_status: 'AKUMULASI MASIF' }
];

export const LiveStockTicker: React.FC<LiveStockTickerProps> = ({
  ihsg,
  stocks,
  onSelectStock
}) => {
  // Format items from scanned stocks or fallback list
  const tickerItems = useMemo(() => {
    if (stocks && stocks.length > 0) {
      return stocks.map(s => {
        const cleanSymbol = s.symbol.replace('.JK', '');
        const price = s.price || 0;
        const changePct = s.change_percentage || 0;
        // approximate change amount from %
        const changeAmt = Math.round(price * (changePct / 100));

        // Detect bandar accumulation status
        let isAccum = false;
        let bandarLabel: string | undefined = undefined;
        if (s.bandar_status) {
          bandarLabel = s.bandar_status;
          isAccum = s.bandar_status.includes('AKUMULASI');
        } else if ((s.momentum_score && s.momentum_score >= 70) || (s.volume && s.volume > 50000000 && changePct > 0.5)) {
          isAccum = true;
          bandarLabel = changePct >= 2.0 ? 'AKUMULASI MASIF' : 'AKUMULASI NORMAL';
        }

        return {
          symbol: cleanSymbol,
          rawSymbol: s.symbol,
          price,
          change: changeAmt,
          change_percentage: changePct,
          isAccum,
          bandarLabel
        };
      });
    }

    return DEFAULT_TICKER_DATA.map(d => ({
      symbol: d.symbol,
      rawSymbol: `${d.symbol}.JK`,
      price: d.price,
      change: d.change,
      change_percentage: d.change_percentage,
      isAccum: !!d.bandar_status,
      bandarLabel: d.bandar_status
    }));
  }, [stocks]);

  // Duplicate the array to make the infinite continuous CSS ticker seamless
  const duplicatedItems = useMemo(() => [...tickerItems, ...tickerItems], [tickerItems]);

  const ihsgPositive = (ihsg?.change || 0) >= 0;
  const ihsgPrice = ihsg ? ihsg.price.toLocaleString('id-ID', { minimumFractionDigits: 2 }) : '6,441.16';
  const ihsgChange = ihsg?.change ? Math.abs(ihsg.change).toFixed(2) : '21.27';
  const ihsgChangePct = ihsg?.change_percentage ? Math.abs(ihsg.change_percentage).toFixed(2) : '0.33';

  return (
    <aside
      aria-label="Live Saham Running Ticker"
      className="fixed bottom-14 md:bottom-0 left-0 right-0 z-40 bg-[#070D1B]/95 border-t border-slate-800/90 backdrop-blur-xl h-8 sm:h-9 flex items-center overflow-hidden shadow-2xl shadow-black select-none"
    >
      {/* ===================================================================== */}
      {/* 1. LEFT PINNED SECTION: LIVE IHSG BADGE */}
      {/* ===================================================================== */}
      <div className="shrink-0 flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3.5 h-full bg-[#0B132B]/95 border-r border-slate-800/90 z-20 shadow-md">
        {/* Blinking Live Indicator */}
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
        <span className="text-[9px] sm:text-[10px] font-mono font-black tracking-wider text-emerald-400 uppercase hidden xs:inline">
          LIVE
        </span>

        {/* IHSG Mini Chip */}
        <div
          title="Indeks Harga Saham Gabungan (^JKSE)"
          className="flex items-center gap-1 sm:gap-1.5 px-1.5 py-0.5 rounded bg-slate-900/90 border border-slate-800 text-[10px] sm:text-[11px] font-mono"
        >
          <span className="font-extrabold text-slate-300">IHSG</span>
          <span className="font-bold text-white hidden sm:inline">{ihsgPrice}</span>
          <span
            className={`flex items-center gap-0.5 font-bold ${
              ihsgPositive ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {ihsgPositive ? (
              <TrendingUp className="w-2.5 h-2.5 inline" />
            ) : (
              <TrendingDown className="w-2.5 h-2.5 inline" />
            )}
            <span>
              {ihsgPositive ? '+' : '-'}
              {ihsgChange} ({ihsgPositive ? '+' : '-'}
              {ihsgChangePct}%)
            </span>
          </span>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* 2. MIDDLE SECTION: CONTINUOUS INFINITE RUNNING TICKER TAPE */}
      {/* ===================================================================== */}
      <div className="flex-1 overflow-hidden relative h-full flex items-center">
        {/* Subtle gradient edges for smooth tape fading */}
        <div className="pointer-events-none absolute left-0 top-0 bottom-0 w-4 bg-gradient-to-r from-[#070D1B] to-transparent z-10" />
        <div className="pointer-events-none absolute right-0 top-0 bottom-0 w-4 bg-gradient-to-l from-[#070D1B] to-transparent z-10" />

        {/* Continuous Running Marquee */}
        <div className="animate-ticker flex items-center gap-4 sm:gap-6 whitespace-nowrap pl-4">
          {duplicatedItems.map((item, index) => {
            const isUp = item.change_percentage >= 0;
            return (
              <div
                key={`${item.rawSymbol}-${index}`}
                onClick={() => onSelectStock(item.rawSymbol)}
                title={`${item.symbol}: Rp ${item.price.toLocaleString('id-ID')} (${isUp ? '+' : ''}${item.change_percentage.toFixed(2)}%) — Klik untuk buka detail`}
                className="inline-flex items-center gap-1.5 text-[11px] sm:text-xs font-mono cursor-pointer hover:bg-slate-800/80 px-2 py-0.5 rounded transition-colors group shrink-0"
              >
                {/* Stock Symbol */}
                <span className="font-bold text-slate-100 group-hover:text-[#22C7F0] transition-colors">
                  {item.symbol}
                </span>

                {/* Price */}
                <span className="text-slate-300 font-semibold">
                  {item.price.toLocaleString('id-ID')}
                </span>

                {/* Change Arrow & Percentage */}
                <span
                  className={`inline-flex items-center gap-0.5 font-bold text-[10px] sm:text-[11px] ${
                    isUp ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {isUp ? (
                    <TrendingUp className="w-2.5 h-2.5 shrink-0" />
                  ) : (
                    <TrendingDown className="w-2.5 h-2.5 shrink-0" />
                  )}
                  <span>
                    {isUp ? '+' : ''}
                    {item.change_percentage.toFixed(2)}%
                  </span>
                </span>

                {/* Bandar Accumulation Badge Highlight */}
                {item.isAccum && (
                  <span
                    className="inline-flex items-center gap-0.5 px-1 py-0.2 rounded text-[9px] font-black uppercase tracking-tight bg-gradient-to-r from-purple-500/25 to-pink-500/25 text-purple-300 border border-purple-500/40 shadow-sm shadow-purple-500/20"
                    title="Saham terdeteksi sedang diakumulasi oleh Bandar / Institusi"
                  >
                    <Flame className="w-2 h-2 text-purple-400 fill-purple-400" />
                    <span className="hidden xs:inline">AKUMULASI</span>
                  </span>
                )}

                {/* Subtle Divider */}
                <span className="text-slate-700 ml-1 select-none">|</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ===================================================================== */}
      {/* 3. RIGHT PINNED SECTION: MARKET STATUS & CLOCK */}
      {/* ===================================================================== */}
      <div className="hidden lg:flex shrink-0 items-center gap-2 px-3 h-full bg-[#0B132B]/95 border-l border-slate-800/90 text-[10px] font-mono text-slate-400 z-20">
        <div className="flex items-center gap-1.5">
          <Activity className="w-3 h-3 text-[#22C7F0]" />
          <span className="text-slate-300 font-semibold">IDX COMPOSITE</span>
        </div>
        <span className="w-1 h-1 rounded-full bg-slate-700" />
        <span className="text-slate-400">PASAR REGULER</span>
      </div>
    </aside>
  );
};
