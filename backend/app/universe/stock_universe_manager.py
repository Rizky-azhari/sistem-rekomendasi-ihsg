import os
import json
import csv
import io
import datetime
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.database.connection import get_db, engine, get_supabase, Base
from app.models.stock_model import StockUniverse


class StockUniverseManager:
    """
    Stock Universe Manager for Indonesia Stock Exchange (IDX).
    
    Responsibilities:
    - Multi-tiered source resolution (Priority A: Official IDX, Priority B: Online Master Dataset, Priority C: Local Master Fallback)
    - Dynamic universe management without hardcoded lists
    - Standardization to Yahoo Finance symbols (.JK)
    - Database synchronization, delisting management, and IPO tracking
    """

    DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
    LOCAL_FALLBACK_FILE = DATA_DIR / "idx_stock_universe.json"
    
    # Priority B source
    ONLINE_DATASET_URL = "https://raw.githubusercontent.com/wildangunawan/Dataset-Saham-IDX/master/List%20Emiten/all.csv"
    
    _CACHE_UNIVERSE: List[Dict[str, Any]] = []
    _SYMBOL_LOOKUP: Dict[str, Dict[str, Any]] = {}
    _CACHE_LAST_SYNC: Optional[datetime.datetime] = None

    @classmethod
    def normalize_ticker(cls, symbol: str) -> str:
        """Ensures the ticker has the .JK Yahoo Finance suffix."""
        sym = symbol.strip().upper()
        if not sym.endswith(".JK") and not "." in sym:
            sym = f"{sym}.JK"
        return sym

    @classmethod
    def get_stock_by_symbol(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """O(1) ticker lookup from Stock Universe."""
        sym = cls.normalize_ticker(symbol)
        if not cls._SYMBOL_LOOKUP:
            cls.fetch_all_idx_stocks()
        return cls._SYMBOL_LOOKUP.get(sym)

    @classmethod
    def fetch_priority_a_idx_api(cls) -> Optional[List[Dict[str, Any]]]:
        """
        Priority A: Official IDX API or Public Portal
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.idx.co.id/"
        }
        url = "https://www.idx.co.id/primary/ListedCompany/GetCompanyProfiles?emitenType=s&start=0&length=1200"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    profiles = data.get("data", [])
                    if profiles and len(profiles) > 50:
                        results = []
                        for p in profiles:
                            code = p.get("KodeEmiten", "").strip().upper()
                            if code:
                                results.append({
                                    "symbol": cls.normalize_ticker(code),
                                    "code": code,
                                    "company_name": p.get("NamaEmiten", "").strip(),
                                    "sector": p.get("Sektor", "General"),
                                    "board": p.get("PapanPencatatan", "Utama"),
                                    "is_active": True,
                                    "source": "IDX_OFFICIAL_API"
                                })
                        print(f"[StockUniverse] Priority A success: Fetched {len(results)} stocks from IDX Official API.")
                        return results
        except Exception as e:
            # Fallback to Priority B smoothly
            pass
        return None

    @classmethod
    def fetch_priority_b_online_dataset(cls) -> Optional[List[Dict[str, Any]]]:
        """
        Priority B: Online IDX Master Dataset Mirror (950+ stocks)
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            req = urllib.request.Request(cls.ONLINE_DATASET_URL, headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status == 200:
                    content = resp.read().decode("utf-8")
                    reader = csv.DictReader(io.StringIO(content))
                    results = []
                    for row in reader:
                        code = row.get("code", "").strip().upper()
                        if not code:
                            continue
                        results.append({
                            "symbol": cls.normalize_ticker(code),
                            "code": code,
                            "company_name": row.get("name", "").strip(),
                            "sector": "IDX Equities",
                            "board": row.get("listingBoard", "Utama").strip(),
                            "is_active": True,
                            "source": "ONLINE_MASTER_DATASET"
                        })
                    if len(results) > 100:
                        print(f"[StockUniverse] Priority B success: Fetched {len(results)} stocks from Online Dataset.")
                        return results
        except Exception as e:
            pass
        return None

    @classmethod
    def fetch_priority_c_local_master(cls) -> List[Dict[str, Any]]:
        """
        Priority C: Local IDX Master Dataset Fallback (idx_stock_universe.json)
        """
        if cls.LOCAL_FALLBACK_FILE.exists():
            try:
                with open(cls.LOCAL_FALLBACK_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        print(f"[StockUniverse] Priority C success: Loaded {len(data)} stocks from local master dataset.")
                        return data
            except Exception as e:
                print(f"[StockUniverse] Error reading local master file: {e}")

        # Absolute minimal fallback if even local json is missing
        return [
            {"symbol": "BBCA.JK", "code": "BBCA", "company_name": "Bank Central Asia Tbk.", "sector": "Financials", "board": "Utama", "is_active": True},
            {"symbol": "BBRI.JK", "code": "BBRI", "company_name": "Bank Rakyat Indonesia Tbk.", "sector": "Financials", "board": "Utama", "is_active": True},
            {"symbol": "BMRI.JK", "code": "BMRI", "company_name": "Bank Mandiri Tbk.", "sector": "Financials", "board": "Utama", "is_active": True},
            {"symbol": "TLKM.JK", "code": "TLKM", "company_name": "Telkom Indonesia Tbk.", "sector": "Infrastructures", "board": "Utama", "is_active": True}
        ]

    @classmethod
    def fetch_from_database(cls) -> Optional[List[Dict[str, Any]]]:
        """
        Primary source of truth: Query active stocks directly from stock_universe database table.
        Uses Supabase HTTPS REST Client or SQLAlchemy engine session.
        """
        # 1. Try Supabase REST Client
        sb = get_supabase()
        if sb is not None:
            try:
                res = sb.table("stock_universe").select("symbol, company_name, sector, board, market_cap, is_active").eq("is_active", True).execute()
                if res.data and len(res.data) > 50:
                    stocks = []
                    for row in res.data:
                        sym = cls.normalize_ticker(row.get("symbol", ""))
                        stocks.append({
                            "symbol": sym,
                            "code": sym.replace(".JK", ""),
                            "company_name": row.get("company_name") or sym.replace(".JK", ""),
                            "sector": row.get("sector") or "IDX Equities",
                            "board": row.get("board") or "Utama",
                            "market_cap": row.get("market_cap") or 0.0,
                            "is_active": row.get("is_active", True),
                            "source": "DATABASE_SUPABASE"
                        })
                    print(f"[StockUniverse] Database success: Loaded {len(stocks)} active stocks from Supabase stock_universe table.")
                    return stocks
            except Exception as e:
                print(f"[StockUniverse] Supabase DB fetch notice: {e}")

        # 2. Try SQLAlchemy engine session
        if engine is not None:
            try:
                with Session(engine) as session:
                    records = session.query(StockUniverse).filter_by(is_active=True).all()
                    if records and len(records) > 50:
                        stocks = []
                        for r in records:
                            sym = cls.normalize_ticker(r.symbol)
                            stocks.append({
                                "symbol": sym,
                                "code": sym.replace(".JK", ""),
                                "company_name": r.company_name or sym.replace(".JK", ""),
                                "sector": r.sector or "IDX Equities",
                                "board": r.board or "Utama",
                                "market_cap": r.market_cap or 0.0,
                                "is_active": r.is_active,
                                "source": "DATABASE_SQLALCHEMY"
                            })
                        print(f"[StockUniverse] Database success: Loaded {len(stocks)} active stocks from PostgreSQL Session.")
                        return stocks
            except Exception as e:
                print(f"[StockUniverse] SQLAlchemy DB fetch notice: {e}")

        return None

    @classmethod
    def fetch_all_idx_stocks(cls, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Fetches full IDX stock universe with primary source: stock_universe database table.
        Cascade: stock_universe Database -> Priority A -> Priority B -> Priority C
        """
        if not force_refresh and cls._CACHE_UNIVERSE:
            return cls._CACHE_UNIVERSE

        # 1. Primary Source: stock_universe database table
        stocks = cls.fetch_from_database()

        # 2. Fallback to external sources if database is empty or not yet reachable
        if not stocks:
            stocks = cls.fetch_priority_a_idx_api()

        if not stocks:
            stocks = cls.fetch_priority_b_online_dataset()

        if not stocks:
            stocks = cls.fetch_priority_c_local_master()

        cls._CACHE_UNIVERSE = stocks
        cls._SYMBOL_LOOKUP = {s["symbol"]: s for s in stocks}
        cls._CACHE_LAST_SYNC = datetime.datetime.now()
        return stocks

    @classmethod
    def get_active_symbols(cls, limit: Optional[int] = None) -> List[str]:
        """
        Returns dynamic list of active Yahoo Finance symbols (e.g. ['AALI.JK', 'BBCA.JK', ...]).
        """
        all_stocks = cls.fetch_all_idx_stocks()
        symbols = [s["symbol"] for s in all_stocks if s.get("is_active", True)]
        if limit:
            return symbols[:limit]
        return symbols

    @classmethod
    def sync_to_database(cls) -> Dict[str, Any]:
        """
        Synchronizes the fetched Stock Universe to PostgreSQL / Supabase stock_universe table.
        - Inserts new IPO stocks
        - Updates active stocks and sectors
        - Updates last_update timestamp
        """
        stocks = cls.fetch_all_idx_stocks(force_refresh=True)
        now = datetime.datetime.now()
        inserted = 0
        updated = 0

        # Ensure database tables exist
        try:
            Base.metadata.create_all(bind=engine, tables=[StockUniverse.__table__], checkfirst=True)
        except Exception as e:
            print(f"[StockUniverse] Note on table ensure: {e}")

        try:
            with Session(engine) as session:
                # Query existing symbols in DB
                existing_records = {u.symbol: u for u in session.query(StockUniverse).all()}

                for item in stocks:
                    sym = cls.normalize_ticker(item["symbol"])
                    name = item.get("company_name") or sym.replace(".JK", "")
                    sec = item.get("sector") or "General"
                    brd = item.get("board") or "Utama"
                    mcap = item.get("shares", 0.0)

                    if sym in existing_records:
                        record = existing_records[sym]
                        record.company_name = name
                        record.sector = sec
                        record.board = brd
                        record.is_active = item.get("is_active", True)
                        record.last_update = now
                        updated += 1
                    else:
                        new_record = StockUniverse(
                            symbol=sym,
                            company_name=name,
                            sector=sec,
                            board=brd,
                            market_cap=mcap,
                            is_active=item.get("is_active", True),
                            last_update=now
                        )
                        session.add(new_record)
                        inserted += 1

                session.commit()
                print(f"[StockUniverse] DB Sync complete: {inserted} inserted, {updated} updated.")
        except Exception as e:
            print(f"[StockUniverse] Database sync error: {e}")

        return {
            "total_universe": len(stocks),
            "inserted_new_ipos": inserted,
            "updated_existing": updated,
            "last_update": now.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def get_universe_stats(cls) -> Dict[str, Any]:
        """
        Returns real-time universe statistics for Dashboard:
        - Total Universe: xxx saham
        - Aktif: xxx saham
        - Delisted / Non-aktif: xxx saham
        - Last Update: tanggal
        """
        stocks = cls.fetch_all_idx_stocks()
        total = len(stocks)
        active = sum(1 for s in stocks if s.get("is_active", True))
        inactive = total - active

        last_scan_dt = None
        try:
            from app.screener.batch_scanner_engine import BatchScannerEngine
            last_scan_dt = BatchScannerEngine._end_time or BatchScannerEngine._start_time
        except Exception:
            pass

        if not last_scan_dt:
            last_scan_dt = cls._CACHE_LAST_SYNC or datetime.datetime.now()

        last_sync_str = last_scan_dt.strftime("%d %B %Y")
        last_scan_formatted = last_scan_dt.strftime("%d %b %Y, %H:%M WIB")

        return {
            "total_universe": total,
            "active_stocks": active,
            "inactive_stocks": inactive,
            "universe_name": "IDX All Stock",
            "last_update": last_sync_str,
            "last_scan": last_scan_formatted,
            "display_label": f"{total} Emiten",
            "source_status": "Dinamis Terverifikasi"
        }

    @classmethod
    def deactivate_delisted(cls, symbol: str) -> bool:
        """Marks a delisted stock as is_active = False."""
        sym = cls.normalize_ticker(symbol)
        try:
            with Session(engine) as session:
                rec = session.query(StockUniverse).filter_by(symbol=sym).first()
                if rec:
                    rec.is_active = False
                    rec.last_update = datetime.datetime.now()
                    session.commit()
                    return True
        except Exception as e:
            print(f"[StockUniverse] Error deactivating {sym}: {e}")
        return False
