import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import {
  X,
  AlertCircle,
  CheckCircle2,
  Eye,
  EyeOff,
  Lock,
  Mail,
  ArrowLeft,
  KeyRound
} from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type AuthMode = 'login' | 'forgot_password' | 'verify_code';

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { loginWithGoogle, loginWithEmail } = useAuth();

  // Modal View Modes
  const [mode, setMode] = useState<AuthMode>('login');

  // Form Fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Forgot Password / Verification Fields
  const [resetEmail, setResetEmail] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);


  // Status & Feedback
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const resetAllStates = () => {
    setError(null);
    setSuccessMsg(null);
    setIsSubmitting(false);
  };

  const handleClose = () => {
    resetAllStates();
    setMode('login');
    onClose();
  };

  // 1. Handle Login with Email & Password
  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setError('Harap masukkan alamat email dan password.');
      return;
    }

    resetAllStates();
    setIsSubmitting(true);
    try {
      await loginWithEmail(email, password);
      handleClose();
    } catch (err: any) {
      console.error('Email login error:', err);
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        'Gagal masuk. Periksa kembali email dan password Anda.';
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 2. Handle Login with Google OAuth
  const handleGoogleLogin = async () => {
    resetAllStates();
    setIsSubmitting(true);
    try {
      await loginWithGoogle();
      // Browser will redirect to Google account selection
    } catch (err: any) {
      console.error('Google OAuth error:', err);
      setError(err?.message || 'Gagal memulai login dengan Google. Pastikan koneksi internet aktif.');
      setIsSubmitting(false);
    }
  };

  // 3. Handle Request Password Reset Code
  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resetEmail.trim()) {
      setError('Harap masukkan alamat Gmail/Email Anda.');
      return;
    }

    resetAllStates();
    setIsSubmitting(true);
    try {
      const res = await api.requestPasswordReset(resetEmail.trim());
      setVerificationCode(''); // User harus input manual dari email
      setSuccessMsg(res.email_sent
        ? `Kode verifikasi 6-digit telah dikirim ke ${resetEmail}. Periksa inbox dan folder spam Anda.`
        : `Kode verifikasi telah disiapkan untuk ${resetEmail}. Periksa email Anda atau hubungi admin.`
      );
      setMode('verify_code');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Email tidak ditemukan. Pastikan email terdaftar.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 4. Handle Verify Reset Code and Set New Password
  const handleVerifyAndReset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!verificationCode.trim()) {
      setError('Harap masukkan kode verifikasi 6-digit.');
      return;
    }
    if (newPassword.length < 6) {
      setError('Password baru minimal harus 6 karakter.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Konfirmasi password tidak cocok.');
      return;
    }

    resetAllStates();
    setIsSubmitting(true);
    try {
      const res = await api.verifyPasswordReset(resetEmail.trim(), verificationCode.trim(), newPassword);
      setSuccessMsg(res.message || 'Password berhasil diperbarui! Silakan masuk dengan password baru.');
      setEmail(resetEmail);
      setPassword(newPassword);
      setMode('login');
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Kode verifikasi salah atau kedaluwarsa.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-[#0b1329] border border-slate-800 rounded-3xl w-full max-w-md overflow-hidden shadow-2xl shadow-cyan-950/40 relative">
        
        {/* Top Gradient Accent Ribbon */}
        <div className="h-1.5 w-full bg-gradient-to-r from-blue-500 via-red-500 to-amber-500" />

        {/* Close Button */}
        <button
          onClick={handleClose}
          aria-label="Tutup"
          className="absolute top-4 right-4 p-1.5 text-slate-400 hover:text-slate-200 rounded-xl hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="p-6 sm:p-8">

          {/* ========================================================================= */}
          {/* VIEW 1: NORMAL SIGN IN (Email & Password + Google OAuth)                   */}
          {/* ========================================================================= */}
          {mode === 'login' && (
            <>
              {/* Header */}
              <div className="text-center mb-6">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/10 via-red-500/10 to-amber-500/10 border border-slate-700/60 flex items-center justify-center mx-auto mb-3 shadow-lg">
                  <svg className="w-7 h-7" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z" />
                    <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z" />
                    <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z" />
                    <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-black text-slate-100 tracking-tight">
                  Masuk ke IHSG Pro
                </h2>
                <p className="text-xs text-slate-400 mt-1 font-medium">
                  Gunakan email Google atau akun Google OAuth Anda
                </p>
              </div>

              {/* Feedback Alerts */}
              {error && (
                <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-2.5 text-xs text-rose-300 animate-in fade-in">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <span className="leading-snug">{error}</span>
                </div>
              )}

              {successMsg && (
                <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-2.5 text-xs text-emerald-300 animate-in fade-in">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span className="leading-snug">{successMsg}</span>
                </div>
              )}

              {/* Email & Password Form (GitHub Style) */}
              <form onSubmit={handleEmailLogin} className="space-y-4">
                {/* Email Input */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Alamat Email / Gmail
                  </label>
                  <div className="relative flex items-center">
                    <Mail className="absolute left-3 w-4 h-4 text-slate-500 pointer-events-none" />
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="nama@gmail.com"
                      className="w-full bg-[#111827] text-slate-100 placeholder-slate-500 text-xs pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-800 focus:outline-none focus:border-[#22C7F0] focus:ring-1 focus:ring-[#22C7F0] transition-all font-mono"
                    />
                  </div>
                </div>

                {/* Password Input with Forgot Password Link */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-semibold text-slate-300">
                      Password
                    </label>
                    <button
                      type="button"
                      onClick={() => {
                        resetAllStates();
                        setResetEmail(email);
                        setMode('forgot_password');
                      }}
                      className="text-[11px] font-medium text-[#22C7F0] hover:text-cyan-300 transition-colors cursor-pointer"
                    >
                      Lupa password?
                    </button>
                  </div>
                  <div className="relative flex items-center">
                    <Lock className="absolute left-3 w-4 h-4 text-slate-500 pointer-events-none" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full bg-[#111827] text-slate-100 placeholder-slate-500 text-xs pl-9 pr-10 py-2.5 rounded-xl border border-slate-800 focus:outline-none focus:border-[#22C7F0] focus:ring-1 focus:ring-[#22C7F0] transition-all font-mono"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 text-slate-500 hover:text-slate-300 cursor-pointer"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Quick Fill Sample Helper Buttons */}
                <div className="pt-0.5 flex flex-wrap items-center gap-1.5 text-[10px] text-slate-400">
                  <span className="text-slate-500">Contoh:</span>
                  <button
                    type="button"
                    onClick={() => {
                      setEmail('rizkyazhariputra2022@gmail.com');
                      setPassword('Password123!');
                    }}
                    className="px-2 py-0.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors font-mono cursor-pointer"
                  >
                    Admin 2022
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setEmail('rizkyazhariputra336@gmail.com');
                      setPassword('Password123!');
                    }}
                    className="px-2 py-0.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors font-mono cursor-pointer"
                  >
                    Admin 336
                  </button>
                </div>

                {/* Submit Sign In Button (GitHub-Style Prominent) */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-[#22C7F0] to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-extrabold text-xs tracking-wide shadow-lg shadow-cyan-500/20 active:scale-[0.99] transition-all cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <span>Masuk</span>
                  )}
                </button>
              </form>

              {/* Divider (or / atau) */}
              <div className="relative my-5">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-800" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-3 bg-[#0b1329] text-slate-500 font-medium">atau</span>
                </div>
              </div>

              {/* Continue with Google Button */}
              <button
                type="button"
                disabled={isSubmitting}
                onClick={handleGoogleLogin}
                className="w-full py-3 px-4 rounded-xl bg-white hover:bg-slate-100 text-slate-900 font-bold text-xs shadow-md active:scale-[0.99] transition-all flex items-center justify-center gap-2.5 cursor-pointer border border-slate-200 disabled:opacity-50"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z" />
                  <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z" />
                  <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z" />
                  <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z" />
                </svg>
                <span>Login dengan Google</span>
              </button>
            </>
          )}

          {/* ========================================================================= */}
          {/* VIEW 2: FORGOT PASSWORD (Enter Registered Gmail)                           */}
          {/* ========================================================================= */}
          {mode === 'forgot_password' && (
            <div>
              <button
                type="button"
                onClick={() => {
                  resetAllStates();
                  setMode('login');
                }}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-[#22C7F0] transition-colors mb-4 cursor-pointer"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Kembali ke Login</span>
              </button>

              <div className="text-center mb-6">
                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto mb-3 text-[#22C7F0]">
                  <KeyRound className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-white tracking-tight">
                  Lupa Password Akun
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Masukkan Gmail Anda untuk menerima verifikasi reset kata sandi
                </p>
              </div>

              {error && (
                <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-2.5 text-xs text-rose-300">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleRequestReset} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Alamat Gmail / Email Terdaftar
                  </label>
                  <div className="relative flex items-center">
                    <Mail className="absolute left-3 w-4 h-4 text-slate-500 pointer-events-none" />
                    <input
                      type="email"
                      required
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      placeholder="nama@gmail.com"
                      className="w-full bg-[#111827] text-slate-100 placeholder-slate-500 text-xs pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-800 focus:outline-none focus:border-[#22C7F0] font-mono"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-2.5 px-4 rounded-xl bg-[#22C7F0] hover:bg-cyan-400 text-slate-950 font-bold text-xs tracking-wide shadow-md transition-all cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <span>Kirim Kode Verifikasi</span>
                  )}
                </button>
              </form>
            </div>
          )}

          {/* ========================================================================= */}
          {/* VIEW 3: VERIFY CODE & SET NEW PASSWORD (Example: 123456)                   */}
          {/* ========================================================================= */}
          {mode === 'verify_code' && (
            <div>
              <button
                type="button"
                onClick={() => {
                  resetAllStates();
                  setMode('forgot_password');
                }}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-[#22C7F0] transition-colors mb-4 cursor-pointer"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Ganti Email</span>
              </button>

              <div className="text-center mb-5">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mx-auto mb-3 text-emerald-400">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-white tracking-tight">
                  Verifikasi & Set Password
                </h3>
                <p className="text-xs text-slate-400 mt-1 font-mono">
                  Untuk: {resetEmail}
                </p>
              </div>

              {/* Email Info Banner */}
              <div className="mb-4 p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-xs text-indigo-300">
                <div className="flex items-center gap-2 mb-1">
                  <Mail className="w-4 h-4 text-indigo-400 shrink-0" />
                  <span className="font-semibold text-slate-200">Periksa Email Anda</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
                  Kode verifikasi 6-digit telah dikirim ke <strong className="text-cyan-400 font-mono">{resetEmail}</strong>. Periksa folder <strong>Inbox</strong> dan <strong>Spam</strong> Anda. Kode berlaku selama 15 menit.
                </p>
              </div>

              {error && (
                <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-2.5 text-xs text-rose-300">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleVerifyAndReset} className="space-y-3.5">
                {/* 6-Digit Code */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Kode Verifikasi (6-Digit)
                  </label>
                  <input
                    type="text"
                    required
                    maxLength={6}
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                    placeholder="123456"
                    className="w-full bg-[#111827] text-center text-slate-100 placeholder-slate-500 text-sm py-2.5 rounded-xl border border-slate-800 focus:outline-none focus:border-[#22C7F0] font-mono tracking-widest font-bold"
                  />
                </div>

                {/* New Password */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Password Baru
                  </label>
                  <div className="relative flex items-center">
                    <Lock className="absolute left-3 w-4 h-4 text-slate-500 pointer-events-none" />
                    <input
                      type={showNewPassword ? 'text' : 'password'}
                      required
                      minLength={6}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Minimal 6 karakter"
                      className="w-full bg-[#111827] text-slate-100 placeholder-slate-500 text-xs pl-9 pr-10 py-2 rounded-xl border border-slate-800 focus:outline-none focus:border-[#22C7F0] font-mono"
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="absolute right-3 text-slate-500 hover:text-slate-300 cursor-pointer"
                    >
                      {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Confirm New Password */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Ulangi Password Baru
                  </label>
                  <div className="relative flex items-center">
                    <Lock className="absolute left-3 w-4 h-4 text-slate-500 pointer-events-none" />
                    <input
                      type={showNewPassword ? 'text' : 'password'}
                      required
                      minLength={6}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Ulangi password baru"
                      className="w-full bg-[#111827] text-slate-100 placeholder-slate-500 text-xs pl-9 pr-3.5 py-2 rounded-xl border border-slate-800 focus:outline-none focus:border-[#22C7F0] font-mono"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-2.5 px-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs tracking-wide shadow-md transition-all cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
                >
                  {isSubmitting ? (
                    <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <span>Verifikasi & Setel Password</span>
                  )}
                </button>
              </form>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

