export interface FeatureContribution {
  token: string;
  weight: number;
  tfidf_value: number;
  contribution: number;
  direction: 'Spam' | 'Legitimate';
  relative_impact: number;
  description: string;
}

export interface ExplanationData {
  model_name: string;
  intercept: number;
  net_decision_score: number;
  calibrated_probability: number | null;
  top_spam_features: FeatureContribution[];
  top_legitimate_features: FeatureContribution[];
  all_contributions: FeatureContribution[];
  attribution_notes: string;
}

export interface LanguageAnalysis {
  detected_language: string;
  language_name?: string;
  confidence: number | null;
  detection_method?: string;
  method?: string;
  primary_script?: string;
  script?: string;
  is_mixed?: boolean;
  mixed_script?: boolean;
  scripts_detected?: Record<string, number>;
  warning?: string | null;
  diagnostics?: Record<string, any>;
}

export interface PhishingIndicator {
  name: string;
  id?: string;
  category?: string;
  severity: 'none' | 'low' | 'medium' | 'high' | 'critical' | 'defensive_bonus';
  description: string;
  weight?: number;
}

export interface PhishingAnalysis {
  risk_score: number;
  risk_level: 'none' | 'low' | 'medium' | 'high' | 'critical';
  indicators: PhishingIndicator[];
  indicators_triggered?: PhishingIndicator[];
  suspicious_urls?: string[];
  has_credential_harvesting?: boolean;
  has_urgency_threat?: boolean;
  has_spoofed_brand?: boolean;
  explanation?: string;
  defensive_dampener_applied?: boolean;
}

export interface PredictResponse {
  id: string;
  prediction: 'Spam' | 'Legitimate';
  is_spam: boolean;
  score: number;
  score_type: 'probability' | 'decision_function';
  calibrated: boolean;
  raw_decision_score: number | null;
  confidence_level: 'High' | 'Medium' | 'Low';
  model_name: string;
  model_version: string;
  threshold_used: number;
  processing_time_ms: number;
  explanations: ExplanationData;
  created_at: string;
  language_analysis?: LanguageAnalysis;
  phishing_analysis?: PhishingAnalysis;
}

export interface HistoryItem {
  id: string;
  timestamp: string;
  subject: string;
  prediction: 'Spam' | 'Legitimate';
  is_spam: boolean;
  score: number;
  score_type: 'probability' | 'decision_function';
  calibrated: boolean;
  confidence_level: 'High' | 'Medium' | 'Low';
  model_name: string;
  model_version: string;
  threshold_used: number;
  processing_time_ms: number;
  is_content_stored: boolean;
  has_feedback: boolean;
}

export interface HistoryDetail extends HistoryItem {
  email_hash: string;
  email_body?: string;
  explanations?: ExplanationData;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  false_positive_rate: number;
  pr_auc: number | null;
  roc_auc: number | null;
  brier_score?: number | null;
  calibration_status?: string | null;
  num_samples: number;
  threshold: number;
  confusion_matrix: {
    tn: number;
    fp: number;
    fn: number;
    tp: number;
  };
  confusion_matrix_grid?: number[][];
}

export interface ModelInfo {
  name: string;
  display_name: string;
  version: string;
  score_type: 'probability' | 'decision_function';
  calibrated: boolean;
  optimal_threshold: number;
  test_metrics: ModelMetrics;
  validation_metrics: ModelMetrics;
}

export interface ModelListResponse {
  models: ModelInfo[];
  active_model: string;
  vocab_size: number;
  dataset_info: {
    source?: string;
    total_samples?: number;
    duplicates_removed?: number;
    train_samples?: number;
    validation_samples?: number;
    test_samples?: number;
  };
}

export interface ThresholdSimulationPoint {
  threshold: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  false_positive_rate: number;
  confusion_matrix: number[][];
  brier_score?: number | null;
  calibration_status?: string | null;
}

export interface ThresholdSimulationResponse {
  model_name: string;
  current_metrics: ThresholdSimulationPoint;
  sweep_curve: ThresholdSimulationPoint[];
}

export interface HealthStatus {
  status: 'healthy' | 'degraded';
  backend: boolean;
  database: boolean;
  model_loaded: boolean;
  active_models: string[];
  environment: string;
  mode: string;
  version: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  created_at: string;
}

export interface MailShieldDesktopAPI {
  platform: string;
  backendPort: number;
  apiBase: string;
  isOffline: () => boolean;
  getAppVersion: () => Promise<string>;
  getBackendHealth: () => Promise<boolean>;
  getApiBase: () => string;
  openExternal?: (url: string) => Promise<void>;
}

declare global {
  interface Window {
    mailshieldDesktop?: MailShieldDesktopAPI;
  }
}

export interface SupportedLanguage {
  code: string;
  name: string;
  script: string;
  test_samples: number;
}

export interface EvaluationMetricsResponse {
  model_name: string;
  split: string;
  language: string;
  threshold: number;
  inference_latency_ms?: number;
  model_size_kb?: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  fpr: number;
  fnr: number;
  brier_score?: number | null;
  pr_auc?: number | null;
  roc_auc?: number | null;
  num_samples?: number;
  confusion_matrix: {
    tn: number;
    fp: number;
    fn: number;
    tp: number;
  };
}

export interface ConfusionMatrixResponse {
  model_name: string;
  split: string;
  language: string;
  grid: number[][];
  tn: number;
  fp: number;
  fn: number;
  tp: number;
  rates: {
    true_negative_rate: number;
    false_positive_rate: number;
    false_negative_rate: number;
    true_positive_rate: number;
  };
  total_samples: number;
}

export interface DrilldownErrorItem {
  model: string;
  email_id: string;
  subject: string;
  body_preview: string;
  sender: string;
  language: string;
  script: string;
  template_group: string;
  provenance: string;
  category: string;
  actual_label: 'spam' | 'ham';
  predicted_label: 'spam' | 'ham';
  score: number;
  threshold: number;
  is_error: boolean;
  error_type: 'FP' | 'FN' | 'CORRECT';
}

export interface ModelComparisonResponse {
  english_baseline: {
    model: string;
    accuracy: number;
    recall: number;
    fpr: number;
    latency_ms: number;
    size_kb: number;
  };
  multilingual_models: {
    logistic_regression: {
      accuracy: number;
      recall: number;
      fpr: number;
      latency_ms: number;
      size_kb: number;
    };
    linear_svm: {
      accuracy: number;
      recall: number;
      fpr: number;
      latency_ms: number;
      size_kb: number;
    };
    naive_bayes: {
      accuracy: number;
      recall: number;
      fpr: number;
      latency_ms: number;
      size_kb: number;
    };
  };
}

export interface DatasetProvenanceResponse {
  total_records: number;
  splits: {
    train: { samples: number; template_groups: number };
    validation: { samples: number; template_groups: number };
    test: { samples: number; template_groups: number };
  };
  zero_group_leakage: boolean;
  provenance_breakdown: Record<string, number>;
  license_breakdown: Record<string, number>;
  language_distribution: Record<string, number>;
  categories: Record<string, number>;
}

export interface DemoSample {
  id: string;
  language: string;
  script: string;
  expected_label: 'spam' | 'ham';
  category: string;
  subject: string;
  body: string;
  sender: string;
}

export interface GmailStatus {
  connected: boolean;
  email: string | null;
  scopes: string[];
  connected_at: string | null;
  is_configured: boolean;
}

export interface GmailAuthUrlResponse {
  auth_url: string;
  state: string;
  client_type: 'web' | 'desktop';
  redirect_uri: string;
  is_configured: boolean;
}

export interface GmailMessageSummary {
  id: string;
  thread_id: string;
  snippet: string;
  sender: string;
  subject: string;
  date: string;
}

export interface GmailMessageListResponse {
  messages: GmailMessageSummary[];
  next_page_token?: string | null;
  result_size_estimate: number;
}

export interface GmailScanResultItem {
  message_id: string;
  sender: string;
  subject: string;
  date: string;
  prediction: 'spam' | 'ham';
  probability: number;
  confidence: number;
  language: string;
  is_mixed?: boolean;
  phishing_risk: {
    risk_level: string;
    risk_score: number;
    indicators_triggered?: any[];
  };
  top_tokens: Array<{
    token: string;
    weight: number;
    direction: string;
    description: string;
  }>;
  error?: string | null;
}

export interface GmailScanBatchResponse {
  results: GmailScanResultItem[];
  total_scanned: number;
  spam_count: number;
  ham_count: number;
  error_count: number;
}

export interface GmailDisconnectResponse {
  disconnected: boolean;
  remote_revocation_succeeded: boolean;
  message: string;
}


