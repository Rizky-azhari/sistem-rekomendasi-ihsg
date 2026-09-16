import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  LineChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Area,
  ReferenceLine
} from 'recharts';
import type { OHLCVData, IndicatorData } from '../../types/stock';

interface StockChartProps {
  symbol: string;
  ohlcv: OHLCVData[];
  indicators: IndicatorData[];
}

export const StockChart: React.FC<StockChartProps> = ({ symbol, ohlcv, indicators }) => {
  const [showSMA, setShowSMA] = useState(true);
  const [showBB, setShowBB] = useState(true);
  const [showVolume, setShowVolume] = useState(true);
  const [subChart, setSubChart] = useState<'RSI' | 'MACD'>('RSI');

  // Merge OHLCV & Indicators into unified data points
  const mergedData = ohlcv.map((item, idx) => {
    const ind = indicators[idx] || {};
    return {
      ...item,
      ...ind
    };
  });

  const formatIDR = (val: number) => `Rp ${val?.toLocaleString('id-ID') || 0}`;

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col gap-4">
      {/* Chart Controls & Toggles */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <span className="font-bold text-lg text-cyan-400">{symbol}</span>
          <span className="text-xs text-slate-400 font-medium">Grafik Teknis Interaktif</span>
        </div>

        <div className="flex items-center gap-2 flex-wrap text-xs">
          <button
            onClick={() => setShowSMA(!showSMA)}
            className={`px-3 py-1.5 rounded-lg border font-medium transition-all ${
              showSMA
                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                : 'bg-slate-900 text-slate-500 border-slate-800'
            }`}
          >
            SMA (20, 50)
          </button>

          <button
            onClick={() => setShowBB(!showBB)}
            className={`px-3 py-1.5 rounded-lg border font-medium transition-all ${
              showBB
                ? 'bg-purple-500/10 text-purple-400 border-purple-500/30'
                : 'bg-slate-900 text-slate-500 border-slate-800'
            }`}
          >
            Bollinger Bands
          </button>

          <button
            onClick={() => setShowVolume(!showVolume)}
            className={`px-3 py-1.5 rounded-lg border font-medium transition-all ${
              showVolume
                ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                : 'bg-slate-900 text-slate-500 border-slate-800'
            }`}
          >
            Volume
          </button>

          <div className="h-4 w-px bg-slate-800 mx-1"></div>

          <button
            onClick={() => setSubChart('RSI')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
              subChart === 'RSI' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            RSI (14)
          </button>

          <button
            onClick={() => setSubChart('MACD')}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
              subChart === 'MACD' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            MACD (12,26,9)
          </button>
        </div>
      </div>

      {/* Main Price & Overlay Chart */}
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={mergedData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <defs>
              <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.5} />
            <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis
              domain={['dataMin - 100', 'dataMax + 100']}
              stroke="#64748b"
              fontSize={11}
              orientation="right"
              tickFormatter={(v) => v.toLocaleString('id-ID')}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
              formatter={(value: any, name: any) => [formatIDR(Number(value)), name]}
            />

            <Area type="monotone" dataKey="close" name="Harga Penutupan" stroke="#06b6d4" strokeWidth={2} fillOpacity={1} fill="url(#colorClose)" />

            {showSMA && (
              <>
                <Line type="monotone" dataKey="sma20" name="SMA 20" stroke="#f59e0b" strokeWidth={1.5} dot={false} />
                <Line type="monotone" dataKey="sma50" name="SMA 50" stroke="#ec4899" strokeWidth={1.5} dot={false} />
              </>
            )}

            {showBB && (
              <>
                <Line type="monotone" dataKey="bb_upper" name="BB Upper" stroke="#a855f7" strokeWidth={1} strokeDasharray="3 3" dot={false} />
                <Line type="monotone" dataKey="bb_lower" name="BB Lower" stroke="#a855f7" strokeWidth={1} strokeDasharray="3 3" dot={false} />
              </>
            )}

            {showVolume && (
              <Bar dataKey="volume" name="Volume" yAxisId="vol" fill="#3b82f6" opacity={0.25} radius={[2, 2, 0, 0]} />
            )}
            <YAxis yAxisId="vol" hide domain={[0, 'dataMax * 4']} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Sub-Chart: RSI or MACD */}
      <div className="h-36 w-full border-t border-slate-800/80 pt-3">
        <div className="text-xs font-semibold text-slate-400 mb-1 flex items-center justify-between">
          <span>{subChart === 'RSI' ? 'RSI (14) Indicator' : 'MACD (12, 26, 9) Oscillator'}</span>
          <span className="text-[10px] text-slate-500">Auto Calculated</span>
        </div>

        {subChart === 'RSI' ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mergedData} margin={{ top: 5, right: 10, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.5} />
              <XAxis dataKey="date" hide />
              <YAxis domain={[0, 100]} orientation="right" stroke="#64748b" fontSize={10} tickCount={4} />
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Overbought 70', fill: '#ef4444', fontSize: 10 }} />
              <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" label={{ value: 'Oversold 30', fill: '#10b981', fontSize: 10 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }} />
              <Line type="monotone" dataKey="rsi14" name="RSI (14)" stroke="#38bdf8" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={mergedData} margin={{ top: 5, right: 10, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.5} />
              <XAxis dataKey="date" hide />
              <YAxis orientation="right" stroke="#64748b" fontSize={10} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }} />
              <Bar dataKey="macd_hist" name="Histogram" fill="#10b981" opacity={0.6} />
              <Line type="monotone" dataKey="macd" name="MACD" stroke="#3b82f6" strokeWidth={1.5} dot={false} />
              <Line type="monotone" dataKey="macd_signal" name="Signal" stroke="#f59e0b" strokeWidth={1.5} dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
