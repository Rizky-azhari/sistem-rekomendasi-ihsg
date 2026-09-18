import React, { useState } from 'react';
import {
  TrendingUp,
  Search,
  SlidersHorizontal,
  LineChart,
  LayoutDashboard,
  ChevronRight,
  FileText,
  ShieldCheck,
  LogOut,
  X
} from 'lucide-react';
import type { IHSGMarketData } from '../../types/stock';
import { useAuth } from '../../context/AuthContext';
import { AuthModal } from '../common/AuthModal';

export type NavTab = 'dashboard' | 'scanner' | 'detail' | 'reports' | 'admin';

interface NavbarProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  onSelectSymbol: (symbol: string) => void;
  stockList: Array<{ symbol: string; name: string }>;
  ihsg?: IHSGMarketData | null;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onSelectSymbol,
  stockList,
  ihsg
}) => {
  const { user, role, isAuthenticated, logout } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);

  const filteredStocks = stockList.filter(
    s =>
      s.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      <header className="sticky top-0 z-40 bg-[#060B18]/95 backdrop-blur-xl border-b border-slate-800/80 px-2.5 sm:px-4 lg:px-6 py-2">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-2 lg:gap-3">
          
          {/* ========================================================================= */}
          {/* LEFT: Brand & IHSG Ticker (shrink-0, compact on medium/tablet) */}
          {/* ========================================================================= */}
          <div className="flex items-center gap-2 lg:gap-3 shrink-0">
            <div
              className="flex items-center gap-2 cursor-pointer group shrink-0"
              onClick={() => setActiveTab('dashboard')}
            >
              <div className="h-8 w-8 sm:h-9 sm:w-9 rounded-xl bg-gradient-to-tr from-[#22C7F0] via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform shrink-0">
                <TrendingUp className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
              </div>
              <div className="shrink-0">
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-sm sm:text-base lg:text-lg tracking-tight text-white">IHSG TERMINAL</span>
                  <span className="text-[9px] sm:text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-[#22C7F0]/20 text-[#22C7F0] border border-[#22C7F0]/30">
                    PRO
                  </span>
                </div>
                <p className="hidden xl:block text-[10px] text-slate-400 font-medium">Smart Stock Recommendation & DSS</p>
              </div>
            </div>

            {/* IHSG Mini Ticker Chip (Shown on 2XL / wide screens only to prevent squeeze) */}
            {ihsg && (
              <div className="hidden 2xl:flex items-center gap-2 px-2.5 py-1 rounded-xl bg-[#111827] border border-slate-800 text-xs font-mono shrink-0">
                <span className="text-slate-400 text-[11px]">IHSG:</span>
                <span className="font-bold text-slate-100">{ihsg.price.toLocaleString('id-ID', { minimumFractionDigits: 2 })}</span>
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    ihsg.change >= 0 ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'
                  }`}
                >
                  {ihsg.change >= 0 ? '+' : ''}{ihsg.change_percentage.toFixed(2)}%
                </span>
              </div>
            )}
          </div>

          {/* ========================================================================= */}
          {/* CENTER: Navigation Menu Tabs (Adaptive: icons on tablet/split, labels on desktop) */}
          {/* ========================================================================= */}
          <nav className="hidden md:flex items-center gap-0.5 lg:gap-1 bg-[#111827]/90 p-1 rounded-xl border border-slate-800/80 shrink-0">
            <button
              onClick={() => setActiveTab('dashboard')}
              title="Dashboard"
              className={`flex items-center gap-1.5 px-2.5 lg:px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'dashboard'
                  ? 'bg-[#22C7F0] text-slate-950 font-bold shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <LayoutDashboard className="h-3.5 w-3.5 shrink-0" />
              <span className="hidden xl:inline">Dashboard</span>
            </button>

            <button
              onClick={() => setActiveTab('scanner')}
              title="Stock Scanner"
              className={`flex items-center gap-1.5 px-2.5 lg:px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'scanner'
                  ? 'bg-[#22C7F0] text-slate-950 font-bold shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <SlidersHorizontal className="h-3.5 w-3.5 shrink-0" />
              <span className="hidden xl:inline">Scanner</span>
            </button>

            <button
              onClick={() => setActiveTab('detail')}
              title="Detail Saham"
              className={`flex items-center gap-1.5 px-2.5 lg:px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'detail'
                  ? 'bg-[#22C7F0] text-slate-950 font-bold shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <LineChart className="h-3.5 w-3.5 shrink-0" />
              <span className="hidden xl:inline">Detail</span>
            </button>

            <button
              onClick={() => setActiveTab('reports')}
              title="Laporan"
              className={`flex items-center gap-1.5 px-2.5 lg:px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'reports'
                  ? 'bg-[#22C7F0] text-slate-950 font-bold shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <FileText className="h-3.5 w-3.5 shrink-0" />
              <span className="hidden xl:inline">Laporan</span>
            </button>

            {role === 'admin' && (
              <button
                onClick={() => setActiveTab('admin')}
                title="Panel Administrator"
                className={`flex items-center gap-1.5 px-2.5 lg:px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  activeTab === 'admin'
                    ? 'bg-indigo-600 text-white font-bold shadow-md shadow-indigo-500/30'
                    : 'text-indigo-400 hover:text-indigo-200 hover:bg-indigo-950/40'
                }`}
              >
                <ShieldCheck className="h-3.5 w-3.5 shrink-0" />
                <span className="hidden xl:inline">Admin</span>
              </button>
            )}
          </nav>

          {/* ========================================================================= */}
          {/* RIGHT: Search & User Profile & Logout (GUARANTEED ALWAYS VISIBLE) */}
          {/* ========================================================================= */}
          <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
            
            {/* Desktop Full Search Bar (only on xl screens where plenty of space exists) */}
            <div className="relative hidden xl:block w-40 2xl:w-48 shrink-0">
              <div className="relative flex items-center">
                <Search className="absolute left-2.5 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
                <input
                  type="text"
                  placeholder="Cari Ticker..."
                  value={searchTerm}
                  onChange={e => {
                    setSearchTerm(e.target.value);
                    setIsOpen(true);
                  }}
                  onFocus={() => setIsOpen(true)}
                  className="w-full bg-[#111827] text-xs text-slate-100 placeholder-slate-500 pl-7 pr-2.5 py-1.5 rounded-xl border border-slate-800 focus:outline-none focus:border-[#22C7F0] focus:ring-1 focus:ring-[#22C7F0] transition-all font-mono"
                />
              </div>

              {/* Desktop Autocomplete Dropdown */}
              {isOpen && searchTerm && (
                <div className="absolute top-full mt-2 right-0 w-64 glass-panel rounded-xl border border-slate-700 shadow-2xl overflow-hidden max-h-60 overflow-y-auto z-50 bg-[#111827]/98">
                  {filteredStocks.length > 0 ? (
                    filteredStocks.map(stock => (
                      <button
                        key={stock.symbol}
                        onClick={() => {
                          onSelectSymbol(stock.symbol);
                          setActiveTab('detail');
                          setSearchTerm('');
                          setIsOpen(false);
                        }}
                        className="w-full text-left px-3 py-2 hover:bg-slate-800/80 flex items-center justify-between border-b border-slate-800/50 last:border-0 transition-colors cursor-pointer"
                      >
                        <div>
                          <span className="font-bold text-[#22C7F0] text-xs font-mono">{stock.symbol}</span>
                          <p className="text-[11px] text-slate-400 truncate max-w-[160px]">{stock.name}</p>
                        </div>
                        <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                      </button>
                    ))
                  ) : (
                    <div className="px-3 py-2.5 text-xs text-slate-400">Ticker tidak ditemukan.</div>
                  )}
                </div>
              )}
            </div>

            {/* Quick Search Button (for Mobile, Tablet, and split-screen < xl) */}
            <button
              onClick={() => setIsSearchModalOpen(!isSearchModalOpen)}
              aria-label="Cari Saham"
              className="xl:hidden p-1.5 sm:p-2 rounded-xl bg-[#111827] border border-slate-800 text-slate-300 hover:text-white shrink-0 cursor-pointer"
            >
              {isSearchModalOpen ? <X className="w-4 h-4" /> : <Search className="w-4 h-4" />}
            </button>

            {/* Authenticated User Profile & Logout */}
            {isAuthenticated && user ? (
              <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
                <div className="flex items-center gap-1.5 sm:gap-2 bg-[#111827] border border-slate-800/90 rounded-xl px-2 sm:px-2.5 py-1 shrink-0">
                  {user.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.full_name}
                      referrerPolicy="no-referrer"
                      className="w-6 h-6 rounded-full object-cover border border-[#22C7F0]/40 shrink-0"
                    />
                  ) : (
                    <div className="w-6 h-6 rounded-full bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-[10px] font-bold text-cyan-300 shrink-0">
                      {user.full_name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                  )}

                  {/* Name shown on wide screens, truncated safely */}
                  <span className="hidden 2xl:inline text-xs font-bold text-slate-200 max-w-[110px] truncate leading-none">
                    {user.full_name}
                  </span>

                  {/* Role Badge */}
                  <span className={`text-[9px] font-mono font-extrabold px-1.5 py-0.2 rounded uppercase shrink-0 ${
                    role === 'admin'
                      ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                      : 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/25'
                  }`}>
                    {role}
                  </span>
                </div>

                {/* Logout Button (ALWAYS VISIBLE) */}
                <button
                  onClick={() => logout()}
                  title="Keluar (Logout)"
                  aria-label="Logout"
                  className="p-1.5 sm:p-2 rounded-xl bg-slate-900 hover:bg-rose-950/30 border border-slate-800 hover:border-rose-800/50 text-slate-400 hover:text-rose-400 transition-all cursor-pointer shrink-0"
                >
                  <LogOut className="w-4 h-4 shrink-0" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsAuthModalOpen(true)}
                title="Login dengan Akun Google"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#111827] hover:bg-slate-800 text-slate-100 hover:text-white border border-slate-700 hover:border-[#22C7F0]/50 font-bold text-xs shadow-md shadow-cyan-500/10 transition-all cursor-pointer active:scale-95 shrink-0"
              >
                <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24">
                  <path fill="#EA4335" d="M12 5c1.56 0 2.96.54 4.07 1.59l3.05-3.05C17.27 1.8 14.82 1 12 1 7.37 1 3.42 3.66 1.48 7.54l3.68 2.85C6.04 7.42 8.78 5 12 5z" />
                  <path fill="#4285F4" d="M23.49 12.28c0-.82-.07-1.6-.2-2.28H12v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58l3.68 2.85c2.15-1.99 3.44-4.92 3.44-8.66z" />
                  <path fill="#FBBC05" d="M5.16 14.61c-.24-.72-.38-1.49-.38-2.28s.14-1.56.38-2.28L1.48 7.2C.54 9.07 0 11.16 0 12s.54 2.93 1.48 4.8l3.68-2.19z" />
                  <path fill="#34A853" d="M12 23c3.24 0 5.95-1.07 7.94-2.91l-3.68-2.85c-1.07.72-2.44 1.16-4.26 1.16-3.22 0-5.96-2.42-6.84-5.39L1.48 16.8C3.42 20.68 7.37 23 12 23z" />
                </svg>
                <span>Masuk Google</span>
              </button>
            )}
          </div>

        </div>

        {/* Dropdown Search Box for Mobile & Tablet */}
        {isSearchModalOpen && (
          <div className="xl:hidden pt-2 pb-1">
            <div className="relative flex items-center">
              <Search className="absolute left-3 h-3.5 w-3.5 text-slate-400" />
              <input
                type="text"
                autoFocus
                placeholder="Cari Ticker Saham IDX (BBCA, BBRI, TLKM)..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="w-full bg-[#111827] text-xs text-slate-100 placeholder-slate-500 pl-8 pr-3 py-2 rounded-xl border border-slate-800 focus:outline-none focus:border-[#22C7F0] font-mono"
              />
            </div>
            {searchTerm && (
              <div className="mt-1 max-h-48 overflow-y-auto rounded-xl bg-[#111827] border border-slate-700 divide-y divide-slate-800 shadow-2xl">
                {filteredStocks.slice(0, 8).map(stock => (
                  <button
                    key={stock.symbol}
                    onClick={() => {
                      onSelectSymbol(stock.symbol);
                      setActiveTab('detail');
                      setSearchTerm('');
                      setIsSearchModalOpen(false);
                    }}
                    className="w-full text-left px-3 py-2 flex items-center justify-between text-xs hover:bg-slate-800/80 cursor-pointer"
                  >
                    <span className="font-bold text-[#22C7F0] font-mono">{stock.symbol}</span>
                    <span className="text-slate-400 truncate max-w-[200px]">{stock.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </header>

      {/* Google OAuth Modal */}
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
    </>
  );
};
