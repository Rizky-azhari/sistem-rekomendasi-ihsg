import React, { useState, useMemo } from 'react';
import type { ScreenerRuleItem } from '../types/stock';
import {
  Search,
  ArrowUpDown,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Info,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

interface ScreenerPageProps {
  stocks: ScreenerRuleItem[];
  isLoading: boolean;
  onSelectStock: (symbol: string) => void;
}

export const ScreenerPage: React.FC<ScreenerPageProps> = ({
  stocks,
  isLoading,
  onSelectStock
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSignal, setFilterSignal] = useState<'ALL' | 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL'>('ALL');
  const [sortBy, setSortBy] = useState<'score' | 'price' | 'change'>('score');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  // Filter and sort stocks
  const filteredStocks = useMemo(() => {
    let list = [...stocks];

    // Search query filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        s => s.symbol.toLowerCase().includes(q) || s.name.toLowerCase().includes(q) || s.sector.toLowerCase().includes(q)
      );
    }

    // Recommendation signal filter
    if (filterSignal !== 'ALL') {
      list = list.filter(s => s.recommendation === filterSignal);
    }

    // Sorting
    list.sort((a, b) => {
      const scoreA = a.final_score ?? a.composite_score ?? 0;
      const scoreB = b.final_score ?? b.composite_score ?? 0;

      let compare = 0;
      if (sortBy === 'score') {
        compare = scoreA - scoreB;
      } else if (sortBy === 'price') {
        compare = a.price - b.price;
      } else if (sortBy === 'change') {
        compare = (a.change_percentage || 0) - (b.change_percentage || 0);
      }

      return sortOrder === 'desc' ? -compare : compare;
    });

    return list;
  }, [stocks, searchQuery, filterSignal, sortBy, sortOrder]);

  const toggleSort = (col: 'score' | 'price' | 'change') => {
    if (sortBy === col) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(col);
      setSortOrder('desc');
    }
  };

  const formatIDR = (num: number) => `Rp ${Math.round(num).toLocaleString('id-ID')}`;

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6">
      {/* Page Title & Stats */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight flex items-center gap-2.5">
            Stock Scanner
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/15 border border-cyan-500/30 text-cyan-400 font-mono font-normal">
              {filteredStocks.length} Hasil Ditemukan
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Penyaringan otomatis saham IHSG dengan 5 aturan teknikal dan scoring komposit kuantitatif.
          </p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="glass-panel rounded-2xl border border-slate-800/80 p-4 bg-slate-900/40 flex flex-wrap items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative min-w-[240px] flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Cari kode saham atau nama perusahaan..."
            className="w-full pl-9 pr-4 py-2 bg-slate-950/80 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors font-mono"
          />
        </div>

        {/* Filter Signal Pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {(['ALL', 'STRONG BUY', 'BUY', 'HOLD', 'SELL'] as const).map(sig => {
            const isActive = filterSignal === sig;
            return (
              <button
                key={sig}
                onClick={() => setFilterSignal(sig)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  isActive
                    ? sig === 'STRONG BUY' || sig === 'BUY'
                      ? 'bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20'
                      : sig === 'HOLD'
                      ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20'
                      : sig === 'SELL'
                      ? 'bg-rose-500 text-slate-950 font-bold shadow-md shadow-rose-500/20'
                      : 'bg-cyan-500 text-slate-950 font-bold'
                    : 'bg-slate-950/80 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {sig}
              </button>
            );
          })}
        </div>
      </div>

      {/* STOCK SCANNER TABLE (Requested columns: Kode, Harga, Score, Recommendation) */}
      <div className="glass-panel rounded-2xl border border-slate-800/80 overflow-hidden bg-slate-900/50 backdrop-blur-xl shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800/80 bg-slate-950/70 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                {/* 1. KODE */}
                <th className="py-3.5 px-5 font-mono">KODE</th>

                {/* 2. HARGA */}
                <th
                  onClick={() => toggleSort('price')}
                  className="py-3.5 px-5 cursor-pointer hover:text-slate-200 transition-colors font-mono"
                >
                  <div className="flex items-center gap-1.5">
                    <span>HARGA</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>

                {/* 3. SCORE */}
                <th
                  onClick={() => toggleSort('score')}
                  className="py-3.5 px-5 cursor-pointer hover:text-slate-200 transition-colors font-mono"
                >
                  <div className="flex items-center gap-1.5">
                    <span>SCORE</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-500" />
                  </div>
                </th>

                {/* 4. RECOMMENDATION */}
                <th className="py-3.5 px-5 font-mono">RECOMMENDATION</th>

                {/* ACTION */}
                <th className="py-3.5 px-5 text-right font-mono">AKSI</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-800/60 text-xs">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-500">
                    <div className="inline-block animate-spin w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full mb-2"></div>
                    <p>Memuat data scanner saham IHSG...</p>
                  </td>
                </tr>
              ) : filteredStocks.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-500">
                    Tidak ada saham yang cocok dengan kriteria pencarian.
                  </td>
                </tr>
              ) : (
                filteredStocks.map(stock => {
                  const finalScore = stock.final_score ?? stock.composite_score ?? 50;
                  const isBuy = stock.recommendation === 'STRONG BUY' || stock.recommendation === 'BUY';
                  const isHold = stock.recommendation === 'HOLD';
                  const isExpanded = expandedRow === stock.symbol;

                  return (
                    <React.Fragment key={stock.symbol}>
                      <tr
                        onClick={() => onSelectStock(stock.symbol)}
                        className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                      >
                        {/* 1. KODE */}
                        <td className="py-4 px-5">
                          <div className="flex items-center gap-2.5">
                            <div>
                              <span className="font-bold text-sm text-slate-100 font-mono tracking-tight group-hover:text-cyan-400 transition-colors">
                                {stock.symbol}
                              </span>
                              <div className="text-[11px] text-slate-400 truncate max-w-[180px]">
                                {stock.name}
                              </div>
                            </div>
                            <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-medium hidden sm:inline-block">
                              {stock.sector}
                            </span>
                          </div>
                        </td>

                        {/* 2. HARGA */}
                        <td className="py-4 px-5 font-mono">
                          <div className="font-bold text-slate-100 text-sm">
                            {formatIDR(stock.price)}
                          </div>
                          <div
                            className={`text-[11px] font-semibold flex items-center gap-0.5 ${
                              (stock.change_percentage || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
                            }`}
                          >
                            {(stock.change_percentage || 0) >= 0 ? (
                              <TrendingUp className="w-3 h-3" />
                            ) : (
                              <TrendingDown className="w-3 h-3" />
                            )}
                            {(stock.change_percentage || 0) >= 0 ? '+' : ''}
                            {stock.change_percentage?.toFixed(2)}%
                          </div>
                        </td>

                        {/* 3. SCORE */}
                        <td className="py-4 px-5">
                          <div className="flex flex-col gap-1 min-w-[120px]">
                            <div className="flex items-center justify-between font-mono">
                              <span className="text-xs font-bold text-slate-200">
                                {finalScore.toFixed(1)}
                              </span>
                              <span className="text-[10px] text-slate-500">/ 100</span>
                            </div>
                            <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                              <div
                                style={{ width: `${Math.min(100, Math.max(0, finalScore))}%` }}
                                className={`h-full rounded-full ${
                                  finalScore >= 80
                                    ? 'bg-emerald-400'
                                    : finalScore >= 65
                                    ? 'bg-cyan-400'
                                    : finalScore >= 50
                                    ? 'bg-amber-400'
                                    : 'bg-rose-400'
                                }`}
                              ></div>
                            </div>
                          </div>
                        </td>

                        {/* 4. RECOMMENDATION */}
                        <td className="py-4 px-5">
                          <div className="flex items-center gap-2">
                            <span
                              className={`text-xs px-2.5 py-1 rounded-lg font-mono font-bold whitespace-nowrap ${
                                isBuy
                                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                                  : isHold
                                  ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                                  : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                              }`}
                            >
                              {stock.recommendation || 'HOLD'}
                            </span>

                            {/* Expand reason button */}
                            <button
                              onClick={e => {
                                e.stopPropagation();
                                setExpandedRow(isExpanded ? null : stock.symbol);
                              }}
                              title="Lihat Alasan Rekomendasi"
                              className="p-1 rounded-md text-slate-500 hover:text-cyan-400 hover:bg-slate-800 transition-colors"
                            >
                              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            </button>
                          </div>
                        </td>

                        {/* AKSI BUTTON */}
                        <td className="py-4 px-5 text-right">
                          <button
                            onClick={e => {
                              e.stopPropagation();
                              onSelectStock(stock.symbol);
                            }}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-cyan-400 font-medium hover:bg-cyan-500 hover:text-slate-950 transition-all cursor-pointer font-mono"
                          >
                            <span>Detail</span>
                            <ExternalLink className="w-3 h-3" />
                          </button>
                        </td>
                      </tr>

                      {/* Expandable Reasons Row */}
                      {isExpanded && (
                        <tr className="bg-slate-950/80 border-b border-slate-800">
                          <td colSpan={5} className="p-4 sm:px-6">
                            <div className="flex flex-col gap-2 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs">
                              <div className="font-bold text-slate-200 flex items-center gap-1.5">
                                <Info className="w-3.5 h-3.5 text-cyan-400" />
                                Alasan Rekomendasi ({stock.recommendation}):
                              </div>
                              <div className="font-mono text-slate-300 whitespace-pre-line pl-5">
                                {stock.alasan_rekomendasi ||
                                  (stock.reasons && stock.reasons.length > 0
                                    ? `${stock.recommendation} karena:\n` + stock.reasons.map(r => `- ${r}`).join('\n')
                                    : 'Kombinasi skor evaluasi tren, momentum, dan manajemen risiko.')}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
