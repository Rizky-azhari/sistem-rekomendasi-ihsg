# 🇮🇩 IHSG TERMINAL PRO
### Smart Stock Recommendation & Decision Support System (IDX All-Stock Universe)

**IHSG Terminal Pro** adalah platform analitika pasar modal Indonesia berbasis kecerdasan komputasi (*Decision Support System*) dan *quantitative screener* yang memindai seluruh emiten aktif yang terdaftar di **Bursa Efek Indonesia (BEI / IDX)** secara dinamis.

Platform ini mengintegrasikan **FastAPI backend (Python)**, **PostgreSQL (Supabase)**, **Google OAuth Authentication**, serta antarmuka modern **React (Vite) + Tailwind CSS + Recharts** dengan pendekatan *Mobile First* dan dukungan *Progressive Web App (PWA)*.

---

## 🌟 Fitur Utama

1. **IDX All-Stock Dynamic Universe (950+ Emiten)**:
   - Mengambil data seluruh emiten aktif Indonesia secara dinamis dari database Supabase PostgreSQL (`stock_universe`), dengan fallback bertingkat (API IDX resmi -> mirror data -> lokal).
   - Format standar Yahoo Finance: `BBCA.JK`, `BBRI.JK`, `TLKM.JK`, dll.

2. **5-Factor Rule-Based Screener Engine**:
   - **Momentum Screener**: `Close > MA20` & `Volume > Volume Rata-rata 20 Hari`.
   - **Trend Screener**: `MA20 > MA50 > MA200` (Strong Bullish Alignment).
   - **Oversold Screener**: `RSI(14) < 35` & Harga mendekati Support area.
   - **Breakout Screener**: `Close > Highest High 20 Hari`.
   - **Trading Setup Screener**: Evaluasi rasio Risk-Reward $\ge 1:2$.

3. **Composite Recommendation Engine**:
   $$\text{Final Score} = (\text{Trend} \times 25\%) + (\text{Momentum} \times 25\%) + (\text{Breakout} \times 20\%) + (\text{Oversold} \times 10\%) + (\text{Setup} \times 20\%)$$
   - **85 - 100**: `STRONG BUY`
   - **70 - 84**: `BUY`
   - **50 - 69**: `HOLD`
   - **< 50**: `SELL`
   - Dilengkapi narasi alasan rekomendasi otomatis berdasarkan indikator teknikal.

4. **Automated Trading Plan Generator**:
   - Menghasilkan rencana eksekusi trading otomatis:
     - **Buy Area** (rentang harga beli ideal)
     - **Stop Loss** (proteksi risiko berbasis Support & ATR)
     - **Take Profit 1, 2, 3** (target bertahap)
     - **Risk-Reward Ratio** (RR $\ge 1:2$)

5. **Sistem Autentikasi Google OAuth & Role Supabase**:
   - Login instan satu klik menggunakan Google OAuth melalui Supabase Auth.
   - **Otomatisasi Role**: Pengguna Google pertama yang mendaftar otomatis menjadi `ADMIN`, pengguna berikutnya otomatis menjadi `USER`.
   - Proteksi rute halaman `/admin/*` dengan tampilan eksplisit *Access Denied*.

6. **Desain Mobile-First & Dark Trading Terminal**:
   - Palet warna terminal profesional: Background `#060B18`, Surface `#111827`, Primary Cyan `#22C7F0`.
   - Navigasi adaptif: **Top Navbar** di Desktop & Tablet, **Bottom Navigation Bar** di Mobile.
   - PWA (*Progressive Web App*) siap install di Android dan iOS.

---

## 🏗️ Arsitektur Sistem

```
Sistem Rekomendasi IHSG/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Endpoint FastAPI (auth, screening, stocks, admin, reports)
│   │   ├── core/            # Config, security middleware JWT, role guards
│   │   ├── database/        # SQLAlchemy engine & Supabase connection
│   │   ├── engine/          # Batch scanner multi-threading
│   │   ├── indicators/      # Penghitung MA, RSI, MACD, ATR, Support/Resistance
│   │   ├── recommendation/  # 5-factor scoring & reasoning generator
│   │   ├── rule_engine/     # Modul screener (momentum, trend, oversold, breakout, setup)
│   │   ├── screener/        # Stock screener coordinator
│   │   ├── trading_plan/    # Generator Buy Area, Stop Loss, TP1-3, RR
│   │   └── universe/        # Dynamic IDX Universe Manager
│   ├── data/                # IDX Stock Master Catalog
│   ├── migrations/          # File SQL skema database PostgreSQL Supabase
│   ├── main.py              # Entry point server FastAPI
│   └── requirements.txt     # Dependensi Python
├── frontend/
│   ├── public/              # Manifest PWA, service worker, icons
│   ├── src/
│   │   ├── api/             # HTTP Client Axios & Supabase SDK
│   │   ├── components/      # UI Components (Navbar, BottomNav, Charts, Tables)
│   │   ├── context/         # AuthContext (Google OAuth & Role Session)
│   │   ├── pages/           # Dashboard, Scanner, Detail, Reports, Admin
│   │   ├── index.css        # Tailwind CSS & Dark Trading Terminal tokens
│   │   └── App.tsx          # Router, code-splitting & PWA prompt
│   ├── package.json         # Dependensi React, Vite, Tailwind CSS, Recharts
│   └── vercel.json          # Konfigurasi deployment Vercel
├── .env.example             # Template variabel lingkungan
└── README.md                # Dokumentasi proyek
```

---

## 🚀 Panduan Instalasi Lokal

### Prasyarat
- Python 3.10+
- Node.js 18+ & npm
- Proyek Supabase aktif (URL & Anon/Service Role Key)

### 1. Setup Backend (FastAPI)

```bash
# Buka folder backend
cd backend

# Buat virtual environment (opsional namun disarankan)
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependensi
pip install -r requirements.txt

# Buat file .env di folder backend/
# Isi variabel SUPABASE_URL, SUPABASE_KEY, SUPABASE_DB_URL, JWT_SECRET

# Jalankan server FastAPI
python -m uvicorn main:app --reload --port 8000
```
Backend akan aktif di `http://127.0.0.1:8000` (Dokumentasi Swagger di `http://127.0.0.1:8000/docs`).

### 2. Setup Frontend (React + Vite)

```bash
# Buka folder frontend
cd frontend

# Install dependensi
npm install

# Buat file .env di folder frontend/
# VITE_SUPABASE_URL=https://your-supabase-id.supabase.co
# VITE_SUPABASE_KEY=your-anon-key
# VITE_API_BASE_URL=http://localhost:8000

# Jalankan server frontend development
npm run dev
```
Aplikasi web akan dapat diakses di `http://localhost:5173`.

---

## 🌐 Panduan Deployment Online

### 1. Database (Supabase PostgreSQL)
1. Buat proyek baru di [Supabase](https://supabase.com).
2. Jalankan skrip migrasi SQL yang berada di `backend/migrations/` secara berurutan pada SQL Editor Supabase:
   - `init_schema.sql` (tabel `stock_universe`, `screening_results`, `trading_plans`)
   - `create_profiles_google_auth.sql` (tabel `profiles`, trigger otomatis admin `handle_new_user()`)
3. Aktifkan **Google OAuth Provider** di Supabase Dashboard:
   `Authentication` -> `Providers` -> `Google` (masukkan Client ID & Client Secret dari Google Cloud Console).
   Tambahkan URL redirect: `https://<proyek-anda>.supabase.co/auth/v1/callback` dan URL domain aplikasi.

### 2. Frontend (Vercel)
1. Hubungkan repositori GitHub ke [Vercel](https://vercel.com).
2. Tentukan **Root Directory**: `frontend`.
3. Framework Preset: **Vite**.
4. Masukkan Environment Variables:
   - `VITE_SUPABASE_URL`: URL Supabase Anda.
   - `VITE_SUPABASE_KEY`: Anon Key Supabase.
   - `VITE_API_BASE_URL`: URL Backend produksi (misal `https://api-ihsg.up.railway.app`).
5. Deploy. File `frontend/vercel.json` akan otomatis menangani SPA routing.

### 3. Backend (Railway / Render)
1. Hubungkan repositori ke [Railway](https://railway.app) atau [Render](https://render.com).
2. Tentukan **Root Directory**: `backend`.
3. Start Command:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
4. Tambahkan Environment Variables dari `.env.example`.

---

## 🔒 Variabel Lingkungan (.env)

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
SUPABASE_DB_URL=postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres

# Security
JWT_SECRET=your-secure-jwt-secret-string
ALGORITHM=HS256

# Frontend (.env)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_KEY=your-anon-key
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📱 Dukungan Progressive Web App (PWA)
Aplikasi mendukung instalasi langsung di perangkat smartphone (Android / iOS):
- **Android**: Buka di Chrome -> Muncul banner *"Install IHSG Terminal"* atau ketuk menu titik tiga -> *"Add to Home Screen"*.
- **iOS (iPhone/iPad)**: Buka di Safari -> Ketuk ikon Share -> *"Add to Home Screen"*.

---

## 📄 Lisensi
Hak Cipta © 2026 IHSG Terminal Pro. Dikembangkan untuk analisis kuantitatif pasar modal dan edukasi investasi.
