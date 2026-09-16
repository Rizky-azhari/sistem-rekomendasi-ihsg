import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { FileText, Plus, Search, Trash2, Calendar, User, Target, ShieldAlert, Sparkles, X } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const { user, role } = useAuth();
  const [reports, setReports] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedSymbolFilter, setSelectedSymbolFilter] = useState<string>('ALL');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [formSymbol, setFormSymbol] = useState<string>('BBCA.JK');
  const [formTitle, setFormTitle] = useState<string>('');
  const [formRecommendation, setFormRecommendation] = useState<string>('BUY');
  const [formTargetPrice, setFormTargetPrice] = useState<string>('10500');
  const [formStopLoss, setFormStopLoss] = useState<string>('9750');
  const [formContent, setFormContent] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const fetchReports = async () => {
    setIsLoading(true);
    try {
      const data = await api.getReports();
      setReports(data.reports || []);
    } catch (err) {
      console.error('Error fetching reports:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleCreateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    setIsSubmitting(true);
    try {
      await api.createReport({
        title: formTitle,
        symbol: formSymbol,
        recommendation: formRecommendation,
        target_price: formTargetPrice ? parseFloat(formTargetPrice) : undefined,
        stop_loss: formStopLoss ? parseFloat(formStopLoss) : undefined,
        content: formContent,
        report_type: 'TECHNICAL_ANALYSIS',
        is_public: true
      });
      setIsModalOpen(false);
      // Reset form
      setFormTitle('');
      setFormContent('');
      await fetchReports();
    } catch (err: any) {
      setSubmitError(err?.response?.data?.detail || err?.message || 'Gagal menyimpan laporan.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteReport = async (reportId: string) => {
    if (!window.confirm('Apakah Anda yakin ingin menghapus laporan ini?')) return;
    try {
      await api.deleteReport(reportId);
      setReports((prev) => prev.filter((r) => r.id !== reportId));
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Gagal menghapus laporan.');
    }
  };

  const handleAutoFillIndicator = async () => {
    try {
      const [techRes, recRes] = await Promise.allSettled([
        api.getTechnicalAnalysis(formSymbol),
        api.getRecommendation(formSymbol)
      ]);

      let notes = `Laporan Analisis Otomatis untuk ${formSymbol}:\n`;
      if (techRes.status === 'fulfilled' && techRes.value) {
        const t = techRes.value;
        notes += `- Harga Terakhir: Rp ${t.price?.toLocaleString('id-ID') || '-'}\n`;
        notes += `- MA20: Rp ${t.MA20?.toLocaleString('id-ID') || '-'}\n`;
        notes += `- MA50: Rp ${t.MA50?.toLocaleString('id-ID') || '-'}\n`;
        notes += `- MA200: Rp ${t.MA200?.toLocaleString('id-ID') || '-'}\n`;
        notes += `- RSI (14): ${t.RSI?.toFixed(2) || '-'}\n`;
        notes += `- Trend: ${t.trend || 'NEUTRAL'}\n`;
      }

      if (recRes.status === 'fulfilled' && recRes.value) {
        const r = recRes.value as any;
        const signal = r.signal || r.recommendation || 'BUY';
        setFormRecommendation(signal);
        const reasonsList = r.rule_breakdowns?.map((b: any) => `• ${b.rule_name}: ${b.description}`) || r.reasons?.map((x: string) => `• ${x}`) || ['Sinyal terkonfirmasi.'];
        notes += `\nAlasan Rekomendasi (${signal}):\n${reasonsList.join('\n')}`;
      }

      setFormTitle(`Analisis Teknikal & Rekomendasi ${formSymbol}`);
      setFormContent(notes);
    } catch (err) {
      console.warn('Auto fill notice:', err);
    }
  };

  const filteredReports = reports.filter((r) => {
    const matchQuery =
      r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.author_name && r.author_name.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchSymbol = selectedSymbolFilter === 'ALL' || r.symbol === selectedSymbolFilter;
    return matchQuery && matchSymbol;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800/80 bg-gradient-to-br from-slate-900 via-slate-950 to-indigo-950/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <FileText className="w-5 h-5" />
            </div>
            <h1 className="text-2xl font-black text-slate-100 tracking-tight">
              Laporan Analisis Saham
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            Daftar riset, jurnal trading, dan laporan teknikal emiten IDX dari seluruh pengguna dan analis.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 font-bold text-xs tracking-wider uppercase transition-all shadow-lg shadow-cyan-500/20 cursor-pointer shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Buat Laporan Baru</span>
        </button>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Cari judul laporan, ticker saham, atau nama analis..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 whitespace-nowrap">Filter Saham:</span>
          <select
            value={selectedSymbolFilter}
            onChange={(e) => setSelectedSymbolFilter(e.target.value)}
            className="px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">Semua Saham</option>
            <option value="BBCA.JK">BBCA.JK</option>
            <option value="BBRI.JK">BBRI.JK</option>
            <option value="BMRI.JK">BMRI.JK</option>
            <option value="BBNI.JK">BBNI.JK</option>
            <option value="TLKM.JK">TLKM.JK</option>
            <option value="ASII.JK">ASII.JK</option>
          </select>
        </div>
      </div>

      {/* Report Grid */}
      {isLoading ? (
        <div className="py-16 text-center text-slate-500 font-mono text-xs">
          Memuat data laporan saham...
        </div>
      ) : filteredReports.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800/80 bg-slate-900/40">
          <FileText className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-300 font-bold text-sm">Belum Ada Laporan Dibuat</p>
          <p className="text-xs text-slate-500 mt-1 mb-4">
            Jadilah yang pertama membuat laporan analisis teknikal saham IDX.
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="py-2 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold border border-slate-700 transition-colors cursor-pointer"
          >
            + Buat Laporan Sekarang
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredReports.map((report) => {
            const isOwner = user?.id === report.user_id;
            const isAdmin = role === 'admin';
            const canDelete = isOwner || isAdmin;

            return (
              <div
                key={report.id}
                className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-slate-700 bg-slate-900/60 backdrop-blur-xl flex flex-col justify-between transition-all group"
              >
                <div>
                  {/* Top Bar: Symbol & Recommendation */}
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className="font-mono font-bold text-xs px-2.5 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      {report.symbol}
                    </span>

                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        report.recommendation === 'STRONG BUY' || report.recommendation === 'BUY'
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                          : report.recommendation === 'SELL'
                          ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                          : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                      }`}
                    >
                      {report.recommendation || 'BUY'}
                    </span>
                  </div>

                  {/* Title */}
                  <h3 className="font-bold text-sm text-slate-100 group-hover:text-cyan-400 transition-colors line-clamp-2 mb-2">
                    {report.title}
                  </h3>

                  {/* Targets */}
                  {(report.target_price || report.stop_loss) && (
                    <div className="grid grid-cols-2 gap-2 my-2.5 p-2 rounded-xl bg-slate-950/70 border border-slate-800 text-[11px] font-mono">
                      {report.target_price && (
                        <div className="flex items-center gap-1.5 text-emerald-400">
                          <Target className="w-3 h-3 shrink-0" />
                          <span>TP: <strong>{report.target_price.toLocaleString('id-ID')}</strong></span>
                        </div>
                      )}
                      {report.stop_loss && (
                        <div className="flex items-center gap-1.5 text-rose-400">
                          <ShieldAlert className="w-3 h-3 shrink-0" />
                          <span>SL: <strong>{report.stop_loss.toLocaleString('id-ID')}</strong></span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Content Preview */}
                  <p className="text-xs text-slate-400 whitespace-pre-line line-clamp-4 leading-relaxed mt-2">
                    {report.content}
                  </p>
                </div>

                {/* Footer: Author & Timestamp */}
                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <div className="flex items-center gap-1 truncate mr-2">
                    <User className="w-3 h-3 shrink-0 text-slate-400" />
                    <span className="truncate">{report.author_name || 'Trader'}</span>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      <span>{new Date(report.created_at).toLocaleDateString('id-ID')}</span>
                    </div>

                    {canDelete && (
                      <button
                        onClick={() => handleDeleteReport(report.id)}
                        title="Hapus Laporan"
                        className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal: Buat Laporan Baru */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl relative">
            <div className="h-1.5 w-full bg-gradient-to-r from-cyan-500 to-indigo-600" />

            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 p-1 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-100">Buat Laporan Analisis</h2>
                  <p className="text-xs text-slate-400">Publikasikan analisa teknikal atau strategi trading Anda</p>
                </div>
              </div>

              {submitError && (
                <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300">
                  {submitError}
                </div>
              )}

              <form onSubmit={handleCreateReport} className="space-y-3.5">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Ticker Saham</label>
                    <input
                      type="text"
                      required
                      value={formSymbol}
                      onChange={(e) => setFormSymbol(e.target.value.toUpperCase())}
                      placeholder="BBCA.JK"
                      className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Rekomendasi</label>
                    <select
                      value={formRecommendation}
                      onChange={(e) => setFormRecommendation(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-cyan-500 font-semibold"
                    >
                      <option value="STRONG BUY">STRONG BUY</option>
                      <option value="BUY">BUY</option>
                      <option value="HOLD">HOLD</option>
                      <option value="SELL">SELL</option>
                    </select>
                  </div>
                </div>

                {/* Auto-fill Helper */}
                <button
                  type="button"
                  onClick={handleAutoFillIndicator}
                  className="w-full py-1.5 px-3 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  <span>Ambil Data Indikator Otomatis untuk {formSymbol}</span>
                </button>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Judul Laporan</label>
                  <input
                    type="text"
                    required
                    value={formTitle}
                    onChange={(e) => setFormTitle(e.target.value)}
                    placeholder="Contoh: BBCA Rebound dari MA20 Menuju Target 10,500"
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Target Price (TP)</label>
                    <input
                      type="number"
                      value={formTargetPrice}
                      onChange={(e) => setFormTargetPrice(e.target.value)}
                      placeholder="10500"
                      className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Stop Loss (SL)</label>
                    <input
                      type="number"
                      value={formStopLoss}
                      onChange={(e) => setFormStopLoss(e.target.value)}
                      placeholder="9750"
                      className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Isi Laporan / Analisis</label>
                  <textarea
                    rows={5}
                    required
                    value={formContent}
                    onChange={(e) => setFormContent(e.target.value)}
                    placeholder="Tuliskan ulasan analisis, katalis pasar, support & resistance..."
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 font-sans focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-slate-950 font-bold text-xs tracking-wider uppercase transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50 cursor-pointer"
                >
                  {isSubmitting ? 'Menyimpan...' : 'Simpan & Publikasikan Laporan'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
