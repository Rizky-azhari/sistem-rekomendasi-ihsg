from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1 import stocks, recommendations, screening, auth, admin, reports
from app.routes.ihsg_routes import router as ihsg_router
from app.database.connection import init_db, get_supabase
from app.core.idx80_validator import IDX80ValidationError


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables and connections
    init_db()
    
    # Start daily universe scheduler in background
    try:
        from app.universe.scheduler import UniverseScheduler
        UniverseScheduler.start()
    except Exception as e:
        print(f"[Main] Warning starting UniverseScheduler: {e}")

    # Kick off IDX80 quick scan in background so dashboard has instant data
    try:
        import threading
        from app.screener.batch_scanner_engine import BatchScannerEngine
        threading.Thread(
            target=BatchScannerEngine._initialize_quick_top_universe,
            daemon=True,
            name="IDX80QuickInit"
        ).start()
    except Exception as e:
        print(f"[Main] Warning starting initial IDX80 quick scan: {e}")

    yield
    # Shutdown logic
    try:
        from app.universe.scheduler import UniverseScheduler
        UniverseScheduler.stop()
    except Exception:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IDX80 validation exception handler — returns 400 for non-IDX80 tickers
@app.exception_handler(IDX80ValidationError)
async def handle_idx80_validation_error(request: Request, exc: IDX80ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "ticker": exc.symbol,
            "allowed_universe": "IDX80"
        }
    )

# 1. Direct root endpoints as requested (/stocks, /stock/{symbol}, /analysis/{symbol})
app.include_router(ihsg_router)

# 2. Mount Routes under /api prefix (Primary endpoints for Vite proxy & client.ts)
app.include_router(ihsg_router, prefix="/api")
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(recommendations.router, prefix="/api/recommendation", tags=["recommendation-alias"])
app.include_router(screening.router, prefix="/api/screening", tags=["screening"])
app.include_router(screening.router, prefix="/api/scanner", tags=["scanner-alias"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

# 3. Versioned API Routers (/api/v1/...)
app.include_router(ihsg_router, prefix=settings.API_V1_STR)
app.include_router(stocks.router, prefix=f"{settings.API_V1_STR}/stocks", tags=["stocks-v1"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["recommendations-v1"])
app.include_router(screening.router, prefix=f"{settings.API_V1_STR}/screening", tags=["screening-v1"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth-v1"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin-v1"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports-v1"])



@app.get("/")
def root():
    return {
        "message": "Welcome to IHSG Smart Stock Recommendation API (IDX80 Universe)",
        "universe": "IDX80",
        "universe_count": 80,
        "endpoints": {
            "stocks": "/stocks",
            "stock_detail": "/stock/{symbol} (e.g. /stock/BBCA.JK)",
            "analysis": "/analysis/{symbol} (e.g. /analysis/BBCA.JK)",
            "screener": "/screener/rules",
            "docs": "/docs"
        },
        "version": "2.0.0",
        "supabase_connected": get_supabase() is not None
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "universe": "IDX80",
        "supabase_connected": get_supabase() is not None
    }
