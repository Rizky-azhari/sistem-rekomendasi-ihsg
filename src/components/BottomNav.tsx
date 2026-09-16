import React from 'react';
import { Home, SlidersHorizontal, LineChart, FileText, User, ShieldCheck } from 'lucide-react';
import type { NavTab } from './Navbar';
import { useAuth } from '../context/AuthContext';

interface BottomNavProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  onOpenAuthModal?: () => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({
  activeTab,
  setActiveTab,
  onOpenAuthModal
}) => {
  const { user, role, isAuthenticated } = useAuth();

  const handleProfileClick = () => {
    if (!isAuthenticated) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }
    // If admin, navigate to admin dashboard; else can navigate to reports or open profile
    if (role === 'admin') {
      setActiveTab('admin');
    } else {
      setActiveTab('reports');
    }
  };

  const navItems = [
    {
      id: 'dashboard' as NavTab,
      label: 'Home',
      icon: Home,
      onClick: () => setActiveTab('dashboard'),
      isActive: activeTab === 'dashboard'
    },
    {
      id: 'scanner' as NavTab,
      label: 'Scanner',
      icon: SlidersHorizontal,
      onClick: () => setActiveTab('scanner'),
      isActive: activeTab === 'scanner'
    },
    {
      id: 'detail' as NavTab,
      label: 'Detail',
      icon: LineChart,
      onClick: () => setActiveTab('detail'),
      isActive: activeTab === 'detail'
    },
    {
      id: 'reports' as NavTab,
      label: 'Report',
      icon: FileText,
      onClick: () => setActiveTab('reports'),
      isActive: activeTab === 'reports'
    },
    {
      id: 'profile' as any,
      label: role === 'admin' ? 'Admin' : 'Profile',
      icon: role === 'admin' ? ShieldCheck : User,
      onClick: handleProfileClick,
      isActive: activeTab === 'admin' || (!isAuthenticated && false),
      avatar: user?.avatar_url
    }
  ];

  return (
    <nav
      aria-label="Mobile Navigation"
      className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-[#111827]/95 border-t border-slate-800/80 backdrop-blur-xl px-2 py-1.5 shadow-2xl shadow-black"
      style={{ paddingBottom: 'max(0.5rem, env(safe-area-inset-bottom, 0.5rem))' }}
    >
      <div className="flex items-center justify-around w-full">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = item.isActive;
          return (
            <button
              key={item.label}
              onClick={item.onClick}
              className={`flex flex-col items-center justify-center py-1 px-2.5 rounded-xl transition-all cursor-pointer relative ${
                active
                  ? 'text-[#22C7F0]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {active && (
                <span className="absolute -top-1.5 w-6 h-0.5 bg-[#22C7F0] rounded-full shadow-[0_0_8px_#22C7F0]" />
              )}
              {item.avatar && isAuthenticated ? (
                <img
                  src={item.avatar}
                  alt={user?.full_name || 'Profile'}
                  className={`w-5 h-5 rounded-full object-cover mb-0.5 border ${
                    active ? 'border-[#22C7F0]' : 'border-slate-700'
                  }`}
                />
              ) : (
                <Icon className={`w-5 h-5 mb-0.5 transition-transform ${active ? 'scale-110' : ''}`} />
              )}
              <span className={`text-[10px] font-medium tracking-tight ${active ? 'font-bold text-[#22C7F0]' : ''}`}>
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
