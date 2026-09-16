import React from 'react';
import type { RecommendationResponse } from '../../types/stock';
import { CheckCircle2, AlertTriangle, AlertOctagon, HelpCircle, Award, ShieldAlert } from 'lucide-react';

interface RecommendationCardProps {
  recommendation: RecommendationResponse;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
  const { signal, total_score, confidence_level, summary, rule_breakdowns } = recommendation;

  // Signal Badge Styling
  const getSignalBadge = (sig: string) => {
    switch (sig) {
      case 'STRONG BUY':
        return {
          bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
          icon: <CheckCircle2 className="h-5 w-5 text-emerald-400" />,
          gradient: 'from-emerald-500 to-teal-600'
        };
      case 'BUY':
        return {
          bg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
          icon: <CheckCircle2 className="h-5 w-5 text-cyan-400" />,
          gradient: 'from-cyan-500 to-blue-600'
        };
      case 'HOLD':
        return {
          bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
          icon: <AlertTriangle className="h-5 w-5 text-amber-400" />,
          gradient: 'from-amber-500 to-orange-600'
        };
      case 'SELL':
        return {
          bg: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
          icon: <ShieldAlert className="h-5 w-5 text-rose-400" />,
          gradient: 'from-rose-500 to-red-600'
        };
      case 'STRONG SELL':
        return {
          bg: 'bg-red-600/20 text-red-500 border-red-500/40',
          icon: <AlertOctagon className="h-5 w-5 text-red-500" />,
          gradient: 'from-red-600 to-rose-700'
        };
      default:
        return {
          bg: 'bg-slate-800 text-slate-400 border-slate-700',
          icon: <HelpCircle className="h-5 w-5" />,
          gradient: 'from-slate-600 to-slate-800'
        };
    }
  };

  const badgeStyle = getSignalBadge(signal);

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col gap-6">
      {/* Top Header & DSS Score */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Rekomendasi Rule-Based DSS</span>
          <div className="flex items-center gap-3 mt-1">
            <span className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-xl border text-sm font-bold shadow-md ${badgeStyle.bg}`}>
              {badgeStyle.icon}
              {signal}
            </span>
            <span className="text-xs px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 text-slate-300 font-medium">
              Konfidensi: {confidence_level}
            </span>
          </div>
        </div>

        {/* Score Dial / Counter */}
        <div className="flex items-center gap-3 bg-slate-900/90 px-4 py-2.5 rounded-2xl border border-slate-800 shadow-inner">
          <div className="text-right">
            <div className="text-2xl font-black text-white">{total_score}<span className="text-xs text-slate-500 font-normal"> / 100</span></div>
            <div className="text-[10px] text-slate-400 font-medium">Skor Teknis Total</div>
          </div>
          <div className="h-10 w-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center">
            <Award className="h-5 w-5 text-cyan-400" />
          </div>
        </div>
      </div>

      {/* Summary Narrative */}
      <div className="bg-slate-900/70 p-4 rounded-xl border border-slate-800 text-sm text-slate-300 leading-relaxed">
        <p className="font-medium text-slate-200 mb-1 flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
          Ringkasan Evaluasi Aturan:
        </p>
        {summary}
      </div>

      {/* Detailed Rule Breakdown List */}
      <div>
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Rincian Evaluasi Aturan Teknis</h4>
        <div className="grid grid-cols-1 gap-2.5">
          {rule_breakdowns.map((rule, idx) => {
            const isBull = rule.status === 'BULLISH';
            const isBear = rule.status === 'BEARISH';
            return (
              <div
                key={idx}
                className="bg-slate-900/50 p-3.5 rounded-xl border border-slate-800/80 flex items-center justify-between gap-3 hover:border-slate-700 transition-all"
              >
                <div className="flex flex-col gap-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-xs text-white">{rule.rule_name}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">{rule.category}</span>
                  </div>
                  <p className="text-xs text-slate-400">{rule.description}</p>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <span
                    className={`text-xs font-bold px-2 py-0.5 rounded-md ${
                      rule.score > 0
                        ? 'text-emerald-400 bg-emerald-500/10'
                        : rule.score < 0
                        ? 'text-rose-400 bg-rose-500/10'
                        : 'text-slate-400 bg-slate-800'
                    }`}
                  >
                    {rule.score > 0 ? `+${rule.score}` : rule.score} pts
                  </span>

                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${
                      isBull
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : isBear
                        ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                        : 'bg-slate-800 text-slate-400 border-slate-700'
                    }`}
                  >
                    {rule.status}
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
