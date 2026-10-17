import {
  ConfusionMatrixResponse,
  DatasetProvenanceResponse,
  DemoSample,
  DrilldownErrorItem,
  EvaluationMetricsResponse,
  GmailAuthUrlResponse,
  GmailDisconnectResponse,
  GmailMessageListResponse,
  GmailScanBatchResponse,
  GmailStatus,
  HealthStatus,
  HistoryDetail,
  HistoryResponse,
  ModelComparisonResponse,
  ModelListResponse,
  PredictResponse,
  SupportedLanguage,
  ThresholdSimulationResponse,
} from '../types';

function getApiBase(): string {
  if (typeof window !== 'undefined' && window.mailshieldDesktop?.apiBase) {
    return window.mailshieldDesktop.apiBase;
  }
  return import.meta.env.VITE_API_BASE_URL || '/api/v1';
}

function buildApiUrl(endpoint: string): string {
  const base = getApiBase();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  if (base.startsWith('http://') || base.startsWith('https://')) {
    return `${base}${cleanEndpoint}`;
  }
  const origin =
    typeof window !== 'undefined' && window.location.origin && window.location.origin !== 'null'
      ? window.location.origin
      : 'http://127.0.0.1:8000';
  return `${origin}${base}${cleanEndpoint}`;
}

function getHeaders(isJson = true): HeadersInit {
  const headers: Record<string, string> = {};
  if (isJson) {
    headers['Content-Type'] = 'application/json';
  }
  const token = localStorage.getItem('mailshield_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  async getHealth(): Promise<HealthStatus> {
    const res = await fetch(buildApiUrl('/health'), { headers: getHeaders() });
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async predict(data: {
    subject?: string;
    body: string;
    sender?: string;
    model_name?: string;
    threshold?: number;
    store_content?: boolean;
  }): Promise<PredictResponse> {
    const res = await fetch(buildApiUrl('/predict'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Prediction failed' }));
      throw new Error(err.detail || 'Prediction failed');
    }
    return res.json();
  },

  async predictFile(
    file: File,
    options?: {
      model_name?: string;
      threshold?: number;
      store_content?: boolean;
    }
  ): Promise<PredictResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (options?.model_name) formData.append('model_name', options.model_name);
    if (options?.threshold !== undefined) formData.append('threshold', String(options.threshold));
    if (options?.store_content !== undefined) formData.append('store_content', String(options.store_content));

    const res = await fetch(buildApiUrl('/predict/file'), {
      method: 'POST',
      headers: getHeaders(false),
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'File analysis failed' }));
      throw new Error(err.detail || 'File analysis failed');
    }
    return res.json();
  },

  async getHistory(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    label?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<HistoryResponse> {
    const url = new URL(buildApiUrl('/history'));
    if (params?.page) url.searchParams.set('page', String(params.page));
    if (params?.page_size) url.searchParams.set('page_size', String(params.page_size));
    if (params?.search) url.searchParams.set('search', params.search);
    if (params?.label) url.searchParams.set('label', params.label);
    if (params?.sort_by) url.searchParams.set('sort_by', params.sort_by);
    if (params?.sort_order) url.searchParams.set('sort_order', params.sort_order);

    const res = await fetch(url.toString(), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to load history');
    return res.json();
  },

  async getAnalysisDetail(id: string): Promise<HistoryDetail> {
    const res = await fetch(buildApiUrl(`/history/${id}`), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to load analysis detail');
    return res.json();
  },

  async deleteAnalysis(id: string): Promise<void> {
    const res = await fetch(buildApiUrl(`/history/${id}`), {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to delete analysis');
  },

  async bulkDelete(ids: string[]): Promise<number> {
    const res = await fetch(buildApiUrl('/history'), {
      method: 'DELETE',
      headers: getHeaders(),
      body: JSON.stringify({ ids }),
    });
    if (!res.ok) throw new Error('Failed to bulk delete');
    const data = await res.json();
    return data.deleted_count || 0;
  },

  async getModels(): Promise<ModelListResponse> {
    const res = await fetch(buildApiUrl('/models'), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to load models');
    return res.json();
  },

  async getThresholdSimulation(model: string, threshold: number): Promise<ThresholdSimulationResponse> {
    const url = new URL(buildApiUrl('/models/threshold-metrics'));
    url.searchParams.set('model', model);
    url.searchParams.set('threshold', String(threshold));
    const res = await fetch(url.toString(), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to simulate threshold');
    return res.json();
  },

  async submitFeedback(analysisId: string, suggestedLabel: 'Spam' | 'Legitimate', comments?: string): Promise<void> {
    const res = await fetch(buildApiUrl('/feedback'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        analysis_id: analysisId,
        suggested_label: suggestedLabel,
        comments,
      }),
    });
    if (!res.ok) throw new Error('Failed to submit feedback');
  },

  getExportUrl(format: 'csv' | 'json'): string {
    const url = new URL(buildApiUrl('/reports/export'));
    url.searchParams.set('format', format);
    return url.toString();
  },

  async downloadExport(format: 'csv' | 'json'): Promise<void> {
    const url = new URL(buildApiUrl('/reports/export'));
    url.searchParams.set('format', format);
    const res = await fetch(url.toString(), {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Export failed');
    const blob = await res.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `mailshield_analyses.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(downloadUrl);
  },

  async getEvaluationLanguages(): Promise<SupportedLanguage[]> {
    const res = await fetch(buildApiUrl('/evaluation/languages'), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch supported languages');
    return res.json();
  },

  async getEvaluationMetrics(
    modelName: string = 'linear_svm',
    split: string = 'test',
    language: string = 'all'
  ): Promise<EvaluationMetricsResponse> {
    const url = new URL(buildApiUrl('/evaluation/metrics'));
    url.searchParams.set('model_name', modelName);
    url.searchParams.set('split', split);
    url.searchParams.set('language', language);
    const res = await fetch(url.toString(), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch evaluation metrics');
    return res.json();
  },

  async getEvaluationConfusionMatrix(
    modelName: string = 'linear_svm',
    split: string = 'test',
    language: string = 'all'
  ): Promise<ConfusionMatrixResponse> {
    const url = new URL(buildApiUrl('/evaluation/confusion-matrix'));
    url.searchParams.set('model_name', modelName);
    url.searchParams.set('split', split);
    url.searchParams.set('language', language);
    const res = await fetch(url.toString(), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch confusion matrix');
    return res.json();
  },

  async getEvaluationErrors(
    modelName: string = 'linear_svm',
    errorType: string = 'ALL',
    language: string = 'all',
    limit: number = 50
  ): Promise<DrilldownErrorItem[]> {
    const url = new URL(buildApiUrl('/evaluation/errors'));
    url.searchParams.set('model_name', modelName);
    url.searchParams.set('error_type', errorType);
    url.searchParams.set('language', language);
    url.searchParams.set('limit', String(limit));
    const res = await fetch(url.toString(), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch evaluation errors');
    return res.json();
  },

  async getEvaluationComparison(): Promise<ModelComparisonResponse> {
    const res = await fetch(buildApiUrl('/evaluation/compare'), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch model comparison');
    return res.json();
  },

  async getEvaluationProvenance(): Promise<DatasetProvenanceResponse> {
    const res = await fetch(buildApiUrl('/evaluation/provenance'), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch dataset provenance');
    return res.json();
  },

  async getEvaluationDemoSamples(language: string = 'all'): Promise<DemoSample[]> {
    const url = new URL(buildApiUrl('/evaluation/demo-samples'));
    url.searchParams.set('language', language);
    const res = await fetch(url.toString(), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch demo samples');
    return res.json();
  },

  async getGmailAuthUrl(clientType: 'web' | 'desktop' = 'web'): Promise<GmailAuthUrlResponse> {
    const url = new URL(buildApiUrl('/gmail/auth-url'));
    url.searchParams.set('client_type', clientType);
    const res = await fetch(url.toString(), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to generate Gmail authorization URL');
    return res.json();
  },

  async submitGmailCallback(code: string, state: string): Promise<GmailStatus> {
    const res = await fetch(buildApiUrl('/gmail/callback'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ code, state }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to complete Gmail connection');
    }
    return res.json();
  },

  async getGmailStatus(): Promise<GmailStatus> {
    const res = await fetch(buildApiUrl('/gmail/status'), { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch Gmail connection status');
    return res.json();
  },

  async disconnectGmail(): Promise<GmailDisconnectResponse> {
    const res = await fetch(buildApiUrl('/gmail/disconnect'), {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to disconnect Gmail account');
    return res.json();
  },

  async listGmailMessages(limit: number = 10, pageToken?: string, q?: string): Promise<GmailMessageListResponse> {
    const url = new URL(buildApiUrl('/gmail/messages'));
    url.searchParams.set('limit', String(limit));
    if (pageToken) url.searchParams.set('page_token', pageToken);
    if (q) url.searchParams.set('q', q);
    const res = await fetch(url.toString(), { headers: getHeaders() });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to fetch Gmail messages');
    }
    return res.json();
  },

  async scanGmailMessages(messageIds: string[], storeContent: boolean = false): Promise<GmailScanBatchResponse> {
    const res = await fetch(buildApiUrl('/gmail/scan'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ message_ids: messageIds, store_content: storeContent }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to scan Gmail messages');
    }
    return res.json();
  },
};
