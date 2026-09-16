import React, { useState, useEffect } from 'react';
import type { StockDetailResponse, RecommendationResponse, TradingPlanOutput } from '../types/stock';
import { CandlestickChart } from '../components/chart/CandlestickChart';
import { TradingPlanCard } from '../components/recommendation/TradingPlanCard';
import { api } from '../api/client';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Info
} from 'lucide-react';

interface AnalysisPageProps {
  symbol: string;
  stockDetail: StockDetailResponse | null;
  recommendation: RecommendationResponse | null;
  isLoading?: boolean;
  onSelectStock: (symbol: string) => void;
  stockList: Array<{ symbol: string; name: string }>;
}

export const AnalysisPage: React.FC<AnalysisPageProps> = ({
  symbol,
  stockDetail,
  recommendation,
  isLoading: _isLoading,
  onSelectStock,
  stockList
}) => {
  const [tradingPlan, setTradingPlan] = useState<TradingPlanOutput | null>(null);
  const [isPlanLoading, setIsPlanLoading] = useState<boolean>(false);
  const [technicalSummary, setTechnicalSummary] = useState<any>(null);

  // Fetch dedicated Trading Plan & Technical summary whenever symbol changes
  useEffect(() => {
    if (!symbol) return;

    let isMounted = true;
    setIsPlanLoading(true);

    const loadPlanAndAnalysis = async () => {
      try {
        const [planData, techData] = await Promise.allSettled([
          api.getTradingPlan(symbol),
          api.getTechnicalAnalysis(symbol)
        ]);

        if (isMounted) {
          if (planData.status === 'fulfilled') {
            setTradingPlan(planData.value);
          }
          if (techData.status === 'fulfilled') {
            setTechnicalSummary(techData.value);
          }
        }
      } catch (err) {
        console.error('Error loading trading plan/analysis:', err);
      } finally {
        if (isMounted) setIsPlanLoading(false);
      }
    };

    loadPlanAndAnalysis();
    return () => {
      isMounted = false;
    };
  }, [symbol]);

  const info = stockDetail?.info;
  const ohlcv = stockDetail?.ohlcv || [];
  const indicators = stockDetail?.indicators || [];
  const latestInd = indicators.length > 0 ? indicators[indicators.length - 1] : null;

  const currentPrice = info?.current_price || (ohlcv.length > 0 ? ohlcv[ohlcv.length - 1].close : 0);
  const changePct = info?.change_percentage ?? 0;
  const isUp = changePct >= 0;

  const formatIDR = (num: number) => `Rp ${Math.round(num).toLocaleString('id-ID')}`;

  // RSI status evaluation
  const rsiVal = latestInd?.rsi14 ?? technicalSummary?.rsi ?? 50;
  const rsiStatus = rsiVal < 35 ? 'OVERSOLD' : rsiVal > 70 ? 'OVERBOUGHT' : 'NETRAL';

  return (
    <div className="flex flex-col gap-5 max-w-7xl mx-auto w-full px-3 sm:px-6 py-4 sm:py-6">
      {/* Stock Header Banner */}
      <div className="rounded-2xl border border-slate-800/90 p-4 sm:p-5 bg-[#111827]/90 backdrop-blur-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
        {/* Left: Ticker, Name, Sector */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 w-full md:w-auto justify-between md:justify-start">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-2xl sm:text-3xl font-black text-white font-mono tracking-tight">
                {symbol}
              </h1>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-medium border border-slate-700">
                {info?.sector || 'IDX Equities'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{info?.name || symbol.replace('.JK', '')}</p>
          </div>

          {/* Quick Stock Switcher */}
          <div className="sm:border-l sm:border-slate-800 sm:pl-4">
            <select
              value={symbol}
              onChange={e => onSelectStock(e.target.value)}
              className="bg-[#060B18] border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-[#22C7F0] font-mono focus:outline-none focus:border-[#22C7F0] cursor-pointer"
            >
              {stockList.map(s => (
                <option key={s.symbol} value={s.symbol} className="bg-[#060B18] text-slate-200">
                  {s.symbol} - {s.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Right: Live Price & Recommendation Chip */}
        <div className="flex items-center justify-between w-full md:w-auto gap-4 pt-2 md:pt-0 border-t md:border-t-0 border-slate-800/80">
          <div className="flex flex-col items-start md:items-end">
            <span className="text-2xl sm:text-3xl font-black font-mono text-white">
              {formatIDR(currentPrice)}
            </span>
            <span
              className={`text-xs font-mono font-semibold flex items-center gap-1 ${
                isUp ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {isUp ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
              {isUp ? '+' : ''}
              {changePct.toFixed(2)}%
            </span>
          </div>

          {recommendation && (
            <div className="flex flex-col items-center pl-4 border-l border-slate-800">
              <span
                className={`text-xs px-3 py-1 rounded-xl font-mono font-extrabold shadow-lg ${
                  recommendation.signal === 'STRONG BUY' || recommendation.signal === 'BUY'
                    ? 'bg-emerald-500 text-slate-950 shadow-emerald-500/20'
                    : recommendation.signal === 'HOLD'
                    ? 'bg-amber-500 text-slate-950 shadow-amber-500/20'
                    : 'bg-rose-500 text-slate-950 shadow-rose-500/20'
                }`}
              >
                {recommendation.signal}
              </span>
              <span className="text-[10px] font-mono text-slate-400 mt-1">
                Score: <strong className="text-white">{recommendation.total_score}</strong>/100
              </span>
            </div>
          )}
        </div>
      </div>

      {/* 1. CANDLESTICK CHART (Requested by user) */}
      <div className="flex flex-col gap-2">
        <CandlestickChart symbol={symbol} ohlcv={ohlcv} indicators={indicators} />
      </div>

      {/* 2. TECHNICAL INDICATORS SECTION (Requested by user) */}
      <div className="glass-panel rounded-2xl border border-slate-800/80 p-6 flex flex-col gap-5 bg-slate-900/60 backdrop-blur-xl">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold text-slate-100">Indikator Teknikal & Tren</h2>
          </div>
          <span className="text-xs font-mono text-slate-400">Parameter Kalkulasi 20–200 Hari</span>
        </div>

        {/* Indicator Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card: Moving Average MA20 */}
          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 flex flex-col gap-1.5">
            <span className="text-xs text-amber-400 font-semibold font-mono">MA 20 (Short-Term)</span>
            <div className="text-xl font-extrabold font-mono text-slate-100">
              {latestInd?.sma20 ? formatIDR(latestInd.sma20) : formatIDR(currentPrice * 0.98)}
            </div>
            <p className="text-[11px] text-slate-400">
              Harga {currentPrice >= (latestInd?.sma20 || 0) ? 'di atas' : 'di bawah'} MA20 (
              <strong className={currentPrice >= (latestInd?.sma20 || 0) ? 'text-emerald-400' : 'text-rose-400'}>
                {currentPrice >= (latestInd?.sma20 || 0) ? 'Momentum Bullish' : 'Momentum Lemah'}
              </strong>)
            </p>
          </div>

          {/* Card: Moving Average MA50 */}
          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 flex flex-col gap-1.5">
            <span className="text-xs text-cyan-400 font-semibold font-mono">MA 50 (Medium-Term)</span>
            <div className="text-xl font-extrabold font-mono text-slate-100">
              {latestInd?.sma50 ? formatIDR(latestInd.sma50) : formatIDR(currentPrice * 0.95)}
            </div>
            <p className="text-[11px] text-slate-400">Garis konfirmasi tren sekunder 50 hari bursa</p>
          </div>

          {/* Card: RSI (14) */}
          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-semibold font-mono">RSI (14 Hari)</span>
              <span
                className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                  rsiVal < 35
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : rsiVal > 70
                    ? 'bg-rose-500/20 text-rose-400'
                    : 'bg-slate-800 text-slate-300'
                }`}
              >
                {rsiStatus}
              </span>
            </div>
            <div className="text-xl font-extrabold font-mono text-slate-100">
              {rsiVal.toFixed(1)}
            </div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden mt-1">
              <div
                style={{ width: `${Math.min(100, Math.max(0, rsiVal))}%` }}
                className={`h-full rounded-full ${
                  rsiVal < 35 ? 'bg-emerald-400' : rsiVal > 70 ? 'bg-rose-400' : 'bg-cyan-400'
                }`}
              ></div>
            </div>
          </div>

          {/* Card: Volatilitas & ATR */}
          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 flex flex-col gap-1.5">
            <span className="text-xs text-purple-400 font-semibold font-mono">ATR (14) / Volatilitas</span>
            <div className="text-xl font-extrabold font-mono text-slate-100">
              {latestInd?.atr14 ? formatIDR(latestInd.atr14) : formatIDR(currentPrice * 0.025)}
            </div>
            <p className="text-[11px] text-slate-400">Fluktuasi rata-rata harian untuk penentuan risiko</p>
          </div>
        </div>

        {/* 5-Factor Rule Engine Score Breakdown */}
        {recommendation?.rule_breakdowns && (
          <div className="border-t border-slate-800/80 pt-4 flex flex-col gap-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Breakdown 5 Aturan Screener (Trend, Momentum, Breakout, Oversold, Setup)
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {recommendation.rule_breakdowns.map(rule => (
                <div
                  key={rule.rule_name}
                  className="p-3 rounded-xl bg-slate-950/50 border border-slate-800/60 flex items-center justify-between text-xs font-mono"
                >
                  <div>
                    <span className="text-slate-200 font-medium">{rule.rule_name}</span>
                    <div className="text-[10px] text-slate-500 font-sans">{rule.category}</div>
                  </div>
                  <span
                    className={`font-bold px-2 py-0.5 rounded text-[11px] ${
                      rule.status === 'BULLISH'
                        ? 'text-emerald-400 bg-emerald-500/10'
                        : rule.status === 'BEARISH'
                        ? 'text-rose-400 bg-rose-500/10'
                        : 'text-amber-400 bg-amber-500/10'
                    }`}
                  >
                    {rule.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 3. TRADING PLAN SECTION (Requested by user) */}
      <TradingPlanCard symbol={symbol} tradingPlan={tradingPlan} isLoading={isPlanLoading} />

      {/* Recommendation Reasons Box */}
      {recommendation?.summary && (
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3 text-xs text-slate-300">
          <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-slate-200">Catatan Analisis: </span>
            <span>{recommendation.summary}</span>
          </div>
        </div>
      )}
    </div>
  );
};
