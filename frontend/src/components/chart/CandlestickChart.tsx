import React, { useState, useMemo } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart
} from 'recharts';
import type { OHLCVData, IndicatorData } from '../../types/stock';
import { BarChart2 } from 'lucide-react';

interface CandlestickChartProps {
  symbol: string;
  ohlcv: OHLCVData[];
  indicators?: IndicatorData[];
}

// Custom SVG renderer for Candlestick bars + wicks
const CandleStickItem = (props: any) => {
  const { x, width, payload, yAxis } = props;
  if (!payload || !yAxis || typeof yAxis.scale !== 'function') return null;

  const { open, close, high, low } = payload;
  if (open === undefined || close === undefined || high === undefined || low === undefined) {
    return null;
  }

  const isBullish = close >= open;
  const color = isBullish ? '#10B981' : '#F43F5E';

  const scale = yAxis.scale;
  const openY = scale(open);
  const closeY = scale(close);
  const highY = scale(high);
  const lowY = scale(low);

  const topY = Math.min(openY, closeY);
  const bodyHeight = Math.max(Math.abs(closeY - openY), 2);
  const candleWidth = Math.max(width * 0.65, 3);
  const candleX = x + (width - candleWidth) / 2;
  const wickX = x + width / 2;

  return (
    <g className="transition-opacity duration-150 hover:opacity-80">
      {/* High-Low Wick */}
      <line
        x1={wickX}
        y1={highY}
        x2={wickX}
        y2={lowY}
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
      />
      {/* Candle Body */}
      <rect
        x={candleX}
        y={topY}
        width={candleWidth}
        height={bodyHeight}
        fill={color}
        rx={1}
      />
    </g>
  );
};

export const CandlestickChart: React.FC<CandlestickChartProps> = ({ symbol, ohlcv, indicators = [] }) => {
  const [timeframe, setTimeframe] = useState<'1M' | '3M' | '6M' | '1Y'>('3M');
  const [showMA20, setShowMA20] = useState(true);
  const [showMA50, setShowMA50] = useState(true);
  const [showMA200, setShowMA200] = useState(false);
  const [showVolume, setShowVolume] = useState(true);

  // Filter based on timeframe
  const filteredData = useMemo(() => {
    let days = 60; // 3M
    if (timeframe === '1M') days = 22;
    else if (timeframe === '6M') days = 120;
    else if (timeframe === '1Y') days = 250;

    const slicedOHLCV = ohlcv.slice(-days);
    const slicedIndicators = indicators.slice(-days);

    return slicedOHLCV.map((item, i) => {
      const ind = slicedIndicators[i] || {};
      const isUp = item.close >= item.open;
      return {
        ...item,
        isUp,
        sma20: ind.sma20,
        sma50: ind.sma50,
        sma200: ind.sma200,
        // Range for YAxis calculation
        candleRange: [item.low, item.high]
      };
    });
  }, [ohlcv, indicators, timeframe]);

  // Calculate dynamic Min & Max for YAxis with padding
  const yDomain = useMemo(() => {
    if (!filteredData.length) return [0, 100];
    const lows = filteredData.map(d => d.low).filter(v => typeof v === 'number' && !isNaN(v));
    const highs = filteredData.map(d => d.high).filter(v => typeof v === 'number' && !isNaN(v));
    const min = Math.min(...lows);
    const max = Math.max(...highs);
    const pad = (max - min) * 0.05 || 10;
    return [Math.floor(min - pad), Math.ceil(max + pad)];
  }, [filteredData]);

  // Latest price info
  const latest = filteredData[filteredData.length - 1];
  const prevClose = filteredData.length > 1 ? filteredData[filteredData.length - 2].close : (latest?.open || 0);
  const priceChange = latest ? latest.close - prevClose : 0;
  const pctChange = prevClose > 0 ? (priceChange / prevClose) * 100 : 0;
  const isUp = priceChange >= 0;

  const formatIDR = (num: number) => `Rp ${Math.round(num).toLocaleString('id-ID')}`;

  return (
    <div className="glass-panel rounded-2xl border border-slate-800/80 p-5 flex flex-col gap-4 bg-slate-900/50 backdrop-blur-xl">
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        {/* Left: Ticker & Live Price */}
        <div className="flex items-baseline gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xl font-extrabold text-slate-100 tracking-tight">{symbol}</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono font-medium">
              CANDLESTICK
            </span>
          </div>

          {latest && (
            <div className="flex items-center gap-2 font-mono">
              <span className="text-xl font-bold text-slate-100">{formatIDR(latest.close)}</span>
              <span
                className={`text-xs px-2 py-0.5 rounded-md font-semibold ${
                  isUp ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'
                }`}
              >
                {isUp ? '+' : ''}{priceChange.toFixed(0)} ({isUp ? '+' : ''}{pctChange.toFixed(2)}%)
              </span>
            </div>
          )}
        </div>

        {/* Controls: Timeframe + Indicators */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Indicators Toggle */}
          <div className="flex flex-wrap items-center gap-1 bg-[#060B18]/90 rounded-xl p-1 border border-slate-800">
            <button
              onClick={() => setShowMA20(!showMA20)}
              className={`px-2 py-1 text-[11px] font-mono font-semibold rounded-lg transition-all ${
                showMA20 ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              MA20
            </button>
            <button
              onClick={() => setShowMA50(!showMA50)}
              className={`px-2 py-1 text-[11px] font-mono font-semibold rounded-lg transition-all ${
                showMA50 ? 'bg-blue-500/20 text-blue-400 border border-blue-500/40' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              MA50
            </button>
            <button
              onClick={() => setShowMA200(!showMA200)}
              className={`px-2 py-1 text-[11px] font-mono font-semibold rounded-lg transition-all ${
                showMA200 ? 'bg-purple-500/20 text-purple-400 border border-purple-500/40' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              MA200
            </button>
            <button
              onClick={() => setShowVolume(!showVolume)}
              className={`px-2 py-1 text-[11px] font-mono font-semibold rounded-lg transition-all flex items-center gap-1 ${
                showVolume ? 'bg-slate-800 text-[#22C7F0]' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <BarChart2 className="w-3 h-3" />
              VOL
            </button>
          </div>

          {/* Timeframe Selector: Mobile Dropdown vs Desktop Buttons */}
          <div className="sm:hidden">
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value as any)}
              className="bg-[#060B18] border border-slate-800 rounded-xl px-2.5 py-1 text-xs text-[#22C7F0] font-mono font-bold focus:outline-none"
            >
              <option value="1M">1M</option>
              <option value="3M">3M</option>
              <option value="6M">6M</option>
              <option value="1Y">1Y</option>
            </select>
          </div>

          <div className="hidden sm:flex items-center bg-[#060B18]/90 rounded-xl p-1 border border-slate-800">
            {(['1M', '3M', '6M', '1Y'] as const).map(tf => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
                  timeframe === tf
                    ? 'bg-[#22C7F0] text-slate-950 font-bold shadow-md shadow-cyan-500/20'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Candlestick Chart */}
      <div className="w-full h-[290px] sm:h-[380px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={filteredData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" opacity={0.6} />
            <XAxis
              dataKey="date"
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
              tickFormatter={str => {
                const parts = str.split('-');
                return parts.length >= 3 ? `${parts[2]}/${parts[1]}` : str;
              }}
            />
            <YAxis
              domain={yDomain}
              orientation="right"
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
              tickFormatter={val => `${val.toLocaleString('id-ID')}`}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                const data = payload[0].payload;
                const isBull = data.close >= data.open;
                const chg = data.close - data.open;
                const chgP = data.open > 0 ? (chg / data.open) * 100 : 0;

                return (
                  <div className="bg-slate-950/95 border border-slate-800 p-3.5 rounded-xl shadow-2xl backdrop-blur-md text-xs font-mono min-w-[210px] flex flex-col gap-1.5">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-slate-400 font-sans font-medium">
                      <span>{data.date}</span>
                      <span className={isBull ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                        {isBull ? 'BULLISH' : 'BEARISH'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-x-3 gap-y-1 pt-1">
                      <div className="text-slate-400">Open: <span className="text-slate-200">{formatIDR(data.open)}</span></div>
                      <div className="text-slate-400">High: <span className="text-slate-200">{formatIDR(data.high)}</span></div>
                      <div className="text-slate-400">Low: <span className="text-slate-200">{formatIDR(data.low)}</span></div>
                      <div className="text-slate-400">Close: <span className="text-slate-100 font-bold">{formatIDR(data.close)}</span></div>
                    </div>

                    <div className="flex justify-between items-center text-[11px] pt-1 border-t border-slate-800/80">
                      <span className="text-slate-500">Rentang:</span>
                      <span className={isBull ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>
                        {isBull ? '+' : ''}{chg.toFixed(0)} ({isBull ? '+' : ''}{chgP.toFixed(2)}%)
                      </span>
                    </div>

                    {data.volume > 0 && (
                      <div className="flex justify-between items-center text-[11px]">
                        <span className="text-slate-500">Volume:</span>
                        <span className="text-slate-300">{data.volume.toLocaleString('id-ID')}</span>
                      </div>
                    )}

                    {(data.sma20 || data.sma50 || data.sma200) && (
                      <div className="flex items-center gap-2 pt-1 border-t border-slate-800/80 text-[10px]">
                        {data.sma20 && <span className="text-amber-400">MA20: {data.sma20.toFixed(0)}</span>}
                        {data.sma50 && <span className="text-cyan-400">MA50: {data.sma50.toFixed(0)}</span>}
                        {data.sma200 && <span className="text-purple-400">MA200: {data.sma200.toFixed(0)}</span>}
                      </div>
                    )}
                  </div>
                );
              }}
            />

            {/* Custom Candlestick rendering */}
            <Bar
              dataKey="close"
              shape={<CandleStickItem />}
              isAnimationActive={false}
            />

            {/* Moving Average Overlays */}
            {showMA20 && (
              <Line
                type="monotone"
                dataKey="sma20"
                stroke="#F59E0B"
                strokeWidth={1.8}
                dot={false}
                isAnimationActive={false}
                name="MA20"
              />
            )}
            {showMA50 && (
              <Line
                type="monotone"
                dataKey="sma50"
                stroke="#06B6D4"
                strokeWidth={1.8}
                dot={false}
                isAnimationActive={false}
                name="MA50"
              />
            )}
            {showMA200 && (
              <Line
                type="monotone"
                dataKey="sma200"
                stroke="#A855F7"
                strokeWidth={1.8}
                dot={false}
                isAnimationActive={false}
                name="MA200"
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Synchronized Volume Sub-chart */}
      {showVolume && (
        <div className="w-full h-[90px] border-t border-slate-800/60 pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={filteredData} margin={{ top: 0, right: 10, left: 10, bottom: 0 }}>
              <XAxis dataKey="date" hide />
              <YAxis orientation="right" hide />
              <Tooltip
                content={({ active, payload }) => {
                  if (!active || !payload || !payload.length) return null;
                  const d = payload[0].payload;
                  return (
                    <div className="bg-slate-950 border border-slate-800 px-2.5 py-1 rounded text-[11px] font-mono text-slate-300">
                      Vol: {Number(d.volume).toLocaleString('id-ID')}
                    </div>
                  );
                }}
              />
              <Bar
                dataKey="volume"
                shape={(props: any) => {
                  const { x, y, width, height, payload } = props;
                  const color = payload?.isUp ? '#10B98180' : '#F43F5E80';
                  return <rect x={x} y={y} width={Math.max(width * 0.7, 1)} height={height} fill={color} rx={1} />;
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};
