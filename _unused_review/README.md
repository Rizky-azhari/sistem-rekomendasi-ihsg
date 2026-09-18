# Arsip File yang Tidak Digunakan (_unused_review)

Folder ini menyimpan file-file yang diidentifikasi tidak lagi digunakan secara aktif oleh sistem (prototype lama, duplikat fungsionalitas, atau stub file), untuk memastikan keamanan dan stabilitas sebelum diputuskan untuk dihapus secara permanen.

## Daftar File yang Diarsipkan

| File Asal | Lokasi Arsip | Alasan Pengarsipan |
| :--- | :--- | :--- |
| `frontend/` | `_unused_review/frontend_leftover/` | Sisa instalasi parsial lama sebelum proyek disatukan ke root (`src/`). |
| `backend/data/idx_stock_universe.json` | `_unused_review/idx_stock_universe.json` | Data dump statis lama 900+ saham IHSG. Sistem kini menggunakan whitelist IDX80 konstituen & PostgreSQL. |
| `backend/app/rule_engine/` | `_unused_review/backend_rule_engine/` | Duplikat dari `backend/app/engine/`. Tidak pernah diimpor oleh sistem aktif. |
| `backend/app/indicators/technical.py` | `_unused_review/backend_indicators_technical.py` | Duplikat persis dari `backend/app/engine/indicators.py`. |
| `backend/app/routes/stock_routes.py` | `_unused_review/backend_routes_stock_routes.py` | Mock prototype route awal. Endpoint aktif ditangani oleh `app/api/v1/stocks.py`. |
| `backend/app/routes/recommendation_routes.py` | `_unused_review/backend_routes_recommendation_routes.py` | Mock prototype route awal. Endpoint aktif ditangani oleh `app/api/v1/recommendations.py`. |
| `backend/app/routes/screener_routes.py` | `_unused_review/backend_routes_screener_routes.py` | Mock prototype route awal. Endpoint aktif ditangani oleh `app/api/v1/screening.py`. |
| `backend/app/schemas/recommendation_schema.py` | `_unused_review/backend_schemas_recommendation_schema.py` | Schema stub lama. Digantikan oleh `app/schemas/recommendation.py`. |
| `backend/app/schemas/stock_schema.py` | `_unused_review/backend_schemas_stock_schema.py` | Schema stub lama. Digantikan oleh `app/schemas/stock.py`. |
| `backend/app/services/stock_service.py` | `_unused_review/backend_services_stock_service.py` | Class kosong (6 baris stub `pass`). |
| `src/services/stockService.ts` | `_unused_review/frontend_stockService.ts` | Client API parsial lama. Digantikan secara komprehensif oleh `src/api/client.ts`. |
