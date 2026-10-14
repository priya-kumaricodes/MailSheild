import React from 'react';
import { Shield, Activity, Sparkles, Inbox, History, FlaskConical, Settings, Globe2, Mail } from 'lucide-react';
import { HealthStatus } from '../types';

interface HeaderProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  health: HealthStatus | null;
}

export const Header: React.FC<HeaderProps> = ({ currentTab, onTabChange, health }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'analyzer', label: 'Email Analyzer', icon: Inbox },
    { id: 'gmail', label: 'Gmail Scanner', icon: Mail },
    { id: 'history', label: 'History', icon: History },
    { id: 'modellab', label: 'Model Lab', icon: FlaskConical },
    { id: 'evaluationlab', label: 'Evaluation Lab', icon: Globe2 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-shield-border/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Identity */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => onTabChange('dashboard')}>
            <div className="relative p-2 rounded-xl bg-gradient-to-tr from-indigo-500/20 via-cyan-500/20 to-transparent border border-cyan-500/30">
              <Shield className="w-6 h-6 text-shield-cyan" />
              <div className="absolute inset-0 rounded-xl bg-shield-cyan/10 blur-sm pointer-events-none" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-shield-cyan bg-clip-text text-transparent">
                  MailShield
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-shield-accent/20 text-shield-accent border border-shield-accent/30 font-medium">
                  v2.1
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Multilingual Spam & Phishing Defense</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1 sm:gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-shield-surface text-shield-cyan shadow-sm border border-shield-borderLight shadow-shield-cyan/5'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-shield-cyan' : 'text-slate-400'}`} />
                  <span className="hidden md:inline">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* System Health Indicator */}
          <div className="flex items-center gap-3">
            <div
              className={`flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-mono border ${
                health?.status === 'healthy'
                  ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/50'
                  : 'bg-rose-950/40 text-rose-400 border-rose-800/50'
              }`}
              title={health?.status === 'healthy' ? 'Backend & Model Online' : 'System Degraded'}
            >
              <div
                className={`w-1.5 h-1.5 rounded-full ${
                  health?.status === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'
                }`}
              />
              <span className="hidden sm:inline">
                {health?.mode === 'desktop' ? 'OFFLINE SECURE' : health?.status === 'healthy' ? 'ONLINE' : 'OFFLINE'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
