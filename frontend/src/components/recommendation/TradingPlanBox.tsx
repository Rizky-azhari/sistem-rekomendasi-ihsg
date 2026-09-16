import React from 'react';
import type { TradingPlan } from '../../types/stock';
import { Target, ArrowDownRight, ArrowUpRight, Scale, AlertCircle } from 'lucide-react';

interface TradingPlanBoxProps {
  plan: TradingPlan;
}

export const TradingPlanBox: React.FC<TradingPlanBoxProps> = ({ plan }) => {
  const formatIDR = (val: number) => `Rp ${val?.toLocaleString('id-ID') || 0}`;

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <Target className="h-5 w-5 text-cyan-400" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-white">Rencana Trading Otomatis (Trading Plan)</h3>
            <p className="text-xs text-slate-400">Parameter Entry, Stop Loss, dan Take Profit berbasis Volatilitas ATR</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full text-xs font-bold text-emerald-400">
          <Scale className="h-3.5 w-3.5" />
          R:R Ratio {plan.risk_reward_ratio}:1
        </div>
      </div>

      {/* Grid Display of Execution Parameters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Entry Target */}
        <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Area Entry (Beli)</span>
            <Target className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="text-lg font-black text-cyan-400">{formatIDR(plan.entry_price)}</div>
          <div className="text-[11px] text-slate-400 mt-1 truncate">{plan.entry_range}</div>
        </div>

        {/* Stop Loss (SL) */}
        <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Stop Loss (SL)</span>
            <ArrowDownRight className="h-4 w-4 text-rose-400" />
          </div>
          <div className="text-lg font-black text-rose-400">{formatIDR(plan.stop_loss)}</div>
          <div className="text-[11px] text-rose-400/80 mt-1 font-medium">
            Batas Risiko (Max 2% Portofolio)
          </div>
        </div>

        {/* Take Profit 1 (TP1) */}
        <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Take Profit 1 (TP1)</span>
            <ArrowUpRight className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-lg font-black text-emerald-400">{formatIDR(plan.take_profit_1)}</div>
          <div className="text-[11px] text-emerald-400/80 mt-1 font-medium">
            Target Moderat (1.5x Risk)
          </div>
        </div>

        {/* Take Profit 2 (TP2) */}
        <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Take Profit 2 (TP2)</span>
            <ArrowUpRight className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-lg font-black text-emerald-300">{formatIDR(plan.take_profit_2)}</div>
          <div className="text-[11px] text-slate-400 mt-1 font-medium">
            Target Optimis (3.0x Risk)
          </div>
        </div>
      </div>

      {/* Trading Management Notes */}
      <div className="flex items-start gap-3 bg-cyan-950/30 border border-cyan-800/40 p-3.5 rounded-xl text-xs text-cyan-200">
        <AlertCircle className="h-4 w-4 text-cyan-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-cyan-300">Catatan Manajemen Risiko: </span>
          {plan.notes}
        </div>
      </div>
    </div>
  );
};
