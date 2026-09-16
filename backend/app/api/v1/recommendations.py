from fastapi import APIRouter, HTTPException
import datetime
from app.services.yfinance_service import fetch_stock_info, fetch_stock_history, normalize_symbol
from app.engine.indicators import calculate_technical_indicators
from app.engine.rules import evaluate_rules
from app.engine.trading_plan import generate_trading_plan
from app.schemas.recommendation import RecommendationResponse

router = APIRouter()

@router.get("/{symbol}", response_model=RecommendationResponse)
def get_recommendation(symbol: str):
    sym = normalize_symbol(symbol)
    info = fetch_stock_info(sym)
    df_raw = fetch_stock_history(sym, period="1y")
    
    if df_raw.empty:
        raise HTTPException(status_code=404, detail=f"Stock data not available for {sym}")
        
    df_ind = calculate_technical_indicators(df_raw)
    dss_result = evaluate_rules(df_ind)
    trading_plan = generate_trading_plan(df_ind, dss_result["signal"])
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return RecommendationResponse(
        symbol=sym,
        name=info.get("name", sym.replace(".JK", "")),
        current_price=float(info.get("current_price", 0.0)),
        signal=dss_result["signal"],
        total_score=dss_result["total_score"],
        confidence_level=dss_result["confidence_level"],
        summary=dss_result["summary"],
        rule_breakdowns=dss_result["rule_breakdowns"],
        trading_plan=trading_plan,
        updated_at=current_time
    )
