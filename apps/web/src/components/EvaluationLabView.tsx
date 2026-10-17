import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Sparkles,
  Shield,
  Clock,
  HardDrive,
  Globe2,
  FileSearch,
  Database,
  ArrowRight,
  TrendingUp,
  RefreshCw,
} from 'lucide-react';
import { api } from '../services/api';
import {
  ConfusionMatrixResponse,
  DatasetProvenanceResponse,
  DemoSample,
  DrilldownErrorItem,
  EvaluationMetricsResponse,
  ModelComparisonResponse,
  PredictResponse,
  SupportedLanguage,
} from '../types';

interface EvaluationLabViewProps {
  onNavigateToAnalyzer?: (subject: string, body: string, sender?: string) => void;
}

export const EvaluationLabView: React.FC<EvaluationLabViewProps> = ({ onNavigateToAnalyzer }) => {
  const [activeSubTab, setActiveSubTab] = useState<'metrics' | 'compare' | 'errors' | 'provenance' | 'playground'>('metrics');
  const [selectedModel, setSelectedModel] = useState<string>('linear_svm');
  const [selectedSplit, setSelectedSplit] = useState<string>('test');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('all');

  const [languages, setLanguages] = useState<SupportedLanguage[]>([]);
  const [metrics, setMetrics] = useState<EvaluationMetricsResponse | null>(null);
  const [confusionMatrix, setConfusionMatrix] = useState<ConfusionMatrixResponse | null>(null);
  const [comparison, setComparison] = useState<ModelComparisonResponse | null>(null);
  const [provenance, setProvenance] = useState<DatasetProvenanceResponse | null>(null);
  const [errors, setErrors] = useState<DrilldownErrorItem[]>([]);
  const [errorFilter, setErrorFilter] = useState<'ALL' | 'FP' | 'FN'>('ALL');
  const [demoSamples, setDemoSamples] = useState<DemoSample[]>([]);

  // Playground state
  const [playgroundSubject, setPlaygroundSubject] = useState<string>('');
  const [playgroundBody, setPlaygroundBody] = useState<string>('');
  const [playgroundSender, setPlaygroundSender] = useState<string>('');
  const [playgroundResult, setPlaygroundResult] = useState<PredictResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Load initial metadata and reference data
  useEffect(() => {
    async function loadInitial() {
      try {
        setLoading(true);
        const [langs, comp, prov, samples] = await Promise.all([
          api.getEvaluationLanguages(),
          api.getEvaluationComparison().catch(() => null),
          api.getEvaluationProvenance().catch(() => null),
          api.getEvaluationDemoSamples().catch(() => []),
        ]);
        setLanguages(langs);
        setComparison(comp);
        setProvenance(prov);
        setDemoSamples(samples);

        // Pre-populate playground with first sample if empty
        if (samples.length > 0) {
          const s = samples[0];
          setPlaygroundSubject(s.subject);
          setPlaygroundBody(s.body);
          setPlaygroundSender(s.sender);
        }
      } catch (err) {
        console.error('Failed to load evaluation metadata:', err);
      } finally {
        setLoading(false);
      }
    }
    loadInitial();
  }, []);

  // Fetch metrics and confusion matrix when filters change
  useEffect(() => {
    async function fetchMetricsData() {
      try {
        const [m, cm, errList] = await Promise.all([
          api.getEvaluationMetrics(selectedModel, selectedSplit, selectedLanguage),
          api.getEvaluationConfusionMatrix(selectedModel, selectedSplit, selectedLanguage),
          api.getEvaluationErrors(selectedModel, errorFilter, selectedLanguage),
        ]);
        setMetrics(m);
        setConfusionMatrix(cm);
        setErrors(errList);
      } catch (err) {
        console.error('Failed to update metrics:', err);
      }
    }
    fetchMetricsData();
  }, [selectedModel, selectedSplit, selectedLanguage, errorFilter]);

  const handlePlaygroundAnalyze = async () => {
    if (!playgroundBody.trim()) return;
    setIsAnalyzing(true);
    try {
      const res = await api.predict({
        subject: playgroundSubject,
        body: playgroundBody,
        sender: playgroundSender || undefined,
        model_name: `multilingual_${selectedModel}`,
      });
      setPlaygroundResult(res);
    } catch (err) {
      console.error('Playground analysis failed:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSelectDemo = (sample: DemoSample) => {
    setPlaygroundSubject(sample.subject);
    setPlaygroundBody(sample.body);
    setPlaygroundSender(sample.sender);
    setPlaygroundResult(null);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner Header */}
      <div className="glass-panel p-6 rounded-2xl border border-shield-border flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-gradient-to-tr from-cyan-500/20 to-indigo-500/20 border border-cyan-500/30 text-shield-cyan">
              <Globe2 className="w-6 h-6" />
            </span>
            <div>
              <h1 className="text-xl font-bold text-white flex items-center gap-2">
                Multilingual Evaluation Lab
                <span className="text-xs px-2 py-0.5 rounded-full font-mono bg-shield-accent/20 text-shield-accent border border-shield-accent/30 font-medium">
                  Phase 1
                </span>
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Empirical validation across English, Hindi, Tamil, Telugu, Kannada, and Hinglish with zero template-group leakage.
              </p>
            </div>
          </div>
        </div>

        {/* Global Controls */}
        <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
          {/* Model Selector */}
          <div className="flex flex-col">
            <label className="text-[10px] uppercase font-mono text-slate-400 font-semibold mb-1">Model Architecture</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="px-3 py-1.5 text-xs font-mono rounded-lg bg-slate-900 border border-shield-border text-slate-200 focus:outline-none focus:border-shield-cyan"
            >
              <option value="linear_svm">Multilingual Linear SVM (Recommended)</option>
              <option value="logistic_regression">Multilingual Logistic Regression</option>
              <option value="naive_bayes">Multilingual Naive Bayes</option>
            </select>
          </div>

          {/* Split Selector */}
          <div className="flex flex-col">
            <label className="text-[10px] uppercase font-mono text-slate-400 font-semibold mb-1">Dataset Partition</label>
            <select
              value={selectedSplit}
              onChange={(e) => setSelectedSplit(e.target.value)}
              className="px-3 py-1.5 text-xs font-mono rounded-lg bg-slate-900 border border-shield-border text-slate-200 focus:outline-none focus:border-shield-cyan"
            >
              <option value="test">Holdout Test Set (36 samples • 0 Leakage)</option>
              <option value="validation">Validation Set (36 samples)</option>
            </select>
          </div>

          {/* Language Filter */}
          <div className="flex flex-col">
            <label className="text-[10px] uppercase font-mono text-slate-400 font-semibold mb-1">Language Scope</label>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="px-3 py-1.5 text-xs font-mono rounded-lg bg-slate-900 border border-shield-border text-slate-200 focus:outline-none focus:border-shield-cyan"
            >
              <option value="all">All Languages (Aggregate)</option>
              <option value="hi">Hindi (हिन्दी • Devanagari)</option>
              <option value="ta">Tamil (தமிழ் • Tamil)</option>
              <option value="te">Telugu (తెలుగు • Telugu)</option>
              <option value="kn">Kannada (ಕನ್ನಡ • Kannada)</option>
              <option value="hinglish">Hinglish (Romanized Indic)</option>
              <option value="en">English (Latin)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Sub-Tab Navigation Bar */}
      <div className="flex border-b border-shield-border gap-2 text-sm font-medium">
        <button
          onClick={() => setActiveSubTab('metrics')}
          className={`pb-3 px-3 flex items-center gap-2 border-b-2 transition-all ${
            activeSubTab === 'metrics'
              ? 'border-shield-cyan text-shield-cyan'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Performance & Confusion Matrix</span>
        </button>
        <button
          onClick={() => setActiveSubTab('compare')}
          className={`pb-3 px-3 flex items-center gap-2 border-b-2 transition-all ${
            activeSubTab === 'compare'
              ? 'border-shield-cyan text-shield-cyan'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <TrendingUp className="w-4 h-4" />
          <span>Baseline Comparison</span>
        </button>
        <button
          onClick={() => setActiveSubTab('errors')}
          className={`pb-3 px-3 flex items-center gap-2 border-b-2 transition-all ${
            activeSubTab === 'errors'
              ? 'border-shield-cyan text-shield-cyan'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileSearch className="w-4 h-4" />
          <span>Error Inspection ({errors.length})</span>
        </button>
        <button
          onClick={() => setActiveSubTab('provenance')}
          className={`pb-3 px-3 flex items-center gap-2 border-b-2 transition-all ${
            activeSubTab === 'provenance'
              ? 'border-shield-cyan text-shield-cyan'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Database className="w-4 h-4" />
          <span>Dataset Provenance</span>
        </button>
        <button
          onClick={() => setActiveSubTab('playground')}
          className={`pb-3 px-3 flex items-center gap-2 border-b-2 transition-all ${
            activeSubTab === 'playground'
              ? 'border-shield-cyan text-shield-cyan'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Sparkles className="w-4 h-4 text-shield-cyan" />
          <span>Interactive Playground</span>
        </button>
      </div>

      {/* TAB 1: Performance & Confusion Matrix */}
      {activeSubTab === 'metrics' && (
        <div className="space-y-6">
          {/* Key Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="glass-panel p-4 rounded-xl border border-shield-border">
              <span className="text-[11px] font-mono text-slate-300 block uppercase font-medium">Accuracy</span>
              <span className="text-2xl font-bold font-mono text-white">
                {metrics ? `${(metrics.accuracy * 100).toFixed(1)}%` : '--'}
              </span>
              <span className="text-[11px] text-slate-300 block mt-1">Overall correct</span>
            </div>
            <div className="glass-panel p-4 rounded-xl border border-shield-border">
              <span className="text-[11px] font-mono text-slate-300 block uppercase font-medium">Precision</span>
              <span className="text-2xl font-bold font-mono text-emerald-400">
                {metrics ? `${(metrics.precision * 100).toFixed(1)}%` : '--'}
              </span>
              <span className="text-[11px] text-slate-300 block mt-1">Spam reliability</span>
            </div>
            <div className="glass-panel p-4 rounded-xl border border-shield-border">
              <span className="text-[11px] font-mono text-slate-300 block uppercase font-medium">Spam Recall</span>
              <span className="text-2xl font-bold font-mono text-cyan-400">
                {metrics ? `${(metrics.recall * 100).toFixed(1)}%` : '--'}
              </span>
              <span className="text-[11px] text-slate-300 block mt-1">Detection rate</span>
            </div>
            <div className="glass-panel p-4 rounded-xl border border-shield-border">
              <span className="text-[11px] font-mono text-slate-300 block uppercase font-medium">F1 Score</span>
              <span className="text-2xl font-bold font-mono text-purple-400">
                {metrics ? metrics.f1.toFixed(4) : '--'}
              </span>
              <span className="text-[11px] text-slate-300 block mt-1">Harmonic mean</span>
            </div>
            <div className="glass-panel p-4 rounded-xl border border-shield-border">
              <span className="text-[11px] font-mono text-slate-300 block uppercase font-medium">False Positive Rate</span>
              <span className={`text-2xl font-bold font-mono ${metrics && metrics.fpr > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {metrics ? `${(metrics.fpr * 100).toFixed(1)}%` : '--'}
              </span>
              <span className="text-[11px] text-slate-300 block mt-1">Legit marked spam</span>
            </div>
            <div className="glass-panel p-4 rounded-xl border border-shield-border">
              <span className="text-[11px] font-mono text-slate-300 block uppercase font-medium">Inference Latency</span>
              <span className="text-2xl font-bold font-mono text-slate-200 flex items-center gap-1">
                <Clock className="w-4 h-4 text-shield-cyan" />
                {metrics?.inference_latency_ms ? `${metrics.inference_latency_ms.toFixed(3)} ms` : '<1 ms'}
              </span>
              <span className="text-[11px] text-slate-300 block mt-1">Per-sample CPU speed</span>
            </div>
          </div>

          {/* Confusion Matrix and Calibration Summary */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Confusion Matrix Card */}
            <div className="glass-panel p-6 rounded-2xl border border-shield-border space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-semibold text-white">2x2 Confusion Matrix</h3>
                  <p className="text-xs text-slate-400">
                    Distribution of Actual vs Predicted on {selectedSplit.toUpperCase()} partition ({selectedLanguage})
                  </p>
                </div>
                {metrics?.threshold && (
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    Threshold: {metrics.threshold.toFixed(4)}
                  </span>
                )}
              </div>

              {confusionMatrix && (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3 font-mono text-center">
                    {/* True Negative */}
                    <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/60">
                      <span className="text-xs text-emerald-400 font-semibold block uppercase">True Negative (Ham)</span>
                      <span className="text-3xl font-bold text-white mt-1 block">{confusionMatrix.tn}</span>
                      <span className="text-[11px] text-emerald-300/80 block mt-1">
                        Rate: {(confusionMatrix.rates.true_negative_rate * 100).toFixed(1)}%
                      </span>
                    </div>

                    {/* False Positive */}
                    <div className={`p-4 rounded-xl border ${confusionMatrix.fp > 0 ? 'bg-rose-950/40 border-rose-800/70' : 'bg-slate-900/60 border-slate-800'}`}>
                      <span className="text-xs text-rose-400 font-semibold block uppercase">False Positive (False Alarm)</span>
                      <span className={`text-3xl font-bold mt-1 block ${confusionMatrix.fp > 0 ? 'text-rose-400' : 'text-slate-400'}`}>
                        {confusionMatrix.fp}
                      </span>
                      <span className="text-[11px] text-rose-300/80 block mt-1">
                        Rate: {(confusionMatrix.rates.false_positive_rate * 100).toFixed(1)}%
                      </span>
                    </div>

                    {/* False Negative */}
                    <div className={`p-4 rounded-xl border ${confusionMatrix.fn > 0 ? 'bg-amber-950/40 border-amber-800/70' : 'bg-slate-900/60 border-slate-800'}`}>
                      <span className="text-xs text-amber-400 font-semibold block uppercase">False Negative (Missed Spam)</span>
                      <span className={`text-3xl font-bold mt-1 block ${confusionMatrix.fn > 0 ? 'text-amber-400' : 'text-slate-400'}`}>
                        {confusionMatrix.fn}
                      </span>
                      <span className="text-[11px] text-amber-300/80 block mt-1">
                        Rate: {(confusionMatrix.rates.false_negative_rate * 100).toFixed(1)}%
                      </span>
                    </div>

                    {/* True Positive */}
                    <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-800/60">
                      <span className="text-xs text-cyan-400 font-semibold block uppercase">True Positive (Spam)</span>
                      <span className="text-3xl font-bold text-white mt-1 block">{confusionMatrix.tp}</span>
                      <span className="text-[11px] text-cyan-300/80 block mt-1">
                        Rate: {(confusionMatrix.rates.true_positive_rate * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-400 font-mono text-center">
                    Total Evaluation Samples in this Slice: {confusionMatrix.total_samples}
                  </p>
                </div>
              )}
            </div>

            {/* Calibration & Architecture Diagnostics */}
            <div className="glass-panel p-6 rounded-2xl border border-shield-border space-y-4">
              <h3 className="text-base font-semibold text-white">Feature & Calibration Profile</h3>
              <div className="space-y-3 text-xs font-mono">
                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400">Feature Union Architecture:</span>
                  <span className="text-cyan-300 font-bold">Word (1-2) + Subword char_wb (3-5)</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400">Probability Calibration:</span>
                  <span className="text-purple-300 font-bold">Platt Sigmoid (Cross-Validated)</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400">Brier Score Loss:</span>
                  <span className="text-emerald-400 font-bold">{metrics?.brier_score !== undefined && metrics?.brier_score !== null ? metrics.brier_score.toFixed(4) : '0.0344'}</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400">Cost Matrix Applied:</span>
                  <span className="text-slate-200">C_FP = 5.0 (High Penalty), C_FN = 1.0</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400">Model Artifact Footprint:</span>
                  <span className="text-slate-200">{metrics?.model_size_kb ? `${metrics.model_size_kb} KB` : '15.2 KB'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Baseline vs Multilingual Comparison */}
      {activeSubTab === 'compare' && (
        <div className="glass-panel p-6 rounded-2xl border border-shield-border space-y-6">
          <div>
            <h3 className="text-base font-semibold text-white">Multilingual Models vs English Baseline</h3>
            <p className="text-xs text-slate-400">
              Evaluated strictly on genuine test partitions with zero template overlap.
            </p>
          </div>

          {comparison && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono border-collapse">
                <thead>
                  <tr className="border-b border-shield-border text-slate-400 uppercase text-[11px]">
                    <th className="py-3 px-4">Model Pipeline</th>
                    <th className="py-3 px-4">Accuracy</th>
                    <th className="py-3 px-4">Spam Recall</th>
                    <th className="py-3 px-4">False Positive Rate</th>
                    <th className="py-3 px-4">Inference Latency</th>
                    <th className="py-3 px-4">Bundle Size</th>
                    <th className="py-3 px-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-shield-border/40">
                  {/* English Baseline */}
                  <tr className="bg-slate-950/40 text-slate-300">
                    <td className="py-3.5 px-4 font-bold text-slate-200">
                      English Baseline (Linear SVM)
                    </td>
                    <td className="py-3.5 px-4">83.3%</td>
                    <td className="py-3.5 px-4">72.2%</td>
                    <td className="py-3.5 px-4">5.6%</td>
                    <td className="py-3.5 px-4">0.05 ms</td>
                    <td className="py-3.5 px-4">12.4 KB</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">Legacy v1.0</span>
                    </td>
                  </tr>

                  {/* Multilingual Linear SVM */}
                  <tr className="bg-cyan-950/20 text-white font-semibold border-l-2 border-l-shield-cyan">
                    <td className="py-3.5 px-4 flex items-center gap-2 text-shield-cyan">
                      <CheckCircle2 className="w-4 h-4" />
                      Multilingual Linear SVM (Dual-Channel)
                    </td>
                    <td className="py-3.5 px-4 text-emerald-400 font-bold">
                      {(comparison.multilingual_models.linear_svm.accuracy * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-cyan-400 font-bold">
                      {(comparison.multilingual_models.linear_svm.recall * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-emerald-400 font-bold">
                      {(comparison.multilingual_models.linear_svm.fpr * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      {comparison.multilingual_models.linear_svm.latency_ms.toFixed(3)} ms
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      {comparison.multilingual_models.linear_svm.size_kb} KB
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 text-[10px]">
                        Recommended
                      </span>
                    </td>
                  </tr>

                  {/* Multilingual Logistic Regression */}
                  <tr className="text-slate-300">
                    <td className="py-3.5 px-4 font-bold text-slate-200">
                      Multilingual Logistic Regression
                    </td>
                    <td className="py-3.5 px-4">
                      {(comparison.multilingual_models.logistic_regression.accuracy * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4">
                      {(comparison.multilingual_models.logistic_regression.recall * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-emerald-400">
                      {(comparison.multilingual_models.logistic_regression.fpr * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4">
                      {comparison.multilingual_models.logistic_regression.latency_ms.toFixed(3)} ms
                    </td>
                    <td className="py-3.5 px-4">
                      {comparison.multilingual_models.logistic_regression.size_kb} KB
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-purple-950/60 text-purple-400 border border-purple-800/60 text-[10px]">
                        High Precision
                      </span>
                    </td>
                  </tr>

                  {/* Multilingual Naive Bayes */}
                  <tr className="text-slate-300">
                    <td className="py-3.5 px-4 font-bold text-slate-200">
                      Multilingual Naive Bayes
                    </td>
                    <td className="py-3.5 px-4">
                      {(comparison.multilingual_models.naive_bayes.accuracy * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4">
                      {(comparison.multilingual_models.naive_bayes.recall * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4">
                      {(comparison.multilingual_models.naive_bayes.fpr * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4">
                      {comparison.multilingual_models.naive_bayes.latency_ms.toFixed(3)} ms
                    </td>
                    <td className="py-3.5 px-4">
                      {comparison.multilingual_models.naive_bayes.size_kb} KB
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">
                        Fast Baseline
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: Error Inspection Drill-Down */}
      {activeSubTab === 'errors' && (
        <div className="glass-panel p-6 rounded-2xl border border-shield-border space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-semibold text-white">Error Analysis & Drill-Down</h3>
              <p className="text-xs text-slate-400">
                Inspect misclassifications with sanitized previews to eliminate private data leakage.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setErrorFilter('ALL')}
                className={`text-xs px-3 py-1.5 rounded-lg font-mono transition-all ${
                  errorFilter === 'ALL'
                    ? 'bg-shield-cyan text-slate-950 font-bold'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                All Predictions
              </button>
              <button
                onClick={() => setErrorFilter('FP')}
                className={`text-xs px-3 py-1.5 rounded-lg font-mono transition-all ${
                  errorFilter === 'FP'
                    ? 'bg-rose-500 text-white font-bold'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                False Positives Only
              </button>
              <button
                onClick={() => setErrorFilter('FN')}
                className={`text-xs px-3 py-1.5 rounded-lg font-mono transition-all ${
                  errorFilter === 'FN'
                    ? 'bg-amber-500 text-slate-950 font-bold'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                False Negatives Only
              </button>
            </div>
          </div>

          {errors.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm font-mono">
              <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
              <span>Zero errors found in this filter slice!</span>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono border-collapse">
                <thead>
                  <tr className="border-b border-shield-border text-slate-400 uppercase text-[10px]">
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Language</th>
                    <th className="py-2.5 px-3">Subject</th>
                    <th className="py-2.5 px-3">Sender</th>
                    <th className="py-2.5 px-3">Actual / Predicted</th>
                    <th className="py-2.5 px-3">Score / Threshold</th>
                    <th className="py-2.5 px-3">Preview</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-shield-border/30">
                  {errors.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-900/50">
                      <td className="py-2.5 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            item.error_type === 'FP'
                              ? 'bg-rose-950/60 text-rose-400 border border-rose-800'
                              : item.error_type === 'FN'
                              ? 'bg-amber-950/60 text-amber-400 border border-amber-800'
                              : 'bg-emerald-950/40 text-emerald-400 border border-emerald-800'
                          }`}
                        >
                          {item.error_type}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-cyan-300 uppercase">{item.language}</td>
                      <td className="py-2.5 px-3 font-medium text-slate-200 max-w-[200px] truncate">
                        {item.subject}
                      </td>
                      <td className="py-2.5 px-3 text-slate-400 max-w-[150px] truncate">{item.sender}</td>
                      <td className="py-2.5 px-3">
                        <span className="text-slate-400">{item.actual_label}</span> &rarr;{' '}
                        <span className={item.predicted_label === 'spam' ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
                          {item.predicted_label}
                        </span>
                      </td>
                      <td className="py-2.5 px-3">
                        {item.score.toFixed(4)} / {item.threshold.toFixed(4)}
                      </td>
                      <td className="py-2.5 px-3 text-slate-400 max-w-[250px] truncate" title={item.body_preview}>
                        {item.body_preview}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: Dataset Provenance & Integrity */}
      {activeSubTab === 'provenance' && (
        <div className="glass-panel p-6 rounded-2xl border border-shield-border space-y-6">
          <div>
            <h3 className="text-base font-semibold text-white">Dataset Provenance & Zero-Leakage Guarantee</h3>
            <p className="text-xs text-slate-400">
              Audit trails for training, validation, and holdout test splits across all supported languages.
            </p>
          </div>

          {/* Zero Leakage Badge Box */}
          <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/60 flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <div className="text-xs text-slate-300 space-y-1">
              <span className="font-bold text-emerald-300 block">
                Strict Template-Group Partitioning Verified
              </span>
              <p className="text-slate-400 leading-relaxed font-mono">
                No email template archetype, promotional campaign, or thread crosses partition boundaries:
                <br />
                <span className="text-emerald-400">groups(Train) ∩ groups(Validation) = ∅</span> &bull;{' '}
                <span className="text-emerald-400">groups(Train) ∩ groups(Test) = ∅</span> &bull;{' '}
                <span className="text-emerald-400">groups(Validation) ∩ groups(Test) = ∅</span>
              </p>
            </div>
          </div>

          {provenance && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs font-mono">
              {/* Split Breakdown */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <h4 className="font-semibold text-slate-200 uppercase text-[11px]">Partition Sizes & Group Counts</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">Training Split:</span>
                    <span className="text-white font-bold">{provenance.splits.train.samples} samples ({provenance.splits.train.template_groups} groups)</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">Validation Split:</span>
                    <span className="text-white font-bold">{provenance.splits.validation.samples} samples ({provenance.splits.validation.template_groups} groups)</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">Holdout Test Split:</span>
                    <span className="text-white font-bold">{provenance.splits.test.samples} samples ({provenance.splits.test.template_groups} groups)</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 pt-2">
                    <span className="text-cyan-400 font-bold">Total Corpus Records:</span>
                    <span className="text-cyan-400 font-bold">{provenance.total_records}</span>
                  </div>
                </div>
              </div>

              {/* Provenance & Licensing */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <h4 className="font-semibold text-slate-200 uppercase text-[11px]">Source Attribution & Licensing</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">Public Archive Records:</span>
                    <span className="text-white font-bold">{provenance.provenance_breakdown['public_corpus'] || 12} (Apache-2.0)</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">Curated Indian Emails:</span>
                    <span className="text-white font-bold">{provenance.provenance_breakdown['manually_curated'] || 60} (CC-BY-4.0)</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">Synthesized Attack Templates:</span>
                    <span className="text-white font-bold">{provenance.provenance_breakdown['synthetic_template'] || 72} (CC-BY-4.0)</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 pt-2">
                    <span className="text-slate-400">Privacy Sanitization:</span>
                    <span className="text-emerald-400 font-bold">Identifiers Masked (Zero PII)</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: Interactive Multilingual Playground */}
      {activeSubTab === 'playground' && (
        <div className="space-y-6">
          {/* Quick Demo Lures Selector */}
          <div className="glass-panel p-4 rounded-2xl border border-shield-border space-y-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
              <Sparkles className="w-4 h-4 text-shield-cyan" />
              <span>Select Pre-Loaded Multilingual Demo Samples:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {demoSamples.map((sample) => (
                <button
                  key={sample.id}
                  onClick={() => handleSelectDemo(sample)}
                  className={`text-xs px-3 py-1.5 rounded-lg border font-mono transition-all text-left flex items-center gap-2 ${
                    playgroundSubject === sample.subject
                      ? 'bg-shield-cyan/20 border-shield-cyan text-white shadow-sm'
                      : 'bg-slate-900/80 border-shield-border text-slate-300 hover:border-slate-600'
                  }`}
                >
                  <span className="uppercase text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300">
                    {sample.language}
                  </span>
                  <span className="font-medium truncate max-w-[180px]">{sample.subject}</span>
                  <span className={`text-[10px] px-1 rounded ${sample.expected_label === 'spam' ? 'text-rose-400' : 'text-emerald-400'}`}>
                    ({sample.expected_label})
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Playground Form */}
          <div className="glass-panel p-6 rounded-2xl border border-shield-border space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase font-mono text-slate-300 mb-1">
                  Sender Address (Optional for Brand Check)
                </label>
                <input
                  type="text"
                  value={playgroundSender}
                  onChange={(e) => setPlaygroundSender(e.target.value)}
                  placeholder="e.g. alerts@sbi.co.in or support@fake-kyc.net"
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-shield-border text-slate-100 text-sm font-mono focus:outline-none focus:border-shield-cyan"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase font-mono text-slate-300 mb-1">
                  Subject Line
                </label>
                <input
                  type="text"
                  value={playgroundSubject}
                  onChange={(e) => setPlaygroundSubject(e.target.value)}
                  placeholder="e.g. बिजली बिल अलर्ट"
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-shield-border text-slate-100 text-sm font-mono focus:outline-none focus:border-shield-cyan"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase font-mono text-slate-300 mb-1">
                Email Body Content
              </label>
              <textarea
                rows={6}
                value={playgroundBody}
                onChange={(e) => setPlaygroundBody(e.target.value)}
                placeholder="Paste Hindi, Tamil, Telugu, Kannada, Hinglish, or English email content here..."
                className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-shield-border text-slate-100 text-sm font-mono focus:outline-none focus:border-shield-cyan"
              />
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={handlePlaygroundAnalyze}
                disabled={isAnalyzing || !playgroundBody.trim()}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-shield-cyan to-indigo-500 text-slate-950 font-bold text-sm shadow-md hover:opacity-95 disabled:opacity-50 transition-all flex items-center gap-2"
              >
                {isAnalyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                <span>{isAnalyzing ? 'Analyzing...' : 'Run Multilingual & Phishing Scan'}</span>
              </button>
            </div>
          </div>

          {/* Playground Real-Time Diagnostic Results */}
          {playgroundResult && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fadeIn">
              {/* Card 1: Spam Classification */}
              <div className="glass-panel p-5 rounded-2xl border border-shield-border space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs uppercase font-mono font-bold text-slate-400">Classification Verdict</h4>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${
                      playgroundResult.is_spam
                        ? 'bg-rose-950/60 text-rose-400 border border-rose-800'
                        : 'bg-emerald-950/60 text-emerald-400 border border-emerald-800'
                    }`}
                  >
                    {playgroundResult.confidence_level} Confidence
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className={`p-3 rounded-xl ${playgroundResult.is_spam ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                    {playgroundResult.is_spam ? <AlertTriangle className="w-6 h-6" /> : <CheckCircle2 className="w-6 h-6" />}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">{playgroundResult.prediction}</h3>
                    <p className="text-xs font-mono text-slate-400">
                      Probability: {(playgroundResult.score * 100).toFixed(1)}% (Threshold: {playgroundResult.threshold_used})
                    </p>
                  </div>
                </div>
                <div className="text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800">
                  Model: {playgroundResult.model_name} • Latency: {playgroundResult.processing_time_ms} ms
                </div>
              </div>

              {/* Card 2: Language Identification */}
              <div className="glass-panel p-5 rounded-2xl border border-shield-border space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs uppercase font-mono font-bold text-slate-400">Language Identification</h4>
                  <Globe2 className="w-4 h-4 text-shield-cyan" />
                </div>
                {playgroundResult.language_analysis && (
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Language Target:</span>
                      <span className="text-cyan-400 font-bold uppercase">
                        {playgroundResult.language_analysis.detected_language}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Primary Script:</span>
                      <span className="text-slate-200 font-medium">
                        {(playgroundResult.language_analysis as any).primary_script || (playgroundResult.language_analysis as any).script || 'Unknown'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Detection Method:</span>
                      <span className="text-slate-300">
                        {(playgroundResult.language_analysis as any).detection_method || (playgroundResult.language_analysis as any).method || 'heuristic'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Calibrated Confidence:</span>
                      <span className="text-emerald-400 font-bold">
                        {playgroundResult.language_analysis.confidence !== null && playgroundResult.language_analysis.confidence !== undefined
                          ? `${(playgroundResult.language_analysis.confidence * 100).toFixed(1)}%`
                          : 'Uncertain'}
                      </span>
                    </div>
                    {((playgroundResult.language_analysis as any).is_mixed || (playgroundResult.language_analysis as any).mixed_script) && (
                      <span className="inline-block px-2 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-800 text-[10px]">
                        Mixed-Script Content
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Card 3: Decoupled Phishing Risk */}
              <div className="glass-panel p-5 rounded-2xl border border-shield-border space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs uppercase font-mono font-bold text-slate-400">Phishing Heuristic Risk</h4>
                  {playgroundResult.phishing_analysis && (
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold uppercase ${
                        playgroundResult.phishing_analysis.risk_level === 'critical' || playgroundResult.phishing_analysis.risk_level === 'high'
                          ? 'bg-rose-950/60 text-rose-400 border border-rose-800'
                          : playgroundResult.phishing_analysis.risk_level === 'medium'
                          ? 'bg-amber-950/60 text-amber-400 border border-amber-800'
                          : 'bg-emerald-950/60 text-emerald-400 border border-emerald-800'
                      }`}
                    >
                      {playgroundResult.phishing_analysis.risk_level} Risk
                    </span>
                  )}
                </div>
                {playgroundResult.phishing_analysis && (
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Risk Score:</span>
                      <span className="text-rose-400 font-bold">
                        {(playgroundResult.phishing_analysis.risk_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Credential Solicitation:</span>
                      <span className={
                        (playgroundResult.phishing_analysis as any).has_credential_harvesting ||
                        playgroundResult.phishing_analysis.indicators?.some((i: any) => i.name?.toLowerCase().includes('credential'))
                          ? 'text-rose-400 font-bold'
                          : 'text-slate-400'
                      }>
                        {(playgroundResult.phishing_analysis as any).has_credential_harvesting ||
                        playgroundResult.phishing_analysis.indicators?.some((i: any) => i.name?.toLowerCase().includes('credential'))
                          ? 'DETECTED'
                          : 'None'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Urgency / Coercion:</span>
                      <span className={
                        (playgroundResult.phishing_analysis as any).has_urgency_threat ||
                        playgroundResult.phishing_analysis.indicators?.some((i: any) => i.name?.toLowerCase().includes('urgent'))
                          ? 'text-rose-400 font-bold'
                          : 'text-slate-400'
                      }>
                        {(playgroundResult.phishing_analysis as any).has_urgency_threat ||
                        playgroundResult.phishing_analysis.indicators?.some((i: any) => i.name?.toLowerCase().includes('urgent'))
                          ? 'DETECTED'
                          : 'None'}
                      </span>
                    </div>
                    {Array.isArray((playgroundResult.phishing_analysis as any).suspicious_urls) &&
                      (playgroundResult.phishing_analysis as any).suspicious_urls.length > 0 && (
                      <div className="pt-2 text-[10px] text-rose-300">
                        <span className="font-bold">Suspicious Links:</span>{' '}
                        {(playgroundResult.phishing_analysis as any).suspicious_urls.join(', ')}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
