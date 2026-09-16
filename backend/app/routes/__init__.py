# Routes package init
from .stock_routes import router as stock_router
from .recommendation_routes import router as recommendation_router
from .screener_routes import router as screener_router

__all__ = ["stock_router", "recommendation_router", "screener_router"]
