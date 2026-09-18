"""
Stock Universe Manager — IDX80 Only
=====================================
Simplified universe manager that operates exclusively on IDX80 constituents.
No external API calls, no CSV downloads, no cascading fallbacks.
The IDX80 ticker list is the authoritative source.
"""

import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.database.connection import get_db, engine, get_supabase, Base
from app.models.stock_model import IDX80Stock
from app.config.idx80_tickers import (
    IDX80_TICKERS,
    IDX80_METADATA,
    normalize_ticker,
    is_idx80,
    get_all_idx80_tickers,
    get_idx80_stocks_for_db,
)


class StockUniverseManager:
    """
    IDX80 Stock Universe Manager.

    Responsibilities:
    - Provides IDX80 ticker list as the only stock universe
    - Database synchronization (seed/update idx80_stocks table)
    - O(1) ticker lookups from IDX80_METADATA
    - Universe statistics for dashboard
    """

    _CACHE_UNIVERSE: List[Dict[str, Any]] = []
    _SYMBOL_LOOKUP: Dict[str, Dict[str, Any]] = {}
    _CACHE_LAST_SYNC: Optional[datetime.datetime] = None

    @classmethod
    def normalize_ticker(cls, symbol: str) -> str:
        """Ensures the ticker has the .JK Yahoo Finance suffix."""
        return normalize_ticker(symbol)

    @classmethod
    def get_stock_by_symbol(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """O(1) ticker lookup from IDX80 metadata."""
        sym = normalize_ticker(symbol)
        meta = IDX80_METADATA.get(sym)
        if meta:
            return {
                "symbol": sym,
                "code": sym.replace(".JK", ""),
                "company_name": meta["company_name"],
                "sector": meta["sector"],
                "market": "IDX80",
                "board": "Utama",
                "is_active": True,
            }
        return None

    @classmethod
    def fetch_from_database(cls) -> Optional[List[Dict[str, Any]]]:
        """
        Query active IDX80 stocks from idx80_stocks database table.
        Uses Supabase REST Client or SQLAlchemy engine session.
        """
        # 1. Try Supabase REST Client
        sb = get_supabase()
        if sb is not None:
            try:
                res = sb.table("idx80_stocks").select(
                    "ticker, company_name, sector, market, is_active"
                ).eq("is_active", True).execute()
                if res.data and len(res.data) > 10:
                    stocks = []
                    for row in res.data:
                        sym = normalize_ticker(row.get("ticker", ""))
                        stocks.append({
                            "symbol": sym,
                            "code": sym.replace(".JK", ""),
                            "company_name": row.get("company_name") or sym.replace(".JK", ""),
                            "sector": row.get("sector") or "IDX Equities",
                            "market": row.get("market") or "IDX80",
                            "board": "Utama",
                            "is_active": row.get("is_active", True),
                            "source": "DATABASE_SUPABASE"
                        })
                    print(f"[StockUniverse] Database: Loaded {len(stocks)} active IDX80 stocks from Supabase.")
                    return stocks
            except Exception as e:
                print(f"[StockUniverse] Supabase DB fetch notice: {e}")

        # 2. Try SQLAlchemy engine session
        if engine is not None:
            try:
                with Session(engine) as session:
                    records = session.query(IDX80Stock).filter_by(is_active=True).all()
                    if records and len(records) > 10:
                        stocks = []
                        for r in records:
                            sym = normalize_ticker(r.ticker)
                            stocks.append({
                                "symbol": sym,
                                "code": sym.replace(".JK", ""),
                                "company_name": r.company_name or sym.replace(".JK", ""),
                                "sector": r.sector or "IDX Equities",
                                "market": r.market or "IDX80",
                                "board": "Utama",
                                "is_active": r.is_active,
                                "source": "DATABASE_SQLALCHEMY"
                            })
                        print(f"[StockUniverse] Database: Loaded {len(stocks)} active IDX80 stocks from PostgreSQL.")
                        return stocks
            except Exception as e:
                print(f"[StockUniverse] SQLAlchemy DB fetch notice: {e}")

        return None

    @classmethod
    def fetch_all_idx_stocks(cls, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Returns the IDX80 stock universe.
        Source priority: Database → IDX80 config fallback.
        """
        if not force_refresh and cls._CACHE_UNIVERSE:
            return cls._CACHE_UNIVERSE

        # 1. Try database first
        stocks = cls.fetch_from_database()

        # 2. Fallback to IDX80 config (always available, no network needed)
        if not stocks:
            stocks = get_idx80_stocks_for_db()
            print(f"[StockUniverse] Using IDX80 config fallback: {len(stocks)} stocks.")

        cls._CACHE_UNIVERSE = stocks
        cls._SYMBOL_LOOKUP = {s["symbol"]: s for s in stocks}
        cls._CACHE_LAST_SYNC = datetime.datetime.now()
        return stocks

    @classmethod
    def get_active_symbols(cls, limit: Optional[int] = None) -> List[str]:
        """Returns IDX80 ticker list."""
        tickers = get_all_idx80_tickers()
        if limit:
            return tickers[:limit]
        return tickers

    @classmethod
    def sync_to_database(cls) -> Dict[str, Any]:
        """
        Seeds/updates the idx80_stocks table with IDX80 constituent data.
        No external API calls — uses the hardcoded IDX80 config.
        """
        stocks = get_idx80_stocks_for_db()
        now = datetime.datetime.now()
        inserted = 0
        updated = 0

        # Ensure database table exists
        try:
            Base.metadata.create_all(bind=engine, tables=[IDX80Stock.__table__], checkfirst=True)
        except Exception as e:
            print(f"[StockUniverse] Note on table ensure: {e}")

        try:
            with Session(engine) as session:
                existing_records = {u.ticker: u for u in session.query(IDX80Stock).all()}

                for item in stocks:
                    ticker = item["ticker"]
                    name = item["company_name"]
                    sector = item["sector"]
                    market = item.get("market", "IDX80")

                    if ticker in existing_records:
                        record = existing_records[ticker]
                        record.company_name = name
                        record.sector = sector
                        record.market = market
                        record.is_active = True
                        record.updated_at = now
                        updated += 1
                    else:
                        new_record = IDX80Stock(
                            ticker=ticker,
                            company_name=name,
                            sector=sector,
                            market=market,
                            is_active=True,
                            updated_at=now
                        )
                        session.add(new_record)
                        inserted += 1

                # Deactivate any tickers in DB that are no longer in IDX80
                idx80_set = {s["ticker"] for s in stocks}
                for ticker, record in existing_records.items():
                    if ticker not in idx80_set:
                        record.is_active = False
                        record.updated_at = now

                session.commit()
                print(f"[StockUniverse] IDX80 sync complete: {inserted} inserted, {updated} updated.")
        except Exception as e:
            print(f"[StockUniverse] Database sync error: {e}")

        # Refresh cache
        cls._CACHE_UNIVERSE = []
        cls.fetch_all_idx_stocks(force_refresh=True)

        return {
            "total_universe": len(stocks),
            "universe_name": "IDX80",
            "inserted_new": inserted,
            "updated_existing": updated,
            "last_update": now.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def get_universe_stats(cls) -> Dict[str, Any]:
        """
        Returns IDX80 universe statistics for Dashboard.
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
            "universe_name": "IDX80",
            "last_update": last_sync_str,
            "last_scan": last_scan_formatted,
            "display_label": f"{total} Emiten IDX80",
            "source_status": "IDX80 Whitelist"
        }
