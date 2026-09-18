/**
 * Application Constants
 * Single source of truth for UI configurations, timeframe filters, and defaults.
 */

export const APP_CONFIG = {
  NAME: 'IHSG Smart Stock Recommender',
  UNIVERSE: 'IDX80',
  DEFAULT_TIMEFRAME: '1y',
  DEFAULT_PAGE_SIZE: 20,
  AUTO_REFRESH_INTERVAL_MS: 60000,
} as const;

export const TIMEFRAMES = [
  { label: '1B', value: '1mo' },
  { label: '3B', value: '3mo' },
  { label: '6B', value: '6mo' },
  { label: '1T', value: '1y' },
  { label: '5T', value: '5y' },
] as const;

export const SIGNAL_BADGES = {
  'STRONG BUY': { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20' },
  'BUY': { bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/20' },
  'HOLD': { bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/20' },
  'SELL': { bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/20' },
  'STRONG SELL': { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20' },
} as const;
