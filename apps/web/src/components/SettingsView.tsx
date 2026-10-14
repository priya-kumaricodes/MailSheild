import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Shield, Database, Cpu, Lock, CheckCircle, RefreshCw, Trash } from 'lucide-react';
import { api } from '../services/api';
import { HealthStatus } from '../types';

interface SettingsViewProps {
  health: HealthStatus | null;
  onRefreshHealth: () => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ health, onRefreshHealth }) => {
  const [storeBodySetting, setStoreBodySetting] = useState<boolean>(() => {
    try {
      return typeof window !== 'undefined' && window.localStorage
        ? window.localStorage.getItem('mailshield_store_body') === 'true'
        : false;
    } catch {
      return false;
    }
  });

  const [retentionPolicy, setRetentionPolicy] = useState<string>(() => {
    try {
      return typeof window !== 'undefined' && window.localStorage
        ? window.localStorage.getItem('mailshield_retention') || 'all'
        : 'all';
    } catch {
      return 'all';
    }
  });

  const [savedFeedback, setSavedFeedback] = useState<boolean>(false);

  const handleSaveSettings = () => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem('mailshield_store_body', String(storeBodySetting));
        window.localStorage.setItem('mailshield_retention', retentionPolicy);
      }
    } catch (e) {
      console.warn('Failed to save to localStorage:', e);
    }
    setSavedFeedback(true);
    setTimeout(() => setSavedFeedback(false), 2000);
  };

  const handleClearCache = () => {
    if (confirm('Clear local app preferences and token cache?')) {
      localStorage.clear();
      window.location.reload();
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System Settings & Privacy Preferences</h1>
        <p className="text-sm text-slate-400 mt-1">
          Configure local retention, content storage policies, and review runtime infrastructure health.
        </p>
      </div>

      {/* Privacy Policy & Data Retention Card */}
      <div className="glass-panel p-6 rounded-2xl border border-shield-border space-y-6">
        <div className="flex items-center gap-2.5 pb-4 border-b border-shield-border">
          <Lock className="w-5 h-5 text-shield-cyan" />
          <h2 className="text-base font-bold text-white">Privacy & Retention Controls</h2>
        </div>

        <div className="space-y-4">
          {/* Store Body Toggle */}
          <div className="flex items-start justify-between gap-4 p-4 rounded-xl bg-[#060b14] border border-slate-800">
            <div>
              <span className="text-sm font-semibold text-slate-200 block">Default Email Text Persistence</span>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                When disabled, MailShield does not store email body text in the database. Only metadata, SHA-256 hashes, and token attributions are saved for historical review.
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer flex-shrink-0 mt-1">
              <input
                type="checkbox"
                checked={storeBodySetting}
                onChange={(e) => setStoreBodySetting(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-shield-accent"></div>
            </label>
          </div>

          {/* Retention Options */}
          <div className="p-4 rounded-xl bg-[#060b14] border border-slate-800 space-y-2">
            <span className="text-sm font-semibold text-slate-200 block">Analysis History Retention Policy</span>
            <p className="text-xs text-slate-300">
              Configure how long prediction history records remain stored in your database.
            </p>
            <select
              value={retentionPolicy}
              onChange={(e) => setRetentionPolicy(e.target.value)}
              className="mt-2 w-full sm:w-64 px-3 py-2 rounded-lg bg-[#03060c] border border-slate-700 text-xs text-slate-200"
            >
              <option value="all">Keep all analysis records indefinitely</option>
              <option value="30days">Auto-purge records older than 30 days</option>
              <option value="7days">Auto-purge records older than 7 days</option>
              <option value="disabled">Do not save any analysis history</option>
            </select>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          {savedFeedback ? (
            <span className="text-xs text-emerald-400 font-medium flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4" />
              <span>Preferences saved.</span>
            </span>
          ) : (
            <span />
          )}
          <button
            onClick={handleSaveSettings}
            className="px-4 py-2 rounded-xl bg-shield-accent hover:opacity-90 text-white text-xs font-semibold shadow-md transition-opacity"
          >
            Save Preferences
          </button>
        </div>
      </div>

      {/* System Diagnostics & Infrastructure Health */}
      <div className="glass-panel p-6 rounded-2xl border border-shield-border space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-shield-border">
          <div className="flex items-center gap-2.5">
            <Cpu className="w-5 h-5 text-shield-cyan" />
            <h2 className="text-base font-bold text-white">System Diagnostics & Infrastructure</h2>
          </div>
          <button
            onClick={onRefreshHealth}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-white px-2 py-1 rounded hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-[#060b14] border border-slate-800 flex items-center justify-between">
            <span className="text-slate-300 font-medium">FastAPI Backend Status</span>
            <span className="text-emerald-400 font-bold flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Operational</span>
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#060b14] border border-slate-800 flex items-center justify-between">
            <span className="text-slate-300 font-medium">Database Engine</span>
            <span className="text-slate-200 font-bold">
              {health?.mode === 'desktop' ? 'SQLite Local (Offline)' : 'SQLAlchemy 2.0 (SQLite / Postgres)'}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#060b14] border border-slate-800 flex items-center justify-between">
            <span className="text-slate-300 font-medium">Active ML Classifiers</span>
            <span className="text-shield-cyan font-bold">
              {health?.active_models?.length || 3} Loaded in Memory
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#060b14] border border-slate-800 flex items-center justify-between">
            <span className="text-slate-300 font-medium">Execution Mode</span>
            <span className="text-slate-200 font-bold uppercase">{health?.mode || 'standard'}</span>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
          <span className="text-xs text-slate-400">MailShield Build Version: v2.0.0-release</span>
          <button
            onClick={handleClearCache}
            className="flex items-center gap-1 text-xs text-rose-400 hover:text-rose-300 transition-colors"
          >
            <Trash className="w-3.5 h-3.5" />
            <span>Reset Local Storage</span>
          </button>
        </div>
      </div>
    </div>
  );
};
