import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { ScreenerResultItem } from '../types/stock';

/**
 * Custom hook to fetch screener data with optional filtering.
 */
export function useScreener(params?: { signal?: string; min_score?: number; sort_by?: string }) {
  const [data, setData] = useState<ScreenerResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadScreener = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await api.getScreener(params);
      setData(result);
    } catch (err) {
      setError('Failed to load screener data');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadScreener();
  }, []);

  return { data, isLoading, error, refresh: loadScreener };
}
