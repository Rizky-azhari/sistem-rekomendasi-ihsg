import React, { useState, useMemo } from 'react';
import type { ScreenerResultItem } from '../../types/stock';
import {
  ArrowUpRight,
  ArrowDownRight,
  ChevronRight,
  ChevronLeft,
  Search,
  SlidersHorizontal
} from 'lucide-react';

interface ScreenerTableProps {
  items: ScreenerResultItem[];
  onSelectSymbol: (symbol: string) => void;
  isLoading: boolean;
}

export const ScreenerTable: React.FC<ScreenerTableProps> = ({ items, onSelectSymbol, isLoading }) => {
  const [selectedSignal, setSelectedSignal] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [minScoreFilter, setMinScoreFilter] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);

  const filteredItems = useMemo(() => {
    return items.filter(item => {
      const matchesSignal = selectedSignal === 'ALL' || item.signal.toUpperCase() === selectedSignal;
      const matchesSearch = item.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            item.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesScore = item.total_score >= minScoreFilter;
      return matchesSignal && matchesSearch && matchesScore;
    });
  }, [items, selectedSignal, searchTerm, minScoreFilter]);

  // Reset to page 1 on filter changes
  React.useEffect(() => {
    setCurrentPage(1);
  }, [selectedSignal, searchTerm, minScoreFilter, pageSize]);

  // Pagination calculation
  const totalPages = Math.max(1, Math.ceil(filteredItems.length / pageSize));
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedItems = filteredItems.slice(startIndex, startIndex + pageSize);

  const getSignalBadge = (signal: string) => {
    switch (signal) {
      case 'STRONG BUY':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'BUY':
        return 'bg-cyan-500/20 text-[#22C7F0] border-cyan-500/40';
      case 'HOLD':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'SELL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  const formatIDR = (val: number) => `Rp ${val?.toLocaleString('id-ID') || 0}`;

  return (
    <div className="rounded-2xl p-4 sm:p-6 bg-[#111827]/90 border border-slate-800/90 shadow-xl backdrop-blur-xl flex flex-col gap-4">
      {/* Header & Filter Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div>
          <h2 className="font-bold text-base sm:text-lg text-white flex items-center gap-2">
            <SlidersHorizontal className="h-5 w-5 text-[#22C7F0]" />
            Screener & Ranking Saham (Indeks IDX80)
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Menampilkan {filteredItems.length} saham terfilter dari 80 konstituen Indeks IDX80 Bursa Efek Indonesia.
          </p>
        </div>

        {/* Quick Filter Buttons */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {['ALL', 'STRONG BUY', 'BUY', 'HOLD', 'SELL'].map((sig) => (
            <button
              key={sig}
              onClick={() => setSelectedSignal(sig)}
              className={`px-2.5 py-1 rounded-xl text-xs font-bold transition-all border cursor-pointer ${
                selectedSignal === sig
                  ? 'bg-[#22C7F0] text-slate-950 border-[#22C7F0] shadow-md shadow-cyan-500/20 font-black'
                  : 'bg-slate-900/90 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-white'
              }`}
            >
              {sig}
            </button>
          ))}
        </div>
      </div>

      {/* Filter Inputs & Score Slider */}
      <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-center">
        <div className="sm:col-span-6 relative">
          <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Cari Ticker atau Nama Perusahaan..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#060B18] text-xs text-slate-100 placeholder-slate-500 pl-9 pr-4 py-2 rounded-xl border border-slate-800 focus:outline-none focus:border-[#22C7F0] font-mono"
          />
        </div>

        <div className="sm:col-span-4 flex items-center gap-2.5 bg-[#060B18] px-3.5 py-1.5 rounded-xl border border-slate-800">
          <span className="text-[11px] text-slate-400 whitespace-nowrap">
            Min Skor: <strong className="text-[#22C7F0]">{minScoreFilter}</strong>
          </span>
          <input
            type="range"
            min="0"
            max="100"
            value={minScoreFilter}
            onChange={(e) => setMinScoreFilter(Number(e.target.value))}
            className="w-full accent-[#22C7F0] cursor-pointer"
          />
        </div>

        <div className="sm:col-span-2 flex items-center justify-end gap-2">
          <span className="text-[11px] text-slate-400">Limit:</span>
          <select
            value={pageSize}
            onChange={(e) => setPageSize(Number(e.target.value))}
            className="bg-[#060B18] text-xs text-slate-200 border border-slate-800 rounded-xl px-2.5 py-1.5 focus:outline-none font-mono cursor-pointer"
          >
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>
      </div>

      {/* Desktop Table View */}
      <div className="hidden md:block overflow-x-auto rounded-xl border border-slate-800/80">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#060B18] text-slate-400 uppercase font-mono text-[11px] border-b border-slate-800">
            <tr>
              <th className="py-3 px-3.5">Ticker / Saham</th>
              <th className="py-3 px-3.5 text-right">Harga</th>
              <th className="py-3 px-3.5 text-right">Chg 24h</th>
              <th className="py-3 px-3.5 text-center">Score DSS</th>
              <th className="py-3 px-3.5 text-center">Sinyal</th>
              <th className="py-3 px-3.5 text-center">RSI(14)</th>
              <th className="py-3 px-3.5 text-center">Trend MACD</th>
              <th className="py-3 px-3.5 text-right">Aksi</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800/60 font-mono">
            {isLoading ? (
              <tr>
                <td colSpan={8} className="py-12 text-center text-slate-400">
                  <div className="inline-block h-6 w-6 border-2 border-[#22C7F0] border-t-transparent rounded-full animate-spin"></div>
                  <p className="mt-2 text-xs">Memproses matriks data indikator...</p>
                </td>
              </tr>
            ) : paginatedItems.length > 0 ? (
              paginatedItems.map((item) => (
                <tr
                  key={item.symbol}
                  className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                  onClick={() => onSelectSymbol(item.symbol)}
                >
                  <td className="py-3 px-3.5">
                    <span className="font-bold text-[#22C7F0] text-xs">{item.symbol}</span>
                    <p className="text-[11px] text-slate-400 font-sans truncate max-w-[180px]">{item.name}</p>
                  </td>

                  <td className="py-3 px-3.5 text-right font-bold text-white">
                    {formatIDR(item.current_price)}
                  </td>

                  <td className="py-3 px-3.5 text-right">
                    <span
                      className={`inline-flex items-center gap-0.5 font-bold ${
                        item.change_percentage >= 0 ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {item.change_percentage >= 0 ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                      {item.change_percentage >= 0 ? `+${item.change_percentage.toFixed(2)}%` : `${item.change_percentage.toFixed(2)}%`}
                    </span>
                  </td>

                  <td className="py-3 px-3.5 text-center">
                    <span className="font-bold text-slate-100">{item.total_score}</span>
                    <span className="text-[10px] text-slate-500">/100</span>
                  </td>

                  <td className="py-3 px-3.5 text-center font-sans">
                    <span className={`px-2 py-0.5 rounded-full border text-[10px] font-extrabold ${getSignalBadge(item.signal)}`}>
                      {item.signal}
                    </span>
                  </td>

                  <td className="py-3 px-3.5 text-center">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[11px] font-bold ${
                        (item.rsi || 50) < 35
                          ? 'bg-emerald-500/15 text-emerald-400'
                          : (item.rsi || 50) > 70
                          ? 'bg-rose-500/15 text-rose-400'
                          : 'text-slate-300'
                      }`}
                    >
                      {Math.round(item.rsi || 50)}
                    </span>
                  </td>

                  <td className="py-3 px-3.5 text-center font-sans">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        item.macd_status === 'BULLISH'
                          ? 'bg-emerald-500/10 text-emerald-400'
                          : 'bg-rose-500/10 text-rose-400'
                      }`}
                    >
                      {item.macd_status}
                    </span>
                  </td>

                  <td className="py-3 px-3.5 text-right font-sans">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectSymbol(item.symbol);
                      }}
                      className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-[#22C7F0] hover:text-slate-950 text-slate-300 text-[11px] font-bold transition-all cursor-pointer"
                    >
                      Detail
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-400">
                  Tidak ada saham yang sesuai kriteria filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View (< md) */}
      <div className="md:hidden flex flex-col gap-2.5">
        {isLoading ? (
          <div className="py-8 text-center text-slate-400">
            <div className="inline-block h-6 w-6 border-2 border-[#22C7F0] border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-2 text-xs">Memuat data emiten...</p>
          </div>
        ) : paginatedItems.length > 0 ? (
          paginatedItems.map((item) => (
            <div
              key={item.symbol}
              onClick={() => onSelectSymbol(item.symbol)}
              className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 active:scale-[0.99] transition-all cursor-pointer flex flex-col gap-2 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-black font-mono text-[#22C7F0]">
                    {item.symbol}
                  </span>
                  <span className={`px-2 py-0.2 rounded-full border text-[9px] font-extrabold ${getSignalBadge(item.signal)}`}>
                    {item.signal}
                  </span>
                </div>
                <span className="text-sm font-black font-mono text-white">
                  {formatIDR(item.current_price)}
                </span>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="truncate max-w-[180px]">{item.name}</span>
                <span
                  className={`font-mono font-bold ${
                    item.change_percentage >= 0 ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {item.change_percentage >= 0 ? `+${item.change_percentage.toFixed(2)}%` : `${item.change_percentage.toFixed(2)}%`}
                </span>
              </div>

              <div className="flex items-center justify-between text-[11px] font-mono pt-2 border-t border-slate-800/80 text-slate-400">
                <span>Score: <strong className="text-white">{item.total_score}</strong>/100</span>
                <span>RSI: <strong className="text-slate-200">{Math.round(item.rsi || 50)}</strong></span>
                <span className="text-[#22C7F0] font-bold flex items-center gap-0.5">
                  Detail <ChevronRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))
        ) : (
          <div className="py-8 text-center text-xs text-slate-400">
            Tidak ada saham yang sesuai kriteria filter.
          </div>
        )}
      </div>

      {/* Pagination Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-slate-800/80 text-xs text-slate-400 font-mono">
        <div>
          Menampilkan <strong className="text-white">{Math.min(startIndex + 1, filteredItems.length)}</strong> -{' '}
          <strong className="text-white">{Math.min(startIndex + pageSize, filteredItems.length)}</strong> dari{' '}
          <strong className="text-[#22C7F0]">{filteredItems.length}</strong> saham
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Sebelumnya</span>
          </button>

          <span className="px-2 font-bold text-white">
            {currentPage} / {totalPages}
          </span>

          <button
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            <span>Selanjutnya</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
