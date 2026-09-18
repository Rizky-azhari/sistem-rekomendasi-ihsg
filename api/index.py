"""
Vercel Serverless Function — IDX80 Only
==========================================
Entry point for Vercel serverless deployment with IDX80 validation.
"""

import sys
import os
from pathlib import Path
from typing import Optional

# 1. Path Resolution: add project root and backend directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.core.config import settings
from app.api.v1 import stocks, recommendations, screening, auth, admin, reports
from app.routes.ihsg_routes import router as ihsg_router
from app.database.connection import init_db, get_supabase
from app.core.idx80_validator import IDX80ValidationError

# Lazy DB Initialization flag
_DB_INITIALIZED = False

def ensure_db():
    global _DB_INITIALIZED
    if not _DB_INITIALIZED:
        try:
            init_db()
            _DB_INITIALIZED = True
        except Exception as e:
            print(f"[API Serverless] Warning initializing DB: {e}")

# Create FastAPI App
app = FastAPI(
    title=f"{settings.PROJECT_NAME} (Vercel Serverless — IDX80)",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IDX80 validation exception handler
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

# Global Exception Handler for resilience
@app.middleware("http")
async def db_and_error_middleware(request: Request, call_next):
    ensure_db()
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        print(f"[API Error] Path: {request.url.path} Error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(exc), "path": request.url.path}
        )

# 3. Mount Routes under /api prefix (Primary endpoints)
app.include_router(ihsg_router, prefix="/api")
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(recommendations.router, prefix="/api/recommendation", tags=["recommendation-alias"])
app.include_router(screening.router, prefix="/api/screening", tags=["screening"])
app.include_router(screening.router, prefix="/api/scanner", tags=["scanner-alias"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

# 4. Mount Routes under /api/v1 prefix for backward compatibility
app.include_router(ihsg_router, prefix="/api/v1")
app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["stocks-v1"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations-v1"])
app.include_router(screening.router, prefix="/api/v1/screening", tags=["screening-v1"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth-v1"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin-v1"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports-v1"])

# Also mount under root
app.include_router(ihsg_router)

# Health & Root Check Endpoints
@app.get("/api")
@app.get("/api/health")
@app.get("/health")
def serverless_health():
    ensure_db()
    return {
        "status": "ok",
        "runtime": "Vercel Serverless Function (Python Mangum)",
        "universe": "IDX80",
        "supabase_connected": get_supabase() is not None,
        "endpoints": {
            "stocks": "/api/stocks",
            "scanner": "/api/screener/rules",
            "recommendation": "/api/recommendations/{symbol}",
            "auth": "/api/auth/login",
            "market": "/api/market/ihsg",
            "docs": "/api/docs"
        }
    }

# 5. Mangum Adapter Entrypoint for Vercel Serverless Function
handler = Mangum(app, lifespan="off")
