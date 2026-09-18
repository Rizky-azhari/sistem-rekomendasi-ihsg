import axios from 'axios';
import type { StockDetailResponse, RecommendationResponse, ScreenerResultItem } from '../types/stock';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const api = {
  searchStocks: async (query: string = '') => {
    const res = await axios.get(`${API_BASE}/stocks/search`, { params: { q: query } });
    return res.data;
  },

  getStockDetail: async (symbol: string, period: string = '1y'): Promise<StockDetailResponse> => {
    const res = await axios.get(`${API_BASE}/stocks/${symbol}`, { params: { period } });
    return res.data;
  },

  getRecommendation: async (symbol: string): Promise<RecommendationResponse> => {
    const res = await axios.get(`${API_BASE}/recommendations/${symbol}`);
    return res.data;
  },

  getScreener: async (params?: {
    signal?: string;
    min_score?: number;
    sort_by?: string;
  }): Promise<ScreenerResultItem[]> => {
    const res = await axios.get(`${API_BASE}/screening`, { params });
    return res.data;
  }
};
