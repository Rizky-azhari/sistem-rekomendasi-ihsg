"""
Bandarmology & Smart Money Accumulation Detector
=================================================
Mendeteksi fase akumulasi, netral, atau distribusi oleh investor institusi / smart money
berdasarkan analisis volume, price spread (VSA), dan aliran dana (Money Flow / CMF).
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def evaluate_bandar_accumulation(df: pd.DataFrame, symbol: str = "") -> Dict[str, Any]:
    """
    Menganalisis pergerakan volume dan spread harga untuk mendeteksi akumulasi bandar.

    Parameter yang dianalisis:
    1. Volume Surge Ratio vs Vol SMA20
    2. Close Location Value (CLV / posisi penutupan dalam rentang candle harian)
    3. Chaikin Money Flow (CMF 10-hari)
    4. Price vs Volume divergence (akumulasi tersembunyi / absorption)
    """
    if df is None or df.empty or "Close" not in df.columns or "Volume" not in df.columns or len(df) < 5:
        return {
            "status": "NETRAL",
            "score": 50.0,
            "volume_ratio": 1.0,
            "cmf": 0.0,
            "close_location": 0.5,
            "action": "Netral",
            "details": "Data volume dan harga historis belum mencukupi."
        }

    close = df["Close"]
    volume = df["Volume"].replace(0, np.nan).fillna(1)
    high = df["High"] if "High" in df.columns else close
    low = df["Low"] if "Low" in df.columns else close

    # 1. 20-day Volume Average
    vol_sma20 = float(volume.rolling(window=20, min_periods=3).mean().iloc[-1])
    current_vol = float(volume.iloc[-1])
    vol_ratio = round(current_vol / vol_sma20, 2) if vol_sma20 > 0 else 1.0

    # 2. Daily Price Spread & Close Location Value (CLV)
    last_close = float(close.iloc[-1])
    last_high = float(high.iloc[-1])
    last_low = float(low.iloc[-1])
    spread = max(1e-4, last_high - last_low)
    clv = round((last_close - last_low) / spread, 2)  # 0.0 = Low, 1.0 = High

    # 3. Daily Change Percentage
    prev_close = float(close.iloc[-2]) if len(close) >= 2 else last_close
    change_pct = round(((last_close - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0.0

    # 4. Chaikin Money Flow (CMF 10-day)
    try:
        mf_mult = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
        mf_vol = mf_mult.fillna(0.0) * volume
        cmf_series = mf_vol.rolling(window=10, min_periods=3).sum() / volume.rolling(window=10, min_periods=3).sum()
        cmf = round(float(cmf_series.iloc[-1]), 3) if not np.isnan(cmf_series.iloc[-1]) else 0.0
    except Exception:
        cmf = 0.0

    # 5. Determine Status & Bandar Score (0 - 100)
    # Akumulasi Masif: Volume >= 1.5x, penutupan di atas 55% rentang candle, dan CMF/Perubahan positif
    if (vol_ratio >= 1.5 and clv >= 0.55 and (change_pct >= 0.0 or cmf >= 0.05)) or (vol_ratio >= 2.0 and clv >= 0.5):
        status = "AKUMULASI MASIF"
        base_score = 80.0
        bonus_vol = min(12.0, (vol_ratio - 1.5) * 6.0)
        bonus_clv = min(8.0, (clv - 0.5) * 16.0)
        score = round(min(99.0, base_score + bonus_vol + bonus_clv), 1)
        action = "Akumulasi Masif"
        details = (
            f"Terdeteksi lonjakan volume signifikan {vol_ratio}x di atas rata-rata 20 hari "
            f"dengan posisi penutupan di {int(clv * 100)}% rentang candle, mengonfirmasi aliran likuiditas beli besar (Smart Money Inflow)."
        )

    # Akumulasi Normal: Volume >= 1.15x, penutupan di separuh atas, atau CMF solid
    elif (vol_ratio >= 1.15 and clv >= 0.48 and change_pct >= -0.5) or (cmf >= 0.08 and clv >= 0.5):
        status = "AKUMULASI NORMAL"
        base_score = 62.0
        bonus_vol = min(10.0, (vol_ratio - 1.0) * 8.0)
        bonus_cmf = min(8.0, max(0.0, cmf * 40.0))
        score = round(min(79.0, base_score + bonus_vol + bonus_cmf), 1)
        action = "Akumulasi Normal"
        details = (
            f"Aktivitas akumulasi teratur dengan volume {vol_ratio}x Vol SMA20 "
            f"dan Money Flow positif (CMF: {cmf:+0.2f}), mengindikasikan serapan saham secara bertahap."
        )

    # Distribusi: Volume besar saat harga dibanting turun atau penutupan di dasar candle
    elif (vol_ratio >= 1.25 and change_pct <= -1.2 and clv <= 0.4) or (cmf <= -0.12 and change_pct < 0):
        status = "DISTRIBUSI"
        score = round(max(10.0, 40.0 - min(25.0, (vol_ratio - 1.0) * 15.0)), 1)
        action = "Distribusi"
        details = (
            f"Tekanan jual institusi terdeteksi dengan volume {vol_ratio}x "
            f"dan pelemahan harga {change_pct}%, penutupan berada di area bawah ({int(clv * 100)}%)."
        )

    # Netral: Aktivitas perdagangan wajar tanpa anomali volume
    else:
        status = "NETRAL"
        score = round(45.0 + max(-10.0, min(10.0, change_pct * 2.0)), 1)
        action = "Netral"
        details = f"Volume relatif berimbang ({vol_ratio}x vs 20-day avg) tanpa indikasi akumulasi atau distribusi agresif."

    return {
        "status": status,
        "score": score,
        "volume_ratio": vol_ratio,
        "cmf": cmf,
        "close_location": clv,
        "action": action,
        "details": details
    }
