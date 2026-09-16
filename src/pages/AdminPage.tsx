import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import {
  ShieldCheck,
  Users,
  Activity,
  FileText,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  RefreshCw,
  ArrowLeft,
  User,
  Search,
  UserCheck,
  Clock,
  Lock
} from 'lucide-react';

const MASTER_ADMIN_EMAILS = [
  'rizkyazhariputra2022@gmail.com',
  'rizkyazhariputra336@gmail.com'
];

export const AdminPage: React.FC = () => {
  const { user, role } = useAuth();
  const [activeTab, setActiveTab] = useState<'users' | 'activities' | 'reports'>('users');

  // Admin Data States
  const [users, setUsers] = useState<any[]>([]);
  const [activities, setActivities] = useState<any[]>([]);
  const [adminReports, setAdminReports] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Search & Filter States
  const [userSearch, setUserSearch] = useState<string>('');
  const [roleFilter, setRoleFilter] = useState<'ALL' | 'ADMIN' | 'USER'>('ALL');

  // Load data based on tab
  const loadAdminData = async () => {
    setIsLoading(true);
    setFeedbackMsg(null);
    try {
      if (activeTab === 'users') {
        const data = await api.getAdminUsers();
        setUsers(data.users || []);
      } else if (activeTab === 'activities') {
        const data = await api.getAdminActivities(100);
        setActivities(data.activities || []);
      } else if (activeTab === 'reports') {
        const data = await api.getAdminReports();
        setAdminReports(data.reports || []);
      }
    } catch (err: any) {
      console.error('Error loading admin data:', err);
      setFeedbackMsg({
        type: 'error',
        text: err?.response?.data?.detail || 'Gagal memuat data panel administrator.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (role === 'admin') {
      loadAdminData();
    }
  }, [activeTab, role]);

  // Handle Role Change
  const handleToggleRole = async (userId: string, currentRole: string) => {
    const targetUser = users.find(u => u.id === userId);
    if (targetUser && MASTER_ADMIN_EMAILS.includes((targetUser.email || '').toLowerCase().trim())) {
      alert('Akun Master Administrator ini berstatus permanen dan tidak dapat diubah menjadi USER.');
      return;
    }

    const newRole = currentRole === 'admin' ? 'user' : 'admin';
    if (!window.confirm(`Ubah peran pengguna ini menjadi ${newRole.toUpperCase()}?`)) return;

    try {
      await api.updateUserRole(userId, newRole);
      setFeedbackMsg({ type: 'success', text: `Peran berhasil diubah menjadi ${newRole.toUpperCase()}.` });
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: err?.response?.data?.detail || 'Gagal mengubah role.' });
    }
  };

  // Handle Delete User
  const handleDeleteUser = async (userId: string, email: string) => {
    if (MASTER_ADMIN_EMAILS.includes((email || '').toLowerCase().trim())) {
      alert('Akun Master Administrator berstatus permanen dan tidak dapat dihapus.');
      return;
    }

    if (!window.confirm(`Hapus pengguna ${email}? Tindakan ini permanen.`)) return;

    try {
      await api.deleteUser(userId);
      setFeedbackMsg({ type: 'success', text: `Pengguna ${email} berhasil dihapus.` });
      setUsers((prev) => prev.filter((u) => u.id !== userId));
    } catch (err: any) {
      setFeedbackMsg({ type: 'error', text: err?.response?.data?.detail || 'Gagal menghapus user.' });
    }
  };

  // Filtered Users
  const filteredUsers = useMemo(() => {
    return users.filter((u) => {
      const matchesSearch =
        (u.full_name || '').toLowerCase().includes(userSearch.toLowerCase()) ||
        (u.email || '').toLowerCase().includes(userSearch.toLowerCase());
      const matchesRole =
        roleFilter === 'ALL' || (u.role || '').toUpperCase() === roleFilter;
      return matchesSearch && matchesRole;
    });
  }, [users, userSearch, roleFilter]);

  // Metric stats
  const totalAdmins = users.filter((u) => (u.role || '').toLowerCase() === 'admin').length;
  const totalUsers = users.filter((u) => (u.role || '').toLowerCase() === 'user').length;

  // Role Guard View: If non-admin attempts to view /admin/dashboard
  if (role !== 'admin') {
    return (
      <div className="py-20 px-4 max-w-lg mx-auto text-center">
        <div className="p-8 rounded-3xl border border-rose-500/30 bg-[#111827]/95 shadow-2xl relative overflow-hidden">
          <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-rose-500 to-red-600" />
          <div className="w-16 h-16 rounded-2xl bg-rose-500/15 border border-rose-500/30 flex items-center justify-center mx-auto mb-4 text-rose-400">
            <ShieldAlert className="w-8 h-8" />
          </div>

          <h2 className="text-2xl font-black text-rose-400 tracking-tight mb-2 uppercase">
            Access Denied
          </h2>

          <p className="text-xs text-slate-300 mb-5 leading-relaxed font-medium">
            Anda tidak memiliki izin untuk mengakses halaman administrator ini. Halaman <code className="bg-[#060B18] px-1.5 py-0.5 rounded text-rose-300 font-mono">/admin/*</code> dilindungi dan hanya dapat dibuka oleh role <strong>ADMIN</strong>.
          </p>

          <div className="p-3.5 rounded-xl bg-[#060B18] border border-slate-800 text-xs text-slate-400 mb-6 flex flex-col gap-1 text-left font-mono">
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Akun Anda:</span>
              <span className="text-slate-200 truncate max-w-[200px]">{user?.email || 'Guest'}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Role Anda:</span>
              <span className="font-bold text-[#22C7F0] uppercase">{role || 'GUEST'}</span>
            </div>
          </div>

          <button
            onClick={() => {
              window.history.replaceState(null, '', '/dashboard');
              window.dispatchEvent(new PopStateEvent('popstate'));
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

  return (
    <div className="flex flex-col gap-5 max-w-7xl mx-auto w-full px-3 sm:px-6 py-4 sm:py-6">
      
      {/* Header Banner */}
      <div className="p-4 sm:p-5 rounded-2xl bg-[#111827]/90 border border-indigo-500/30 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4 backdrop-blur-xl">
        <div className="flex items-start sm:items-center gap-3.5">
          <div className="p-2.5 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-400 shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                Panel Administrator
              </h1>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
                ROLE: ADMIN
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Pusat manajemen hak akses pengguna Google, audit trail aktivitas real-time, dan moderasi laporan.
            </p>
          </div>
        </div>

        <button
          onClick={loadAdminData}
          disabled={isLoading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#060B18] hover:bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold border border-slate-800 transition-all cursor-pointer shrink-0 self-end md:self-center disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-[#22C7F0]' : ''}`} />
          <span>Segarkan Data</span>
        </button>
      </div>

      {/* Feedback Alert */}
      {feedbackMsg && (
        <div
          className={`p-3.5 rounded-xl text-xs flex items-center gap-2.5 shadow-md ${
            feedbackMsg.type === 'success'
              ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
              : 'bg-rose-500/10 border border-rose-500/30 text-rose-300'
          }`}
        >
          {feedbackMsg.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
          ) : (
            <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
          )}
          <span className="font-medium">{feedbackMsg.text}</span>
        </div>
      )}

      {/* 4 Summary Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-2xl bg-[#111827]/80 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-[11px]">
            <span className="font-semibold uppercase tracking-wider">Total User</span>
            <Users className="w-4 h-4 text-[#22C7F0]" />
          </div>
          <div className="my-1">
            <span className="text-2xl font-black font-mono text-white">{users.length}</span>
            <span className="text-[11px] text-slate-400 ml-1.5">Akun Google</span>
          </div>
          <div className="text-[10px] text-slate-500 font-mono">
            {totalUsers} User • {totalAdmins} Admin
          </div>
        </div>

        <div className="p-3.5 rounded-2xl bg-[#111827]/80 border border-indigo-500/30 flex flex-col justify-between">
          <div className="flex items-center justify-between text-indigo-300 text-[11px]">
            <span className="font-semibold uppercase tracking-wider">Admin Aktif</span>
            <UserCheck className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="my-1">
            <span className="text-2xl font-black font-mono text-indigo-300">{totalAdmins}</span>
            <span className="text-[11px] text-slate-400 ml-1.5">Administrator</span>
          </div>
          <div className="text-[10px] text-indigo-400/80 font-mono">Role: admin</div>
        </div>

        <div className="p-3.5 rounded-2xl bg-[#111827]/80 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-[11px]">
            <span className="font-semibold uppercase tracking-wider">Audit Trail</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="my-1">
            <span className="text-2xl font-black font-mono text-white">{activities.length || '100+'}</span>
            <span className="text-[11px] text-slate-400 ml-1.5">Log Event</span>
          </div>
          <div className="text-[10px] text-slate-500 font-mono">Tabel: activity_logs</div>
        </div>

        <div className="p-3.5 rounded-2xl bg-[#111827]/80 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-[11px]">
            <span className="font-semibold uppercase tracking-wider">Laporan Saham</span>
            <FileText className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="my-1">
            <span className="text-2xl font-black font-mono text-white">{adminReports.length}</span>
            <span className="text-[11px] text-slate-400 ml-1.5">Riset Tersimpan</span>
          </div>
          <div className="text-[10px] text-slate-500 font-mono">Tabel: public.reports</div>
        </div>
      </div>

      {/* Admin Navigation Tabs */}
      <div className="flex items-center gap-1.5 p-1 rounded-2xl bg-[#111827] border border-slate-800 w-full sm:w-auto overflow-x-auto">
        <button
          onClick={() => setActiveTab('users')}
          className={`flex items-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'users'
              ? 'bg-[#22C7F0] text-slate-950 shadow-md shadow-cyan-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <Users className="w-3.5 h-3.5" />
          <span>Kelola Pengguna ({users.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('activities')}
          className={`flex items-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'activities'
              ? 'bg-[#22C7F0] text-slate-950 shadow-md shadow-cyan-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          <span>Log Audit Trail</span>
        </button>

        <button
          onClick={() => setActiveTab('reports')}
          className={`flex items-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'reports'
              ? 'bg-[#22C7F0] text-slate-950 shadow-md shadow-cyan-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Moderasi Laporan ({adminReports.length})</span>
        </button>
      </div>

      {/* TAB 1: KELOLA USER */}
      {activeTab === 'users' && (
        <div className="rounded-2xl border border-slate-800 bg-[#111827]/90 shadow-xl overflow-hidden flex flex-col">
          {/* Table Header & Search Filter */}
          <div className="p-3.5 sm:p-4 border-b border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[#060B18]/60">
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-[#22C7F0]" />
              <h3 className="font-bold text-sm text-white">
                Daftar Akun Google Terdaftar ({filteredUsers.length} dari {users.length})
              </h3>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <div className="relative flex-1 sm:w-60">
                <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Cari nama / email..."
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  className="w-full bg-[#060B18] text-xs text-slate-100 placeholder-slate-500 pl-8 pr-3 py-1.5 rounded-xl border border-slate-800 focus:outline-none focus:border-[#22C7F0] font-mono"
                />
              </div>

              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value as any)}
                className="bg-[#060B18] text-xs text-slate-300 border border-slate-800 rounded-xl px-2.5 py-1.5 focus:outline-none font-mono cursor-pointer"
              >
                <option value="ALL">Semua Role</option>
                <option value="ADMIN">Admin</option>
                <option value="USER">User</option>
              </select>
            </div>
          </div>

          {isLoading ? (
            <div className="py-16 text-center text-slate-400 font-mono text-xs">
              <div className="inline-block h-6 w-6 border-2 border-[#22C7F0] border-t-transparent rounded-full animate-spin mb-2"></div>
              <p>Memuat profil pengguna dari database Supabase...</p>
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              Tidak ada profil pengguna yang sesuai kriteria pencarian.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#060B18] text-slate-400 uppercase font-mono text-[11px] border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Pengguna Google</th>
                    <th className="py-3 px-4">Email</th>
                    <th className="py-3 px-4 text-center">Peran (Role)</th>
                    <th className="py-3 px-4 text-center">Terdaftar</th>
                    <th className="py-3 px-4 text-right">Aksi Kelola</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300 font-sans">
                  {filteredUsers.map((u) => {
                    const isSelf = u.id === user?.id;
                    const uEmail = (u.email || '').toLowerCase().trim();
                    const isMasterAdmin = MASTER_ADMIN_EMAILS.includes(uEmail);
                    const uRole = (u.role || 'user').toLowerCase();
                    return (
                      <tr key={u.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3 px-4 font-medium text-white">
                          <div className="flex items-center gap-2.5">
                            {u.avatar_url ? (
                              <img
                                src={u.avatar_url}
                                alt={u.full_name}
                                referrerPolicy="no-referrer"
                                className="w-7 h-7 rounded-lg object-cover border border-slate-700 shrink-0"
                              />
                            ) : (
                              <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 font-bold text-[10px] shrink-0">
                                <User className="w-3.5 h-3.5" />
                              </div>
                            )}
                            <div className="flex items-center gap-1.5">
                              <span className="font-semibold">{u.full_name || '-'}</span>
                              {isSelf && (
                                <span className="text-[9px] bg-slate-800 text-[#22C7F0] px-1.5 py-0.2 rounded border border-slate-700 font-mono">
                                  Anda
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-300">{u.email}</td>
                        <td className="py-3 px-4 text-center">
                          {isMasterAdmin ? (
                            <span className="inline-flex items-center gap-1 font-mono text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border uppercase bg-indigo-500/25 text-indigo-300 border-indigo-500/50 shadow-sm">
                              <ShieldCheck className="w-3 h-3 text-indigo-400" />
                              MASTER ADMIN
                            </span>
                          ) : (
                            <span
                              className={`font-mono text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase ${
                                uRole === 'admin'
                                  ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
                                  : 'bg-cyan-500/15 text-[#22C7F0] border-cyan-500/30'
                              }`}
                            >
                              {uRole}
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center font-mono text-[11px] text-slate-400">
                          {u.created_at ? new Date(u.created_at).toLocaleDateString('id-ID') : '-'}
                        </td>
                        <td className="py-3 px-4 text-right font-sans">
                          {isMasterAdmin ? (
                            <div className="flex items-center justify-end">
                              <span className="inline-flex items-center gap-1.5 py-1 px-3 rounded-lg bg-indigo-950/60 text-indigo-300 border border-indigo-800/50 text-[11px] font-mono font-medium">
                                <Lock className="w-3 h-3 text-indigo-400" />
                                Admin Utama (Permanen)
                              </span>
                            </div>
                          ) : (
                            <div className="flex items-center justify-end gap-2">
                              <button
                                onClick={() => handleToggleRole(u.id, uRole)}
                                disabled={isSelf}
                                title={isSelf ? 'Tidak dapat mengubah peran sendiri' : `Ubah role ke ${uRole === 'admin' ? 'USER' : 'ADMIN'}`}
                                className={`py-1 px-3 rounded-lg text-xs font-bold transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer border ${
                                  uRole === 'user'
                                    ? 'bg-gradient-to-r from-indigo-600/30 to-blue-600/30 hover:from-indigo-600 hover:to-blue-600 text-indigo-200 hover:text-white border-indigo-500/50 shadow-sm'
                                    : 'bg-slate-800 hover:bg-amber-600/30 text-slate-300 hover:text-amber-300 border-slate-700 hover:border-amber-500/50'
                                }`}
                              >
                                {uRole === 'user' ? '+ Jadikan ADMIN' : 'Jadikan USER'}
                              </button>

                              <button
                                onClick={() => handleDeleteUser(u.id, u.email)}
                                disabled={isSelf}
                                title={isSelf ? 'Tidak dapat menghapus akun sendiri' : 'Hapus Pengguna'}
                                className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: MELIHAT AKTIVITAS AUDIT TRAIL */}
      {activeTab === 'activities' && (
        <div className="rounded-2xl border border-slate-800 bg-[#111827]/90 shadow-xl overflow-hidden flex flex-col">
          <div className="p-3.5 sm:p-4 border-b border-slate-800/80 flex items-center justify-between bg-[#060B18]/60">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-[#22C7F0]" />
              <h3 className="font-bold text-sm text-white">
                Log Audit Trail Aktivitas Sistem ({activities.length} Event)
              </h3>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">Tabel: public.activity_logs</span>
          </div>

          {isLoading ? (
            <div className="py-16 text-center text-slate-400 font-mono text-xs">
              <div className="inline-block h-6 w-6 border-2 border-[#22C7F0] border-t-transparent rounded-full animate-spin mb-2"></div>
              <p>Memuat rekaman log aktivitas...</p>
            </div>
          ) : activities.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              Belum ada log aktivitas tercatat.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#060B18] text-slate-400 uppercase font-mono text-[11px] border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Waktu (WIB)</th>
                    <th className="py-3 px-4">Pengguna</th>
                    <th className="py-3 px-4 text-center">Role</th>
                    <th className="py-3 px-4">Aksi Event</th>
                    <th className="py-3 px-4">Detail</th>
                    <th className="py-3 px-4 text-right">IP Address</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono text-[11px] text-slate-300">
                  {activities.map((act) => (
                    <tr key={act.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 text-slate-400 whitespace-nowrap flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        <span>{act.created_at ? new Date(act.created_at).toLocaleString('id-ID') : '-'}</span>
                      </td>
                      <td className="py-3 px-4 text-white font-medium">
                        {act.user_email}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span
                          className={`text-[9px] px-1.5 py-0.2 rounded font-bold uppercase ${
                            String(act.role).toLowerCase() === 'admin'
                              ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                              : 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/25'
                          }`}
                        >
                          {act.role}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-bold text-[#22C7F0]">
                        <span className="bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                          {act.action}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400 max-w-xs truncate font-sans">
                        {typeof act.details === 'object' ? JSON.stringify(act.details) : String(act.details || '-')}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-500">
                        {act.ip_address || '127.0.0.1'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: MELIHAT SEMUA LAPORAN */}
      {activeTab === 'reports' && (
        <div className="rounded-2xl border border-slate-800 bg-[#111827]/90 shadow-xl overflow-hidden flex flex-col">
          <div className="p-3.5 sm:p-4 border-b border-slate-800/80 flex items-center justify-between bg-[#060B18]/60">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#22C7F0]" />
              <h3 className="font-bold text-sm text-white">
                Seluruh Laporan Riset Saham Pengguna ({adminReports.length})
              </h3>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">Tabel: public.reports</span>
          </div>

          {isLoading ? (
            <div className="py-16 text-center text-slate-400 font-mono text-xs">
              <div className="inline-block h-6 w-6 border-2 border-[#22C7F0] border-t-transparent rounded-full animate-spin mb-2"></div>
              <p>Memuat data laporan dari seluruh pengguna...</p>
            </div>
          ) : adminReports.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              Belum ada laporan riset tersimpan.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#060B18] text-slate-400 uppercase font-mono text-[11px] border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Tanggal</th>
                    <th className="py-3 px-4">Penulis</th>
                    <th className="py-3 px-4 font-mono">Ticker</th>
                    <th className="py-3 px-4">Judul Laporan</th>
                    <th className="py-3 px-4 text-center">Rekomendasi</th>
                    <th className="py-3 px-4 text-right">Target Price</th>
                    <th className="py-3 px-4 text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {adminReports.map((rep) => (
                    <tr key={rep.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                        {rep.created_at ? new Date(rep.created_at).toLocaleDateString('id-ID') : '-'}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-medium text-white">{rep.author_name}</div>
                        <div className="text-[10px] font-mono text-slate-500">{rep.author_email}</div>
                      </td>
                      <td className="py-3 px-4 font-mono font-bold text-[#22C7F0]">{rep.symbol}</td>
                      <td className="py-3 px-4 max-w-sm truncate text-slate-200">{rep.title}</td>
                      <td className="py-3 px-4 text-center">
                        <span className="font-bold text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                          {rep.recommendation || 'BUY'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right font-mono text-white">
                        {rep.target_price ? `Rp ${rep.target_price.toLocaleString('id-ID')}` : '-'}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={async () => {
                            if (!window.confirm(`Hapus laporan "${rep.title}"?`)) return;
                            await api.deleteReport(rep.id);
                            setAdminReports((prev) => prev.filter((r) => r.id !== rep.id));
                          }}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors cursor-pointer"
                          title="Hapus Laporan Sebagai Admin"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

    </div>
  );
};
