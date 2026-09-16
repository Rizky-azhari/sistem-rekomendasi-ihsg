/**
 * Returns a tailwind text color class based on DSS signal.
 */
export function getSignalColor(signal: string): string {
  switch (signal) {
    case 'STRONG BUY':
      return 'text-emerald-400';
    case 'BUY':
      return 'text-cyan-400';
    case 'HOLD':
      return 'text-amber-400';
    case 'SELL':
      return 'text-rose-400';
    case 'STRONG SELL':
      return 'text-red-500';
    default:
      return 'text-slate-400';
  }
}

/**
 * Returns a tailwind badge class (bg + text + border) based on DSS signal.
 */
export function getSignalBgClass(signal: string): string {
  switch (signal) {
    case 'STRONG BUY':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    case 'BUY':
      return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
    case 'HOLD':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    case 'SELL':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    case 'STRONG SELL':
      return 'bg-red-600/20 text-red-500 border-red-500/40';
    default:
      return 'bg-slate-800 text-slate-400 border-slate-700';
  }
}
