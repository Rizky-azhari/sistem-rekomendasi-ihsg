import os
import sys
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv
try:
    from sqlalchemy import create_engine  # type: ignore
    from sqlalchemy.orm import sessionmaker, declarative_base  # type: ignore
except ImportError:
    create_engine = None  # type: ignore
    sessionmaker = None  # type: ignore
    declarative_base = lambda: None  # type: ignore

# Add backend directory to sys.path so this file can be executed directly from anywhere
BACKEND_DIR = str(Path(__file__).resolve().parent.parent.parent)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Load environment variables
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

try:
    from app.core.config import settings
except ImportError:
    from backend.app.core.config import settings

# SQLAlchemy engine & session for Supabase PostgreSQL
DATABASE_URL = settings.DATABASE_URL or os.getenv("DATABASE_URL", "")

engine = None
SessionLocal = None
Base = declarative_base()

# Initialize Supabase Python Client (REST API)
supabase_client: Optional[Any] = None
supabase_url = settings.SUPABASE_URL or os.getenv("SUPABASE_URL", "")
supabase_key = settings.SUPABASE_SECRET_KEY or os.getenv("SUPABASE_SECRET_KEY", "") or settings.SUPABASE_KEY or os.getenv("SUPABASE_KEY", "")

if supabase_url and supabase_key:
    try:
        from supabase import create_client  # type: ignore
        supabase_client = create_client(supabase_url, supabase_key)
        print("[DB] Supabase Python Client connected successfully via HTTPS.")
    except Exception as e:
        print(f"[DB] Warning: Could not initialize Supabase client: {e}")

if DATABASE_URL:
    try:
        # connect_timeout prevents long freezes if network has IPv6 routing issues
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=False,
            connect_args={"connect_timeout": 5}
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print(f"[DB] SQLAlchemy engine configured: {DATABASE_URL.split('@')[-1]}")
    except Exception as e:
        print(f"[DB] Warning: Could not create engine: {e}")
        engine = None
        SessionLocal = None
else:
    print("[DB] No DATABASE_URL configured.")


def get_db():
    """Dependency: yields a database session, auto-closes on completion."""
    if SessionLocal is None:
        raise RuntimeError("Database is not configured. Set DATABASE_URL in .env")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_raw_connection():
    """Returns a raw psycopg2 connection if direct database is reachable."""
    if not DATABASE_URL:
        return None
    try:
        import psycopg2  # type: ignore
        return psycopg2.connect(DATABASE_URL, connect_timeout=5)
    except Exception as e:
        print(f"[DB] Notice: raw psycopg2 connection failed ({e})")
        return None


def get_supabase():
    """Dependency: yields the Supabase client."""
    return supabase_client


def get_supabase_admin():
    """
    Returns an isolated Supabase client initialized directly with SUPABASE_SECRET_KEY,
    guaranteeing unpolluted admin access for auth.admin operations.
    """
    url = settings.SUPABASE_URL or os.getenv("SUPABASE_URL", "")
    secret_key = settings.SUPABASE_SECRET_KEY or os.getenv("SUPABASE_SECRET_KEY", "") or settings.SUPABASE_KEY or os.getenv("SUPABASE_KEY", "")
    if url and secret_key:
        try:
            from supabase import create_client  # type: ignore
            return create_client(url, secret_key)
        except Exception as e:
            print(f"[DB] Error creating fresh admin Supabase client: {e}")
    return supabase_client


def init_db():
    """Create all tables defined by ORM models. Gracefully skips if direct connection fails."""
    try:
        import app.models.stock_model  # noqa: F401
    except ImportError:
        import backend.app.models.stock_model  # noqa: F401

    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
            print("[DB] Tables created/verified successfully on PostgreSQL.")
        except Exception as e:
            print(f"[DB] Notice: Direct PostgreSQL connection failed ({type(e).__name__}).")
            print("[DB] Note: db.<ref>.supabase.co requires IPv6 or connection pooler. HTTPS client remains active.")
    else:
        print("[DB] Skipping table creation — no database engine available.")


if __name__ == "__main__":
    print("Testing connection.py directly...")
    print("DATABASE_URL configured:", bool(DATABASE_URL))
    print("Supabase Client:", supabase_client)
    print("SQLAlchemy Engine:", engine)
    init_db()
