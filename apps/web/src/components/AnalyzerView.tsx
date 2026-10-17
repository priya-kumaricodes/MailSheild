import React, { useState } from 'react';
import {
  Inbox,
  UploadCloud,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Clock,
  HelpCircle,
  Sparkles,
  Sliders,
  Send,
  RotateCcw,
  MessageSquare,
  TrendingUp,
  TrendingDown,
  Info,
  Globe,
  ShieldAlert,
  ShieldCheck,
  Shield,
  AlertCircle,
} from 'lucide-react';
import { api } from '../services/api';
import { PredictResponse, PhishingIndicator } from '../types';

interface SampleEmail {
  title: string;
  category: 'phishing' | 'scam' | 'work' | 'receipt' | 'multilingual';
  sender?: string;
  subject: string;
  body: string;
}

const SAMPLE_EMAILS: SampleEmail[] = [
  {
    title: 'Phishing: Bank Alert',
    category: 'phishing',
    sender: 'security@chase-fraud-portal.net',
    subject: 'URGENT NOTICE: Your Chase Online Banking Access Has Been Suspended',
    body: `Dear Valued Customer,\n\nWe detected suspicious unauthorized login attempts on your Chase checking account from an unrecognized IP address in Moscow, Russia.\n\nTo safeguard your funds and prevent permanent account termination, you must verify your identity immediately.\n\nClick the link below to verify your account credentials, social security number, and debit card PIN:\nhttp://chase-security-verification-portal.online/login?ref=urgent\n\nFailure to verify within 12 hours will result in permanent account closure.\n\nChase Fraud Prevention Department`,
  },
  {
    title: 'Hinglish: OTP Fraud',
    category: 'phishing',
    sender: 'alerts@paytm-verify-account.org',
    subject: 'Aapka Paytm wallet KYC pending hai - Turant verify kijiye',
    body: `Namaste,\n\nAapka Paytm account aaj raat 12 baje block ho jayega agar aapne biometric KYC complete nahi kiya.\n\nTurant apna password aur OTP enter kijiye:\nhttp://bit.ly/paytm-kyc-verify\n\nDhanyawad,\nPaytm KYC Team`,
  },
  {
    title: 'Bank OTP Alert (Defensive Ham)',
    category: 'receipt',
    sender: 'alerts@hdfcbank.com',
    subject: 'HDFC Bank: OTP for online transaction of INR 3,450.00',
    body: `Dear Customer,\n\nYour One Time Password (OTP) for transaction on card ending 4091 is 482910. Valid for 10 minutes.\n\nDo not share your OTP or password with anyone, including bank officials. HDFC Bank will never ask for your confidential credentials.\n\nIf not initiated by you, please report immediately to our 24x7 fraud helpline at 1800-202-6161.`,
  },
  {
    title: 'Hindi Ham: Project Meeting',
    category: 'multilingual',
    sender: 'rajesh.sharma@tcs-consulting.com',
    subject: 'नमस्ते - कल की प्रोजेक्ट समीक्षा बैठक का समय',
    body: `नमस्ते अनुराग,\n\nआशा है आप सकुशल हैं। हमारी आगामी प्रोजेक्ट समीक्षा बैठक कल सुबह 11:00 बजे निर्धारित की गई है।\n\nकृपया अपने नवीनतम कोड परिवर्तनों और यूनिट टेस्ट रिपोर्ट को गिट रिपॉजिटरी में पुश कर दें ताकि हम कल की चर्चा में समीक्षा कर सकें।\n\nधन्यवाद,\nविकास टीम`,
  },
  {
    title: 'Tamil Spam: Lottery Prize',
    category: 'scam',
    sender: 'prize-notification@win-tamil-crores.org',
    subject: 'வாழ்த்துக்கள்! உங்கள் எண் 10 லட்சம் ரூபாய் பரிசு வென்றுள்ளது',
    body: `வாழ்த்துக்கள் அன்பான வாடிக்கையாளரே,\n\nஉங்கள் தொலைபேசி எண் மாநில அளவிலான மாதாந்திர அதிர்ஷ்டக் குலுக்கலில் தேர்வு செய்யப்பட்டு 10 லட்சம் ரூபாய் ரொக்கப் பரிசு வென்றுள்ளது.\n\nபரிசுத் தொகையை உடனடியாகப் பெற உங்கள் வங்கிக் கணக்கு மற்றும் ஆதார் விவரங்களை கீழே உள்ள இணைப்பில் பதிவு செய்யவும்:\nhttp://tamil-lottery-claims-portal.net/claim?id=9281\n\nஅதிர்ஷ்ட குலுக்கல் துறை`,
  },
  {
    title: 'Work: Sprint Planning',
    category: 'work',
    sender: 'sarah.jenkins@company.internal',
    subject: 'Sprint Planning Agenda - Q4 Infrastructure Modernization',
    body: `Hi team,\n\nOur sprint planning meeting is scheduled for tomorrow at 10:30 AM in Conference Room B and via Google Meet.\n\nAgenda items:\n1. Review velocity and completed story points from Sprint 42.\n2. Architecture review for the Kubernetes migration.\n3. Ticket grooming for database replication setup.\n\nPlease ensure your Jira boards are updated before end of day today.\n\nBest regards,\nSarah Jenkins\nEngineering Manager`,
  },
  {
    title: 'Travel: Flight Booking',
    category: 'receipt',
    sender: 'confirmations@horizonair.com',
    subject: 'Your flight reservation is confirmed: SFO to ORD (Booking Ref: #KJ894L)',
    body: `Thank you for booking with Horizon Air.\n\nFlight Details:\nPassenger: David Miller\nFlight: HA 482\nDeparture: San Francisco International (SFO) - Oct 24, 08:15 AM\nArrival: Chicago O'Hare (ORD) - Oct 24, 02:30 PM\nSeat: 14C (Window)\n\nYou can manage your reservation or check in online 24 hours prior to departure at our official portal.`,
  },
];

export interface AnalyzerViewProps {
  backendReady?: boolean;
}

export const AnalyzerView: React.FC<AnalyzerViewProps> = ({ backendReady = true }) => {
  const [sender, setSender] = useState<string>('');
  const [subject, setSubject] = useState<string>('');
  const [body, setBody] = useState<string>('');
  const [modelName, setModelName] = useState<string>('logistic_regression');
  const [threshold, setThreshold] = useState<number>(0.5);
  const [storeContent, setStoreContent] = useState<boolean>(() => {
    try {
      return typeof window !== 'undefined' && window.localStorage
        ? window.localStorage.getItem('mailshield_store_body') === 'true'
        : false;
    } catch {
      return false;
    }
  });
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Feedback Modal
  const [showFeedbackModal, setShowFeedbackModal] = useState<boolean>(false);
  const [feedbackLabel, setFeedbackLabel] = useState<'Spam' | 'Legitimate'>('Legitimate');
  const [feedbackComments, setFeedbackComments] = useState<string>('');
  const [feedbackSent, setFeedbackSent] = useState<boolean>(false);

  const handleSelectSample = (sample: SampleEmail) => {
    setSender(sample.sender || '');
    setSubject(sample.subject);
    setBody(sample.body);
    setError(null);
  };

  const handleAnalyze = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!body.trim()) {
      setError('Please provide email body text or import an email file.');
      return;
    }

    try {
      setAnalyzing(true);
      if (typeof window !== 'undefined') window.dispatchEvent(new CustomEvent('mailshield:analyzing'));
      setError(null);
      const res = await api.predict({
        sender: sender.trim() || undefined,
        subject: subject.trim(),
        body: body.trim(),
        model_name: modelName,
        threshold: threshold,
        store_content: storeContent,
      });
      setResult(res);
      setFeedbackSent(false);
      if (typeof window !== 'undefined') {
        window.dispatchEvent(
          new CustomEvent('mailshield:result', {
            detail: { isSpam: res.prediction === 'Spam' || res.is_spam || res.score >= res.threshold_used },
          })
        );
      }
    } catch (err: any) {
      setError(err.message || 'Analysis failed. Please check backend connection.');
      if (typeof window !== 'undefined') window.dispatchEvent(new CustomEvent('mailshield:idle'));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      setAnalyzing(true);
      if (typeof window !== 'undefined') window.dispatchEvent(new CustomEvent('mailshield:analyzing'));
      setError(null);
      const res = await api.predictFile(file, {
        model_name: modelName,
        threshold: threshold,
        store_content: storeContent,
      });
      setSubject(file.name);
      setBody(`[File content analyzed from ${file.name}]`);
      setResult(res);
      setFeedbackSent(false);
      if (typeof window !== 'undefined') {
        window.dispatchEvent(
          new CustomEvent('mailshield:result', {
            detail: { isSpam: res.prediction === 'Spam' || res.is_spam || res.score >= res.threshold_used },
          })
        );
      }
    } catch (err: any) {
      setError(err.message || 'Failed to analyze uploaded file.');
      if (typeof window !== 'undefined') window.dispatchEvent(new CustomEvent('mailshield:idle'));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFeedbackSubmit = async () => {
    if (!result) return;
    try {
      await api.submitFeedback(result.id, feedbackLabel, feedbackComments);
      setFeedbackSent(true);
      setShowFeedbackModal(false);
    } catch (err: any) {
      alert('Could not submit feedback: ' + err.message);
    }
  };

  return (
    <div className="space-y-8">
      {/* View Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Email Analyzer & Feature Attribution</h1>
        <p className="text-sm text-slate-400 mt-1">
          Paste email content or import `.eml` / `.txt` files to classify and examine exact contributing tokens.
        </p>
      </div>

      {/* Pre-loaded Sample Selector */}
      <div className="p-4 rounded-xl glass-panel border border-shield-border">
        <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-300">
          <Sparkles className="w-4 h-4 text-shield-cyan" />
          <span>Quick Benchmark Samples (1-Click Test):</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {SAMPLE_EMAILS.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelectSample(sample)}
              className="text-xs px-3 py-1.5 rounded-lg bg-[#0c1424] hover:bg-[#14223d] text-slate-200 border border-slate-700/80 hover:border-shield-cyan/60 transition-all text-left shadow-sm"
            >
              <span className="font-medium text-white">{sample.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Offline / degraded notice when backend is unavailable */}
      {!backendReady && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-amber-300">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5 text-amber-400" />
          <div className="text-xs space-y-1">
            <p className="font-semibold text-amber-200">Inference Engine Offline or Initializing</p>
            <p className="text-amber-300/80 leading-relaxed">
              The local backend service is currently offline or waiting for health verification. Scanning and uploads are paused until the service becomes ready.
            </p>
          </div>
        </div>
      )}

      {/* Main Analysis Form & Drag-and-drop */}
      <form onSubmit={handleAnalyze} className="space-y-5">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Email Input Fields */}
          <div className="lg:col-span-2 space-y-4">
            {/* Sender & Subject Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1">
                  Sender / From (Optional)
                </label>
                <input
                  type="text"
                  value={sender}
                  onChange={(e) => setSender(e.target.value)}
                  placeholder="e.g. alerts@hdfcbank.com or support@sbi-fraud.net"
                  className="w-full px-4 py-2.5 rounded-xl bg-[#060b14] border border-slate-700/90 text-slate-100 placeholder-slate-400 text-sm font-mono text-xs focus:outline-none focus:border-shield-cyan focus:ring-1 focus:ring-shield-cyan/30 transition-colors shadow-inner"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1">
                  Subject Line (Optional)
                </label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g. Account Security Verification Alert"
                  className="w-full px-4 py-2.5 rounded-xl bg-[#060b14] border border-slate-700/90 text-slate-100 placeholder-slate-400 text-sm focus:outline-none focus:border-shield-cyan focus:ring-1 focus:ring-shield-cyan/30 transition-colors shadow-inner"
                />
              </div>
            </div>

            {/* Email Body Text Area */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Email Body Content <span className="text-rose-400">*</span>
                </label>
                <span className="text-[11px] font-mono text-slate-400">{body.length} characters</span>
              </div>
              <div className="relative overflow-hidden rounded-xl">
                <textarea
                  rows={10}
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  placeholder="Paste the full email text, headers, or body here..."
                  className="w-full px-4 py-3 rounded-xl bg-[#060b14] border border-slate-700/90 text-slate-100 placeholder-slate-400 text-sm font-mono focus:outline-none focus:border-shield-cyan focus:ring-1 focus:ring-shield-cyan/30 transition-colors resize-y shadow-inner"
                />
                {analyzing && <div id="cyber-scanline" />}
              </div>
            </div>

            {/* Drag & Drop File Zone */}
            <div
              onDragOver={(e) => {
                e.preventDefault();
                if (backendReady) setDragActive(true);
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => {
                if (backendReady) handleDrop(e);
              }}
              className={`border-2 border-dashed rounded-xl p-5 text-center transition-all ${
                !backendReady
                  ? 'border-slate-800/50 bg-slate-900/20 opacity-60 cursor-not-allowed'
                  : dragActive
                  ? 'border-shield-cyan bg-cyan-950/20'
                  : 'border-slate-800 hover:border-slate-700 bg-slate-900/40'
              }`}
            >
              <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="text-xs text-slate-300 font-medium">
                Drag & drop email file here, or{' '}
                <label className={backendReady ? "text-shield-cyan hover:underline cursor-pointer" : "text-slate-500 cursor-not-allowed"}>
                  browse files
                  <input
                    type="file"
                    accept=".txt,.eml"
                    disabled={!backendReady}
                    className="hidden"
                    onChange={(e) => backendReady && e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                  />
                </label>
              </p>
              <p className="text-[11px] text-slate-500 mt-1">Supports RFC 822 `.eml` and `.txt` files up to 5MB</p>
            </div>
          </div>

          {/* Right Column: Model Options & Threshold Parameters */}
          <div className="glass-panel p-5 rounded-2xl border border-shield-border space-y-6">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Sliders className="w-4 h-4 text-shield-cyan" />
              <span>Inference Parameters</span>
            </h3>

            {/* Model Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Classifier Model</label>
              <select
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[#060b14] border border-slate-700 text-slate-100 text-xs focus:outline-none focus:border-shield-cyan focus:ring-1 focus:ring-shield-cyan/30"
              >
                <option value="logistic_regression">Logistic Regression (Calibrated & Explainable)</option>
                <option value="naive_bayes">Multinomial Naive Bayes</option>
                <option value="linear_svm">Linear SVM (Platt Calibrated)</option>
              </select>
              <p className="text-[11px] text-slate-300 mt-1">
                {modelName === 'logistic_regression'
                  ? 'Computes additive token log-odds and true posterior probabilities.'
                  : modelName === 'naive_bayes'
                  ? 'Fast baseline using vocabulary frequency log-likelihood.'
                  : 'High-margin hyper-plane with Platt-scaled validation calibration.'}
              </p>
            </div>

            {/* Decision Threshold Slider */}
            <div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="font-semibold text-slate-300">Decision Threshold</span>
                <span className="font-mono text-shield-cyan font-bold">{threshold.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.95"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-shield-cyan"
              />
              <div className="flex justify-between text-[11px] text-slate-400 font-mono mt-1">
                <span>0.05 (High Recall)</span>
                <span>0.50 (Balanced)</span>
                <span>0.95 (Low FPR)</span>
              </div>
            </div>

            {/* Privacy Setting: Store Email Body */}
            <div className="pt-4 border-t border-slate-800">
              <label className="flex items-start gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={storeContent}
                  onChange={(e) => setStoreContent(e.target.checked)}
                  className="mt-0.5 rounded border-slate-700 bg-slate-900 text-shield-accent focus:ring-0"
                />
                <div className="text-xs">
                  <span className="font-medium text-slate-200 block">Persist Full Email Text</span>
                  <span className="text-slate-300 block mt-0.5 leading-relaxed text-[11px]">
                    By default, MailShield only stores SHA-256 hashes and token scores for privacy. Enable only if you wish to review original body text in history.
                  </span>
                </div>
              </label>
            </div>

            {/* Action Buttons */}
            <div className="pt-2 flex flex-col gap-2">
              <button
                type="button"
                onClick={() => handleAnalyze()}
                disabled={analyzing || !backendReady}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-shield-accent to-shield-cyan hover:opacity-95 text-white text-sm font-semibold shadow-lg shadow-shield-cyan/10 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {analyzing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                    <span>Analyzing Features...</span>
                  </>
                ) : !backendReady ? (
                  <>
                    <Clock className="w-4 h-4" />
                    <span>Engine Initializing...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Analyze Email</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={() => {
                  setSubject('');
                  setBody('');
                  setResult(null);
                  setError(null);
                  if (typeof window !== 'undefined') window.dispatchEvent(new CustomEvent('mailshield:idle'));
                }}
                className="w-full flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset Form</span>
              </button>
            </div>
          </div>
        </div>
      </form>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Analysis Result Card */}
      {result && (
        <div className="glass-panel rounded-2xl p-6 border border-shield-border space-y-6 animate-fadeIn">
          {/* Top Result Banner */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-shield-border">
            <div className="flex items-center gap-4">
              <div
                className={`p-3.5 rounded-2xl ${
                  result.is_spam
                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                    : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                }`}
              >
                {result.is_spam ? <AlertTriangle className="w-8 h-8" /> : <CheckCircle2 className="w-8 h-8" />}
              </div>
              <div>
                <div className="flex items-center gap-3">
                  <h2 className="text-2xl font-extrabold text-white">
                    Prediction: {result.prediction.toUpperCase()}
                  </h2>
                  <span
                    className={`text-xs px-2.5 py-0.5 rounded-full font-mono font-semibold border ${
                      result.confidence_level === 'High'
                        ? 'bg-emerald-950/50 text-emerald-300 border-emerald-800/60'
                        : result.confidence_level === 'Medium'
                        ? 'bg-amber-950/50 text-amber-300 border-amber-800/60'
                        : 'bg-slate-800 text-slate-300 border-slate-700'
                    }`}
                  >
                    {result.confidence_level} Confidence
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-400 font-mono mt-1">
                  <span>Model: {result.model_name} (v{result.model_version})</span>
                  <span>•</span>
                  <span className={result.calibrated ? 'text-purple-300' : 'text-slate-400'}>
                    {result.calibrated ? 'Calibrated (Platt/Sigmoid)' : 'Uncalibrated'}
                  </span>
                  <span>•</span>
                  <span>Threshold: {result.threshold_used}</span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {result.processing_time_ms} ms
                  </span>
                </div>
              </div>
            </div>

            {/* Score Radial or Gauge Display */}
            <div className="flex items-center gap-4 bg-[#060b14] p-3.5 rounded-xl border border-slate-700/80 shadow-sm">
              <div className="text-right">
                <span className="text-[11px] font-mono text-slate-400 block uppercase">
                  {result.score_type === 'probability'
                    ? result.calibrated
                      ? 'Calibrated Probability'
                      : 'Posterior Probability'
                    : 'Decision Margin Score'}
                </span>
                <span
                  className={`text-2xl font-bold font-mono ${
                    result.is_spam ? 'text-rose-400' : 'text-emerald-400'
                  }`}
                >
                  {result.score_type === 'probability'
                    ? `${(result.score * 100).toFixed(1)}%`
                    : result.score.toFixed(3)}
                </span>
              </div>
            </div>
          </div>

          {/* Multilingual & Phishing Risk Intelligence Grid */}
          {(result.language_analysis || result.phishing_analysis) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Language Identification Card */}
              {result.language_analysis && (() => {
                const lang = result.language_analysis;
                const scriptName = lang.primary_script || lang.script || 'Latin';
                const methodStr = lang.detection_method || lang.method || 'Unicode Script Analysis';
                const isMixed = lang.is_mixed ?? lang.mixed_script ?? false;
                return (
                  <div className="p-4 rounded-xl bg-[#060b14] border border-slate-700/80 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-shield-cyan uppercase tracking-wider flex items-center gap-1.5">
                        <Globe className="w-4 h-4 text-shield-cyan" />
                        <span>Language Identification</span>
                      </span>
                      <span className="text-xs px-2.5 py-0.5 rounded-full font-mono font-bold bg-cyan-950/60 text-cyan-300 border border-cyan-800/60">
                        {lang.detected_language.toUpperCase()} ({scriptName})
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                      <div className="bg-[#03060c] p-2.5 rounded-lg border border-slate-800/80">
                        <span className="text-slate-300 block text-[11px] uppercase">Detection Method</span>
                        <span className="text-slate-200 font-semibold">{methodStr}</span>
                      </div>
                      <div className="bg-[#03060c] p-2.5 rounded-lg border border-slate-800/80">
                        <span className="text-slate-300 block text-[11px] uppercase">Confidence</span>
                        <span className="text-slate-200 font-semibold">
                          {typeof lang.confidence === 'number'
                            ? `${(lang.confidence * 100).toFixed(0)}%`
                            : String(lang.confidence ?? 'Calibrated')}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-300 pt-1">
                      <span>Mixed Script Detected:</span>
                      <span className={`font-mono font-semibold ${isMixed ? 'text-amber-400' : 'text-slate-300'}`}>
                        {isMixed ? 'Yes (Multilingual/Code-Switched)' : 'No (Single Script)'}
                      </span>
                    </div>
                  </div>
                );
              })()}

              {/* Decoupled Phishing Risk Card */}
              {result.phishing_analysis && (() => {
                const phish = result.phishing_analysis;
                const indicators = (phish.indicators_triggered || phish.indicators || []) as any[];
                return (
                  <div className="p-4 rounded-xl bg-[#060b14] border border-slate-700/80 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                        <ShieldAlert className="w-4 h-4 text-amber-400" />
                        <span>Decoupled Phishing Risk</span>
                      </span>
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full font-mono font-bold border ${
                          phish.risk_level === 'critical'
                            ? 'bg-rose-950/80 text-rose-300 border-rose-800'
                            : phish.risk_level === 'high'
                            ? 'bg-orange-950/80 text-orange-300 border-orange-800'
                            : phish.risk_level === 'medium'
                            ? 'bg-amber-950/80 text-amber-300 border-amber-800'
                            : 'bg-emerald-950/60 text-emerald-300 border-emerald-800'
                        }`}
                      >
                        {phish.risk_level.toUpperCase()} RISK ({(phish.risk_score * 100).toFixed(0)}%)
                      </span>
                    </div>

                    <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                      {indicators.length === 0 ? (
                        <div className="flex items-center gap-2 p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-900/40 text-emerald-300 text-xs">
                          <ShieldCheck className="w-4 h-4 flex-shrink-0" />
                          <span>No suspicious URL structures, brand spoofing, or urgency heuristics detected.</span>
                        </div>
                      ) : (
                        indicators.map((ind: any, idx: number) => {
                          const name = ind.name || ind.rule || 'Suspicious Pattern';
                          const severity = ind.severity || 'medium';
                          const desc = ind.description || ind.explanation || '';
                          return (
                            <div
                              key={idx}
                              className={`p-2 rounded-lg text-xs border ${
                                severity === 'critical'
                                  ? 'bg-rose-950/40 border-rose-800/60 text-rose-200'
                                  : severity === 'high'
                                  ? 'bg-orange-950/40 border-orange-800/60 text-orange-200'
                                  : severity === 'medium'
                                  ? 'bg-amber-950/40 border-amber-800/60 text-amber-200'
                                  : 'bg-slate-950/40 border-slate-800 text-slate-300'
                              }`}
                            >
                              <div className="flex items-center justify-between font-mono font-semibold text-[11px]">
                                <span>{name}</span>
                                <span className="uppercase text-[10px] tracking-wide">{severity}</span>
                              </div>
                              {desc && <p className="text-[11px] opacity-90 mt-0.5">{desc}</p>}
                            </div>
                          );
                        })
                      )}
                    </div>

                    <p className="text-[10px] text-slate-400 italic pt-1">
                      Independent heuristic layer: Evaluates technical URL structures and coercive lures separately from vocabulary spam weights.
                    </p>
                  </div>
                );
              })()}
            </div>
          )}

          {/* Mathematical Feature Explanation Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-white">Feature Attribution Breakdown</h3>
                <p className="text-xs text-slate-300">
                  Exact linear contributions ($w_i \cdot x_i$) pushing toward Spam (+) or Legitimate (-)
                </p>
              </div>
              <span className="text-xs font-mono text-slate-300">
                Prior Bias / Intercept: {result.explanations.intercept > 0 ? '+' : ''}
                {result.explanations.intercept.toFixed(3)}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Spam Signals (Positive Contributions) */}
              <div className="p-4 rounded-xl bg-[#060b14] border border-rose-900/50 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                    <TrendingUp className="w-4 h-4 text-rose-400" />
                    <span>Spam Evidence (Positive Weight)</span>
                  </span>
                  <span className="text-xs font-mono text-rose-400/80">
                    {result.explanations.top_spam_features.length} tokens
                  </span>
                </div>

                {result.explanations.top_spam_features.length === 0 ? (
                  <p className="text-xs text-slate-400 italic py-4 text-center">No spam tokens matched vocabulary.</p>
                ) : (
                  <div className="space-y-2">
                    {result.explanations.top_spam_features.map((feat, idx) => (
                      <div key={idx} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="font-mono text-slate-200 font-semibold">{feat.token}</span>
                          <span className="font-mono text-rose-400">+{feat.contribution.toFixed(3)}</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-rose-500 h-full rounded-full"
                            style={{ width: `${Math.min(feat.relative_impact, 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Legitimate Signals (Negative Contributions) */}
              <div className="p-4 rounded-xl bg-[#060b14] border border-emerald-900/50 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                    <TrendingDown className="w-4 h-4 text-emerald-400" />
                    <span>Legitimate Evidence (Negative Weight)</span>
                  </span>
                  <span className="text-xs font-mono text-emerald-400/80">
                    {result.explanations.top_legitimate_features.length} tokens
                  </span>
                </div>

                {result.explanations.top_legitimate_features.length === 0 ? (
                  <p className="text-xs text-slate-400 italic py-4 text-center">
                    No legitimate tokens matched vocabulary.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {result.explanations.top_legitimate_features.map((feat, idx) => (
                      <div key={idx} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="font-mono text-slate-200 font-semibold">{feat.token}</span>
                          <span className="font-mono text-emerald-400">{feat.contribution.toFixed(3)}</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-emerald-500 h-full rounded-full"
                            style={{ width: `${Math.min(feat.relative_impact, 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Narrative Notes */}
            <div className="p-3.5 rounded-xl bg-[#060b14] border border-slate-800 flex items-start gap-2.5 text-xs text-slate-300">
              <Info className="w-4 h-4 text-shield-cyan flex-shrink-0 mt-0.5" />
              <span>{result.explanations.attribution_notes}</span>
            </div>
          </div>

          {/* Feedback & Action Footer */}
          <div className="pt-4 border-t border-shield-border flex items-center justify-between">
            <span className="text-xs text-slate-400">ID: {result.id}</span>
            {feedbackSent ? (
              <span className="text-xs text-emerald-400 font-medium">Feedback submitted. Thank you!</span>
            ) : (
              <button
                type="button"
                onClick={() => setShowFeedbackModal(true)}
                className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 transition-colors"
              >
                <MessageSquare className="w-3.5 h-3.5 text-shield-cyan" />
                <span>Report Prediction Accuracy</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="glass-panel p-6 rounded-2xl border border-shield-border w-full max-w-md space-y-4">
            <h3 className="text-base font-bold text-white">Report Prediction Accuracy</h3>
            <p className="text-xs text-slate-300">
              Help improve the educational benchmark by suggesting the true classification label.
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">True / Suggested Label</label>
              <select
                value={feedbackLabel}
                onChange={(e) => setFeedbackLabel(e.target.value as any)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs"
              >
                <option value="Legitimate">Legitimate (Ham)</option>
                <option value="Spam">Spam</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Optional Notes</label>
              <textarea
                rows={3}
                value={feedbackComments}
                onChange={(e) => setFeedbackComments(e.target.value)}
                placeholder="Why do you think this classification was incorrect?"
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowFeedbackModal(false)}
                className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleFeedbackSubmit}
                className="px-4 py-1.5 rounded-lg text-xs bg-shield-accent text-white font-semibold hover:opacity-90"
              >
                Submit Feedback
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
