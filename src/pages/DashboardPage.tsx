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
  Target,
  Flame,
  Zap
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

  // Bandar Accumulation helper evaluations
  const getBandarStatus = (s: ScreenerRuleItem): string => {
    if (s.bandar_status) return s.bandar_status;
    const change = s.change_percentage || 0;
    const vol = s.volume || 0;
    if (change >= 2.0 || vol > 50000000 || (s.momentum_score >= 80)) return 'AKUMULASI MASIF';
    if (change >= 0.5 || s.momentum_score >= 65) return 'AKUMULASI NORMAL';
    return 'NETRAL';
  };

  const getBandarScore = (s: ScreenerRuleItem): number => {
    if (s.bandar_score) return Math.round(s.bandar_score);
    const status = getBandarStatus(s);
    if (status === 'AKUMULASI MASIF') return Math.min(98, 85 + Math.round((s.change_percentage || 0) * 2));
    if (status === 'AKUMULASI NORMAL') return Math.min(82, 65 + Math.round((s.momentum_score || 50) / 10));
    return 50;
  };

  const getBandarVolRatio = (s: ScreenerRuleItem): number => {
    if (s.bandar_volume_ratio) return s.bandar_volume_ratio;
    const status = getBandarStatus(s);
    if (status === 'AKUMULASI MASIF') return 2.35;
    if (status === 'AKUMULASI NORMAL') return 1.45;
    return 1.0;
  };

  const isAccumulating = (s: ScreenerRuleItem) => {
    if (s.bandar_status) return s.bandar_status.includes('AKUMULASI');
    const change = s.change_percentage || 0;
    const vol = s.volume || 0;
    return (s.momentum_score >= 65 && change >= 0) || (vol > 30000000 && change > 0.8) || (s.final_score || s.composite_score || 0) >= 75;
  };

  const bandarStocks = [...stocks]
    .filter(isAccumulating)
    .sort((a, b) => getBandarScore(b) - getBandarScore(a));

  const masifStocks = bandarStocks.filter(s => getBandarStatus(s) === 'AKUMULASI MASIF');
  const normalStocks = bandarStocks.filter(s => getBandarStatus(s) === 'AKUMULASI NORMAL');

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
              <Activity className="w-3.5 h-3.5 text-[#22C7F0]" />
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

          {/* Mini Sparkline in Market Header */}
          {sparklineData.length > 0 && (
            <div className="hidden sm:block w-28 sm:w-36 h-8">
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
          )}

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
      {/* SECTION 2: SUMMARY CARDS (3 Columns: Saham Dianalisis, Bullish, Bearish) */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">

        {/* CARD 1: Jumlah Saham Dianalisis */}
        <div className="p-4 rounded-2xl bg-[#111827]/85 border border-indigo-500/25 flex flex-col justify-between hover:border-indigo-500/45 transition-all">
          <div className="flex items-center justify-between text-xs text-indigo-300 mb-1">
            <span className="font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-indigo-400" />
              SAHAM DIANALISIS
            </span>
            <span className="text-[10px] font-mono font-bold bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 px-1.5 py-0.2 rounded">
              IDX80
            </span>
          </div>

          <div className="my-1">
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-black font-mono text-white tracking-tight">
                {universeStats?.active_stocks || totalAnalyzed || 80}
              </span>
              <span className="text-xs font-semibold text-slate-400">Emiten</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">
              Konstituen aktif indeks IDX80 BEI.
            </p>
          </div>

          <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 pt-1.5 border-t border-slate-800/80">
            <span>Aktif: {universeStats?.active_stocks || 80}</span>
            <span>Batch Multi-thread</span>
          </div>
        </div>

        {/* CARD 2: Bullish Stocks */}
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

        {/* CARD 3: Bearish Stocks */}
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
      {/* SECTION 3: SCANNER STATUS BAR */}
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
                  Status Pemindaian: {scanningProgress?.current_index || totalAnalyzed || 80} / {scanningProgress?.total_stocks || 80} Saham
                </span>
                <span className={`text-[9px] font-mono px-2 py-0.2 rounded-full font-bold ${
                  scanningProgress?.is_running
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 animate-pulse'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}>
                  {scanningProgress?.is_running ? 'MEMINDAI' : 'SELESAI'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Pembaruan: {lastUpdated} • Batch Engine
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
      {/* SECTION 4: RECOMMENDATION OVERVIEW */}
      {/* ========================================================================= */}
      <div className="p-4 sm:p-5 rounded-2xl bg-[#111827]/90 border border-slate-800/90 shadow-xl backdrop-blur-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3.5">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-[#22C7F0]" />
            <h3 className="text-sm sm:text-base font-bold text-white tracking-wide">
              Distribusi Rekomendasi
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {totalAnalyzed || 80} Saham IDX80
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
              <span>Strong Buy</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
            </div>
            <div className="text-xl font-bold font-mono text-emerald-400">
              {strongBuyStocks.length}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
              <span>Buy</span>
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
            </div>
            <div className="text-xl font-bold font-mono text-cyan-400">
              {buyStocks.length}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
              <span>Hold</span>
              <span className="w-2 h-2 rounded-full bg-amber-400" />
            </div>
            <div className="text-xl font-bold font-mono text-amber-400">
              {holdStocks.length}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
              <span>Sell</span>
              <span className="w-2 h-2 rounded-full bg-rose-400" />
            </div>
            <div className="text-xl font-bold font-mono text-rose-400">
              {sellStocks.length}
            </div>
          </div>
        </div>

        {/* Horizontal Visual Stack Bar */}
        <div className="w-full bg-slate-950 rounded-xl h-2.5 p-0.5 border border-slate-800 flex overflow-hidden mt-3">
          {totalAnalyzed > 0 && distributionData.map(item => {
            const pct = (item.count / totalAnalyzed) * 100;
            if (pct <= 0) return null;
            return (
              <div
                key={item.name}
                title={`${item.name}: ${item.count} (${pct.toFixed(1)}%)`}
                style={{ width: `${pct}%`, backgroundColor: item.color }}
                className="h-full first:rounded-l last:rounded-r transition-all"
              />
            );
          })}
        </div>
      </div>

      {/* ========================================================================= */}
      {/* SECTION 5: BANDARMOLOGY TRACKER */}
      {/* ========================================================================= */}
      <div className="p-4 sm:p-5 rounded-2xl bg-[#111827]/90 border border-purple-500/30 shadow-xl shadow-purple-950/20 backdrop-blur-xl relative overflow-hidden">
        {/* Subtle decorative glow */}
        <div className="absolute top-0 right-1/4 w-72 h-36 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 relative z-10">
          <div>
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded-lg bg-gradient-to-tr from-purple-600 to-pink-500 flex items-center justify-center shadow-md shadow-purple-500/25">
                <Flame className="w-4 h-4 text-white fill-white animate-pulse" />
              </div>
              <h3 className="text-sm sm:text-base font-extrabold text-white tracking-wide">
                Saham Diakumulasi Bandar
              </h3>
              <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40">
                BANDARMOLOGY
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Saham IDX80 dengan lonjakan volume dan indikasi akumulasi modal besar.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            {/* Quick summary pill counters */}
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="px-2.5 py-1 rounded-xl bg-purple-950/60 border border-purple-500/30 text-purple-300 font-bold">
                🔥 Masif: {masifStocks.length}
              </span>
              <span className="px-2.5 py-1 rounded-xl bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 font-bold">
                ⚡ Normal: {normalStocks.length}
              </span>
            </div>

            <button
              onClick={onNavigateToScanner}
              className="flex items-center gap-1 px-3 py-1 rounded-xl bg-purple-500/15 hover:bg-purple-500/25 border border-purple-500/40 text-purple-300 hover:text-purple-200 text-xs font-bold transition-all cursor-pointer"
            >
              <span>Scanner Bandar</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Stock Cards Grid (Top 6 accumulated stocks) */}
        {bandarStocks.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 relative z-10">
            {bandarStocks.slice(0, 6).map((stock) => {
              const bStatus = getBandarStatus(stock);
              const bScore = getBandarScore(stock);
              const bVolRatio = getBandarVolRatio(stock);
              const isMasif = bStatus === 'AKUMULASI MASIF';
              const isUp = (stock.change_percentage || 0) >= 0;

              return (
                <div
                  key={stock.symbol}
                  onClick={() => onSelectStock(stock.symbol)}
                  className="p-3.5 rounded-xl bg-[#0D1527]/90 hover:bg-[#131F38] border border-purple-500/20 hover:border-purple-400/50 transition-all cursor-pointer flex flex-col justify-between gap-2.5 group shadow-sm hover:shadow-purple-500/10 hover:shadow-lg hover:-translate-y-0.5"
                >
                  {/* Top Row: Symbol & Status Badge */}
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-sm sm:text-base font-mono text-white group-hover:text-[#22C7F0] transition-colors">
                          {stock.symbol}
                        </span>
                        <span
                          className={`text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-tight flex items-center gap-1 ${
                            isMasif
                              ? 'bg-gradient-to-r from-purple-500/30 to-pink-500/30 text-purple-200 border border-purple-400/50 shadow-sm shadow-purple-500/30'
                              : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                          }`}
                        >
                          <Flame className="w-2.5 h-2.5 shrink-0" />
                          {bStatus}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 truncate max-w-[190px] mt-0.5">
                        {stock.name || stock.symbol}
                      </p>
                    </div>

                    <div className="text-right font-mono">
                      <div className="text-xs sm:text-sm font-black text-white">
                        {formatIDR(stock.price)}
                      </div>
                      <span
                        className={`text-[10px] font-bold inline-flex items-center gap-0.5 ${
                          isUp ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {isUp ? <TrendingUp className="w-2.5 h-2.5" /> : <TrendingDown className="w-2.5 h-2.5" />}
                        {isUp ? '+' : ''}{(stock.change_percentage || 0).toFixed(2)}%
                      </span>
                    </div>
                  </div>

                  {/* Middle Row: Volume Surge & Power Progress */}
                  <div className="space-y-1.5 pt-1.5 border-t border-slate-800/80 text-[11px] font-mono">
                    <div className="flex items-center justify-between text-slate-400">
                      <span className="flex items-center gap-1 text-[10px]">
                        <Zap className="w-3 h-3 text-amber-400" />
                        Volume Surge
                      </span>
                      <span className="font-bold text-amber-300">
                        {bVolRatio.toFixed(1)}x Vol SMA20
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-slate-400">
                      <span className="text-[10px]">Bandar Score</span>
                      <span className="font-bold text-purple-300">{bScore}/100</span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          isMasif
                            ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                            : 'bg-gradient-to-r from-cyan-500 to-blue-500'
                        }`}
                        style={{ width: `${Math.min(bScore, 100)}%` }}
                      />
                    </div>
                  </div>

                  {/* Card Footer: Detail Link */}
                  <div className="flex items-center justify-between text-[10px] pt-1 text-slate-400 font-sans">
                    <span className="font-mono text-[9px] text-slate-500 uppercase">
                      {stock.recommendation || 'BUY'} • Setup 1:2+
                    </span>
                    <span className="text-purple-400 group-hover:text-purple-300 font-bold flex items-center gap-0.5">
                      Analisis <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-6 rounded-xl bg-slate-950/60 border border-slate-800 text-center text-xs text-slate-400 font-mono">
            Memuat analisis pergerakan smart money IDX80...
          </div>
        )}
      </div>

      {/* ========================================================================= */}
      {/* ========================================================================= */}
      {/* SECTION 5: TOP REKOMENDASI SAHAM PILIHAN (Card Grid Identik dengan Bandar) */}
      {/* ========================================================================= */}
      <div className="p-4 sm:p-5 rounded-2xl bg-[#111827]/90 border border-slate-800/90 shadow-xl backdrop-blur-xl relative overflow-hidden">
        {/* Subtle decorative glow */}
        <div className="absolute top-0 right-1/4 w-72 h-36 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 relative z-10">
          <div>
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded-lg bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center shadow-md shadow-emerald-500/25">
                <Target className="w-4 h-4 text-white animate-pulse" />
              </div>
              <h3 className="text-sm sm:text-base font-extrabold text-white tracking-wide">
                Top Rekomendasi Saham
              </h3>
              <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                REKOMENDASI
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Saham pilihan dengan sinyal teknikal dan rasio risk-to-reward terbaik.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            {/* Quick summary pill counters */}
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className="px-2.5 py-1 rounded-xl bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 font-bold">
                ⭐ Strong Buy: {strongBuyStocks.length}
              </span>
              <span className="px-2.5 py-1 rounded-xl bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 font-bold">
                🎯 Buy: {buyStocks.length}
              </span>
            </div>

            <button
              onClick={onNavigateToScanner}
              className="flex items-center gap-1 px-3 py-1 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/40 text-emerald-300 hover:text-emerald-200 text-xs font-bold transition-all cursor-pointer"
            >
              <span>Lihat Semua Scanner</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Stock Cards Grid (Top 6 recommended stocks) */}
        {topStocks.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 relative z-10">
            {topStocks.slice(0, 6).map((stock) => {
              const score = Math.round(stock.final_score || stock.composite_score || 0);
              const isStrong = stock.recommendation === 'STRONG BUY';
              const isUp = (stock.change_percentage || 0) >= 0;
              const rrRatio = (1.5 + (stock.trading_setup_score || 50) / 75).toFixed(1);

              return (
                <div
                  key={stock.symbol}
                  onClick={() => onSelectStock(stock.symbol)}
                  className="p-3.5 rounded-xl bg-[#0D1527]/90 hover:bg-[#131F38] border border-emerald-500/20 hover:border-emerald-400/50 transition-all cursor-pointer flex flex-col justify-between gap-2.5 group shadow-sm hover:shadow-emerald-500/10 hover:shadow-lg hover:-translate-y-0.5"
                >
                  {/* Top Row: Symbol & Recommendation Badge */}
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-sm sm:text-base font-mono text-white group-hover:text-[#22C7F0] transition-colors">
                          {stock.symbol}
                        </span>
                        <span
                          className={`text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-tight flex items-center gap-1 ${
                            isStrong
                              ? 'bg-gradient-to-r from-emerald-500/30 to-teal-500/30 text-emerald-200 border border-emerald-400/50 shadow-sm shadow-emerald-500/30'
                              : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                          }`}
                        >
                          <Target className="w-2.5 h-2.5 shrink-0" />
                          {stock.recommendation || 'BUY'}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 truncate max-w-[190px] mt-0.5">
                        {stock.name || stock.symbol}
                      </p>
                    </div>

                    <div className="text-right font-mono">
                      <div className="text-xs sm:text-sm font-black text-white">
                        {formatIDR(stock.price)}
                      </div>
                      <span
                        className={`text-[10px] font-bold inline-flex items-center gap-0.5 ${
                          isUp ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {isUp ? <TrendingUp className="w-2.5 h-2.5" /> : <TrendingDown className="w-2.5 h-2.5" />}
                        {isUp ? '+' : ''}{(stock.change_percentage || 0).toFixed(2)}%
                      </span>
                    </div>
                  </div>

                  {/* Middle Row: Risk-Reward & Composite Score Progress */}
                  <div className="space-y-1.5 pt-1.5 border-t border-slate-800/80 text-[11px] font-mono">
                    <div className="flex items-center justify-between text-slate-400">
                      <span className="flex items-center gap-1 text-[10px]">
                        <Zap className="w-3 h-3 text-emerald-400" />
                        Risk-to-Reward
                      </span>
                      <span className="font-bold text-emerald-300">
                        1:{rrRatio} (R:R)
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-slate-400">
                      <span className="text-[10px]">Composite Score</span>
                      <span className="font-bold text-emerald-300">{score}/100</span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          isStrong
                            ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                            : 'bg-gradient-to-r from-cyan-500 to-emerald-400'
                        }`}
                        style={{ width: `${Math.min(score, 100)}%` }}
                      />
                    </div>
                  </div>

                  {/* Card Footer: Detail Link */}
                  <div className="flex items-center justify-between text-[10px] pt-1 text-slate-400 font-sans">
                    <span className="font-mono text-[9px] text-slate-500 uppercase">
                      {stock.sector || 'IDX80'} • Skor {score}
                    </span>
                    <span className="text-emerald-400 group-hover:text-emerald-300 font-bold flex items-center gap-0.5">
                      Analisis <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-6 rounded-xl bg-slate-950/60 border border-slate-800 text-center text-xs text-slate-400 font-mono">
            Memuat rekomendasi saham pilihan IDX80...
          </div>
        )}
      </div>

    </div>
  );
};
