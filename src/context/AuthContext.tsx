import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { supabase } from '../services/supabaseClient';
import { api, setApiAuthToken } from '../api/client';

export type UserRole = 'admin' | 'user';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  avatar_url: string;
  role: UserRole;
  created_at?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  role: UserRole | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  loginWithGoogle: () => Promise<void>;
  loginWithEmail: (email: string, password: string) => Promise<UserProfile | null>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const MASTER_ADMIN_EMAILS = [
  'rizkyazhariputra2022@gmail.com',
  'rizkyazhariputra336@gmail.com'
];

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [role, setRole] = useState<UserRole | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('ihsg_auth_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Helper to fetch and sync profile from Supabase profiles table
  const fetchAndSyncProfile = async (userId: string, accessToken: string) => {
    try {
      setApiAuthToken(accessToken);
      setToken(accessToken);

      // 1. Direct query to public.profiles via Supabase client
      const { data, error } = await supabase
        .from('profiles')
        .select('id, email, full_name, avatar_url, role, created_at')
        .eq('id', userId)
        .maybeSingle();

      if (!error && data) {
        const emailLower = (data.email || '').toLowerCase().trim();
        const userRole: UserRole = MASTER_ADMIN_EMAILS.includes(emailLower) || (data.role || 'user').toLowerCase() === 'admin' ? 'admin' : 'user';
        const profile: UserProfile = {
          id: data.id,
          email: data.email,
          full_name: data.full_name || data.email.split('@')[0],
          avatar_url: data.avatar_url || '',
          role: userRole,
          created_at: data.created_at
        };
        setUser(profile);
        setRole(userRole);
        return profile;
      }

      // 2. Fallback via backend getMe()
      const backendProfile = await api.getMe();
      if (backendProfile) {
        const emailLower = (backendProfile.email || '').toLowerCase().trim();
        const userRole: UserRole = MASTER_ADMIN_EMAILS.includes(emailLower) || (backendProfile.role || 'user').toLowerCase() === 'admin' ? 'admin' : 'user';
        const profile: UserProfile = {
          id: backendProfile.id,
          email: backendProfile.email,
          full_name: backendProfile.full_name || backendProfile.email.split('@')[0],
          avatar_url: backendProfile.avatar_url || '',
          role: userRole
        };
        setUser(profile);
        setRole(userRole);
        return profile;
      }
    } catch (err) {
      console.warn('[AuthContext] Error fetching profile:', err);
    }
    return null;
  };

  useEffect(() => {
    // 1. Check existing session on mount
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      if (session && session.user) {
        await fetchAndSyncProfile(session.user.id, session.access_token);
      }
      setIsLoading(false);
    });

    // 2. Listen for auth changes (OAuth redirect back, sign in, sign out)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log(`[Supabase Auth] Event: ${event}`);
      if (session && session.user) {
        const profile = await fetchAndSyncProfile(session.user.id, session.access_token);
        // Call backend callback to register audit log
        api.syncGoogleCallback().catch(() => {});

        // Automatic redirect rule specified by user:
        // Jika role = admin -> /admin/dashboard
        // Jika role = user -> /dashboard
        if (event === 'SIGNED_IN' && profile) {
          const targetPath = profile.role === 'admin' ? '/admin/dashboard' : '/dashboard';
          if (window.location.pathname !== targetPath) {
            window.history.replaceState(null, '', targetPath);
            window.dispatchEvent(new PopStateEvent('popstate'));
          }
        }
      } else if (event === 'SIGNED_OUT') {
        setUser(null);
        setRole(null);
        setToken(null);
        setApiAuthToken(null);
      }
      setIsLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const loginWithGoogle = async () => {
    setIsLoading(true);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: window.location.origin
        }
      });
      if (error) {
        throw error;
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithEmail = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await api.loginEmail(email, password);
      if (res && res.user && res.access_token) {
        const userRole: UserRole = (res.user.role || 'user').toLowerCase() === 'admin' ? 'admin' : 'user';
        const profile: UserProfile = {
          id: res.user.id,
          email: res.user.email,
          full_name: res.user.full_name || res.user.email.split('@')[0],
          avatar_url: res.user.avatar_url || '',
          role: userRole
        };
        setUser(profile);
        setRole(userRole);
        setToken(res.access_token);
        setApiAuthToken(res.access_token);

        const targetPath = userRole === 'admin' ? '/admin/dashboard' : '/dashboard';
        if (window.location.pathname !== targetPath) {
          window.history.replaceState(null, '', targetPath);
          window.dispatchEvent(new PopStateEvent('popstate'));
        }
        return profile;
      }
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await api.logout().catch(() => {});
      await supabase.auth.signOut();
    } finally {
      setUser(null);
      setRole(null);
      setToken(null);
      setApiAuthToken(null);
      setIsLoading(false);
      window.history.replaceState(null, '', '/dashboard');
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        token,
        isAuthenticated: !!user,
        isLoading,
        loginWithGoogle,
        loginWithEmail,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
