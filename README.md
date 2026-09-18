# IHSG Terminal Pro — Platform Rekomendasi Saham & Terminal Analisis Pasar BEI

Aplikasi terminal cerdas berbasis web untuk pemantauan pasar saham, analisis kuantitatif multi-faktor, pelacakan akumulasi *smart money* (*Bandarmology*), dan perumusan rencana trading otomatis bagi saham-saham konstituen **IDX80** di Bursa Efek Indonesia (BEI) secara objektif dan real-time.

---

## Daftar Isi
1. [Gambaran Sistem](#1-gambaran-sistem)
2. [Cara Kerja Sistem](#2-cara-kerja-sistem)
3. [Ada Apa Saja pada Sistem (Fitur & Modul)](#3-ada-apa-saja-pada-sistem-fitur--modul)
4. [Struktur Berkas & Direktori Proyek](#4-struktur-berkas--direktori-proyek)
5. [Teknologi yang Digunakan](#5-teknologi-yang-digunakan)
6. [Spesifikasi Antarmuka REST API](#6-spesifikasi-antarmuka-rest-api)
7. [Panduan Instalasi & Menjalankan Sistem](#7-panduan-instalasi--menjalankan-sistem)
8. [Deployment Produksi Terpadu](#8-deployment-produksi-terpadu)
9. [Disklaimer Pasar Modal](#9-disklaimer-pasar-modal)

---

# 1. Gambaran Sistem

**IHSG Terminal Pro** dirancang sebagai platform terintegrasi yang menjembatani kebutuhan investor dan trader dalam menyaring (*screening*), menganalisis, dan merumuskan strategi transaksi saham di Bursa Efek Indonesia secara cepat, objektif, dan berbasis data.

Sistem menghilangkan bias emosional dalam transaksi saham dengan memproses data historis harga, indikator teknikal teruji, pergerakan volume, dan aliran dana institusi secara komputasional.

### Fokus Universe: Indeks IDX80 BEI
Sistem secara khusus beroperasi pada 80 saham pilihan dalam indeks **IDX80** karena:
- **Likuiditas Pasar Tinggi**: Saham dengan nilai transaksi dan frekuensi perdagangan harian terbesar di bursa, meminimalkan risiko likuiditas (*slippage*).
- **Kematangan Fundamental**: Terdiri dari perusahaan berkapitalisasi pasar besar dan menengah (*large & mid-cap*) dengan kelangsungan bisnis yang teruji.
- **Efisiensi & Stabilitas Pemindaian**: Memungkinkan proses pemindaian batch berlangsung simultan dalam hitungan detik (15–25 detik) tanpa risiko pembatasan kuota (*rate limiting*).

---

# 2. Cara Kerja Sistem

Sistem bekerja secara otomatis melalui alur pemrosesan data berjenjang (*end-to-end processing pipeline*). Seluruh proses dirancang efisien dan terstruktur:

```mermaid
flowchart TD
    A["1. Ingesti Data Pasar Real-Time<br/>(Yahoo Finance API - IDX80 & IHSG)"] --> B["2. Mesin Pemindai Cepat Paralel<br/>(Batch Scanner Engine & ThreadPool)"]
    B --> C["3. Evaluasi Kuantitatif Multi-Dimensi<br/>(Tren, Momentum, Volatilitas, Likuiditas, Bandarmology)"]
    C --> D["4. Klasifikasi Sinyal Rekomendasi<br/>(Strong Buy • Buy • Hold • Sell)"]
    D --> E["5. Perumusan Rencana Trading Otomatis<br/>(Entry Area, Stop Loss, Target TP1-TP3, Risk-to-Reward)"]
    E --> F["6. Distribusi ke Antarmuka Pengguna<br/>(Fixed Top Header, Stationary Bottom Ticker, Dashboard, Screener)"]
```

### Tahap 1: Ingesti Data Pasar (*Market Data Ingestion*)
- Sistem secara berkala mengambil data harga harian (OHLCV: *Open, High, Low, Close, Volume*) untuk seluruh emiten konstituen IDX80 serta Indeks Harga Saham Gabungan (IHSG / `^JKSE`).
- Data divalidasi terhadap daftar resmi emiten aktif BEI (*whitelist*) guna memastikan integritas data sebelum diproses lebih lanjut.

### Tahap 2: Pemrosesan Pemindaian Paralel (*Batch Scanner Engine*)
- Menggunakan arsitektur pemrosesan paralel (*multi-threading*) dengan `ThreadPoolExecutor` di sisi backend.
- Seluruh 80 saham diunduh dan dianalisis secara simultan dalam satu siklus batch tanpa membebani sistem secara berlebih, menghasilkan performa pemindaian yang cepat dan hemat bandwidth.

### Tahap 3: Evaluasi Kuantitatif Multi-Dimensi (*Multi-Dimensional Analysis*)
Sistem menguji kondisi setiap saham melalui kombinasi dimensi analisis teknikal dan likuiditas:
- **Analisis Struktur Tren**: Mengevaluasi arah pergerakan harga jangka pendek dan menengah terhadap rata-rata harga pasar dinamis (Moving Average).
- **Analisis Momentum**: Mengukur kecepatan akselerasi perubahan harga serta mendeteksi kondisi kejenuhan beli (*overbought*) maupun kejenuhan jual (*oversold*).
- **Analisis Volatilitas & Penembusan Level**: Mengukur rentang fluktuasi harga harian (*Average True Range*) untuk mengenali fase konsolidasi maupun penembusan level resistensi (*breakout*).
- **Konfirmasi Volume Transaksi**: Menguji apakah kenaikan harga didukung oleh lonjakan volume perdagangan yang signifikan di atas rata-rata volume reguler.
- **Deteksi Akumulasi Bandar (*Bandarmology Tracker*)**:
  - Menganalisis konsistensi sebaran volume harga (*Volume Spread Analysis*) dan posisi harga penutupan harian.
  - Memantau akumulasi likuiditas oleh pelaku pasar bermodal besar (*smart money* / institusi) sebelum terjadinya pergerakan tren signifikan.
  - Mengelompokkan status akumulasi ke dalam kategori objektif: *Akumulasi Masif*, *Akumulasi Normal*, *Netral*, atau *Distribusi*.

> *Catatan: Logika pembobotan analitis dan parameter matematis internal dijaga kerahasiaannya untuk melindungi integritas algoritma sistem.*

### Tahap 4: Pembentukan Sinyal Rekomendasi (*Signal Classification*)
Berdasarkan hasil pengujian multi-dimensi, sistem memetakan saham ke dalam sinyal rekomendasi yang jelas dan terstandarisasi:
- **STRONG BUY**: Saham berada dalam konfirmasi tren naik yang sangat kuat, didukung lonjakan volume, akumulasi institusi, dan rasio potensi imbal hasil yang tinggi.
- **BUY**: Saham memiliki struktur teknikal positif dan berada di area beli yang menarik secara rasio risiko-keuntungan.
- **HOLD**: Saham berada dalam fase konsolidasi, menunggu arah tren berikutnya, atau sinyal teknikal saling mengimbangi.
- **SELL**: Saham menunjukkan tanda-tanda pelemahan tren, penembusan batas pengaman ke bawah, atau tertekan aksi distribusi volume.

### Tahap 5: Perumusan Rencana Trading Otomatis (*Automated Trading Plan*)
Untuk membantu eksekusi disiplin pengguna, sistem secara otomatis menghitung parameter operasional transaksi:
- **Area Beli (*Entry Area*)**: Rentang harga beli optimal yang dekat dengan area penyangga (*support*).
- **Batas Toleransi Risiko (*Stop Loss*)**: Level pengaman modal yang terukur secara teknikal untuk membatasi kerugian bila pasar berbalik arah.
- **Sasaran Keuntungan Bertahap (*Take Profit 1, 2, 3*)**: Target harga untuk merealisasikan keuntungan secara terukur.
- **Rasio Imbal Hasil terhadap Risiko (*Risk-to-Reward Ratio*)**: Memastikan setiap skenario trading yang disarankan memiliki potensi keuntungan yang jauh lebih besar daripada risiko toleransi (minimal R:R $\ge$ 1:2).

### Tahap 6: Distribusi Data & Antarmuka Interaktif (*Live UI Delivery*)
- Hasil perhitungan langsung disinkronkan ke antarmuka pengguna melalui antarmuka REST API.
- Tampilan antarmuka menyajikan informasi secara ergonomis: dari pita pemantau harga berjalan di bagian bawah, kartu intelijen pasar di dashboard, hingga tabel screener yang dapat difilter secara fleksibel.

---

# 3. Ada Apa Saja pada Sistem (Fitur & Modul)

Sistem dirancang dengan arsitektur modular yang menyajikan informasi secara komprehensif mulai dari ringkasan makro pasar hingga detail mikro emiten individual:

```mermaid
graph LR
    subgraph Platform ["Arsitektur Fitur IHSG Terminal Pro"]
        direction TB
        F1["1. Header Navigasi Atas Terkunci (Fixed Top Navbar)"]
        F2["2. Running Ticker Saham Bawah Terkunci (Stationary Live Ticker)"]
        F3["3. Dashboard Intelijen Pasar & Bandarmology"]
        F4["4. Screener Saham Interaktif Multi-Filter"]
        F5["5. Halaman Detail Saham & Candlestick Interaktif"]
        F6["6. Modul Laporan Riset Saham"]
        F7["7. Panel Administrator & Kontrol Hak Akses (RBAC)"]
        F8["8. Sistem Autentikasi Pengguna Terintegrasi"]
    end
```

---

### 1. Header Navigasi Atas Terkunci (*Fixed Top Navbar*)
- **Posisi Terkunci (*Stationary Header*)**: Navbar berada di posisi tetap di bagian paling atas layar (`fixed top-0 left-0 right-0 z-50`) dengan efek *glassmorphism* modern dan bayangan halus. Ketika halaman digulir (*scroll*) ke bawah, navbar tidak ikut bergeser sehingga navigasi selalu dapat diakses seketika.
- **Navigasi Cepat Antar Menu**: Akses langsung ke menu utama: *Dashboard, Screener, Detail Saham, Laporan Riset,* dan *Panel Admin*.
- **Pencarian Cepat Global**: Fasilitas pencarian instan untuk melompat langsung ke emiten yang diinginkan dengan mengetik kode saham (misal: BBCA, TLKM, BMRI) atau nama perusahaannya.
- **Indikator Pengguna & Peran**: Menampilkan avatar profil, nama pengguna, lencana peran (`ADMIN` / `USER`), serta tombol keluar (*Logout*).

---

### 2. Pita Saham Berjalan Terkunci di Bagian Bawah (*Stationary Bottom Live Stock Ticker*)
- **Posisi Terkunci (*Stationary Bottom*)**: Pita pemantau harga menempel di bagian bawah layar (`fixed bottom-0 left-0 right-0 z-40`). Pada perangkat ponsel pintar, posisinya otomatis berada tepat di atas bilah navigasi bawah ponsel (`bottom-14 md:bottom-0`), sehingga tidak pernah menutupi tombol navigasi lain.
- **Animasi Bergerak Tanpa Jeda (*Continuous Infinite Tape*)**: Daftar harga saham bergerak horizontal secara halus dan berkesinambungan menggunakan akselerasi grafis GPU tanpa membebani performa browser.
- **Indikator IHSG Terkini**: Menampilkan level penutupan indeks IHSG terbaru, nominal perubahan poin, dan persentase pergerakan pasar (indikator hijau saat menguat, merah saat melemah).
- **Kartu Mini Saham Real-Time**: Menyajikan kode ticker, harga terakhir, nominal naik/turun, persentase perubahan, dan panah arah tren harga.
- **Badge Highlight Akumulasi Bandar**: Saham yang terdeteksi sedang berada dalam fase akumulasi modal besar ditandai dengan badge khusus yang menyala `[AKUMULASI]`.
- **Interaksi Hover-to-Pause**: Pergerakan pita otomatis berhenti (*pause*) saat kursor mouse diarahkan ke atasnya, memudahkan pengguna membaca angka dengan jelas.
- **Klik Interaktif ke Halaman Detail**: Mengklik salah satu kartu saham pada pita berjalan akan langsung membuka halaman analisis mendalam untuk saham tersebut.

---

### 3. Dashboard Intelijen Pasar & Bandarmology (*Market Dashboard*)
- **Ringkasan Indeks IHSG**: Menampilkan angka penutupan IHSG (^JKSE), sparkline grafik tren harian, dan label status sentimen pasar (*BULLISH*, *BEARISH*, atau *NETRAL*).
- **Kartu Metrik & Statistik Pasar**:
  - Total saham IDX80 yang dipantau dalam sistem.
  - Persentase rasio saham Bullish vs Bearish di pasar.
  - Waktu sinkronisasi data terakhir.
- **Status Pemindaian Real-Time (*Scanner Progress Bar*)**: Indikator persentase pemindaian pasar aktif dilengkapi tombol *Scan Semua IHSG* dan *Sync Emiten*.
- **Visualisasi Distribusi Rekomendasi**: Diagram batang proporsional yang memetakan jumlah saham berkategori *Strong Buy*, *Buy*, *Hold*, dan *Sell*.
- **Modul Pelacak Akumulasi Bandar (*Bandarmology Tracker Section*)**:
  - Bagian khusus pada dashboard yang menyorot saham-saham pilihan yang sedang diakumulasi oleh *smart money* / bandar.
  - Kartu saham interaktif dengan aksen bercahaya (*glow card*), status akumulasi (*Masif* atau *Normal*), rasio lonjakan volume terhadap rata-rata 20 hari, dan bar kekuatan akumulasi bandar.
  - Tautan langsung ke analisis detail teknikal saham bersangkutan.
- **Top Rekomendasi Saham Pilihan**: Daftar emiten dengan skor kelayakan tertinggi di pasar beserta parameter harga, rasio risiko-imbal hasil, dan tombol pintas analisis.

---

### 4. Screener Saham Interaktif Multi-Filter (*Stock Scanner*)
- **Filter Cepat Kategori**:
  - `SEMUA`: Menampilkan seluruh hasil pemindaian konstituen IDX80.
  - `AKUMULASI BANDAR`: Menyaring khusus saham-saham yang terkonfirmasi mengalami akumulasi volume oleh institusi.
  - `STRONG BUY`, `BUY`, `HOLD`, `SELL`: Menyaring saham berdasarkan kategori rekomendasi.
- **Pencarian Cerdas Instan**: Filter teks real-time berdasarkan kode ticker, nama perseroan, atau sektor industri.
- **Pengurutan Kolom Dinamis**: Mengurutkan data secara cepat berdasarkan kriteria *Harga Terkini*, *Skor Kelayakan*, atau *Persentase Perubahan*.
- **Tabel Responsif Modern**: Menampilkan informasi terpadu: Kode Emiten, Nama Saham, Sektor Usaha, Harga Pasar, Bar Skor Kuantitatif, Badge Bandarmology, Status Rekomendasi, dan Tombol Analisis.

---

### 5. Halaman Detail Saham & Candlestick Interaktif (*Stock Detail & Analysis*)
- **Banner Profil Emiten**: Menampilkan kode saham, nama perseroan, sektor usaha, harga pasar terkini, badge sinyal rekomendasi, dan status Bandarmology.
- **Grafik Candlestick Interaktif**: Grafik harga harian interaktif berbasis Canvas dengan pergerakan candlestick, garis rata-rata pergerakan tren (MA20 dan MA50), serta riwayat harga 1 tahun.
- **Grid Kartu Indikator Teknikal**:
  - *Moving Average MA20*: Pemantau tren jangka pendek.
  - *Moving Average MA50*: Pemantau tren jangka menengah.
  - *RSI 14 (Relative Strength Index)*: Pengukur kejenuhan harga beli/jual.
  - *ATR 14 (Average True Range)*: Pengukur volatilitas dan fluktuasi harga harian.
  - *Bandarmology & Aliran Modal*: Pengukur serapan volume dan fase akumulasi pasar.
- **Rincian Evaluasi Aturan Screener**: Matriks status kelulusan aturan (Tren, Momentum, Breakout, Kondisi Oversold, dan Setup Struktur).
- **Kartu Rencana Trading Operasional (*Trading Plan Card*)**:
  - Rentang *Entry Area* (Area Beli yang disarankan).
  - Level *Stop Loss* (Level proteksi modal).
  - Target *Take Profit 1, 2, dan 3* (Sasaran realisasi profit bertahap).
  - *Rasio Risk-to-Reward* (Rasio potensi laba berbanding risiko terhitung).
  - Catatan strategi trading operasional.

---

### 6. Modul Laporan Riset Saham (*Research Reports*)
- Modul dokumentasi dan publikasi laporan analisis saham oleh pengguna maupun analis pasar.
- Fitur penulisan laporan terstruktur: kode emiten, judul riset, kategori sinyal rekomendasi, target harga, dan uraian analisis strategi transaksi.
- Filter pencarian laporan berdasarkan kode saham serta pengaturan hak akses visibilitas publik atau pribadi.

---

### 7. Panel Administrator & Kontrol Hak Akses (*Admin Panel & RBAC*)
- Modul khusus bagi pengguna dengan kewenangan peran `admin` (*Role-Based Access Control*).
- **Manajemen Pengguna**: Melihat daftar seluruh pengguna terdaftar, surel, tanggal pembuatan akun, dan status peran aktif.
- **Pengaturan Hak Akses**: Fleksibilitas mengubah peran akun antara pengguna biasa (`user`) dan administrator (`admin`).
- **Log Audit & Pemantauan Sistem**: Pemantauan aktivitas pembaruan data semesta saham dan sinkronisasi katalog.

---

### 8. Sistem Autentikasi Pengguna & Keamanan
- **Google OAuth Login**: Masuk ke aplikasi secara instan dengan satu klik menggunakan akun Google resmi.
- **Autentikasi Surel & Kata Sandi**: Pendaftaran akun baru, masuk, dan pemulihan kata sandi yang aman.
- **Pengelolaan Sesi Terenkripsi**: Manajemen token JWT terenkripsi dengan mekanisme penyegaran otomatis melalui Supabase Auth.
- **Proteksi Rute (*Protected Routes*)**: Memastikan modul sensitif hanya dapat diakses oleh pengguna yang memiliki kewenangan otentikasi sah.

---

# 4. Struktur Berkas & Direktori Proyek

Seluruh kode sumber tersimpan secara rapi di dalam repositori `Sistem Rekomendasi IHSG` tanpa ada berkas yang tidak terpakai:

```text
Sistem Rekomendasi IHSG/
├── api/
│   └── index.py                    # Serverless function entrypoint Vercel (FastAPI + Mangum)
├── backend/                        # Backend API & Mesin Analisis Kuantitatif (Python 3.12)
│   ├── app/
│   │   ├── api/v1/                 # Endpoint RESTful (stocks, recommendations, screener, auth, admin, reports)
│   │   ├── config/                 # Daftar konstituen resmi IDX80 & metadata BEI
│   │   ├── core/                   # Konfigurasi keamanan, enkripsi JWT, & validasi whitelist IDX80
│   │   ├── database/               # Koneksi basis data PostgreSQL & Supabase client
│   │   ├── engine/                 # Indikator statistik deret waktu harga
│   │   ├── indicators/             # Perhitungan indikator teknikal (MA20, MA50, MA200, RSI, ATR)
│   │   ├── middleware/             # Middleware otentikasi & penanganan CORS
│   │   ├── models/                 # Definisi skema tabel basis data relasional
│   │   ├── recommendation/         # Recommendation Engine & penyusunan ringkasan sinyal
│   │   ├── routes/                 # Rute utama market data & batch screener engine
│   │   ├── schemas/                # Skema validasi request/response Pydantic
│   │   ├── screener/               # Aturan screener, Batch Scanner Engine, & Bandar Detector
│   │   ├── services/               # Integrasi penarikan data Yahoo Finance & analisis harga
│   │   ├── trading_plan/           # Generator Trading Plan otomatis & rasio risk-to-reward
│   │   ├── universe/               # Manajer sinkronisasi semesta konstituen IDX80
│   │   └── validators/             # Validasi integritas kode emiten
│   ├── migrations/                 # Skrip migrasi skema tabel basis data PostgreSQL
│   ├── tests/                      # Pengujian unit backend
│   ├── main.py                     # Entrypoint aplikasi FastAPI untuk pengembangan lokal
│   ├── Procfile                    # Konfigurasi runner proses backend
│   ├── render.yaml                 # Konfigurasi deployment alternatif
│   └── requirements.txt            # Daftar pustaka dependensi Python
├── src/                            # Frontend Single Page Application (React 19 + TypeScript)
│   ├── api/                        # Axios HTTP client & token interceptor
│   ├── assets/                     # Aset gambar & ikon grafis
│   ├── components/                 # Komponen antarmuka modular
│   │   ├── chart/                  # Candlestick Chart interaktif berbasis Canvas & Area Sparkline
│   │   ├── common/                 # Modal dialog otentikasi & ProtectedRoute
│   │   ├── dashboard/              # Komponen widget ringkasan pasar & Bandarmology Tracker
│   │   ├── layout/                 # Fixed Navbar atas, Fixed LiveStockTicker bawah, & BottomNav
│   │   ├── recommendation/         # Kartu rekomendasi & rincian Trading Plan
│   │   └── screener/               # Tabel interaktif scanner saham & filter kategori
│   ├── constants/                  # Konstanta aplikasi frontend
│   ├── context/                    # AuthContext (Sesi & Otentikasi Supabase)
│   ├── hooks/                      # Custom React hooks
│   ├── pages/                      # Halaman utama (Dashboard, Scanner, Detail, Laporan, Admin)
│   ├── services/                   # Layanan data frontend
│   ├── types/                      # Definisi tipe data TypeScript (IHSG, stock, screener, user)
│   ├── utils/                      # Utilitas pemformatan mata uang IDR & kalkulasi matematis
│   ├── App.css                     # Gaya CSS lokal aplikasi
│   ├── App.tsx                     # Komponen induk dengan routing tab & fixed layout
│   ├── index.css                   # Sistem desain Dark Terminal & animasi ticker loop
│   └── main.tsx                    # Titik masuk rendering React DOM
├── public/                         # Berkas statis publik (favicon, metadata)
├── .env.example                    # Template konfigurasi variabel lingkungan sistem
├── .gitignore                      # Berkas pengecualian Git
├── .python-version                 # Konfigurasi versi runtime Python (3.12)
├── index.html                      # Berkas HTML utama peramban
├── package.json                    # Konfigurasi paket Node.js, dependensi, & skrip build
├── tsconfig.json                   # Konfigurasi kompilator TypeScript
├── vercel.json                     # Konfigurasi deployment terpadu Vercel (SPA + Serverless API)
├── vite.config.ts                  # Konfigurasi bundler Vite
└── README.md                       # Dokumentasi resmi sistem
```

---

# 5. Teknologi yang Digunakan

| Lapisan Sistem | Teknologi | Peran & Kegunaan |
| :--- | :--- | :--- |
| **Frontend Framework** | **React 19 + TypeScript** | Membangun antarmuka Single Page Application (SPA) yang interaktif, modular, dan bertipe data ketat (*type-safe*). |
| **Bundler & Build Tool**| **Vite** | Bundler modern dengan kecepatan kompilasi tinggi dan fitur Hot Module Replacement (HMR). |
| **Desain & Antarmuka** | **Tailwind CSS (v4)** | Sistem desain visual bergaya *Dark Trading Terminal* dengan efek glassmorphism dan responsif di semua ukuran layar. |
| **Grafik & Visualisasi** | **HTML5 Canvas, Lucide Icons** | Rendering grafik candlestick interaktif tanpa lag dan penyediaan ikon grafis trading modern. |
| **Backend API** | **Python 3.12 + FastAPI** | Framework backend asinkronus berkecepatan tinggi dengan validasi skema Pydantic otomatis. |
| **Serverless Adapter** | **Mangum** | Adapter ASGI untuk mengintegrasikan FastAPI ke dalam serverless function Vercel. |
| **Komputasi & Data** | **Pandas, NumPy** | Pemrosesan deret waktu kuantitatif, kalkulasi matriks teknikal, dan analisis volume spread. |
| **Data Pasar Saham** | **Yahoo Finance (`yfinance`)** | Pengambilan data historis harga OHLCV dan metrik pasar emiten BEI. |
| **Basis Data & Autentikasi** | **Supabase Cloud (PostgreSQL)** | Penyimpanan data relasional (emiten, akun pengguna, laporan riset) dan otentikasi Google OAuth. |
| **Platform Deployment** | **Vercel** | Hosting terpadu satu pintu (*Unified Deployment*) untuk frontend statis dan backend serverless API. |

---

# 6. Spesifikasi Antarmuka REST API

Berikut daftar endpoint RESTful utama yang disediakan oleh backend sistem:

| Method | Endpoint Path | Tingkat Akses | Deskripsi & Fungsi |
| :---: | :--- | :---: | :--- |
| `GET` | `/api/market/ihsg` | Publik | Mengambil data level harga, poin perubahan, persentase, dan sentimen indeks IHSG (`^JKSE`). |
| `GET` | `/api/universe/stats` | Publik | Mengambil statistik jumlah konstituen aktif dalam semesta IDX80. |
| `POST` | `/api/universe/sync` | Admin | Memperbarui dan menyinkronkan katalog konstituen IDX80 ke basis data. |
| `GET` | `/api/screener/rules` | Publik | Menjalankan pemindaian multi-faktor IDX80 dengan opsi filter kategori dan pengurutan kolom. |
| `GET` | `/api/screener/bandar-accumulation` | Publik | Mengambil daftar saham IDX80 yang terkonfirmasi dalam fase akumulasi institusi/bandar. |
| `GET` | `/api/screener/progress` | Publik | Mengambil persentase status proses pemindaian pasar di latar belakang. |
| `POST` | `/api/screener/start-scan` | Pengguna | Memulai pemindaian batch 80 saham IDX80 secara asinkronus. |
| `GET` | `/api/v1/stocks/{symbol}` | Token Pengguna | Mengambil profil emiten, riwayat deret waktu OHLCV, dan indikator teknikal saham. |
| `GET` | `/api/v1/recommendations/{symbol}` | Token Pengguna | Mengambil hasil rekomendasi teknikal, evaluasi aturan, dan ringkasan sinyal. |
| `GET` | `/api/trading-plan/{symbol}` | Token Pengguna | Menghasilkan rincian rencana trading operasional (*Entry, Stop Loss, TP1-TP3, Risk-to-Reward*). |
| `GET` | `/api/v1/reports` | Token Pengguna | Mengambil daftar dokumen laporan riset saham. |
| `POST` | `/api/v1/reports` | Token Pengguna | Menerbitkan dokumen laporan analisis riset saham baru. |
| `GET` | `/api/v1/admin/users` | Peran Admin | Menampilkan seluruh daftar pengguna terdaftar beserta peran otorisasi akun. |
| `PUT` | `/api/v1/admin/users/{id}/role` | Peran Admin | Mengubah tingkat kewenangan peran pengguna (`admin` $\leftrightarrow$ `user`). |

---

# 7. Panduan Instalasi & Menjalankan Sistem

### 1. Prasyarat Lingkungan
- **Node.js**: Versi 18.x atau lebih baru (disarankan Node.js 20 LTS).
- **Python**: Versi 3.11 atau 3.12 (arsitektur 64-bit).
- **Akun Supabase**: Proyek PostgreSQL Supabase yang aktif.

### 2. Konfigurasi Variabel Lingkungan (`.env`)
Buat berkas `.env` pada direktori utama proyek dengan menyalin berkas template:
```bash
cp .env.example .env
```
Isi konfigurasi kredensial sesuai dengan proyek Anda:
```ini
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
DATABASE_URL=postgresql://postgres.your-id:password@pooler.supabase.com:5432/postgres
SECRET_KEY=your-secret-encryption-key-for-jwt
ENVIRONMENT=production
```

### 3. Menjalankan Backend (FastAPI)
```bash
# Buka terminal dan masuk ke direktori backend
cd backend

# Pasang dependensi pustaka Python
pip install -r requirements.txt

# Jalankan server lokal FastAPI
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Dokumentasi interaktif OpenAPI (Swagger) dapat diakses melalui browser di: `http://localhost:8000/docs`

### 4. Menjalankan Frontend (React + Vite)
```bash
# Buka terminal baru pada direktori utama proyek
npm install

# Jalankan server pengembangan Vite
npm run dev
```
Aplikasi terminal dapat diakses melalui peramban di: `http://localhost:5173`

---

# 8. Deployment Produksi Terpadu

Aplikasi ini menggunakan arsitektur **Unified Vercel Deployment**:
- **Frontend SPA**: Dikompilasi otomatis oleh Vite menjadi berkas web statis berkinerja tinggi di direktori `dist/`.
- **Backend Serverless**: Seluruh panggilan API ke rute `/api/*` secara otomatis dialihkan oleh Vercel ke fungsi serverless Python melalui adapter `api/index.py`.
- **Langkah Deploy**:
  1. Hubungkan repositori Git proyek ini ke dashboard Vercel.
  2. Masukkan variabel lingkungan yang ada pada berkas `.env` ke menu *Project Settings $\rightarrow$ Environment Variables* di Vercel.
  3. Lakukan deploy, dan sistem akan langsung aktif secara global.

---

# 9. Disklaimer Pasar Modal

> [!CAUTION]
> **Peringatan Risiko Investasi**:
> Seluruh informasi, analisis teknikal, deteksi Bandarmology, dan rencana trading yang disajikan oleh **IHSG Terminal Pro** merupakan sarana bantu pendukung keputusan (*Decision Support System*) berbasis komputasi matematis historis, **bukan merupakan ajakan jual/beli, anjuran investasi mutlak, atau jaminan keuntungan finansial**. Pasar saham memiliki risiko fluktuasi modal. Pengguna disarankan untuk senantiasa melakukan riset dan analisis mandiri (*Do Your Own Research / DYOR*). Segala keputusan transaksi dan konsekuensi finansial yang timbul sepenuhnya merupakan tanggung jawab mandiri masing-masing investor.
