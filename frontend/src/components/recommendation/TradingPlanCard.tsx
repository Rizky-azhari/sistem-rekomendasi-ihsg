import React from 'react';
import type { TradingPlanOutput } from '../../types/stock';
import { Target, ShieldAlert, TrendingUp, Compass, Award, CheckCircle2 } from 'lucide-react';

interface TradingPlanCardProps {
  symbol: string;
  tradingPlan: TradingPlanOutput | null;
  isLoading?: boolean;
}

export const TradingPlanCard: React.FC<TradingPlanCardProps> = ({ symbol, tradingPlan, isLoading = false }) => {
  if (isLoading) {
    return (
      <div className="glass-panel rounded-2xl border border-slate-800 p-6 flex flex-col gap-4 animate-pulse">
        <div className="h-6 w-40 bg-slate-800 rounded"></div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-20 bg-slate-800/60 rounded-xl"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!tradingPlan) {
    return (
      <div className="glass-panel rounded-2xl border border-slate-800 p-6 text-center text-slate-500 text-sm">
        Trading plan belum tersedia untuk {symbol}.
      </div>
    );
  }

  const { buy_area, stop_loss, tp1, tp2, tp3, risk_reward } = tradingPlan;

  return (
    <div className="glass-panel rounded-2xl border border-slate-800/80 p-6 flex flex-col gap-5 bg-slate-900/60 backdrop-blur-xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              Trading Plan Generator
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono font-normal">
                {symbol}
              </span>
            </h3>
            <p className="text-xs text-slate-400">Parameter eksekusi berbasis Support, Resistance, ATR & Volatility</p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-950/80 px-3 py-1.5 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 font-medium">Risk/Reward:</span>
          <span className="text-sm font-bold font-mono text-emerald-400">{risk_reward}</span>
        </div>
      </div>

      {/* Grid of Key Plan Levels */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {/* 1. Buy Area */}
        <div className="p-4 rounded-xl bg-slate-950/70 border border-cyan-500/30 flex flex-col gap-1.5 relative overflow-hidden shadow-lg shadow-cyan-950/20">
          <div className="absolute top-0 right-0 w-16 h-16 bg-cyan-500/5 rounded-full blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between text-xs text-cyan-400 font-semibold">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" />
              BUY AREA
            </span>
            <span className="text-[10px] text-cyan-500/80 uppercase">Area Masuk</span>
          </div>
          <div className="text-lg font-extrabold font-mono text-slate-100 tracking-tight">
            {buy_area}
          </div>
          <p className="text-[11px] text-slate-400">Rentang beli optimal dekat support</p>
        </div>

        {/* 2. Stop Loss */}
        <div className="p-4 rounded-xl bg-slate-950/70 border border-rose-500/30 flex flex-col gap-1.5 relative overflow-hidden shadow-lg shadow-rose-950/20">
          <div className="absolute top-0 right-0 w-16 h-16 bg-rose-500/5 rounded-full blur-xl pointer-events-none"></div>
          <div className="flex items-center justify-between text-xs text-rose-400 font-semibold">
            <span className="flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5" />
              STOP LOSS
            </span>
            <span className="text-[10px] text-rose-500/80 uppercase">Batasan Rugi</span>
          </div>
          <div className="text-lg font-extrabold font-mono text-rose-400 tracking-tight">
            {stop_loss}
          </div>
          <p className="text-[11px] text-slate-400">Disangga bantalan 0.5x ATR di bawah support</p>
        </div>

        {/* 3. Take Profit 1 */}
        <div className="p-4 rounded-xl bg-slate-950/70 border border-emerald-500/20 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs text-emerald-400 font-semibold">
            <span className="flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5" />
              TAKE PROFIT 1
            </span>
            <span className="text-[10px] text-slate-500 uppercase font-mono">1.5x Risk</span>
          </div>
          <div className="text-lg font-extrabold font-mono text-emerald-400 tracking-tight">
            {tp1}
          </div>
          <p className="text-[11px] text-slate-400">Target pertama / resistance terdekat</p>
        </div>

        {/* 4. Take Profit 2 */}
        <div className="p-4 rounded-xl bg-slate-950/70 border border-emerald-500/30 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs text-emerald-300 font-semibold">
            <span className="flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5" />
              TAKE PROFIT 2
            </span>
            <span className="text-[10px] text-emerald-400/80 uppercase font-mono">2.5x Risk</span>
          </div>
          <div className="text-lg font-extrabold font-mono text-emerald-300 tracking-tight">
            {tp2}
          </div>
          <p className="text-[11px] text-slate-400">Target swing utama / target keuntungan ideal</p>
        </div>

        {/* 5. Take Profit 3 */}
        <div className="p-4 rounded-xl bg-slate-950/70 border border-purple-500/20 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs text-purple-400 font-semibold">
            <span className="flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5" />
              TAKE PROFIT 3
            </span>
            <span className="text-[10px] text-purple-400/80 uppercase font-mono">4.0x Risk</span>
          </div>
          <div className="text-lg font-extrabold font-mono text-purple-400 tracking-tight">
            {tp3}
          </div>
          <p className="text-[11px] text-slate-400">Target runner untuk tren rally lanjutan</p>
        </div>

        {/* 6. Risk Reward Assessment */}
        <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs text-slate-300 font-semibold">
            <span>PROFIL RISIKO</span>
            <span className="text-[10px] text-emerald-400 uppercase font-mono">Setup Valid</span>
          </div>
          <div className="text-lg font-extrabold font-mono text-slate-100 tracking-tight">
            R:R {risk_reward}
          </div>
          <p className="text-[11px] text-slate-400">Potensi imbal hasil lebih dari 2x toleransi resiko</p>
        </div>
      </div>
    </div>
  );
};
