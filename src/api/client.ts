import axios from 'axios';
import type {
  StockDetailResponse,
  RecommendationResponse,
  ScreenerResultItem,
  IHSGMarketData,
  TradingPlanOutput,
  ScreenerRuleItem,
  UniverseStats,
  ScanningProgress
} from '../types/stock';

// All requests go through /api/ which Vercel Serverless routes to api/index.py
const ROOT_API = '/api';
const API_BASE = '/api/v1';

// Token interceptor
let authToken: string | null = localStorage.getItem('ihsg_auth_token');

export const setApiAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    localStorage.setItem('ihsg_auth_token', token);
  } else {
    localStorage.removeItem('ihsg_auth_token');
  }
};

// Set global axios timeout
axios.defaults.timeout = 30000;

axios.interceptors.request.use((config) => {
  if (authToken && config.headers) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      console.warn('[API Timeout] Request exceeded 30s limit.');
    }
    return Promise.reject(error);
  }
);

export const api = {
  // --- AUTHENTICATION (GOOGLE OAUTH & EMAIL) ---
  loginEmail: async (email: string, password: string) => {
    const res = await axios.post(`${API_BASE}/auth/login`, { email, password });
    if (res.data?.access_token) {
      setApiAuthToken(res.data.access_token);
    }
    return res.data;
  },

  requestPasswordReset: async (email: string) => {
    const res = await axios.post(`${API_BASE}/auth/request-reset`, { email });
    return res.data;
  },

  verifyPasswordReset: async (email: string, code: string, newPassword: string) => {
    const res = await axios.post(`${API_BASE}/auth/verify-reset`, {
      email,
      code,
      new_password: newPassword
    });
    return res.data;
  },

  syncGoogleCallback: async () => {
    const res = await axios.post(`${API_BASE}/auth/callback-sync`);
    return res.data;
  },

  logout: async () => {
    try {
      await axios.post(`${API_BASE}/auth/logout`);
    } catch {
      // ignore
    } finally {
      setApiAuthToken(null);
    }
  },

  getMe: async () => {
    const res = await axios.get(`${API_BASE}/auth/me`);
    return res.data;
  },

  // --- ADMIN MANAGEMENT (ADMIN ROLE ONLY) ---
  getAdminUsers: async () => {
    const res = await axios.get(`${API_BASE}/admin/users`);
    return res.data;
  },

  updateUserRole: async (userId: string, role: string) => {
    const res = await axios.put(`${API_BASE}/admin/users/${userId}/role`, { role });
    return res.data;
  },

  deleteUser: async (userId: string) => {
    const res = await axios.delete(`${API_BASE}/admin/users/${userId}`);
    return res.data;
  },

  getAdminActivities: async (limit: number = 50, action?: string) => {
    const res = await axios.get(`${API_BASE}/admin/activities`, {
      params: { limit, action: action || undefined }
    });
    return res.data;
  },

  getAdminReports: async () => {
    const res = await axios.get(`${API_BASE}/admin/reports`);
    return res.data;
  },

  // --- REPORTS (USER & ADMIN) ---
  getReports: async (symbol?: string) => {
    const res = await axios.get(`${API_BASE}/reports`, {
      params: symbol ? { symbol } : undefined
    });
    return res.data;
  },

  createReport: async (payload: {
    title: string;
    symbol: string;
    report_type?: string;
    recommendation?: string;
    target_price?: number;
    stop_loss?: number;
    content: string;
    summary?: any;
    is_public?: boolean;
  }) => {
    const res = await axios.post(`${API_BASE}/reports`, payload);
    return res.data;
  },

  deleteReport: async (reportId: string) => {
    const res = await axios.delete(`${API_BASE}/reports/${reportId}`);
    return res.data;
  },

  // --- UNIVERSE & MARKET ---
  getUniverseStats: async (): Promise<UniverseStats> => {
    const res = await axios.get(`${ROOT_API}/universe/stats`);
    return res.data;
  },

  getScanningProgress: async (): Promise<ScanningProgress> => {
    const res = await axios.get(`${ROOT_API}/screener/progress`);
    return res.data;
  },

  startUniverseScan: async (limit?: number) => {
    const res = await axios.post(`${ROOT_API}/screener/start-scan`, null, {
      params: limit ? { limit } : undefined
    });
    return res.data;
  },

  syncUniverse: async () => {
    const res = await axios.post(`${ROOT_API}/universe/sync`);
    return res.data;
  },

  getIHSG: async (): Promise<IHSGMarketData> => {
    const res = await axios.get(`${ROOT_API}/market/ihsg`);
    return res.data;
  },

  getStocks: async () => {
    const res = await axios.get(`${ROOT_API}/stocks`);
    return res.data;
  },

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

  getScreenerRules: async (params?: {
    filter?: string;
    min_score?: number;
    sort_by?: string;
  }): Promise<{ total_matches: number; results: ScreenerRuleItem[] }> => {
    const res = await axios.get(`${ROOT_API}/screener/rules`, { params });
    return res.data;
  },

  getTradingPlan: async (symbol: string): Promise<TradingPlanOutput> => {
    const res = await axios.get(`${ROOT_API}/trading-plan/${symbol}`);
    return res.data;
  },

  getTechnicalAnalysis: async (symbol: string) => {
    const res = await axios.get(`${ROOT_API}/analysis/${symbol}`);
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
