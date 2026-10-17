import React, { useEffect, useState } from 'react';
import {
  FlaskConical,
  BarChart3,
  Sliders,
  Shield,
  Layers,
  Database,
  Info,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Cpu,
} from 'lucide-react';
import { api } from '../services/api';
import { ModelInfo, ModelListResponse, ThresholdSimulationResponse } from '../types';

export const ModelLabView: React.FC = () => {
  const [modelData, setModelData] = useState<ModelListResponse | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('logistic_regression');
  const [simThreshold, setSimThreshold] = useState<number>(0.5);
  const [simResult, setSimResult] = useState<ThresholdSimulationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function initModelLab() {
      try {
        setLoading(true);
        const res = await api.getModels();
        setModelData(res);
        if (res.models.length > 0) {
          const initialModel = res.active_model || res.models[0].name;
          setSelectedModel(initialModel);
          fetchSimulation(initialModel, 0.5);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load model lab data.');
      } finally {
        setLoading(false);
      }
    }
    initModelLab();
  }, []);

  const fetchSimulation = async (model: string, tau: number) => {
    try {
      setSimulating(true);
      const res = await api.getThresholdSimulation(model, tau);
      setSimResult(res);
    } catch (err: any) {
      console.error('Threshold simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleModelChange = (model: string) => {
    setSelectedModel(model);
    fetchSimulation(model, simThreshold);
  };

  const handleThresholdChange = (tau: number) => {
    setSimThreshold(tau);
    fetchSimulation(selectedModel, tau);
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-slate-800 rounded w-1/4"></div>
        <div className="h-64 bg-shield-surface/60 rounded-xl border border-shield-border"></div>
      </div>
    );
  }

  const currentMetrics = simResult?.current_metrics;
  const cm = currentMetrics?.confusion_matrix || [
    [0, 0],
    [0, 0],
  ];
  const tn = cm[0][0];
  const fp = cm[0][1];
  const fn = cm[1][0];
  const tp = cm[1][1];

  return (
    <div className="space-y-8">
      {/* View Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Model Lab & Performance Benchmarking</h1>
        <p className="text-sm text-slate-400 mt-1">
          Compare scikit-learn classifiers, inspect independent test benchmarks, and simulate decision thresholds using genuine validation predictions.
        </p>
      </div>

      {/* Model Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {modelData?.models.map((m) => {
          const isSelected = selectedModel === m.name;
          return (
            <div
              key={m.name}
              onClick={() => handleModelChange(m.name)}
              className={`p-5 rounded-2xl cursor-pointer transition-all border ${
                isSelected
                  ? 'glass-panel border-shield-cyan shadow-lg shadow-shield-cyan/5 bg-shield-surface/80'
                  : 'glass-card border-shield-border hover:border-slate-700 hover:bg-slate-900/60'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-800 text-shield-cyan">
                  {m.name.toUpperCase()}
                </span>
                <span className="text-[11px] font-mono text-slate-400">
                  {m.calibrated ? 'Calibrated' : 'Uncalibrated'}
                  {m.test_metrics.brier_score !== undefined && m.test_metrics.brier_score !== null && (
                    <span className="text-purple-400 ml-1.5">(Brier: {m.test_metrics.brier_score.toFixed(3)})</span>
                  )}
                </span>
              </div>

              <h3 className="text-sm font-bold text-white mb-1">{m.display_name}</h3>
              <p className="text-xs text-slate-400 mb-4">
                Optimal validation threshold: <span className="font-mono text-white">&tau; = {m.optimal_threshold}</span>
              </p>

              {/* Test Metrics Grid */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-3 border-t border-slate-800/80">
                <div className="p-2 rounded-lg bg-[#060b14] border border-slate-800">
                  <span className="text-slate-300 block text-[11px] font-medium">Test Accuracy</span>
                  <span className="text-slate-100 font-bold">
                    {(m.test_metrics.accuracy * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-2 rounded-lg bg-[#060b14] border border-slate-800">
                  <span className="text-slate-300 block text-[11px] font-medium">Test F1 Score</span>
                  <span className="text-shield-cyan font-bold">
                    {(m.test_metrics.f1_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-2 rounded-lg bg-[#060b14] border border-slate-800">
                  <span className="text-slate-300 block text-[11px] font-medium">Test Recall</span>
                  <span className="text-slate-100 font-bold">
                    {(m.test_metrics.recall * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="p-2 rounded-lg bg-[#060b14] border border-slate-800">
                  <span className="text-slate-300 block text-[11px] font-medium">False Pos. Rate</span>
                  <span className="text-emerald-400 font-bold">
                    {(m.test_metrics.false_positive_rate * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Interactive Threshold Simulator */}
      <div className="glass-panel p-6 rounded-2xl border border-shield-border space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-shield-border">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-shield-cyan text-[11px] font-mono mb-1.5">
              <Sliders className="w-3.5 h-3.5" />
              <span>DYNAMIC VALIDATION SIMULATOR</span>
            </div>
            <h2 className="text-lg font-bold text-white">
              Validation Threshold Sweep: {selectedModel.replace('_', ' ').toUpperCase()}
            </h2>
            <p className="text-xs text-slate-300">
              Evaluated on genuine holdout validation predictions without data fabrication.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-mono text-slate-300">Decision Threshold:</span>
            <span className="text-xl font-bold font-mono text-shield-cyan bg-[#060b14] px-3 py-1 rounded-xl border border-shield-border">
              &tau; = {simThreshold.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Threshold Slider Control */}
        <div className="space-y-2">
          <input
            type="range"
            min="0.05"
            max="0.95"
            step="0.05"
            value={simThreshold}
            onChange={(e) => handleThresholdChange(parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-shield-cyan"
          />
          <div className="flex justify-between text-xs text-slate-300 font-mono">
            <span>0.05 (High Recall, higher FP risk)</span>
            <span>0.50 (Standard Decision Boundary)</span>
            <span>0.95 (Ultra-conservative, near zero FP)</span>
          </div>
        </div>

        {/* Live Metrics at Current Threshold */}
        {currentMetrics && (
          <div className="grid grid-cols-2 sm:grid-cols-6 gap-3 font-mono text-xs">
            <div className="p-3 rounded-xl bg-[#060b14] border border-slate-800">
              <span className="text-slate-300 block mb-1 font-medium">Accuracy</span>
              <span className="text-lg font-bold text-white">{(currentMetrics.accuracy * 100).toFixed(1)}%</span>
            </div>
            <div className="p-3 rounded-xl bg-[#060b14] border border-slate-800">
              <span className="text-slate-300 block mb-1 font-medium">Precision</span>
              <span className="text-lg font-bold text-white">{(currentMetrics.precision * 100).toFixed(1)}%</span>
            </div>
            <div className="p-3 rounded-xl bg-[#060b14] border border-slate-800">
              <span className="text-slate-300 block mb-1 font-medium">Recall</span>
              <span className="text-lg font-bold text-white">{(currentMetrics.recall * 100).toFixed(1)}%</span>
            </div>
            <div className="p-3 rounded-xl bg-[#060b14] border border-slate-800">
              <span className="text-slate-300 block mb-1 font-medium">F1 Score</span>
              <span className="text-lg font-bold text-shield-cyan">{(currentMetrics.f1_score * 100).toFixed(1)}%</span>
            </div>
            <div className="p-3 rounded-xl bg-[#060b14] border border-slate-800">
              <span className="text-slate-300 block mb-1 font-medium">False Pos. Rate</span>
              <span className="text-lg font-bold text-emerald-400">
                {(currentMetrics.false_positive_rate * 100).toFixed(1)}%
              </span>
            </div>
            <div className="p-3 rounded-xl bg-[#060b14] border border-slate-800">
              <span className="text-slate-300 block mb-1 font-medium">Brier Calibration</span>
              <span className="text-lg font-bold text-purple-400">
                {currentMetrics.brier_score !== undefined && currentMetrics.brier_score !== null
                  ? currentMetrics.brier_score.toFixed(4)
                  : 'N/A'}
              </span>
            </div>
          </div>
        )}

        {/* Confusion Matrix Heatmap */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
              Validation Confusion Matrix at &tau; = {simThreshold.toFixed(2)}
            </h4>
            <div className="grid grid-cols-2 gap-3 text-center font-mono">
              {/* True Negative */}
              <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/50">
                <span className="text-[11px] text-emerald-400 block font-semibold mb-1">True Negative (TN)</span>
                <span className="text-2xl font-bold text-white">{tn}</span>
                <span className="text-[10px] text-slate-400 block mt-1">Legitimate correctly identified</span>
              </div>

              {/* False Positive */}
              <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-800/50">
                <span className="text-[11px] text-rose-400 block font-semibold mb-1">False Positive (FP)</span>
                <span className="text-2xl font-bold text-white">{fp}</span>
                <span className="text-[10px] text-slate-400 block mt-1">Legitimate misclassified as Spam</span>
              </div>

              {/* False Negative */}
              <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-800/50">
                <span className="text-[11px] text-amber-400 block font-semibold mb-1">False Negative (FN)</span>
                <span className="text-2xl font-bold text-white">{fn}</span>
                <span className="text-[10px] text-slate-400 block mt-1">Spam leaked to inbox</span>
              </div>

              {/* True Positive */}
              <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-800/50">
                <span className="text-[11px] text-cyan-400 block font-semibold mb-1">True Positive (TP)</span>
                <span className="text-2xl font-bold text-white">{tp}</span>
                <span className="text-[10px] text-slate-400 block mt-1">Spam correctly blocked</span>
              </div>
            </div>
          </div>

          {/* Trade-off Analysis Narrative */}
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                Operational Trade-off Analysis
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                Adjusting the decision threshold &tau; modulates the sensitivity of spam filtering:
              </p>
              <ul className="mt-3 space-y-2 text-xs text-slate-400">
                <li className="flex items-start gap-2">
                  <span className="text-shield-cyan">&bull;</span>
                  <span>
                    <strong>Lower threshold (&lt; 0.30):</strong> Prioritizes spam blocking. Maximizes recall, but increases risk of misclassifying legitimate business emails as spam.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-shield-cyan">&bull;</span>
                  <span>
                    <strong>Higher threshold (&gt; 0.70):</strong> Protects legitimate mail deliverability by pushing False Positive Rate towards 0%, requiring stronger statistical evidence to classify as spam.
                  </span>
                </li>
              </ul>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 font-mono">
              Status: {simulating ? 'Calculating metrics...' : 'Synchronized with validation ground truth.'}
            </div>
          </div>
        </div>
      </div>

      {/* Independent Test Dataset Final Evaluation Table */}
      <div className="glass-panel p-6 rounded-2xl border border-shield-border">
        <h2 className="text-base font-bold text-white mb-1">Independent Test Set Evaluation (Holdout Split)</h2>
        <p className="text-xs text-slate-400 mb-4">
          Unbiased metrics calculated strictly on final unseen test samples. Never used for model fitting or threshold selection.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-shield-border text-slate-400 uppercase tracking-wider">
                <th className="py-2.5 px-3">Model</th>
                <th className="py-2.5 px-3">Test Samples</th>
                <th className="py-2.5 px-3">Accuracy</th>
                <th className="py-2.5 px-3">Precision</th>
                <th className="py-2.5 px-3">Recall</th>
                <th className="py-2.5 px-3">F1 Score</th>
                <th className="py-2.5 px-3">False Pos. Rate</th>
                <th className="py-2.5 px-3">PR-AUC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {modelData?.models.map((m) => (
                <tr key={m.name} className="hover:bg-slate-800/20">
                  <td className="py-3 px-3 font-semibold text-white">{m.display_name}</td>
                  <td className="py-3 px-3">{m.test_metrics.num_samples}</td>
                  <td className="py-3 px-3">{(m.test_metrics.accuracy * 100).toFixed(1)}%</td>
                  <td className="py-3 px-3">{(m.test_metrics.precision * 100).toFixed(1)}%</td>
                  <td className="py-3 px-3">{(m.test_metrics.recall * 100).toFixed(1)}%</td>
                  <td className="py-3 px-3 text-shield-cyan font-bold">
                    {(m.test_metrics.f1_score * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-3 text-emerald-400">
                    {(m.test_metrics.false_positive_rate * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-3">
                    {m.test_metrics.pr_auc !== null ? m.test_metrics.pr_auc.toFixed(3) : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
