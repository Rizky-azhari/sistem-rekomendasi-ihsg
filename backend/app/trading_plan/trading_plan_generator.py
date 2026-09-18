import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union


class TradingPlanGenerator:
    """
    Automated Trading Plan Generator for IHSG Stocks.
    
    Uses:
      - Support (Price action swing low / dynamic level)
      - Resistance (Price action swing high / key ceiling)
      - ATR (Average True Range 14-period volatility distance)
      - Volatility (Standard deviation / Normalized ATR %)
      
    Output format:
      {
        "buy_area": "",
        "stop_loss": "",
        "tp1": "",
        "tp2": "",
        "tp3": "",
        "risk_reward": ""
      }
    """

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
        """Calculates 14-period Average True Range (ATR)."""
        if df.empty or len(df) < 2:
            return 0.0
        
        high = df["High"] if "High" in df.columns else df["Close"]
        low = df["Low"] if "Low" in df.columns else df["Close"]
        close = df["Close"]
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_series = tr.rolling(window=period, min_periods=1).mean()
        
        latest_atr = float(atr_series.iloc[-1])
        if pd.isna(latest_atr) or latest_atr <= 0:
            latest_atr = float(close.iloc[-1]) * 0.025
        return round(latest_atr, 2)

    @staticmethod
    def calculate_volatility(df: pd.DataFrame, period: int = 20) -> float:
        """
        Calculates 20-day annualized historical volatility percentage.
        """
        if df.empty or len(df) < 5 or "Close" not in df.columns:
            return 20.0  # default 20% volatility
        
        close = df["Close"]
        log_returns = np.log(close / close.shift(1)).dropna()
        if len(log_returns) < 5:
            return 20.0
            
        std_dev = log_returns.tail(period).std()
        if pd.isna(std_dev) or std_dev <= 0:
            return 20.0
            
        ann_vol = float(std_dev * np.sqrt(252) * 100)
        return round(ann_vol, 2)

    @staticmethod
    def identify_support_resistance(df: pd.DataFrame, lookback: int = 20) -> Dict[str, float]:
        """
        Identifies key Support and Resistance levels from recent price action.
        """
        if df.empty or "Close" not in df.columns:
            return {"support": 0.0, "resistance": 0.0}

        close = df["Close"]
        high = df["High"] if "High" in df.columns else close
        low = df["Low"] if "Low" in df.columns else close
        current_price = float(close.iloc[-1])

        # Support: Nearest 20-day swing low or 2.5% below price
        recent_low = float(low.tail(lookback).min())  # type: ignore
        if recent_low >= current_price:
            support = round(current_price * 0.97, 2)
        else:
            support = round(recent_low, 2)

        # Resistance: Nearest 20-day or 50-day swing high
        recent_high = float(high.tail(lookback).max())  # type: ignore
        if recent_high <= current_price:
            # Price at or above 20-day high: use 50-day or project 3% above
            extended_high = float(high.tail(min(50, len(high))).max())  # type: ignore
            if extended_high > current_price:
                resistance = round(extended_high, 2)
            else:
                resistance = round(current_price * 1.05, 2)
        else:
            resistance = round(recent_high, 2)

        return {"support": support, "resistance": resistance}

    @classmethod
    def generate_plan_from_values(
        cls,
        current_price: float,
        support: float,
        resistance: float,
        atr: float,
        volatility: float = 20.0,
        currency_prefix: str = "Rp "
    ) -> Dict[str, str]:
        """
        Constructs the Trading Plan strictly from provided Support, Resistance, ATR, and Volatility values.
        
        Returns exact dictionary format:
          {
            "buy_area": "",
            "stop_loss": "",
            "tp1": "",
            "tp2": "",
            "tp3": "",
            "risk_reward": ""
          }
        """
        price = float(current_price)
        if price <= 0:
            return {
                "buy_area": "N/A",
                "stop_loss": "N/A",
                "tp1": "N/A",
                "tp2": "N/A",
                "tp3": "N/A",
                "risk_reward": "N/A"
            }

        supp = float(support) if support > 0 else (price * 0.96)
        res = float(resistance) if resistance > price else (price * 1.05)
        atr_val = float(atr) if atr > 0 else (price * 0.025)
        vol_pct = float(volatility) if volatility > 0 else 20.0

        # 1. Buy Area Calculation:
        # Lower bound: Near support or pullback buffer (price - 0.5x ATR)
        # Upper bound: Current price with minor entry tolerance (+0.5% or +0.25x ATR)
        buy_low = round(max(supp, price - (0.6 * atr_val)), 0)
        buy_high = round(min(price * 1.008, price + (0.3 * atr_val)), 0)
        if buy_low >= buy_high:
            buy_low = round(price * 0.985, 0)
            buy_high = round(price * 1.005, 0)

        # 2. Stop Loss Calculation:
        # Placed below Support buffered by 0.5x ATR adjusted for market volatility
        vol_multiplier = 1.0 + min(0.5, (vol_pct / 100.0))
        atr_buffer = 0.5 * atr_val * vol_multiplier
        candidate_sl = supp - atr_buffer

        # Safeguards: Risk should be at least 2% and at most 8%
        min_sl = price * 0.92  # max 8% risk
        max_sl = price * 0.98  # min 2% risk
        sl_val = round(max(min_sl, min(max_sl, candidate_sl)), 0)

        risk = price - sl_val
        if risk <= 0:
            risk = round(price * 0.03, 0)
            sl_val = round(price - risk, 0)

        # 3. Take Profit Levels:
        # TP1 (Conservative): First Key Resistance or 1.5x Risk
        tp1_candidate = max(res, price + (1.5 * risk))
        tp1_val = round(max(price * 1.02, tp1_candidate), 0)

        # TP2 (Swing / Mid Target): 2.5x to 3.0x Risk
        tp2_val = round(price + (2.5 * risk), 0)

        # TP3 (Extended / Runner Target): 4.0x Risk (Runner expansion)
        tp3_val = round(price + (4.0 * risk), 0)

        # 4. Risk Reward Ratio (based on TP2 standard target):
        reward = tp2_val - price
        rr_ratio = round((reward / risk), 2) if risk > 0 else 2.5
        rr_formatted = f"1:{rr_ratio}"

        def fmt_price(val: float) -> str:
            return f"{currency_prefix}{int(val):,}"

        return {
            "buy_area": f"{fmt_price(buy_low)} - {fmt_price(buy_high)}",
            "stop_loss": fmt_price(sl_val),
            "tp1": fmt_price(tp1_val),
            "tp2": fmt_price(tp2_val),
            "tp3": fmt_price(tp3_val),
            "risk_reward": rr_formatted
        }

    @classmethod
    def generate(
        cls,
        data: Union[pd.DataFrame, Dict[str, Any]],
        symbol: str = "",
        currency_prefix: str = "Rp "
    ) -> Dict[str, str]:
        """
        Main entry point for Trading Plan generation.
        Accepts either an OHLCV DataFrame or a dictionary containing price/indicator fields.
        """
        if isinstance(data, pd.DataFrame):
            if data.empty or "Close" not in data.columns:
                return {
                    "buy_area": "N/A",
                    "stop_loss": "N/A",
                    "tp1": "N/A",
                    "tp2": "N/A",
                    "tp3": "N/A",
                    "risk_reward": "N/A"
                }

            current_price = float(data["Close"].iloc[-1])
            atr = cls.calculate_atr(data, period=14)
            volatility = cls.calculate_volatility(data, period=20)
            sr = cls.identify_support_resistance(data, lookback=20)
            support = sr["support"]
            resistance = sr["resistance"]

        elif isinstance(data, dict):
            current_price = float(data.get("price") or data.get("current_price") or data.get("close") or 0.0)
            support = float(data.get("support") or 0.0)
            resistance = float(data.get("resistance") or 0.0)
            atr = float(data.get("atr") or data.get("ATR") or (current_price * 0.025))
            volatility = float(data.get("volatility") or 20.0)
        else:
            raise ValueError("Input data must be a pandas DataFrame or a dictionary.")

        return cls.generate_plan_from_values(
            current_price=current_price,
            support=support,
            resistance=resistance,
            atr=atr,
            volatility=volatility,
            currency_prefix=currency_prefix
        )


def generate_trading_plan_dict(
    df_or_dict: Union[pd.DataFrame, Dict[str, Any]],
    symbol: str = "",
    currency_prefix: str = "Rp "
) -> Dict[str, str]:
    """Helper functional wrapper returning exact dictionary format."""
    return TradingPlanGenerator.generate(df_or_dict, symbol=symbol, currency_prefix=currency_prefix)
