import React, { useEffect, useState } from 'react';
import {
  History,
  Search,
  Filter,
  Trash2,
  Download,
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock,
  Eye,
  FileSpreadsheet,
  FileCode,
  X,
} from 'lucide-react';
import { api } from '../services/api';
import { HistoryDetail, HistoryItem } from '../types';

export const HistoryView: React.FC = () => {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [search, setSearch] = useState<string>('');
  const [labelFilter, setLabelFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('timestamp');
  const [sortOrder, setSortOrder] = useState<string>('desc');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Detail View Modal
  const [detailItem, setDetailItem] = useState<HistoryDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getHistory({
        page,
        page_size: pageSize,
        search: search.trim() || undefined,
        label: labelFilter || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setItems(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
      setSelectedIds(new Set());
    } catch (err: any) {
      setError(err.message || 'Failed to load analysis history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, labelFilter, sortBy, sortOrder]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  };

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(new Set(items.map((i) => i.id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleToggleSelect = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedIds(next);
  };

  const handleDeleteSingle = async (id: string) => {
    if (!confirm('Are you sure you want to delete this analysis record?')) return;
    try {
      await api.deleteAnalysis(id);
      fetchHistory();
    } catch (err: any) {
      alert('Delete failed: ' + err.message);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!confirm(`Are you sure you want to delete ${selectedIds.size} selected records?`)) return;
    try {
      await api.bulkDelete(Array.from(selectedIds));
      fetchHistory();
    } catch (err: any) {
      alert('Bulk delete failed: ' + err.message);
    }
  };

  const handleViewDetail = async (id: string) => {
    try {
      setLoadingDetail(true);
      const detail = await api.getAnalysisDetail(id);
      setDetailItem(detail);
    } catch (err: any) {
      alert('Could not fetch analysis details: ' + err.message);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      await api.downloadExport(format);
    } catch (err: any) {
      alert('Export failed: ' + err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Analysis History</h1>
          <p className="text-sm text-slate-400 mt-1">
            Search, review feature attributions, and export audit trails of analyzed email records.
          </p>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport('csv')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-shield-border text-xs font-medium transition-colors"
            title="Download CSV report with formula injection protection"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => handleExport('json')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-shield-border text-xs font-medium transition-colors"
            title="Download JSON export"
          >
            <FileCode className="w-3.5 h-3.5 text-cyan-400" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl glass-panel border border-shield-border flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search subjects or predictions..."
            className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-900 border border-shield-border text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-shield-cyan"
          />
        </form>

        {/* Filter Pills and Sort */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-between md:justify-end">
          {/* Label Filter */}
          <div className="flex items-center rounded-lg bg-slate-900 p-0.5 border border-shield-border text-xs">
            {['', 'Spam', 'Legitimate'].map((lbl) => (
              <button
                key={lbl}
                type="button"
                onClick={() => {
                  setLabelFilter(lbl);
                  setPage(1);
                }}
                className={`px-3 py-1 rounded-md font-medium transition-colors ${
                  labelFilter === lbl
                    ? 'bg-shield-surface text-shield-cyan font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {lbl || 'All'}
              </button>
            ))}
          </div>

          {/* Sort By */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-shield-border text-xs text-slate-300 focus:outline-none focus:border-shield-cyan"
          >
            <option value="timestamp">Sort: Date</option>
            <option value="score">Sort: Confidence Score</option>
            <option value="subject">Sort: Subject</option>
          </select>

          {/* Bulk Delete Action */}
          {selectedIds.size > 0 && (
            <button
              onClick={handleBulkDelete}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 hover:bg-rose-900/60 text-xs font-semibold transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete Selected ({selectedIds.size})</span>
            </button>
          )}
        </div>
      </div>

      {/* History Table Container */}
      <div className="glass-panel rounded-2xl border border-shield-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-400 animate-pulse text-sm">
            Loading analysis history records...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-400 text-sm">{error}</div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <History className="w-10 h-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm">No analysis records match your query.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-shield-border bg-slate-900/80 text-slate-400 uppercase font-mono tracking-wider">
                  <th className="py-3 px-4 w-10">
                    <input
                      type="checkbox"
                      checked={selectedIds.size === items.length && items.length > 0}
                      onChange={handleSelectAll}
                      className="rounded border-slate-700 bg-slate-900 text-shield-cyan focus:ring-0"
                    />
                  </th>
                  <th className="py-3 px-4">Subject</th>
                  <th className="py-3 px-4">Prediction</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Model & Threshold</th>
                  <th className="py-3 px-4">Date & Time</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {items.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-slate-800/30 transition-colors group"
                  >
                    <td className="py-3 px-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(item.id)}
                        onChange={() => handleToggleSelect(item.id)}
                        className="rounded border-slate-700 bg-slate-900 text-shield-cyan focus:ring-0"
                      />
                    </td>
                    <td className="py-3 px-4 max-w-xs truncate font-medium text-slate-200">
                      {item.subject}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-mono font-semibold ${
                          item.is_spam
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        }`}
                      >
                        {item.is_spam ? (
                          <AlertTriangle className="w-3 h-3" />
                        ) : (
                          <CheckCircle2 className="w-3 h-3" />
                        )}
                        <span>{item.prediction}</span>
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono">
                      <span className={item.is_spam ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
                        {item.score_type === 'probability'
                          ? `${(item.score * 100).toFixed(1)}%`
                          : item.score.toFixed(3)}
                      </span>
                      <span className="text-[11px] text-slate-300 block font-mono">
                        {item.score_type === 'probability' ? (item.calibrated ? 'Calibrated' : 'Prob') : 'Margin'}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-200">
                      <div>{item.model_name}</div>
                      <div className="text-[11px] text-slate-300">&tau; = {item.threshold_used}</div>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-200">
                      <div>{new Date(item.timestamp).toLocaleDateString()}</div>
                      <div className="text-[11px] text-slate-300">{new Date(item.timestamp).toLocaleTimeString()}</div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => handleViewDetail(item.id)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-shield-cyan hover:bg-slate-800 transition-colors"
                          title="View Feature Explanations"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteSingle(item.id)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 transition-colors"
                          title="Delete Record"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        <div className="p-4 border-t border-shield-border flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing {items.length} of {total} records (Page {page} of {totalPages})
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              disabled={page <= 1}
              className="p-1.5 rounded-lg bg-slate-900 border border-shield-border hover:bg-slate-800 disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-slate-200">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg bg-slate-900 border border-shield-border hover:bg-slate-800 disabled:opacity-40"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Analysis Detail Modal */}
      {detailItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="glass-panel p-6 rounded-2xl border border-shield-border w-full max-w-2xl max-h-[90vh] overflow-y-auto space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-shield-border">
              <div className="flex items-center gap-3">
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-mono font-semibold ${
                    detailItem.is_spam
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  }`}
                >
                  {detailItem.prediction}
                </span>
                <h3 className="text-base font-bold text-white truncate max-w-md">{detailItem.subject}</h3>
              </div>
              <button
                onClick={() => setDetailItem(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Metadata Chips */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block">Score</span>
                <span className="text-white font-bold">
                  {detailItem.score_type === 'probability'
                    ? `${(detailItem.score * 100).toFixed(1)}%`
                    : detailItem.score.toFixed(3)}
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block">Model</span>
                <span className="text-white font-bold">{detailItem.model_name}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block">Latency</span>
                <span className="text-white font-bold">{detailItem.processing_time_ms} ms</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block">Content Hash</span>
                <span className="text-slate-300 truncate block" title={detailItem.email_hash}>
                  {detailItem.email_hash.slice(0, 8)}...
                </span>
              </div>
            </div>

            {/* Email Body if Stored */}
            {detailItem.is_content_stored && detailItem.email_body ? (
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Stored Email Body</label>
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 max-h-48 overflow-y-auto whitespace-pre-wrap">
                  {detailItem.email_body}
                </div>
              </div>
            ) : (
              <div className="p-3 rounded-xl bg-slate-900/40 border border-slate-800 text-xs text-slate-500">
                Email text body was not permanently stored for this record pursuant to user privacy settings.
              </div>
            )}

            {/* Feature Contributions Breakdown */}
            {detailItem.explanations && (
              <div className="space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Feature Attribution Tokens
                </h4>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Spam tokens */}
                  <div className="p-3 rounded-xl bg-slate-900/60 border border-rose-900/30 space-y-2">
                    <span className="text-xs font-bold text-rose-400">Spam Signals</span>
                    {detailItem.explanations.top_spam_features.length === 0 ? (
                      <p className="text-xs text-slate-500 italic">None</p>
                    ) : (
                      detailItem.explanations.top_spam_features.map((f, i) => (
                        <div key={i} className="flex justify-between text-xs font-mono">
                          <span className="text-slate-200">{f.token}</span>
                          <span className="text-rose-400">+{f.contribution.toFixed(3)}</span>
                        </div>
                      ))
                    )}
                  </div>

                  {/* Ham tokens */}
                  <div className="p-3 rounded-xl bg-slate-900/60 border border-emerald-900/30 space-y-2">
                    <span className="text-xs font-bold text-emerald-400">Legitimate Signals</span>
                    {detailItem.explanations.top_legitimate_features.length === 0 ? (
                      <p className="text-xs text-slate-500 italic">None</p>
                    ) : (
                      detailItem.explanations.top_legitimate_features.map((f, i) => (
                        <div key={i} className="flex justify-between text-xs font-mono">
                          <span className="text-slate-200">{f.token}</span>
                          <span className="text-emerald-400">{f.contribution.toFixed(3)}</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setDetailItem(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-white font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
