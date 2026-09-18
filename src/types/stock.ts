export interface StockInfo {
  symbol: string;
  name: string;
  sector: string;
  industry: string;
  current_price: number;
  previous_close: number;
  change_amount: number;
  change_percentage: number;
  volume: number;
  market_cap?: number;
}

export interface OHLCVData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface IndicatorData {
  date: string;
  close: number;
  sma20?: number;
  sma50?: number;
  sma200?: number;
  ema12?: number;
  ema26?: number;
  rsi14?: number;
  macd?: number;
  macd_signal?: number;
  macd_hist?: number;
  bb_upper?: number;
  bb_middle?: number;
  bb_lower?: number;
  atr14?: number;
  vol_sma20?: number;
}

export interface StockDetailResponse {
  info: StockInfo;
  ohlcv: OHLCVData[];
  indicators: IndicatorData[];
}

export interface RuleBreakdown {
  rule_name: string;
  category: string;
  score: number;
  weight: number;
  description: string;
  status: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
}

export interface TradingPlan {
  entry_price: number;
  entry_range: string;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number;
  risk_reward_ratio: number;
  recommended_risk_percent: number;
  notes: string;
}

export interface RecommendationResponse {
  symbol: string;
  name: string;
  current_price: number;
  signal: 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG SELL';
  total_score: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  summary: string;
  rule_breakdowns: RuleBreakdown[];
  trading_plan: TradingPlan;
  updated_at: string;
}

export interface ScreenerResultItem {
  symbol: string;
  name: string;
  sector: string;
  current_price: number;
  change_percentage: number;
  signal: string;
  total_score: number;
  rsi?: number;
  macd_status?: string;
  volume: number;
}

export interface IHSGMarketData {
  symbol: string;
  name: string;
  price: number;
  previous_close: number;
  change: number;
  change_percentage: number;
  high: number;
  low: number;
  volume: number;
  status: 'BULLISH' | 'BEARISH';
  sparkline: number[];
}

export interface TradingPlanOutput {
  buy_area: string;
  stop_loss: string;
  tp1: string;
  tp2: string;
  tp3: string;
  risk_reward: string;
  symbol?: string;
  current_price?: number;
}

export interface ScreenerRuleItem {
  symbol: string;
  name: string;
  sector: string;
  price: number;
  change_percentage: number;
  volume: number;
  composite_score: number;
  final_score: number;
  overall_signal: string;
  recommendation: 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL';
  reasons: string[];
  alasan_rekomendasi: string;
  momentum_score: number;
  trend_score: number;
  breakout_score: number;
  oversold_score: number;
  trading_setup_score: number;
  bandar_status?: 'AKUMULASI MASIF' | 'AKUMULASI NORMAL' | 'NETRAL' | 'DISTRIBUSI' | string;
  bandar_score?: number;
  bandar_volume_ratio?: number;
  bandar_action?: string;
  bandar_details?: string;
  rules_passed?: {
    momentum: boolean;
    trend: boolean;
    breakout: boolean;
    oversold: boolean;
    trading_setup: boolean;
  };
}

export interface UniverseStats {
  total_universe: number;
  active_stocks: number;
  inactive_stocks: number;
  universe_name?: string;
  last_update: string;
  last_scan?: string;
  display_label: string;
  source_status: string;
}

export interface ScanningProgress {
  is_running: boolean;
  current_index: number;
  total_stocks: number;
  current_batch: number;
  total_batches: number;
  percent: number;
  progress_message: string;
  total_scanned_results: number;
  start_time: string | null;
  end_time: string | null;
}


