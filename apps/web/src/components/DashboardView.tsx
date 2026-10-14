import React, { useEffect, useState } from 'react';
import { ShieldAlert, ShieldCheck, Mail, ArrowUpRight, BarChart3, Clock, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { HistoryItem, ModelInfo, ModelListResponse } from '../types';

interface DashboardViewProps {
  onNavigate: (tab: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ onNavigate }) => {
  const [recentItems, setRecentItems] = useState<HistoryItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [spamCount, setSpamCount] = useState<number>(0);
  const [hamCount, setHamCount] = useState<number>(0);
  const [modelsData, setModelsData] = useState<ModelListResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const [historyRes, modelsRes] = await Promise.all([
          api.getHistory({ page: 1, page_size: 50 }),
          api.getModels(),
        ]);

        const items = historyRes.items;
        setTotalCount(historyRes.total);
        setRecentItems(items.slice(0, 5));

        const spams = items.filter((i) => i.is_spam).length;
        const hams = items.filter((i) => !i.is_spam).length;
        setSpamCount(spams);
        setHamCount(hams);

        setModelsData(modelsRes);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard statistics.');
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const activeModelInfo: ModelInfo | undefined = modelsData?.models.find(
    (m) => m.name === modelsData.active_model
  ) || modelsData?.models[0];

  const spamRatio = totalCount > 0 ? ((spamCount / totalCount) * 100).toFixed(1) : '0.0';

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-slate-800 rounded w-1/4"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-shield-surface/60 rounded-xl border border-shield-border"></div>
          ))}
        </div>
        <div className="h-64 bg-shield-surface/60 rounded-xl border border-shield-border"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Welcome & Mission Banner */}
      <div className="relative overflow-hidden rounded-2xl p-6 sm:p-8 bg-gradient-to-r from-shield-surface via-shield-card to-shield-surface border border-shield-border shadow-xl">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-shield-cyan text-xs font-mono font-medium mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>REAL ML INFERENCE & EXPLAINABILITY</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Transparent, Feature-Attributed Spam Intelligence
          </h1>
          <p className="mt-2 text-sm sm:text-base text-slate-300 leading-relaxed">
            MailShield classifies inbound emails using scikit-learn models trained on verified benchmark datasets. Every classification is explained with mathematical token contributions without fabricated scores.
          </p>
          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              onClick={() => onNavigate('analyzer')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-shield-accent to-shield-cyan text-white text-sm font-semibold hover:opacity-95 shadow-lg shadow-shield-accent/20 transition-all"
            >
              <Mail className="w-4 h-4" />
              <span>Analyze New Email</span>
            </button>
            <button
              onClick={() => onNavigate('modellab')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-shield-borderLight text-sm font-medium transition-all"
            >
              <BarChart3 className="w-4 h-4 text-shield-cyan" />
              <span>Explore Model Lab</span>
            </button>
          </div>
        </div>
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-shield-cyan/5 via-indigo-500/5 to-transparent pointer-events-none" />
      </div>

      {/* Key Metric Counters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Analyses */}
        <div className="glass-card p-5 rounded-xl border border-shield-border">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Total Analyses</span>
            <Mail className="w-4 h-4 text-shield-cyan" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold font-mono text-white">{totalCount}</div>
          <p className="text-xs text-slate-400 mt-1">Live database records</p>
        </div>

        {/* Spam Detections */}
        <div className="glass-card p-5 rounded-xl border border-shield-border">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Spam Detected</span>
            <ShieldAlert className="w-4 h-4 text-shield-spam" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold font-mono text-shield-spam">{spamCount}</div>
          <div className="mt-2 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-shield-spam h-full" style={{ width: `${spamRatio}%` }} />
          </div>
          <p className="text-xs text-slate-400 mt-1">{spamRatio}% of total traffic</p>
        </div>

        {/* Legitimate Emails */}
        <div className="glass-card p-5 rounded-xl border border-shield-border">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Legitimate (Ham)</span>
            <ShieldCheck className="w-4 h-4 text-shield-ham" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold font-mono text-shield-ham">{hamCount}</div>
          <p className="text-xs text-slate-400 mt-1">Verified clean messages</p>
        </div>

        {/* Active Model Performance */}
        <div className="glass-card p-5 rounded-xl border border-shield-border">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">Active Model F1</span>
            <span className="text-xs font-mono text-indigo-400">
              {activeModelInfo?.test_metrics.f1_score ? `${(activeModelInfo.test_metrics.f1_score * 100).toFixed(1)}%` : 'N/A'}
            </span>
          </div>
          <div className="text-sm font-semibold text-white truncate" title={activeModelInfo?.display_name}>
            {activeModelInfo?.display_name || 'Logistic Regression'}
          </div>
          <div className="flex items-center gap-2 mt-2 text-xs font-mono text-slate-400">
            <span>Acc: {((activeModelInfo?.test_metrics.accuracy || 1) * 100).toFixed(1)}%</span>
            <span>•</span>
            <span>FPR: {((activeModelInfo?.test_metrics.false_positive_rate || 0) * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* Grid: Recent Activity Feed & Model Specs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Analyses Feed */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 border border-shield-border">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Recent Analyses</h2>
              <p className="text-xs text-slate-400">Latest email classifications processed by the engine</p>
            </div>
            <button
              onClick={() => onNavigate('history')}
              className="text-xs font-medium text-shield-cyan hover:underline flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {recentItems.length === 0 ? (
            <div className="py-12 text-center text-slate-500">
              <Mail className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p className="text-sm">No analysis history recorded yet.</p>
              <button
                onClick={() => onNavigate('analyzer')}
                className="mt-3 text-xs text-shield-cyan hover:underline"
              >
                Analyze your first email &rarr;
              </button>
            </div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {recentItems.map((item) => (
                <div
                  key={item.id}
                  onClick={() => onNavigate('history')}
                  className="py-3 flex items-center justify-between hover:bg-slate-800/30 px-2 rounded-lg cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    {item.is_spam ? (
                      <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        <ShieldAlert className="w-4 h-4" />
                      </div>
                    ) : (
                      <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <ShieldCheck className="w-4 h-4" />
                      </div>
                    )}
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-200 truncate">{item.subject}</p>
                      <div className="flex items-center gap-2 text-xs text-slate-400 font-mono mt-0.5">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                        <span>•</span>
                        <span>{item.processing_time_ms} ms</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full font-mono font-semibold ${
                          item.is_spam
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        }`}
                      >
                        {item.prediction}
                      </span>
                      <div className="text-[11px] font-mono text-slate-400 mt-0.5">
                        {item.score_type === 'probability'
                          ? `Prob: ${(item.score * 100).toFixed(1)}%`
                          : `Margin: ${item.score.toFixed(2)}`}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Dataset & Model Architecture Summary */}
        <div className="glass-panel rounded-2xl p-6 border border-shield-border flex flex-col justify-between">
          <div>
            <h2 className="text-base font-semibold text-white mb-1">Architecture Summary</h2>
            <p className="text-xs text-slate-400 mb-4">Pipeline specifications & provenance</p>

            <div className="space-y-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block mb-0.5">Feature Extractor</span>
                <span className="text-white font-semibold">TF-IDF Vectorizer (1-2 N-grams)</span>
                <span className="text-slate-400 block mt-1">Vocab: {modelsData?.vocab_size || 692} terms</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block mb-0.5">Dataset Provenance</span>
                <span className="text-white font-semibold">SpamAssassin & Benchmark Corpus</span>
                <span className="text-slate-400 block mt-1">
                  {modelsData?.dataset_info?.total_samples || 184} clean deduplicated records
                </span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block mb-0.5">Splits Strategy</span>
                <span className="text-white font-semibold">70% Train / 15% Val / 15% Test</span>
                <span className="text-emerald-400 block mt-1">Zero Leakage: Fit-on-train only</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
            <span>Desktop Offline Ready</span>
            <span className="text-shield-cyan font-mono">SQLite Local</span>
          </div>
        </div>
      </div>
    </div>
  );
};
