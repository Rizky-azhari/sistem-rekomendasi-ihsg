import React from 'react';
import type { IHSGMarketData, ScreenerRuleItem, UniverseStats, ScanningProgress } from '../types/stock';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Layers,
  ArrowRight,
  RefreshCw,
  Sparkles,
  BarChart3,
  Target
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

interface DashboardPageProps {
  ihsg: IHSGMarketData | null;
  stocks: ScreenerRuleItem[];
  universeStats?: UniverseStats | null;
  scanningProgress?: ScanningProgress | null;
  onStartScan?: () => void;
  onSyncUniverse?: () => void;
  isScanning?: boolean;
  isLoading: boolean;
  onSelectStock: (symbol: string) => void;
  onNavigateToScanner: () => void;
  onRefresh: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  ihsg,
  stocks,
  universeStats,
  scanningProgress,
  onStartScan,
  onSyncUniverse,
  isScanning,
  isLoading,
  onSelectStock,
  onNavigateToScanner,
  onRefresh
}) => {
  // 1. Calculations
  const strongBuyStocks = stocks.filter(
    s => s.recommendation === 'STRONG BUY' || (s.final_score || s.composite_score || 0) >= 85
  );
  const buyStocks = stocks.filter(
    s => s.recommendation === 'BUY' || ((s.final_score || s.composite_score || 0) >= 70 && (s.final_score || s.composite_score || 0) < 85)
  );
  const holdStocks = stocks.filter(
    s => s.recommendation === 'HOLD' || ((s.final_score || s.composite_score || 0) >= 50 && (s.final_score || s.composite_score || 0) < 70)
  );
  const sellStocks = stocks.filter(
    s => s.recommendation === 'SELL' || (s.final_score || s.composite_score || 0) < 50
  );

  const bullishStocks = [...strongBuyStocks, ...buyStocks];
  const bearishStocks = sellStocks;

  const totalAnalyzed = stocks.length;
  const bullishPercent = totalAnalyzed > 0 ? Math.round((bullishStocks.length / totalAnalyzed) * 100) : 0;
  const bearishPercent = totalAnalyzed > 0 ? Math.round((bearishStocks.length / totalAnalyzed) * 100) : 0;

  // Market Sentiment Derivation
  const isIHSGPositive = (ihsg?.change || 0) >= 0;
  const marketSentiment = isIHSGPositive && bullishPercent >= 20 ? 'BULLISH' : !isIHSGPositive && bearishPercent >= 50 ? 'BEARISH' : 'NEUTRAL';

  // Recommendation Distribution Chart Data
  const distributionData = [
    { name: 'Strong Buy', count: strongBuyStocks.length, color: '#10B981' },
    { name: 'Buy', count: buyStocks.length, color: '#22C7F0' },
    { name: 'Hold', count: holdStocks.length, color: '#F59E0B' },
    { name: 'Sell', count: sellStocks.length, color: '#EF4444' }
  ];

  // Sparkline data
  const sparklineData = (ihsg?.sparkline || []).map((val, idx) => ({
    idx,
    price: val
  }));

  // Top Recommendations (sorted by score descending)
  const topStocks = [...stocks]
    .sort((a, b) => (b.final_score || b.composite_score || 0) - (a.final_score || a.composite_score || 0))
    .slice(0, 10);

  const formatIDR = (num: number) => `Rp ${Math.round(num).toLocaleString('id-ID')}`;

  const lastUpdated = universeStats?.last_update
    ? new Date(universeStats.last_update).toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' })
    : new Date().toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' });

  return (
    <div className="flex flex-col gap-5 max-w-7xl mx-auto w-full px-3 sm:px-6 py-4 sm:py-6">
      
      {/* ========================================================================= */}
      {/* SECTION 1: MARKET HEADER (Compact) */}
      {/* ========================================================================= */}
      <div className="p-3.5 sm:p-4 rounded-2xl bg-[#111827]/90 border border-slate-800/90 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-3 backdrop-blur-xl">
        <div className="flex flex-wrap items-center gap-3 sm:gap-5">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400 font-bold uppercase tracking-wider">IHSG (IDX COMPOSITE)</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">
                ^JKSE
              </span>
            </div>
            <div className="flex items-baseline gap-2.5 mt-0.5">
              <span className="text-xl sm:text-2xl font-black font-mono text-white tracking-tight">
                {ihsg ? ihsg.price.toLocaleString('id-ID', { minimumFractionDigits: 2 }) : '6,436.85'}
              </span>
              <span
                className={`text-xs font-mono font-bold px-2 py-0.5 rounded-lg ${
                  isIHSGPositive ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'
                }`}
              >
                {isIHSGPositive ? '+' : ''}{ihsg?.change?.toFixed(2) || '-24.30'} ({isIHSGPositive ? '+' : ''}{ihsg?.change_percentage?.toFixed(2) || '-0.38'}%)
              </span>
            </div>
          </div>

          <div className="hidden sm:block h-8 w-[1px] bg-slate-800" />

          {/* Market Sentiment Badge */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-medium">Sentimen:</span>
            <span
              className={`text-xs font-bold font-mono px-2.5 py-1 rounded-xl flex items-center gap-1.5 ${
                marketSentiment === 'BULLISH'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  : marketSentiment === 'BEARISH'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                  : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${
                marketSentiment === 'BULLISH' ? 'bg-emerald-400 animate-pulse' : marketSentiment === 'BEARISH' ? 'bg-rose-400 animate-pulse' : 'bg-amber-400'
              }`} />
              {marketSentiment}
            </span>
          </div>

          <div className="hidden lg:flex items-center gap-1.5 text-xs text-slate-400 font-mono">
            <span className="text-slate-500">Update:</span>
            <span>{lastUpdated}</span>
          </div>
        </div>

        {/* Header Action Button */}
        <div className="flex items-center gap-2 self-end md:self-center">
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition-all cursor-pointer font-medium disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-[#22C7F0]' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* SECTION 2: SUMMARY CARDS (Desktop: 4 Col, Tablet: 2 Col, Mobile: 1 Col) */}
      {/* Compact Height */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        
        {/* CARD 1: IHSG Index */}
        <div className="p-4 rounded-2xl bg-[#111827]/85 border border-slate-800/90 flex flex-col justify-between hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5">
            <span className="font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-[#22C7F0]" />
              IHSG INDEX
            </span>
            <span className="text-[10px] font-mono text-slate-500">^JKSE</span>
          </div>

          <div className="my-1">
            <div className="text-2xl font-black font-mono text-white tracking-tight">
              {ihsg ? ihsg.price.toLocaleString('id-ID', { minimumFractionDigits: 2 }) : '6,436.85'}
            </div>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={`text-[11px] font-mono font-bold ${isIHSGPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                {isIHSGPositive ? '+' : ''}{ihsg?.change?.toFixed(2) || '-24.30'} ({isIHSGPositive ? '+' : ''}{ihsg?.change_percentage?.toFixed(2) || '-0.38'}%)
              </span>
            </div>
          </div>

          {/* Mini Sparkline */}
          <div className="w-full h-8 -mb-1 mt-1">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sparklineData}>
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke={isIHSGPositive ? '#10B981' : '#F43F5E'}
                  strokeWidth={1.5}
                  fill="none"
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* CARD 2: Jumlah Saham Dianalisis */}
        <div className="p-4 rounded-2xl bg-[#111827]/85 border border-indigo-500/25 flex flex-col justify-between hover:border-indigo-500/45 transition-all">
          <div className="flex items-center justify-between text-xs text-indigo-300 mb-1">
            <span className="font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-indigo-400" />
              SAHAM DIANALISIS
            </span>
            <span className="text-[10px] font-mono font-bold bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 px-1.5 py-0.2 rounded">
              IDX ALL
            </span>
          </div>

          <div className="my-1">
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-black font-mono text-white tracking-tight">
                {universeStats?.active_stocks || totalAnalyzed || 951}
              </span>
              <span className="text-xs font-semibold text-slate-400">Emiten</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">
              Dipindai otomatis seluruh universe IDX.
            </p>
          </div>

          <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 pt-1.5 border-t border-slate-800/80">
            <span>Aktif: {universeStats?.active_stocks || 951}</span>
            <span>Batch Multi-thread</span>
          </div>
        </div>

        {/* CARD 3: Bullish Stocks */}
        <div className="p-4 rounded-2xl bg-[#111827]/85 border border-emerald-500/25 flex flex-col justify-between hover:border-emerald-500/45 transition-all">
          <div className="flex items-center justify-between text-xs text-emerald-300 mb-1">
            <span className="font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              BULLISH STOCKS
            </span>
            <span className="text-[10px] font-mono font-bold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 px-1.5 py-0.2 rounded">
              {bullishPercent}%
            </span>
          </div>

          <div className="my-1">
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-black font-mono text-emerald-400 tracking-tight">
                {bullishStocks.length}
              </span>
              <span className="text-xs font-semibold text-slate-400">Saham</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Strong Buy: {strongBuyStocks.length} | Buy: {buyStocks.length}
            </p>
          </div>

          <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden mt-1">
            <div
              className="bg-emerald-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(bullishPercent, 100)}%` }}
            />
          </div>
        </div>

        {/* CARD 4: Bearish Stocks */}
        <div className="p-4 rounded-2xl bg-[#111827]/85 border border-rose-500/25 flex flex-col justify-between hover:border-rose-500/45 transition-all">
          <div className="flex items-center justify-between text-xs text-rose-300 mb-1">
            <span className="font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <TrendingDown className="w-4 h-4 text-rose-400" />
              BEARISH STOCKS
            </span>
            <span className="text-[10px] font-mono font-bold bg-rose-500/15 border border-rose-500/30 text-rose-300 px-1.5 py-0.2 rounded">
              {bearishPercent}%
            </span>
          </div>

          <div className="my-1">
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-black font-mono text-rose-400 tracking-tight">
                {bearishStocks.length}
              </span>
              <span className="text-xs font-semibold text-slate-400">Saham</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Sinyal SELL / Di Bawah MA20
            </p>
          </div>

          <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden mt-1">
            <div
              className="bg-rose-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(bearishPercent, 100)}%` }}
            />
          </div>
        </div>

      </div>

      {/* ========================================================================= */}
      {/* SECTION 3: SCANNER PROGRESS (Compact Bar) */}
      {/* ========================================================================= */}
      <div className="p-3.5 sm:p-4 rounded-2xl bg-[#111827]/90 border border-[#22C7F0]/30 shadow-lg relative overflow-hidden backdrop-blur-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-xl bg-[#22C7F0]/15 border border-[#22C7F0]/30 flex items-center justify-center text-[#22C7F0] shrink-0">
              <Sparkles className={`w-4 h-4 ${scanningProgress?.is_running ? 'animate-spin' : ''}`} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs sm:text-sm font-bold text-white font-mono">
                  Scanning: {scanningProgress?.current_index || totalAnalyzed || 951} / {scanningProgress?.total_stocks || 951} Saham
                </span>
                <span className={`text-[9px] font-mono px-2 py-0.2 rounded-full font-bold ${
                  scanningProgress?.is_running
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 animate-pulse'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}>
                  {scanningProgress?.is_running ? 'PROSES SCAN' : '100% SELESAI'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Last Scan: {lastUpdated} • Multi-threading Batch Screener
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0 self-end sm:self-center">
            {onSyncUniverse && (
              <button
                onClick={onSyncUniverse}
                title="Sinkronisasi emiten baru dari BEI"
                className="px-2.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white transition-all cursor-pointer"
              >
                Sync Emiten
              </button>
            )}
            {onStartScan && (
              <button
                onClick={onStartScan}
                disabled={scanningProgress?.is_running || isScanning}
                className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-[#22C7F0] to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs tracking-wide shadow-md shadow-cyan-500/20 transition-all cursor-pointer disabled:opacity-50 active:scale-95"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${scanningProgress?.is_running || isScanning ? 'animate-spin' : ''}`} />
                <span>{scanningProgress?.is_running || isScanning ? 'Memindai...' : 'Scan Semua IHSG'}</span>
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-2.5 w-full bg-slate-950 rounded-full h-2 p-0.5 border border-slate-800/80 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[#22C7F0] via-blue-500 to-indigo-500 transition-all duration-500"
            style={{ width: `${Math.max(scanningProgress?.percent || 100, 5)}%` }}
          />
        </div>
      </div>

      {/* ========================================================================= */}
      {/* SECTION 4: RECOMMENDATION OVERVIEW (Visual Chart) */}
      {/* ========================================================================= */}
      <div className="p-4 sm:p-5 rounded-2xl bg-[#111827]/90 border border-slate-800/90 shadow-xl backdrop-blur-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3.5">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-[#22C7F0]" />
            <h3 className="text-sm sm:text-base font-bold text-white tracking-wide">
              Overview Distribusi Rekomendasi
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            Total {totalAnalyzed || 951} Emiten Terklasifikasi
          </span>
        </div>

        {/* Visual Cards Breakdown */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-4">
          {distributionData.map(item => (
            <div
              key={item.name}
              className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between"
            >
              <div>
                <span className="text-[11px] text-slate-400 font-medium">{item.name}</span>
                <div className="text-base sm:text-lg font-black font-mono text-white">
                  {item.count}
                </div>
              </div>
              <span
                className="w-3 h-3 rounded-full shrink-0"
                style={{ backgroundColor: item.color }}
              />
            </div>
          ))}
        </div>

        {/* Horizontal Visual Stack Bar */}
        <div className="w-full bg-slate-950 rounded-xl h-4 p-0.5 border border-slate-800 flex overflow-hidden">
          {totalAnalyzed > 0 && distributionData.map(item => {
            const pct = (item.count / totalAnalyzed) * 100;
            if (pct <= 0) return null;
            return (
              <div
                key={item.name}
                title={`${item.name}: ${item.count} (${pct.toFixed(1)}%)`}
                style={{ width: `${pct}%`, backgroundColor: item.color }}
                className="h-full first:rounded-l-lg last:rounded-r-lg transition-all"
              />
            );
          })}
        </div>
      </div>

      {/* ========================================================================= */}
      {/* SECTION 5: TOP RECOMMENDATION (Desktop: Table, Mobile: Card) */}
      {/* ========================================================================= */}
      <div className="p-4 sm:p-5 rounded-2xl bg-[#111827]/90 border border-slate-800/90 shadow-xl backdrop-blur-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm sm:text-base font-bold text-white tracking-wide flex items-center gap-2">
              <Target className="w-4 h-4 text-emerald-400" />
              Top Rekomendasi Saham Pilihan
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Saham dengan skor komposit tertinggi berdasarkan 5 faktor screener kuantitatif.
            </p>
          </div>

          <button
            onClick={onNavigateToScanner}
            className="flex items-center gap-1.5 text-xs text-[#22C7F0] hover:text-cyan-300 font-bold transition-colors cursor-pointer"
          >
            <span>Lihat Semua Scanner</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Desktop View: Responsive Table */}
        <div className="hidden md:block overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-mono uppercase text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-3.5">Kode</th>
                <th className="py-3 px-3.5">Nama Perusahaan</th>
                <th className="py-3 px-3.5 text-right">Harga</th>
                <th className="py-3 px-3.5 text-center">Score</th>
                <th className="py-3 px-3.5 text-center">Signal</th>
                <th className="py-3 px-3.5 text-center">Risk</th>
                <th className="py-3 px-3.5 text-right">Aksi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {topStocks.map((stock) => {
                const score = Math.round(stock.final_score || stock.composite_score || 0);
                const isStrong = stock.recommendation === 'STRONG BUY';
                return (
                  <tr
                    key={stock.symbol}
                    onClick={() => onSelectStock(stock.symbol)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-3.5 font-bold text-[#22C7F0]">
                      {stock.symbol}
                    </td>
                    <td className="py-3 px-3.5 text-slate-300 font-sans truncate max-w-[200px]">
                      {stock.name || stock.symbol}
                    </td>
                    <td className="py-3 px-3.5 text-right text-white font-bold">
                      {formatIDR(stock.price)}
                    </td>
                    <td className="py-3 px-3.5 text-center">
                      <span className="font-extrabold text-slate-100">{score}</span>
                      <span className="text-[10px] text-slate-500">/100</span>
                    </td>
                    <td className="py-3 px-3.5 text-center font-sans">
                      <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${
                        isStrong
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                      }`}>
                        {stock.recommendation}
                      </span>
                    </td>
                    <td className="py-3 px-3.5 text-center font-mono text-[11px] text-slate-300">
                      1:{((1.5 + (stock.trading_setup_score || 50) / 75).toFixed(1))}
                    </td>
                    <td className="py-3 px-3.5 text-right font-sans">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectStock(stock.symbol);
                        }}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-[#22C7F0] hover:text-slate-950 text-slate-300 text-[11px] font-bold transition-colors cursor-pointer"
                      >
                        Detail
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Mobile View: Responsive Cards List */}
        <div className="md:hidden flex flex-col gap-2.5">
          {topStocks.map((stock) => {
            const score = Math.round(stock.final_score || stock.composite_score || 0);
            const isStrong = stock.recommendation === 'STRONG BUY';
            return (
              <div
                key={stock.symbol}
                onClick={() => onSelectStock(stock.symbol)}
                className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 active:scale-[0.99] transition-all cursor-pointer flex flex-col gap-2 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-black font-mono text-[#22C7F0]">
                      {stock.symbol}
                    </span>
                    <span className={`text-[9px] font-extrabold px-2 py-0.2 rounded-full border ${
                      isStrong
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                        : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                    }`}>
                      {stock.recommendation}
                    </span>
                  </div>
                  <span className="text-sm font-black font-mono text-white">
                    {formatIDR(stock.price)}
                  </span>
                </div>

                <p className="text-[11px] text-slate-400 truncate">
                  {stock.name || stock.symbol}
                </p>

                <div className="flex items-center justify-between text-[11px] font-mono pt-2 border-t border-slate-800/80 text-slate-400">
                  <span>Score: <strong className="text-white">{score}</strong>/100</span>
                  <span>Risk-Reward: <strong className="text-emerald-400">1:{((1.5 + (stock.trading_setup_score || 50) / 75).toFixed(1))}</strong></span>
                  <span className="text-[#22C7F0] font-bold flex items-center gap-0.5">
                    Detail <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};
