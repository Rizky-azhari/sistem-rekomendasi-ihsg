import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { StockDetailResponse, RecommendationResponse } from '../types/stock';

/**
 * Custom hook to fetch stock detail data and recommendation by symbol.
 */
export function useStockData(symbol: string) {
  const [stockDetail, setStockDetail] = useState<StockDetailResponse | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) return;
    setIsLoading(true);
    setError(null);

    Promise.all([api.getStockDetail(symbol), api.getRecommendation(symbol)])
      .then(([detail, rec]) => {
        setStockDetail(detail);
        setRecommendation(rec);
      })
      .catch((err) => {
        setError(`Failed to load data for ${symbol}`);
        console.error(err);
      })
      .finally(() => setIsLoading(false));
  }, [symbol]);

  return { stockDetail, recommendation, isLoading, error };
}
