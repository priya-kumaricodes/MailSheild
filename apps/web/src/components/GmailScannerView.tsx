import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  Inbox,
  Lock,
  Mail,
  RefreshCw,
  Search,
  Shield,
  ShieldAlert,
  Trash2,
} from 'lucide-react';
import { api } from '../services/api';
import {
  GmailMessageSummary,
  GmailScanBatchResponse,
  GmailStatus,
} from '../types';

export const GmailScannerView: React.FC = () => {
  const [status, setStatus] = useState<GmailStatus | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);

  // Message listing state
  const [messages, setMessages] = useState<GmailMessageSummary[]>([]);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [batchLimit, setBatchLimit] = useState<number>(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  // Scanning & Privacy state
  const [storeContent, setStoreContent] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scanResults, setScanResults] = useState<GmailScanBatchResponse | null>(null);

  // Error / message alert
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    setLoadingStatus(true);
    setErrorMessage(null);
    try {
      const data = await api.getGmailStatus();
      setStatus(data);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to fetch Gmail status');
    } finally {
      setLoadingStatus(false);
    }
  };

  const handleConnect = async () => {
    setConnecting(true);
    setErrorMessage(null);
    try {
      const isDesktop = typeof window !== 'undefined' && Boolean(window.mailshieldDesktop);
      const clientType = isDesktop ? 'desktop' : 'web';
      const authData = await api.getGmailAuthUrl(clientType);

      if (!authData.is_configured || !authData.auth_url) {
        setErrorMessage(
          'Google OAuth client credentials are not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.'
        );
        return;
      }

      if (isDesktop && window.mailshieldDesktop?.openExternal) {
        window.mailshieldDesktop.openExternal(authData.auth_url);
        setSuccessMessage(
          'Google authorization page opened in your default browser. Complete consent there to connect.'
        );
      } else {
        window.location.href = authData.auth_url;
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to initiate Google authorization');
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Are you sure you want to disconnect your Gmail account from MailShield?')) {
      return;
    }
    setDisconnecting(true);
    setErrorMessage(null);
    try {
      const resp = await api.disconnectGmail();
      setSuccessMessage(resp.message);
      setStatus({
        connected: false,
        email: null,
        scopes: [],
        connected_at: null,
        is_configured: status?.is_configured ?? false,
      });
      setMessages([]);
      setSelectedIds(new Set());
      setScanResults(null);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to disconnect Gmail account');
    } finally {
      setDisconnecting(false);
    }
  };

  const handleFetchMessages = async () => {
    setLoadingMessages(true);
    setErrorMessage(null);
    try {
      const resp = await api.listGmailMessages(batchLimit, undefined, searchQuery || undefined);
      setMessages(resp.messages);
      // Select all by default
      setSelectedIds(new Set(resp.messages.map((m) => m.id)));
      setScanResults(null);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to fetch messages from Gmail');
    } finally {
      setLoadingMessages(false);
    }
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === messages.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(messages.map((m) => m.id)));
    }
  };

  const toggleSelectOne = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedIds(next);
  };

  const handleScanSelected = async () => {
    if (selectedIds.size === 0) {
      setErrorMessage('Please select at least one email message to scan.');
      return;
    }
    setScanning(true);
    setErrorMessage(null);
    try {
      const ids = Array.from(selectedIds);
      const results = await api.scanGmailMessages(ids, storeContent);
      setScanResults(results);
      setSuccessMessage(`Successfully scanned ${results.total_scanned} emails.`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to scan selected emails');
    } finally {
      setScanning(false);
    }
  };

  if (loadingStatus) {
    return (
      <div className="flex items-center justify-center p-12">
        <RefreshCw className="w-8 h-8 text-primary-500 animate-spin" />
        <span className="ml-3 text-slate-300">Loading Gmail integration status...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Banner / Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border border-shield-border shadow-2xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-cyan-950/60 text-shield-cyan border border-cyan-800/60 rounded-xl">
              <Mail className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white flex items-center gap-2">
                Gmail Inbox Scanner
                <span className="px-2.5 py-0.5 text-xs bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 rounded-full font-medium">
                  Read-Only Minimal Scope
                </span>
              </h1>
              <p className="text-sm text-slate-300 mt-0.5">
                Direct inbox scanning powered by MailShield's multilingual classifier and phishing threat engine.
              </p>
            </div>
          </div>
        </div>

        {/* Connection Action */}
        <div className="flex items-center gap-3">
          {status?.connected ? (
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-xs text-slate-400">Connected Account</div>
                <div className="text-sm font-semibold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle className="w-4 h-4" />
                  {status.email}
                </div>
              </div>
              <button
                onClick={handleDisconnect}
                disabled={disconnecting}
                className="px-3.5 py-2 text-sm bg-rose-950/40 hover:bg-rose-900/50 text-rose-300 border border-rose-800/60 rounded-lg transition-colors flex items-center gap-2"
                title="Disconnect account and revoke tokens"
              >
                {disconnecting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                Disconnect
              </button>
            </div>
          ) : (
            <button
              onClick={handleConnect}
              disabled={connecting || !status?.is_configured}
              className={`px-5 py-2.5 text-sm font-semibold rounded-xl shadow-lg flex items-center gap-2.5 transition-all ${
                status?.is_configured
                  ? 'bg-gradient-to-r from-shield-cyan to-shield-accent hover:opacity-95 text-slate-950 cursor-pointer shadow-shield-cyan/10'
                  : 'bg-slate-800 text-slate-400 cursor-not-allowed border border-slate-700'
              }`}
            >
              {connecting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ExternalLink className="w-4 h-4" />}
              Connect Gmail
            </button>
          )}
        </div>
      </div>

      {/* Unconfigured Credentials Warning */}
      {!status?.is_configured && (
        <div className="p-4 bg-amber-950/40 border border-amber-800/60 rounded-xl text-amber-200 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-amber-300">Google OAuth Credentials Required: </span>
            To enable Gmail scanning, please configure <code className="bg-amber-900/60 px-1 py-0.5 rounded text-xs font-mono text-amber-200">GOOGLE_CLIENT_ID</code> and <code className="bg-amber-900/60 px-1 py-0.5 rounded text-xs font-mono text-amber-200">GOOGLE_CLIENT_SECRET</code> in your environment or <code className="bg-amber-900/60 px-1 py-0.5 rounded text-xs font-mono text-amber-200">.env</code> file.
            Consult <span className="font-semibold text-amber-100">docs/GMAIL_SETUP.md</span> for the step-by-step Google Cloud Console setup guide.
          </div>
        </div>
      )}

      {/* Messages / Alerts */}
      {errorMessage && (
        <div className="p-4 bg-rose-950/40 border border-rose-800/60 rounded-xl text-rose-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-slate-400 hover:text-white text-xs">
            Dismiss
          </button>
        </div>
      )}

      {successMessage && (
        <div className="p-4 bg-emerald-950/40 border border-emerald-800/60 rounded-xl text-emerald-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage(null)} className="text-slate-400 hover:text-white text-xs">
            Dismiss
          </button>
        </div>
      )}

      {/* Connected State Content */}
      {status?.connected ? (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="glass-panel p-5 rounded-2xl border border-shield-border flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <label className="text-xs font-medium text-slate-300">Batch Limit:</label>
                <select
                  value={batchLimit}
                  onChange={(e) => setBatchLimit(Number(e.target.value))}
                  className="bg-[#060b14] border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-shield-cyan"
                >
                  <option value={5}>5 emails</option>
                  <option value={10}>10 emails</option>
                  <option value={25}>25 emails</option>
                  <option value={50}>50 emails</option>
                </select>
              </div>

              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Optional query (e.g. label:INBOX)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-[#060b14] border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:border-shield-cyan w-64"
                />
              </div>

              <button
                onClick={handleFetchMessages}
                disabled={loadingMessages}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
              >
                {loadingMessages ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Inbox className="w-4 h-4" />}
                Fetch Recent Messages
              </button>
            </div>

            {/* Privacy Setting & Scan Action */}
            <div className="flex items-center gap-5">
              <label className="flex items-center gap-2.5 text-xs text-slate-300 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={storeContent}
                  onChange={(e) => setStoreContent(e.target.checked)}
                  className="w-4 h-4 rounded text-shield-cyan bg-slate-900 border-slate-700 focus:ring-shield-cyan"
                />
                <span className="flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-slate-400" />
                  Save email bodies to History
                </span>
                <span className="text-slate-400 text-[10px]">(Default off: in-memory only)</span>
              </label>

              <button
                onClick={handleScanSelected}
                disabled={scanning || selectedIds.size === 0}
                className="px-5 py-2 bg-gradient-to-r from-shield-cyan to-shield-accent hover:opacity-95 disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 font-semibold text-sm rounded-xl transition-all flex items-center gap-2 shadow-lg shadow-shield-cyan/10"
              >
                {scanning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
                Scan Selected ({selectedIds.size})
              </button>
            </div>
          </div>

          {/* Messages Table */}
          {messages.length > 0 && (
            <div className="glass-panel rounded-2xl border border-shield-border overflow-hidden shadow-xl">
              <div className="px-5 py-3.5 bg-[#03060c] border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.size === messages.length && messages.length > 0}
                    onChange={toggleSelectAll}
                    className="w-4 h-4 rounded text-shield-cyan bg-slate-900 border-slate-700 focus:ring-shield-cyan"
                  />
                  <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    Recent Inbox Messages ({messages.length})
                  </span>
                </div>
                <div className="text-xs text-slate-400">
                  {selectedIds.size} of {messages.length} selected
                </div>
              </div>

              <div className="divide-y divide-slate-800/80 max-h-96 overflow-y-auto">
                {messages.map((msg) => {
                  const isChecked = selectedIds.has(msg.id);
                  return (
                    <div
                      key={msg.id}
                      onClick={() => toggleSelectOne(msg.id)}
                      className={`p-4 flex items-center gap-4 transition-colors cursor-pointer ${
                        isChecked ? 'bg-cyan-950/20' : 'hover:bg-slate-900/60'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => {}} // handled by row click
                        className="w-4 h-4 rounded text-shield-cyan bg-slate-900 border-slate-700 focus:ring-shield-cyan shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <span className="text-sm font-semibold text-white truncate max-w-sm">{msg.sender}</span>
                          <span className="text-xs text-slate-400 shrink-0">{msg.date}</span>
                        </div>
                        <div className="text-sm text-slate-200 font-medium truncate mb-0.5">{msg.subject}</div>
                        <div className="text-xs text-slate-400 truncate">{msg.snippet}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Scan Results Section */}
          {scanResults && (
            <div className="space-y-4 pt-2">
              <div className="flex flex-wrap items-center justify-between gap-4 glass-panel p-4 rounded-2xl border border-shield-border">
                <div className="flex items-center gap-3">
                  <h2 className="text-lg font-bold text-white">Scan Batch Summary</h2>
                  <span className="text-xs px-2.5 py-1 bg-[#060b14] border border-slate-700 text-slate-200 rounded-full font-medium">
                    Total: {scanResults.total_scanned}
                  </span>
                  <span className="text-xs px-2.5 py-1 bg-rose-950/60 text-rose-300 border border-rose-800/60 rounded-full font-medium">
                    Spam: {scanResults.spam_count}
                  </span>
                  <span className="text-xs px-2.5 py-1 bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 rounded-full font-medium">
                    Legitimate: {scanResults.ham_count}
                  </span>
                  {scanResults.error_count > 0 && (
                    <span className="text-xs px-2.5 py-1 bg-amber-950/60 text-amber-300 border border-amber-800/60 rounded-full font-medium">
                      Errors: {scanResults.error_count}
                    </span>
                  )}
                </div>
                <div className="text-xs text-slate-300 flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-emerald-400" />
                  {storeContent ? 'Saved to prediction history' : 'Processed purely in-memory (privacy default)'}
                </div>
              </div>

              {/* Individual Scanned Email Cards */}
              <div className="space-y-3">
                {scanResults.results.map((res) => {
                  const isSpam = res.prediction.toLowerCase() === 'spam';
                  const riskLevel = res.phishing_risk?.risk_level?.toLowerCase() || 'low';
                  const isHighRisk = riskLevel === 'high' || riskLevel === 'critical';

                  return (
                    <div
                      key={res.message_id}
                      className={`p-5 rounded-xl border transition-all ${
                        isSpam
                          ? 'bg-[#180a0e] border-rose-900/60'
                          : 'bg-[#060b14] border-slate-700/80'
                      }`}
                    >
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
                        <div className="min-w-0">
                          <h3 className="text-base font-bold text-white truncate">{res.subject}</h3>
                          <div className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                            <span className="text-slate-300 font-medium">{res.sender}</span>
                            <span>•</span>
                            <span>{res.date}</span>
                          </div>
                        </div>

                        {/* Badges */}
                        <div className="flex flex-wrap items-center gap-2 shrink-0">
                          {/* Prediction Badge */}
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${
                              isSpam
                                ? 'bg-rose-900/60 text-rose-200 border border-rose-700/60'
                                : 'bg-emerald-900/60 text-emerald-200 border border-emerald-700/60'
                            }`}
                          >
                            {isSpam ? <ShieldAlert className="w-3.5 h-3.5" /> : <Shield className="w-3.5 h-3.5" />}
                            {res.prediction} ({Math.round(res.probability * 100)}%)
                          </span>

                          {/* Phishing Badge */}
                          <span
                            className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                              isHighRisk
                                ? 'bg-amber-900/60 text-amber-200 border border-amber-700/60'
                                : 'bg-slate-700/70 text-slate-300 border border-slate-600/60'
                            }`}
                          >
                            Phishing Risk: {res.phishing_risk?.risk_level || 'Low'}
                          </span>

                          {/* Language Badge */}
                          <span className="px-2.5 py-1 rounded-full text-xs bg-slate-700/70 text-slate-300 border border-slate-600/60 font-medium">
                            {res.language?.toUpperCase() || 'EN'}
                            {res.is_mixed && ' (Mixed)'}
                          </span>
                        </div>
                      </div>

                      {/* Phishing Threat Indicators */}
                      {res.phishing_risk?.indicators_triggered && res.phishing_risk.indicators_triggered.length > 0 && (
                        <div className="mb-3 p-3 bg-amber-950/30 border border-amber-800/40 rounded-lg text-xs text-amber-200 flex flex-wrap gap-2 items-center">
                          <span className="font-semibold text-amber-300 flex items-center gap-1">
                            <AlertTriangle className="w-3.5 h-3.5" /> Threat Indicators:
                          </span>
                          {res.phishing_risk.indicators_triggered.map((ind: any, idx: number) => (
                            <span key={idx} className="bg-amber-900/50 px-2 py-0.5 rounded text-amber-100 border border-amber-700/50">
                              {ind.name || ind}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Top Predictive Explainability Tokens */}
                      {res.top_tokens && res.top_tokens.length > 0 && (
                        <div className="pt-2 border-t border-slate-700/50 flex flex-wrap items-center gap-2">
                          <span className="text-xs text-slate-400 font-medium">Key Evidence:</span>
                          {res.top_tokens.map((tok, idx) => (
                            <span
                              key={idx}
                              className={`text-xs px-2 py-0.5 rounded border font-mono ${
                                tok.direction?.toLowerCase() === 'spam'
                                  ? 'bg-rose-950/50 text-rose-300 border-rose-800/50'
                                  : 'bg-emerald-950/50 text-emerald-300 border-emerald-800/50'
                              }`}
                              title={tok.description}
                            >
                              {tok.token} ({tok.weight > 0 ? `+${tok.weight}` : tok.weight})
                            </span>
                          ))}
                        </div>
                      )}

                      {res.error && (
                        <div className="mt-2 text-xs text-rose-400 font-medium">
                          Note: {res.error}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Disconnected Hero Card */
        <div className="bg-slate-800 p-8 rounded-xl border border-slate-700 text-center max-w-2xl mx-auto space-y-6 shadow-xl">
          <div className="w-16 h-16 bg-primary-950/60 text-primary-400 border border-primary-800/60 rounded-2xl flex items-center justify-center mx-auto shadow-inner">
            <Mail className="w-8 h-8" />
          </div>

          <div className="space-y-2">
            <h2 className="text-xl font-bold text-white">Connect Your Gmail Inbox</h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Scan emails directly from your Gmail inbox using MailShield's explainable multilingual ML models without giving away your password or compromising your privacy.
            </p>
          </div>

          <div className="p-4 bg-slate-900/60 border border-slate-750 rounded-xl text-left space-y-2.5 text-xs text-slate-300">
            <div className="font-semibold text-white flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" />
              Security & Privacy Guarantee
            </div>
            <ul className="space-y-1.5 list-disc list-inside text-slate-400">
              <li><strong className="text-slate-200">Strictly Read-Only:</strong> We only request read permission. MailShield cannot send, modify, or delete your emails.</li>
              <li><strong className="text-slate-200">Zero Password Storage:</strong> Authorization is handled entirely via Google's secure OAuth 2.0 consent screen.</li>
              <li><strong className="text-slate-200">Encrypted Tokens at Rest:</strong> Refresh tokens are encrypted using AES-256-GCM authenticated encryption.</li>
              <li><strong className="text-slate-200">In-Memory Privacy Default:</strong> Email bodies are analyzed in-memory and discarded immediately unless you explicitly opt in to save them.</li>
            </ul>
          </div>

          <button
            onClick={handleConnect}
            disabled={connecting || !status?.is_configured}
            className={`w-full py-3 px-4 text-sm font-semibold rounded-lg shadow-lg flex items-center justify-center gap-2.5 transition-all ${
              status?.is_configured
                ? 'bg-primary-600 hover:bg-primary-500 text-white cursor-pointer'
                : 'bg-slate-700 text-slate-400 cursor-not-allowed border border-slate-600'
            }`}
          >
            {connecting ? <RefreshCw className="w-5 h-5 animate-spin" /> : <ExternalLink className="w-5 h-5" />}
            Connect with Google
          </button>
        </div>
      )}
    </div>
  );
};
