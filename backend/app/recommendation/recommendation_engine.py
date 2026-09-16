from typing import Dict, Any, List, Optional
import math


class RecommendationEngine:
    """
    IHSG Stock Recommendation Engine based on 5-Factor Screener Scores.
    
    Formula:
      Final Score = (Trend * 25%) + (Momentum * 25%) + (Breakout * 20%) + (Oversold * 10%) + (Trading Setup * 20%)
      
    Classification:
      85 - 100 : STRONG BUY
      70 - 84  : BUY
      50 - 69  : HOLD
      < 50     : SELL
    """
    
    # Standard Weights
    WEIGHTS = {
        "trend": 0.25,
        "momentum": 0.25,
        "breakout": 0.20,
        "oversold": 0.10,
        "trading_setup": 0.20
    }

    @classmethod
    def calculate_final_score(
        cls,
        trend: float = 0.0,
        momentum: float = 0.0,
        breakout: float = 0.0,
        oversold: float = 0.0,
        trading_setup: float = 0.0
    ) -> float:
        """
        Calculates weighted final score (0 - 100) using the exact formula.
        """
        trend_s = max(0.0, min(100.0, float(trend or 0.0)))
        mom_s = max(0.0, min(100.0, float(momentum or 0.0)))
        brk_s = max(0.0, min(100.0, float(breakout or 0.0)))
        ovs_s = max(0.0, min(100.0, float(oversold or 0.0)))
        stp_s = max(0.0, min(100.0, float(trading_setup or 0.0)))

        score = (
            (trend_s * cls.WEIGHTS["trend"]) +
            (mom_s * cls.WEIGHTS["momentum"]) +
            (brk_s * cls.WEIGHTS["breakout"]) +
            (ovs_s * cls.WEIGHTS["oversold"]) +
            (stp_s * cls.WEIGHTS["trading_setup"])
        )
        return round(score, 2)

    @classmethod
    def determine_recommendation(cls, final_score: float) -> str:
        """
        Maps final score to recommendation signal:
          85 - 100: STRONG BUY
          70 - 84 : BUY
          50 - 69 : HOLD
          < 50    : SELL
        """
        if final_score >= 85.0:
            return "STRONG BUY"
        elif final_score >= 70.0:
            return "BUY"
        elif final_score >= 50.0:
            return "HOLD"
        else:
            return "SELL"

    @classmethod
    def generate_reasons(
        cls,
        recommendation: str,
        trend: float,
        momentum: float,
        breakout: float,
        oversold: float,
        trading_setup: float,
        details: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Generates contextual Indonesian reasons for the recommendation.
        Example:
          - trend bullish
          - volume meningkat
          - breakout resistance
        """
        reasons: List[str] = []
        details = details or {}

        # 1. STRONG BUY / BUY Reasons
        if recommendation in ("STRONG BUY", "BUY"):
            # Trend reason
            if trend >= 70:
                reasons.append("trend bullish")
            elif trend >= 50:
                reasons.append("trend dalam fase akumulasi positif")

            # Momentum reason
            if momentum >= 70:
                reasons.append("volume meningkat")
            elif momentum >= 60:
                reasons.append("momentum bergerak di atas MA20")

            # Breakout reason
            if breakout >= 70:
                reasons.append("breakout resistance")
            elif breakout >= 50:
                reasons.append("harga menguji resistance terdekat")

            # Trading Setup reason
            if trading_setup >= 70:
                reasons.append("risk reward menarik (>= 1:2)")
            elif trading_setup >= 50:
                reasons.append("setup trading memenuhi parameter rasio risiko")

            # Oversold reason
            if oversold >= 70:
                reasons.append("kondisi oversold dekat area support kuat")

            # Fallback if few high scores triggered
            if len(reasons) < 2:
                reasons.append("indikator teknikal berada dalam zona apresiasi")
                if trend >= momentum:
                    reasons.append("didukung struktur tren jangka menengah")
                else:
                    reasons.append("didukung aliran likuiditas beli")

        # 2. HOLD Reasons
        elif recommendation == "HOLD":
            if 50 <= trend < 70:
                reasons.append("trend sideways / konsolidasi")
            elif trend < 50:
                reasons.append("trend belum mengkonfirmasi kelanjutan bullish")
            else:
                reasons.append("trend masih bertahan di atas support")

            if momentum < 70:
                reasons.append("volume transaksi belum ada lonjakan signifikan")
            else:
                reasons.append("momentum terjaga namun menunggu konfirmasi harga")

            if breakout < 70:
                reasons.append("belum terkonfirmasi breakout resistance")

            if trading_setup < 70:
                reasons.append("menunggu risk/reward setup yang lebih optimal")

            if oversold >= 60:
                reasons.append("harga mulai mendekati area pantulan teknikal")

        # 3. SELL Reasons (< 50)
        else:  # SELL
            if trend < 50:
                reasons.append("trend bearish (berada di bawah moving average)")
            else:
                reasons.append("terjadi pelemahan struktur tren")

            if momentum < 50:
                reasons.append("momentum melemah (harga di bawah MA20)")
            else:
                reasons.append("tekanan jual mulai mendominasi volume")

            if breakout < 50:
                reasons.append("gagal menembus level resistance")

            if trading_setup < 50:
                reasons.append("rasio risk to reward tidak menguntungkan (< 1:2)")

            if oversold < 30:
                reasons.append("belum ada tanda-tanda jenuh jual (oversold) yang valid")

        return reasons

    @classmethod
    def evaluate(
        cls,
        scores: Dict[str, float],
        symbol: str = "",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates screener scores and produces complete Recommendation Output.

        Input scores can use keys:
          - 'trend' or 'trend_score'
          - 'momentum' or 'momentum_score'
          - 'breakout' or 'breakout_score'
          - 'oversold' or 'oversold_score'
          - 'trading_setup' or 'trading_setup_score'
        """
        trend = float(scores.get("trend") or scores.get("trend_score") or 0.0)
        momentum = float(scores.get("momentum") or scores.get("momentum_score") or 0.0)
        breakout = float(scores.get("breakout") or scores.get("breakout_score") or 0.0)
        oversold = float(scores.get("oversold") or scores.get("oversold_score") or 0.0)
        trading_setup = float(scores.get("trading_setup") or scores.get("trading_setup_score") or 0.0)

        final_score = cls.calculate_final_score(
            trend=trend,
            momentum=momentum,
            breakout=breakout,
            oversold=oversold,
            trading_setup=trading_setup
        )

        recommendation = cls.determine_recommendation(final_score)
        reasons = cls.generate_reasons(
            recommendation=recommendation,
            trend=trend,
            momentum=momentum,
            breakout=breakout,
            oversold=oversold,
            trading_setup=trading_setup,
            details=details
        )

        # Format alasan rekomendasi sesuai contoh:
        # BUY karena:
        # - trend bullish
        # - volume meningkat
        # - breakout resistance
        alasan_bullets = "\n".join([f"- {r}" for r in reasons])
        alasan_text = f"{recommendation} karena:\n{alasan_bullets}"

        return {
            "symbol": symbol,
            "final_score": final_score,
            "recommendation": recommendation,
            "reasons": reasons,
            "alasan_rekomendasi": alasan_text,
            "scores": {
                "trend": trend,
                "momentum": momentum,
                "breakout": breakout,
                "oversold": oversold,
                "trading_setup": trading_setup
            },
            "formula": "Final Score = (Trend*25%) + (Momentum*25%) + (Breakout*20%) + (Oversold*10%) + (Trading Setup*20%)",
            "weights": cls.WEIGHTS
        }


def get_recommendation_from_scores(
    scores: Dict[str, float],
    symbol: str = "",
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Helper functional wrapper for RecommendationEngine.evaluate."""
    return RecommendationEngine.evaluate(scores=scores, symbol=symbol, details=details)
