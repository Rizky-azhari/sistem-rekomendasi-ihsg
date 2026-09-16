import React from 'react';
import type { ScreenerResultItem } from '../../types/stock';
import { TrendingUp, Award, Zap, ChevronRight, ShieldCheck, Activity } from 'lucide-react';

interface DashboardOverviewProps {
  topStocks: ScreenerResultItem[];
  onSelectSymbol: (symbol: string) => void;
  onGoToScreener: () => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  topStocks,
  onSelectSymbol,
  onGoToScreener
}) => {
  const strongBuys = topStocks.filter(s => s.signal === 'STRONG BUY');
  const buys = topStocks.filter(s => s.signal === 'BUY');
  const holds = topStocks.filter(s => s.signal === 'HOLD');
  const formatIDR = (val: number) => `Rp ${val?.toLocaleString('id-ID') || 0}`;

  return (
    <div className="flex flex-col gap-6">
      {/* Hero Banner Card */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-8 border border-slate-800 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-xs font-bold text-cyan-400 mb-4">
            <Zap className="h-3.5 w-3.5" />
            Decision Support System Saham Indonesia
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight leading-tight mb-3">
            Analisis Teknis Saham IHSG Berbasis Aturan & Algoritma DSS
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed mb-6">
            Dapatkan skor rekomendasi kuantitatif, analisis sinyal RSI, MACD, Moving Average, serta Rencana Trading (Entry, Stop Loss, Take Profit) secara otomatis.
          </p>

          <div className="flex flex-wrap items-center gap-4">
            <button
              onClick={() => onSelectSymbol('BBCA.JK')}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all"
            >
              <TrendingUp className="h-4 w-4" />
              Analisis BBCA.JK
            </button>

            <button
              onClick={onGoToScreener}
              className="px-5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 flex items-center gap-2 transition-all"
            >
              Buka Screener Pasar
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Saham Dipindai</div>
            <div className="text-2xl font-black text-white mt-1">{topStocks.length} <span className="text-xs text-slate-500 font-normal">Ticker</span></div>
            <div className="text-[11px] text-cyan-400 mt-1">Populer IHSG / IDX</div>
          </div>
          <div className="h-11 w-11 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <Activity className="h-5 w-5 text-blue-400" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Sinyal Strong Buy</div>
            <div className="text-2xl font-black text-emerald-400 mt-1">{strongBuys.length}</div>
            <div className="text-[11px] text-emerald-400/80 mt-1">Peluang Entry Terbaik</div>
          </div>
          <div className="h-11 w-11 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
            <Award className="h-5 w-5 text-emerald-400" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Sinyal Buy</div>
            <div className="text-2xl font-black text-cyan-400 mt-1">{buys.length}</div>
            <div className="text-[11px] text-cyan-400/80 mt-1">Bullish Momentum</div>
          </div>
          <div className="h-11 w-11 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <TrendingUp className="h-5 w-5 text-cyan-400" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Sinyal Konsolidasi</div>
            <div className="text-2xl font-black text-amber-400 mt-1">{holds.length}</div>
            <div className="text-[11px] text-amber-400/80 mt-1">Fase Wait & See</div>
          </div>
          <div className="h-11 w-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
            <ShieldCheck className="h-5 w-5 text-amber-400" />
          </div>
        </div>
      </div>

      {/* Top Ranked Recommendations Grid */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-base text-white">Rekomendasi Saham Unggulan IHSG Hari Ini</h3>
            <p className="text-xs text-slate-400">Peringkat berdasarkan Skor Aturan Teknis tertinggi</p>
          </div>
          <button
            onClick={onGoToScreener}
            className="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            Lihat Semua ({topStocks.length})
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {topStocks.slice(0, 6).map((stock) => (
            <div
              key={stock.symbol}
              onClick={() => onSelectSymbol(stock.symbol)}
              className="glass-card p-4 rounded-xl cursor-pointer hover:border-cyan-500/40 transition-all flex flex-col justify-between gap-3 group"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-bold text-base text-cyan-400 group-hover:text-cyan-300">{stock.symbol}</span>
                  <div className="text-xs text-slate-400 truncate max-w-[170px]">{stock.name}</div>
                </div>

                <div className="text-right">
                  <div className="text-xs font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-200">
                    Skor {stock.total_score}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/60">
                <div>
                  <div className="text-xs font-mono font-bold text-white">{formatIDR(stock.current_price)}</div>
                  <div className={`text-[11px] font-bold ${stock.change_percentage >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {stock.change_percentage >= 0 ? `+${stock.change_percentage}%` : `${stock.change_percentage}%`}
                  </div>
                </div>

                <span
                  className={`text-xs font-bold px-2.5 py-1 rounded-lg border ${
                    stock.signal === 'STRONG BUY'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : stock.signal === 'BUY'
                      ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  }`}
                >
                  {stock.signal}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
