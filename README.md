# 🇮🇩 IHSG TERMINAL PRO
### Smart Stock Recommendation & Decision Support System (IDX80 Index)

**IHSG Terminal Pro** adalah platform analitika kuantitatif pasar modal Indonesia berbasis *Decision Support System (DSS)* yang memindai dan menganalisis 80 saham paling likuid di **Bursa Efek Indonesia (BEI / IDX)** yang tergabung dalam indeks **IDX80**.

Platform ini menggabungkan **FastAPI (Python)**, **PostgreSQL (Supabase)**, **Google OAuth**, serta antarmuka modern **React (Vite) + Tailwind CSS + Recharts** dengan pendekatan *Mobile First* dan dukungan *Progressive Web App (PWA)*.

---

## 🌟 Fitur Utama

1. **IDX80 Constituent Stock Universe (80 Emiten Terlikuid)**:
   - Evaluasi eksklusif pada 80 saham berkapitalisasi pasar dan likuiditas transaksi tinggi di Bursa Efek Indonesia.
   - Format standar Yahoo Finance: `BBCA.JK`, `BBRI.JK`, `BMRI.JK`, `TLKM.JK`, `ASII.JK`, dll.
   - Dilengkapi *IDX80 Validation Layer* yang menolak emiten di luar whitelist demi efisiensi query dan mitigasi *rate limit*.

2. **5-Factor Quantitative Screener Engine**:
   - **Momentum Screener**: `Close > MA20` & `Volume > Volume Rata-rata 20 Hari`.
   - **Trend Screener**: `MA20 > MA50 > MA200` (Strong Bullish Alignment).
   - **Oversold Screener**: `RSI(14) < 35` & Harga mendekati Support area.
   - **Breakout Screener**: `Close > Highest High 20 Hari`.
   - **Trading Setup Screener**: Evaluasi rasio Risk-to-Reward $\ge 1:2$.

3. **Composite Recommendation Engine (DSS)**:
   $$\text{Final Score} = (\text{Trend} \times 25\%) + (\text{Momentum} \times 25\%) + (\text{Breakout} \times 20\%) + (\text{Oversold} \times 10\%) + (\text{Setup} \times 20\%)$$
   - **85 - 100**: `STRONG BUY`
   - **70 - 84**: `BUY`
   - **50 - 69**: `HOLD`
   - **25 - 49**: `SELL`
   - **< 25**: `STRONG SELL`
   - Dilengkapi narasi analisa teknikal otomatis berdasarkan indikator Moving Average, RSI, MACD, dan Bollinger Bands.

4. **Automated Trading Plan Generator**:
   - Menghasilkan rencana eksekusi trading otomatis:
     - **Buy Area** (rentang harga beli ideal berdasarkan support/SMA20)
     - **Stop Loss** (proteksi risiko berbasis Support & ATR 14)
     - **Take Profit 1 & 2** (target bertahap berdasarkan proyeksi swing high)
     - **Risk-Reward Ratio** (RR $\ge 1:2$)

5. **Sistem Autentikasi Google OAuth & Role-Based Access Control (RBAC)**:
   - Login instan satu klik menggunakan akun Google melalui Supabase Auth.
   - **Manajemen Role**: Pengguna pertama otomatis menjadi `ADMIN`, pengguna berikutnya otomatis `USER`.
   - Proteksi rute halaman `/admin/*` untuk pengawasan log aktivitas pengguna dan manajemen hak akses.

6. **Desain Mobile-First & Dark Trading Terminal**:
   - Palet warna terminal profesional: Background `#060B18`, Surface `#111827`, Primary Cyan `#22C7F0`.
   - Navigasi adaptif: **Top Navbar** di Desktop/Tablet, **Bottom Navigation Bar** di Mobile.
   - PWA (*Progressive Web App*) siap dipasang di layar utama Android dan iOS.

---

## 🏗️ Struktur Folder Proyek

```text
Sistem Rekomendasi IHSG/
├── api/                             # Entry point serverless Vercel (Mangum Python adapter)
│   └── index.py
├── backend/
│   ├── app/
│   │   ├── api/v1/                  # Controller & endpoints REST API (admin, auth, recommendations, reports, screening, stocks)
│   │   ├── config/                  # Konfigurasi aplikasi & master tickers whitelist IDX80
│   │   ├── core/                    # Konfigurasi env, keamanan JWT, dan validator IDX80
│   │   ├── database/                # Inisialisasi koneksi database Supabase & SQLAlchemy
│   │   ├── engine/                  # Mesin kalkulasi indikator teknikal & DSS rule evaluation
│   │   ├── middleware/              # Middleware otentikasi role-based access control
│   │   ├── models/                  # Skema ORM SQLAlchemy (Stock, StockPrice, Recommendation, dll.)
│   │   ├── schemas/                 # Skema validasi data request/response Pydantic
│   │   ├── screener/                # 5 strategi screener (trend, momentum, breakout, oversold, setup) & batch scanner
│   │   ├── services/                # Layanan Yahoo Finance, in-memory caching, email sender, technical analysis
│   │   ├── trading_plan/            # Generator Buy Area, Stop Loss, TP1-2, dan Risk-Reward Ratio
│   │   ├── universe/                # Pengelola konstituen IDX80 & sinkronisasi otomatis
│   │   └── validators/              # Gatekeeper validasi ticker IDX80
│   ├── migrations/                  # Script SQL skema tabel PostgreSQL Supabase
│   ├── tests/                       # Unit tests otomatis backend (FastAPI, cache, validator)
│   ├── main.py                      # Entry point server backend FastAPI lokal
│   ├── requirements.txt             # Dependensi Python backend
│   └── render.yaml                  # Konfigurasi deployment Render
├── src/                             # Source code frontend (React 19 + TypeScript + Vite)
│   ├── api/                         # HTTP Client Axios terpusat (seluruh endpoint sistem)
│   ├── assets/                      # Gambar, logo, dan aset statis
│   ├── components/
│   │   ├── common/                  # Komponen utilitas & dialog global (AuthModal, ProtectedRoute)
│   │   ├── layout/                  # Komponen navigasi (Navbar desktop/tablet, BottomNav mobile)
│   │   ├── chart/                   # Visualisasi grafik interaktif (CandlestickChart, StockChart)
│   │   ├── dashboard/               # Widget ringkasan IHSG & top performers
│   │   ├── recommendation/          # Kartu sinyal analisis DSS & Trading Plan
│   │   └── screener/                # Tabel screener saham IDX80 & panel filter
│   ├── constants/                   # Nilai konstan UI (timeframe, signal badge styles, defaults)
│   ├── context/                     # AuthContext (Google OAuth & sesi role pengguna)
│   ├── hooks/                       # Custom React hooks
│   ├── pages/                       # Halaman tampilan utama (Dashboard, Screener, Analysis, Admin, Reports)
│   ├── services/                    # Re-export client API dan Supabase JS client
│   ├── types/                       # TypeScript interfaces & type definitions
│   └── utils/                       # Helper murni (formatters Rupiah, styling sinyal)
├── public/                          # Static assets, PWA manifest, service worker
├── supabase/
│   └── migrations/                  # Skema migrasi Supabase PostgreSQL
├── _unused_review/                  # Arsip aman file tidak terpakai/duplikat untuk ditinjau
├── ARCHITECTURE.md                  # Dokumentasi teknis arsitektur, diagram modul, & alur data
├── package.json                     # Dependensi Node.js frontend
├── pyrightconfig.json               # Konfigurasi Pyright static type checker
├── vercel.json                      # Konfigurasi deployment terpadu Vercel (SPA + Serverless)
├── vite.config.ts                   # Konfigurasi Vite, TailwindCSS, dan reverse proxy /api
└── README.md                        # Dokumentasi utama proyek
```

---

## 🚀 Panduan Menjalankan Proyek

### Prasyarat
- **Node.js**: Versi 18 atau lebih baru & `npm`
- **Python**: Versi 3.10 atau lebih baru & `pip`
- Akun / Proyek **Supabase** aktif dengan PostgreSQL database

---

### 1. Konfigurasi Environment (`.env`)

Buat file `.env` di root direktori proyek (salin dari `.env.example`):

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-publishable-key
SUPABASE_SECRET_KEY=your-supabase-service-role-key
DATABASE_URL=postgresql://postgres.yourproject:password@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres

# JWT Secret
JWT_SECRET=ihsg-smart-stock-secret-jwt-key-2026

# SMTP Configuration (Opsional - untuk kode verifikasi)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

### 2. Menjalankan Backend (FastAPI)

```powershell
# Jalankan langsung dari root direktori proyek
python -m uvicorn backend.main:app --reload --port 8000
```

- Dokumentasi Swagger API: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

---

### 3. Menjalankan Frontend (React + Vite)

```powershell
# Install dependensi (hanya pertama kali)
npm install

# Jalankan dev server Vite
npm run dev
```

- Aplikasi web dapat diakses di: `http://localhost:5173`
- Request ke `/api/*` secara otomatis di-proxy ke backend `http://127.0.0.1:8000`.

---

### 4. Menjalankan Pengujian (Testing & Type Check)

```powershell
# 1. Menjalankan Static Type Checker (Pyright)
npx pyright

# 2. Menjalankan Unit Tests Backend
python -m unittest discover -s backend/tests -p "test_*.py"

# 3. Validasi Build Frontend Production
npm run build
```

---

## 📦 Dependensi Utama

### Frontend (`package.json`)
- `react` & `react-dom` (v19): Framework UI deklaratif.
- `vite` (v8): Build tool berkecepatan tinggi.
- `tailwindcss` & `@tailwindcss/vite` (v4): Utility-first styling engine.
- `@supabase/supabase-js`: Client SDK resmi Supabase Auth & Storage.
- `axios`: HTTP client dengan interceptor token otentikasi.
- `lucide-react`: Paket ikon modern dan elegan.
- `recharts`: Visualisasi grafik interaktif finansial.

### Backend (`requirements.txt`)
- `fastapi`: Framework web asinkronus berperforma tinggi.
- `uvicorn`: ASGI web server.
- `yfinance`: Library pengambil data pasar Yahoo Finance.
- `pandas` & `numpy`: Pemrosesan deret waktu teknikal & manipulasi matriks.
- `sqlalchemy` & `psycopg2-binary`: ORM dan PostgreSQL adapter.
- `supabase`: Python SDK untuk Supabase platform.
- `pydantic` & `pydantic-settings`: Validasi data dan konfigurasi lingkungan.
- `mangum`: Adapter Serverless ASGI untuk Vercel / AWS Lambda.

---

## 🔒 Lisensi & Hak Cipta
Hak Cipta © 2026 **IHSG Terminal Pro**. Dikembangkan untuk investor dan trader pasar modal Indonesia.
