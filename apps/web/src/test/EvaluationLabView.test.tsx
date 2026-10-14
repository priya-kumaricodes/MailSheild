import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { EvaluationLabView } from '../components/EvaluationLabView';
import { api } from '../services/api';
import {
  SupportedLanguage,
  EvaluationMetricsResponse,
  ConfusionMatrixResponse,
  DrilldownErrorItem,
  ModelComparisonResponse,
  DatasetProvenanceResponse,
  DemoSample,
  PredictResponse,
} from '../types';

vi.mock('../services/api', () => ({
  api: {
    getEvaluationLanguages: vi.fn(),
    getEvaluationMetrics: vi.fn(),
    getEvaluationConfusionMatrix: vi.fn(),
    getEvaluationErrors: vi.fn(),
    getEvaluationComparison: vi.fn(),
    getEvaluationProvenance: vi.fn(),
    getEvaluationDemoSamples: vi.fn(),
    predict: vi.fn(),
  },
}));

const mockLanguages: SupportedLanguage[] = [
  { code: 'all', name: 'All Languages (Multilingual Benchmark)', script: 'Mixed', test_samples: 36 },
  { code: 'en', name: 'English', script: 'Latin', test_samples: 6 },
  { code: 'hi', name: 'Hindi', script: 'Devanagari', test_samples: 6 },
  { code: 'hinglish', name: 'Hinglish / Romanized Indic', script: 'Latin', test_samples: 6 },
  { code: 'ta', name: 'Tamil', script: 'Tamil', test_samples: 6 },
  { code: 'te', name: 'Telugu', script: 'Telugu', test_samples: 6 },
  { code: 'kn', name: 'Kannada', script: 'Kannada', test_samples: 6 },
];

const mockMetrics: EvaluationMetricsResponse = {
  model_name: 'linear_svm',
  split: 'test',
  language: 'all',
  threshold: 0.65,
  inference_latency_ms: 0.002,
  model_size_kb: 34.6,
  accuracy: 0.9722,
  precision: 1.0,
  recall: 0.9444,
  f1: 0.9714,
  fpr: 0.0,
  fnr: 0.0556,
  brier_score: 0.0344,
  pr_auc: 0.99,
  roc_auc: 0.99,
  num_samples: 36,
  confusion_matrix: { tn: 18, fp: 0, fn: 1, tp: 17 },
};

const mockConfusionMatrix: ConfusionMatrixResponse = {
  model_name: 'linear_svm',
  split: 'test',
  language: 'all',
  grid: [
    [18, 0],
    [1, 17],
  ],
  tn: 18,
  fp: 0,
  fn: 1,
  tp: 17,
  rates: {
    true_negative_rate: 1.0,
    false_positive_rate: 0.0,
    false_negative_rate: 0.0556,
    true_positive_rate: 0.9444,
  },
  total_samples: 36,
};

const mockErrors: DrilldownErrorItem[] = [
  {
    model: 'linear_svm',
    email_id: 'kn_spam_02',
    subject: 'ವಿಶೇಷ ಕೊಡುಗೆ',
    body_preview: 'ನಿಮ್ಮ ಖಾತೆಗೆ ಬೋನಸ್ ಡೇಟಾ ಬಂದಿದೆ...',
    sender: 'offers@telecom.kn',
    language: 'kn',
    script: 'Kannada',
    template_group: 'kn_telecom_offer',
    provenance: 'manually_curated',
    category: 'telecom',
    actual_label: 'spam',
    predicted_label: 'ham',
    score: 0.58,
    threshold: 0.65,
    is_error: true,
    error_type: 'FN',
  },
];

const mockComparison: ModelComparisonResponse = {
  english_baseline: {
    model: 'English Baseline (TF-IDF + Linear SVM)',
    accuracy: 0.5278,
    recall: 0.0556,
    fpr: 0.0,
    latency_ms: 0.002,
    size_kb: 40.0,
  },
  multilingual_models: {
    linear_svm: {
      accuracy: 0.9722,
      recall: 0.9444,
      fpr: 0.0,
      latency_ms: 0.002,
      size_kb: 34.6,
    },
    logistic_regression: {
      accuracy: 0.9444,
      recall: 0.8889,
      fpr: 0.0,
      latency_ms: 0.002,
      size_kb: 35.9,
    },
    naive_bayes: {
      accuracy: 0.8333,
      recall: 0.7222,
      fpr: 0.0556,
      latency_ms: 0.002,
      size_kb: 36.2,
    },
  },
};

const mockProvenance: DatasetProvenanceResponse = {
  total_records: 144,
  splits: {
    train: { samples: 72, template_groups: 24 },
    validation: { samples: 36, template_groups: 12 },
    test: { samples: 36, template_groups: 12 },
  },
  zero_group_leakage: true,
  provenance_breakdown: {
    public_corpus: 24,
    manually_curated: 60,
    synthetic_template: 60,
  },
  license_breakdown: {
    'Apache-2.0': 24,
    'CC-BY-4.0': 120,
  },
  language_distribution: {
    en: 24,
    hi: 24,
    hinglish: 24,
    ta: 24,
    te: 24,
    kn: 24,
  },
  categories: {
    banking: 48,
    telecom: 24,
    lottery: 24,
    meeting: 24,
    flight: 24,
  },
};

const mockDemoSamples: DemoSample[] = [
  {
    id: 'demo_hi_01',
    language: 'hi',
    script: 'Devanagari',
    expected_label: 'spam',
    category: 'banking',
    sender: 'security@sbi-fraud.net',
    subject: 'महत्वपूर्ण सूचना: आपका खाता बंद कर दिया जाएगा',
    body: 'प्रिय ग्राहक, आपका एसबीआई खाता 24 घंटे में ब्लॉक हो जाएगा। तुरंत केवाईसी अपडेट करें।',
  },
];

const mockPredictResponse: PredictResponse = {
  id: 'test-pred-123',
  prediction: 'Spam',
  is_spam: true,
  score: 0.95,
  score_type: 'probability',
  calibrated: true,
  raw_decision_score: 2.1,
  confidence_level: 'High',
  model_name: 'multilingual_linear_svm',
  model_version: '2.0.0',
  threshold_used: 0.65,
  processing_time_ms: 3.2,
  created_at: new Date().toISOString(),
  language_analysis: {
    detected_language: 'hi',
    language_name: 'Hindi',
    script: 'Devanagari',
    method: 'unicode_script',
    confidence: 0.98,
    mixed_script: false,
    diagnostics: {},
  },
  phishing_analysis: {
    risk_level: 'high',
    risk_score: 0.85,
    indicators: [
      {
        name: 'Urgent Action Threat',
        severity: 'high',
        description: 'Coercive urgency threat detected in Devanagari script',
      },
    ],
    defensive_dampener_applied: false,
  },
  explanations: {
    model_name: 'multilingual_linear_svm',
    intercept: -0.5,
    net_decision_score: 2.1,
    calibrated_probability: 0.95,
    top_spam_features: [
      {
        token: 'ब्लॉक',
        weight: 1.5,
        tfidf_value: 0.4,
        contribution: 0.6,
        direction: 'Spam',
        relative_impact: 0.5,
        description: '',
      },
    ],
    top_legitimate_features: [],
    all_contributions: [],
    attribution_notes: 'Multilingual char_wb and word token contribution.',
  },
};

describe('EvaluationLabView Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.getEvaluationLanguages).mockResolvedValue(mockLanguages);
    vi.mocked(api.getEvaluationMetrics).mockResolvedValue(mockMetrics);
    vi.mocked(api.getEvaluationConfusionMatrix).mockResolvedValue(mockConfusionMatrix);
    vi.mocked(api.getEvaluationErrors).mockResolvedValue(mockErrors);
    vi.mocked(api.getEvaluationComparison).mockResolvedValue(mockComparison);
    vi.mocked(api.getEvaluationProvenance).mockResolvedValue(mockProvenance);
    vi.mocked(api.getEvaluationDemoSamples).mockResolvedValue(mockDemoSamples);
    vi.mocked(api.predict).mockResolvedValue(mockPredictResponse);
  });

  it('renders Evaluation Lab title, description, and sub-navigation tabs', async () => {
    render(<EvaluationLabView />);

    expect(screen.getByText('Multilingual Evaluation Lab')).toBeInTheDocument();
    expect(screen.getByText('Performance & Confusion Matrix')).toBeInTheDocument();
    expect(screen.getByText('Baseline Comparison')).toBeInTheDocument();
    expect(screen.getByText(/Error Inspection/i)).toBeInTheDocument();
    expect(screen.getByText('Dataset Provenance')).toBeInTheDocument();
    expect(screen.getByText('Interactive Playground')).toBeInTheDocument();
  });

  it('loads and displays performance metrics and confusion matrix values', async () => {
    render(<EvaluationLabView />);

    await waitFor(() => {
      expect(screen.getByText('97.2%')).toBeInTheDocument(); // Accuracy
      expect(screen.getByText('100.0%')).toBeInTheDocument(); // Precision
      expect(screen.getByText('94.4%')).toBeInTheDocument(); // Recall
      expect(screen.getByText('0.0%')).toBeInTheDocument(); // FPR
    });

    // Check confusion matrix cells (TN: 18, FP: 0, FN: 1, TP: 17)
    expect(screen.getByText('18')).toBeInTheDocument();
    expect(screen.getByText('17')).toBeInTheDocument();
  });

  it('allows switching to Baseline Comparison tab and displays comparative metrics', async () => {
    render(<EvaluationLabView />);

    const compareTab = screen.getByText('Baseline Comparison');
    fireEvent.click(compareTab);

    await waitFor(() => {
      expect(screen.getByText(/Multilingual Linear SVM/i)).toBeInTheDocument();
      expect(screen.getByText(/Multilingual Logistic Regression/i)).toBeInTheDocument();
    });
  });

  it('allows switching to Error Inspection tab and displays false negatives and details', async () => {
    render(<EvaluationLabView />);

    await waitFor(() => {
      expect(screen.getByText('97.2%')).toBeInTheDocument();
    });

    const drilldownTab = screen.getByRole('button', { name: /Error Inspection/i });
    fireEvent.click(drilldownTab);

    await waitFor(() => {
      expect(screen.getByText('ವಿಶೇಷ ಕೊಡುಗೆ')).toBeInTheDocument();
      expect(screen.getByText(/ನಿಮ್ಮ ಖಾತೆಗೆ ಬೋನಸ್ ಡೇಟಾ ಬಂದಿದೆ/i)).toBeInTheDocument();
      expect(screen.getByText('FN')).toBeInTheDocument();
    });
  });

  it('allows switching to Dataset Provenance tab and displays zero group overlap guarantee', async () => {
    render(<EvaluationLabView />);

    await waitFor(() => {
      expect(screen.getByText('97.2%')).toBeInTheDocument();
    });

    const provenanceTab = screen.getByRole('button', { name: /Dataset Provenance/i });
    fireEvent.click(provenanceTab);

    await waitFor(() => {
      expect(screen.getByText('144')).toBeInTheDocument(); // Total records
      expect(screen.getByText(/Strict Template-Group Partitioning Verified/i)).toBeInTheDocument();
    });
  });

  it('allows selecting demo sample and running prediction in Multilingual Playground', async () => {
    render(<EvaluationLabView />);

    await waitFor(() => {
      expect(screen.getByText('97.2%')).toBeInTheDocument();
    });

    const playgroundTab = screen.getByRole('button', { name: /Interactive Playground/i });
    fireEvent.click(playgroundTab);

    await waitFor(() => {
      expect(screen.getByText(/महत्वपूर्ण सूचना: आपका खाता बंद कर दिया जाएगा/i)).toBeInTheDocument();
    });

    // Click analyze button
    const analyzeBtn = screen.getByRole('button', { name: /Run Multilingual & Phishing Scan/i });
    fireEvent.click(analyzeBtn);

    await waitFor(() => {
      expect(api.predict).toHaveBeenCalled();
      expect(screen.getByText('Devanagari')).toBeInTheDocument();
      expect(screen.getByText(/high Risk/i)).toBeInTheDocument();
    });
  });
});
