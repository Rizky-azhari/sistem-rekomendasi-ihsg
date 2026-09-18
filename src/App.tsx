import { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import { Navbar, type NavTab } from './components/Navbar';
import { BottomNav } from './components/BottomNav';
import { LiveStockTicker } from './components/layout/LiveStockTicker';
import { IDX80_DEFAULT_CATALOG } from './constants/idx80';
import { api } from './api/client';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import type {
  StockDetailResponse,
  RecommendationResponse,
  IHSGMarketData,
  ScreenerRuleItem,
  UniverseStats,
  ScanningProgress
} from './types/stock';
import { AlertCircle } from 'lucide-react';

// Code-Splitting / Lazy-Loaded Pages for high performance
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const ScreenerPage = lazy(() => import('./pages/ScreenerPage').then(m => ({ default: m.ScreenerPage })));
const AnalysisPage = lazy(() => import('./pages/AnalysisPage').then(m => ({ default: m.AnalysisPage })));
const ReportsPage = lazy(() => import('./pages/ReportsPage').then(m => ({ default: m.ReportsPage })));
const AdminPage = lazy(() => import('./pages/AdminPage').then(m => ({ default: m.AdminPage })));

function PageLoadingFallback() {
  return (
    <div className="py-24 text-center">
      <div className="w-8 h-8 border-2 border-[#22C7F0] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
      <p className="text-xs text-slate-400 font-mono">Memuat antarmuka terminal...</p>
    </div>
  );
}

function getTabFromPath(path: string): NavTab {
  if (path.startsWith('/admin')) return 'admin';
  if (path.startsWith('/scanner')) return 'scanner';
  if (path.startsWith('/detail')) return 'detail';
  if (path.startsWith('/reports')) return 'reports';
  return 'dashboard';
}

function getPathFromTab(tab: NavTab): string {
  switch (tab) {
    case 'admin':
      return '/admin/dashboard';
    case 'scanner':
      return '/scanner';
    case 'detail':
      return '/detail';
    case 'reports':
      return '/reports';
    case 'dashboard':
    default:
      return '/dashboard';
  }
}

function MainAppContent() {
  const [activeTab, setActiveTabState] = useState<NavTab>(() => {
    const path = window.location.pathname;
    if (path === '/' || path === '') return 'dashboard';
    return getTabFromPath(path);
  });
  const [selectedSymbol, setSelectedSymbol] = useState<string>('BBCA.JK');

  // Set active tab and update URL
  const setActiveTab = useCallback((tab: NavTab) => {
    setActiveTabState(tab);
    const path = getPathFromTab(tab);
    if (window.location.pathname !== path) {
      window.history.pushState(null, '', path);
    }
  }, []);

  // Listen for browser popstate
  useEffect(() => {
    const handlePopState = () => {
      const tab = getTabFromPath(window.location.pathname);
      setActiveTabState(tab);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Auto-redirect rule on initial open / root access: Always land on dashboard first
  useEffect(() => {
    if (window.location.pathname === '/' || window.location.pathname === '') {
      setActiveTab('dashboard');
    }
  }, [setActiveTab]);

  // Data States
  const [ihsgData, setIhsgData] = useState<IHSGMarketData | null>(null);
  const [screenerStocks, setScreenerStocks] = useState<ScreenerRuleItem[]>([]);
  const [stockDetail, setStockDetail] = useState<StockDetailResponse | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);

  // Universe & Scanner States
  const [universeStats, setUniverseStats] = useState<UniverseStats | null>(null);
  const [scanningProgress, setScanningProgress] = useState<ScanningProgress | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);

  // Loading & Error States
  const [isDataLoading, setIsDataLoading] = useState<boolean>(true);
  const [isDetailLoading, setIsDetailLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Dynamic Full Universe Stock list (Initialized with all 80 IDX80 constituents)
  const [allStocksList, setAllStocksList] = useState<Array<{ symbol: string; name: string }>>(() =>
    IDX80_DEFAULT_CATALOG.map(s => ({ symbol: s.symbol, name: s.name }))
  );

  // Fetch full universe stocks list for global search
  const loadUniverseCatalog = useCallback(async () => {
    try {
      const resp = await api.getStocks();
      const rawList = Array.isArray(resp) ? resp : (resp?.stocks || resp?.data || []);
      if (rawList.length > 0) {
        setAllStocksList(
          rawList.map((s: any) => ({
            symbol: s.symbol,
            name: s.name || s.company_name || s.symbol
          }))
        );
      }
    } catch (err) {
      console.warn('Gagal memuat katalog emiten IDX:', err);
    }
  }, []);

  // Fetch initial market data & screening results
  const loadMarketData = useCallback(async () => {
    setIsDataLoading(true);
    setErrorMsg(null);
    try {
      const [ihsg, screening, universe, progress] = await Promise.allSettled([
        api.getIHSG(),
        api.getScreenerRules(),
        api.getUniverseStats(),
        api.getScanningProgress()
      ]);

      if (ihsg.status === 'fulfilled') setIhsgData(ihsg.value);
      if (screening.status === 'fulfilled') setScreenerStocks(screening.value.results || []);
      if (universe.status === 'fulfilled') setUniverseStats(universe.value);
      if (progress.status === 'fulfilled') setScanningProgress(progress.value);
    } catch (err) {
      setErrorMsg('Gagal terhubung ke API backend. Pastikan server backend berjalan.');
      console.error(err);
    } finally {
      setIsDataLoading(false);
    }
  }, []);

  // Fetch single stock detail & recommendation
  const loadStockDetail = useCallback(async (symbol: string) => {
    setIsDetailLoading(true);
    try {
      const [detail, rec] = await Promise.allSettled([
        api.getStockDetail(symbol),
        api.getRecommendation(symbol)
      ]);

      if (detail.status === 'fulfilled') setStockDetail(detail.value);
      if (rec.status === 'fulfilled') setRecommendation(rec.value);
    } catch (err) {
      console.error(`Gagal memuat data untuk ${symbol}:`, err);
    } finally {
      setIsDetailLoading(false);
    }
  }, []);

  // Initial Load
  useEffect(() => {
    loadMarketData();
    loadUniverseCatalog();
    loadStockDetail(selectedSymbol);
  }, [loadMarketData, loadUniverseCatalog, loadStockDetail, selectedSymbol]);

  // Handle symbol selection
  const handleSelectSymbol = (symbol: string) => {
    setSelectedSymbol(symbol);
    loadStockDetail(symbol);
    setActiveTab('detail');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Trigger full universe background scan
  const handleStartScan = async () => {
    try {
      setIsScanning(true);
      await api.startUniverseScan();
      setTimeout(loadMarketData, 1000);
    } catch (err) {
      console.error('Gagal memulai scan semesta:', err);
    } finally {
      setIsScanning(false);
    }
  };

  // Trigger universe sync from IDX
  const handleSyncUniverse = async () => {
    try {
      await api.syncUniverse();
      await loadMarketData();
      await loadUniverseCatalog();
    } catch (err) {
      console.error('Gagal sinkronisasi emiten:', err);
    }
  };

  // Polling scanner status if running
  useEffect(() => {
    if (!scanningProgress?.is_running) return;

    const interval = setInterval(async () => {
      try {
        const progress = await api.getScanningProgress();
        setScanningProgress(progress);
        if (!progress.is_running) {
          clearInterval(interval);
          loadMarketData();
        }
      } catch (e) {
        console.warn('Polling status error:', e);
      }
    }, 2500);

    return () => clearInterval(interval);
  }, [scanningProgress?.is_running, loadMarketData]);

  return (
    <div className="min-h-screen flex flex-col bg-[#060B18] text-slate-100 overflow-x-hidden">
      {/* Top Navbar for Desktop & Tablet, Clean Header for Mobile */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onSelectSymbol={handleSelectSymbol}
        stockList={allStocksList}
        ihsg={ihsgData}
      />

      {/* Global Error Banner if API Fails */}
      {errorMsg && (
        <div className="fixed top-14 sm:top-16 left-0 right-0 z-40 bg-rose-950/90 border-b border-rose-800/80 px-4 py-2 text-center text-xs text-rose-200 flex items-center justify-center gap-2 backdrop-blur-md">
          <AlertCircle className="w-4 h-4 text-rose-400" />
          <span>{errorMsg}</span>
          <button
            onClick={loadMarketData}
            className="underline font-bold hover:text-rose-300 ml-2 cursor-pointer"
          >
            Coba lagi
          </button>
        </div>
      )}

      {/* Main Content Area with Safe Padding for Fixed Top Navbar & Fixed Bottom Ticker */}
      <main className="flex-1 pt-14 sm:pt-16 pb-32 md:pb-24 w-full max-w-full overflow-x-hidden">
        <Suspense fallback={<PageLoadingFallback />}>
          {/* 1. Dashboard Page */}
          {activeTab === 'dashboard' && (
            <DashboardPage
              ihsg={ihsgData}
              stocks={screenerStocks}
              universeStats={universeStats}
              scanningProgress={scanningProgress}
              onStartScan={handleStartScan}
              onSyncUniverse={handleSyncUniverse}
              isScanning={isScanning}
              isLoading={isDataLoading}
              onSelectStock={handleSelectSymbol}
              onNavigateToScanner={() => setActiveTab('scanner')}
              onRefresh={loadMarketData}
            />
          )}

          {/* 2. Stock Scanner Page — Login Required */}
          {activeTab === 'scanner' && (
            <ProtectedRoute requiredRole="user" onNavigateHome={() => setActiveTab('dashboard')}>
              <ScreenerPage
                stocks={screenerStocks}
                isLoading={isDataLoading}
                onSelectStock={handleSelectSymbol}
              />
            </ProtectedRoute>
          )}

          {/* 3. Detail Saham Page — Login Required */}
          {activeTab === 'detail' && (
            <ProtectedRoute requiredRole="user" onNavigateHome={() => setActiveTab('dashboard')}>
              <AnalysisPage
                symbol={selectedSymbol}
                stockDetail={stockDetail}
                recommendation={recommendation}
                isLoading={isDetailLoading}
                onSelectStock={handleSelectSymbol}
                stockList={allStocksList}
              />
            </ProtectedRoute>
          )}

          {/* 4. Laporan Saham Page — Login Required */}
          {activeTab === 'reports' && (
            <div className="max-w-7xl mx-auto px-3 sm:px-6 pt-4 sm:pt-6">
              <ProtectedRoute requiredRole="user" onNavigateHome={() => setActiveTab('dashboard')}>
                <ReportsPage />
              </ProtectedRoute>
            </div>
          )}

          {/* 5. Admin Panel Page with ProtectedRoute */}
          {activeTab === 'admin' && (
            <div className="max-w-7xl mx-auto px-3 sm:px-6 pt-4 sm:pt-6">
              <ProtectedRoute requiredRole="admin" onNavigateHome={() => setActiveTab('dashboard')}>
                <AdminPage />
              </ProtectedRoute>
            </div>
          )}
        </Suspense>
      </main>

      {/* Mobile Bottom Navigation Bar (md:hidden) */}
      <BottomNav
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Terminal Footer (lifted on desktop to sit cleanly above the live ticker bar) */}
      <footer className="hidden md:block border-t border-slate-800/80 bg-[#060B18]/90 px-4 py-5 text-center text-xs text-slate-500 font-mono mb-10">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>IHSG Terminal Pro · Decision Support System v2.0 (Mobile Ready)</span>
          </div>
          <p className="text-[11px] text-slate-600">
            Autentikasi: Google OAuth & Supabase Auth · Role ADMIN & USER
          </p>
        </div>
      </footer>

      {/* Fixed Running Live Stock Ticker at the bottom */}
      <LiveStockTicker
        ihsg={ihsgData}
        stocks={screenerStocks}
        onSelectStock={handleSelectSymbol}
      />
    </div>
  );
}

export function App() {
  return (
    <AuthProvider>
      <MainAppContent />
    </AuthProvider>
  );
}

export default App;
