import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union


class TechnicalIndicators:
    """
    Reusable Technical Indicator Calculator powered by pandas.
    Provides vectorized methods for Moving Averages (MA20, MA50, MA200),
    RSI, Volatility, Average Volume, and Trend determination.
    """

    @staticmethod
    def calculate_ma(series: pd.Series, window: int) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA/MA) for a given window.
        """
        return pd.Series(series.rolling(window=window, min_periods=1).mean().round(2))

    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI) using Wilder's Smoothing method.
        Bounded between 0.0 and 100.0.
        """
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)

        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()

        # Wilder's smoothing
        for i in range(period, len(series)):
            if pd.notna(gain.iloc[i]) and pd.notna(avg_gain.iloc[i - 1]):
                avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
            if pd.notna(loss.iloc[i]) and pd.notna(avg_loss.iloc[i - 1]):
                avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period

        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = pd.Series(100.0 - (100.0 / (1.0 + rs)))

        # Default fallback for initial periods or NaN
        return pd.Series(rsi.fillna(50.0).round(2))

    @staticmethod
    def calculate_volatility(series: pd.Series, window: int = 20, annualized: bool = True) -> pd.Series:
        """
        Calculate rolling standard deviation of percentage returns.
        Optionally annualizes the volatility using sqrt(252 trading days).
        """
        pct_returns = series.pct_change()
        vol = pct_returns.rolling(window=window, min_periods=5).std()
        if annualized:
            vol = vol * np.sqrt(252)
        return pd.Series(vol.fillna(0.0).round(4))

    @staticmethod
    def calculate_average_volume(series: pd.Series, window: int = 20) -> pd.Series:
        """
        Calculate the 20-period Simple Moving Average of Trading Volume.
        """
        return pd.Series(series.rolling(window=window, min_periods=1).mean().round(2))

    @staticmethod
    def determine_trend(price: float, ma20: Optional[float], ma50: Optional[float], ma200: Optional[float]) -> str:
        """
        Determine market trend direction based on price position and MA alignments.
        """
        if price is None:
            return "Unknown"

        if ma20 is not None and ma50 is not None and ma200 is not None:
            if price > ma20 > ma50 > ma200:
                return "Strong Uptrend"
            elif price > ma20 > ma50:
                return "Uptrend"
            elif price < ma20 < ma50 < ma200:
                return "Strong Downtrend"
            elif price < ma20 < ma50:
                return "Downtrend"
            elif price > ma20 and price < ma50:
                return "Consolidation / Pullback"
            else:
                return "Sideways"
        elif ma20 is not None and ma50 is not None:
            if price > ma20 > ma50:
                return "Uptrend"
            elif price < ma20 < ma50:
                return "Downtrend"
            else:
                return "Sideways"
        elif ma20 is not None:
            return "Uptrend" if price > ma20 else "Downtrend"

        return "Neutral"

    @classmethod
    def process_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies all indicator calculations to an OHLCV DataFrame in-place copy.
        Required columns: ['Close', 'Volume'].
        """
        if df.empty or "Close" not in df.columns:
            return df

        df = df.copy()
        if "Date" in df.columns:
            df = df.sort_values(by="Date").reset_index(drop=True)

        close = pd.Series(df["Close"])
        volume = pd.Series(df["Volume"]) if "Volume" in df.columns else pd.Series(0, index=df.index)

        # 1. Moving Averages
        df["MA20"] = cls.calculate_ma(close, window=20)
        df["MA50"] = cls.calculate_ma(close, window=50)
        df["MA200"] = cls.calculate_ma(close, window=200)

        # 2. RSI
        df["RSI"] = cls.calculate_rsi(close, period=14)

        # 3. Volatility
        df["volatility"] = cls.calculate_volatility(close, window=20, annualized=True)

        # 4. Average Volume & Volume Ratio
        df["avg_volume_20"] = cls.calculate_average_volume(volume, window=20)
        df["volume_ratio"] = (volume / df["avg_volume_20"].replace(0, np.nan)).fillna(1.0).round(2)

        return df

    @classmethod
    def get_summary(cls, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """
        Extracts the latest technical indicator metrics and formats them into the
        standardized JSON structure:
        {
            "symbol": str,
            "price": float,
            "MA20": float,
            "MA50": float,
            "MA200": float,
            "RSI": float,
            "volume_ratio": float,
            "trend": str
        }
        """
        if df.empty or "Close" not in df.columns:
            return {
                "symbol": symbol,
                "price": 0.0,
                "MA20": None,
                "MA50": None,
                "MA200": None,
                "RSI": None,
                "volume_ratio": 1.0,
                "trend": "Insufficient Data"
            }

        df_calc = cls.process_dataframe(df)
        latest = df_calc.iloc[-1]

        price = float(latest["Close"])
        ma20 = float(latest["MA20"]) if pd.notna(latest.get("MA20")) else None
        ma50 = float(latest["MA50"]) if pd.notna(latest.get("MA50")) else None
        ma200 = float(latest["MA200"]) if pd.notna(latest.get("MA200")) else None
        rsi = float(latest["RSI"]) if pd.notna(latest.get("RSI")) else None
        vol_ratio = float(latest["volume_ratio"]) if pd.notna(latest.get("volume_ratio")) else 1.0

        trend = cls.determine_trend(price, ma20, ma50, ma200)

        return {
            "symbol": symbol,
            "price": price,
            "MA20": ma20,
            "MA50": ma50,
            "MA200": ma200,
            "RSI": rsi,
            "volume_ratio": vol_ratio,
            "trend": trend
        }


# Convenience standalone function for direct imports
def calculate_technical_summary(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """Reusable standalone function returning the specified indicator JSON."""
    return TechnicalIndicators.get_summary(df, symbol)
