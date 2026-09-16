import React, { type ReactNode } from 'react';
import { useAuth, type UserRole } from '../context/AuthContext';
import { ShieldAlert, ArrowLeft, LogIn } from 'lucide-react';
import { AuthModal } from './AuthModal';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredRole?: UserRole;
  onNavigateHome?: () => void;
  onOpenLogin?: () => void;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole = 'admin',
  onNavigateHome,
  onOpenLogin
}) => {
  const { user, role, isAuthenticated, isLoading, loginWithGoogle } = useAuth();
  const [showLoginModal, setShowLoginModal] = React.useState(false);

  if (isLoading) {
    return (
      <div className="py-24 text-center">
        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-xs text-slate-400 font-mono">Memeriksa hak akses profil Google...</p>
      </div>
    );
  }

  // 1. Not Authenticated — applies to both 'user' and 'admin' requiredRole
  if (!isAuthenticated || !user) {
    const isAdminRoute = requiredRole === 'admin';
    return (
      <>
        <div className="py-20 px-4 max-w-md mx-auto text-center">
          <div className="glass-panel p-8 rounded-3xl border border-slate-800 bg-slate-900/90 shadow-2xl">
            <div className={`w-14 h-14 rounded-2xl ${isAdminRoute ? 'bg-rose-500/10 border-rose-500/30' : 'bg-cyan-500/10 border-cyan-500/30'} border flex items-center justify-center mx-auto mb-4 ${isAdminRoute ? 'text-rose-400' : 'text-cyan-400'}`}>
              <LogIn className="w-7 h-7" />
            </div>
            <h2 className={`text-xl font-bold ${isAdminRoute ? 'text-rose-400' : 'text-cyan-400'} mb-2 uppercase tracking-wide`}>
              {isAdminRoute ? 'Access Denied' : 'Login Diperlukan'}
            </h2>
            <p className="text-xs text-slate-400 mb-6 leading-relaxed">
              {isAdminRoute
                ? <>Halaman <code className="bg-slate-950 px-1.5 py-0.5 rounded text-rose-300 font-mono">/admin/*</code> dilindungi dan hanya dapat diakses oleh Administrator. Silakan masuk menggunakan akun Google Anda.</>
                : 'Anda harus login terlebih dahulu untuk mengakses fitur ini. Silakan masuk menggunakan akun Google atau email Anda.'
              }
            </p>

            <div className="flex flex-col gap-3">
              <button
                onClick={() => setShowLoginModal(true)}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 font-bold text-xs tracking-wider uppercase transition-all shadow-lg shadow-cyan-500/20 cursor-pointer flex items-center justify-center gap-2"
              >
                <LogIn className="w-4 h-4" />
                <span>Login ke IHSG Pro</span>
              </button>

              {onNavigateHome && (
                <button
                  onClick={onNavigateHome}
                  className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs transition-colors flex items-center justify-center gap-2 cursor-pointer border border-slate-700"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Kembali ke Dashboard</span>
                </button>
              )}
            </div>
          </div>
        </div>

        <AuthModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
      </>
    );
  }

  // 2. Role Check: If user is trying to access admin route but is not admin
  if (requiredRole === 'admin' && role !== 'admin') {
    return (
      <div className="py-20 px-4 max-w-lg mx-auto text-center">
        <div className="glass-panel p-8 rounded-3xl border border-rose-500/30 bg-slate-900/95 shadow-2xl relative overflow-hidden">
          <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-rose-500 to-red-600" />
          
          <div className="w-16 h-16 rounded-2xl bg-rose-500/15 border border-rose-500/30 flex items-center justify-center mx-auto mb-4 text-rose-400 shadow-lg shadow-rose-950/30">
            <ShieldAlert className="w-8 h-8" />
          </div>

          <h2 className="text-2xl font-black text-rose-400 tracking-tight mb-2 uppercase">
            Access Denied
          </h2>

          <p className="text-xs text-slate-300 mb-4 leading-relaxed font-medium">
            Anda tidak memiliki izin untuk membuka halaman administrator ini. Halaman <code className="bg-slate-950 px-1.5 py-0.5 rounded text-rose-300 font-mono">/admin/*</code> hanya dapat diakses oleh akun dengan role <strong>ADMIN</strong>.
          </p>

          <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800 text-xs text-slate-400 mb-6 flex flex-col gap-1 text-left font-mono">
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Akun Terhubung:</span>
              <span className="text-slate-200 truncate max-w-[200px]">{user.email}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Role Anda:</span>
              <span className="font-bold text-cyan-400 uppercase">{role}</span>
            </div>
          </div>

          <button
            onClick={() => {
              if (onNavigateHome) {
                onNavigateHome();
              } else {
                window.history.replaceState(null, '', '/dashboard');
                window.dispatchEvent(new PopStateEvent('popstate'));
              }
            }}
            className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs transition-colors flex items-center justify-center gap-2 cursor-pointer border border-slate-700"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Kembali ke Dashboard (/dashboard)</span>
          </button>
        </div>
      </div>
    );
  }

  // Authorized
  return <>{children}</>;
};
