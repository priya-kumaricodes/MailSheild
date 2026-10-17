import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import App from '../App';

// Mock API calls
vi.mock('../services/api', () => ({
  api: {
    getHealth: vi.fn().mockResolvedValue({
      status: 'healthy',
      backend: true,
      database: true,
      model_loaded: true,
      active_models: ['logistic_regression', 'naive_bayes', 'linear_svm'],
      environment: 'development',
      mode: 'standard',
      version: '1.0.0',
    }),
    getHistory: vi.fn().mockResolvedValue({
      items: [
        {
          id: 'test-1',
          timestamp: new Date().toISOString(),
          subject: 'Sample Phishing Alert',
          prediction: 'Spam',
          is_spam: true,
          score: 0.95,
          score_type: 'probability',
          calibrated: true,
          confidence_level: 'High',
          model_name: 'logistic_regression',
          model_version: '1.0.0',
          threshold_used: 0.5,
          processing_time_ms: 12.5,
          is_content_stored: false,
          has_feedback: false,
        },
      ],
      total: 1,
      page: 1,
      page_size: 10,
      total_pages: 1,
    }),
    getModels: vi.fn().mockResolvedValue({
      models: [
        {
          name: 'logistic_regression',
          display_name: 'Logistic Regression',
          version: '1.0.0',
          score_type: 'probability',
          calibrated: true,
          optimal_threshold: 0.5,
          test_metrics: {
            accuracy: 0.98,
            precision: 0.97,
            recall: 0.99,
            f1_score: 0.98,
            false_positive_rate: 0.02,
            pr_auc: 0.99,
            roc_auc: 0.99,
            num_samples: 28,
            threshold: 0.5,
            confusion_matrix: { tn: 14, fp: 0, fn: 0, tp: 14 },
          },
          validation_metrics: {
            accuracy: 0.98,
            precision: 0.97,
            recall: 0.99,
            f1_score: 0.98,
            false_positive_rate: 0.02,
            pr_auc: 0.99,
            roc_auc: 0.99,
            num_samples: 28,
            threshold: 0.5,
            confusion_matrix: { tn: 14, fp: 0, fn: 0, tp: 14 },
          },
        },
      ],
      active_model: 'logistic_regression',
      vocab_size: 692,
      dataset_info: { total_samples: 184 },
    }),
    getThresholdSimulation: vi.fn().mockResolvedValue({
      model_name: 'logistic_regression',
      current_metrics: {
        threshold: 0.5,
        accuracy: 0.98,
        precision: 0.97,
        recall: 0.99,
        f1_score: 0.98,
        false_positive_rate: 0.02,
        confusion_matrix: [[14, 0], [0, 14]],
      },
      sweep_curve: [],
    }),
    getExportUrl: vi.fn().mockReturnValue('/api/v1/reports/export?format=csv'),
  },
}));

describe('MailShield Web Application', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders branding and navigation header', async () => {
    render(<App />);
    expect(screen.getByText('MailShield')).toBeInTheDocument();
    expect(screen.getByText('Email Analyzer')).toBeInTheDocument();
    expect(screen.getByText('Model Lab')).toBeInTheDocument();
  });

  it('navigates between views when tabs are clicked', async () => {
    render(<App />);

    // Click Email Analyzer
    fireEvent.click(screen.getByText('Email Analyzer'));
    await waitFor(() => {
      expect(screen.getByText('Email Analyzer & Feature Attribution')).toBeInTheDocument();
    });

    // Click Model Lab
    fireEvent.click(screen.getByText('Model Lab'));
    await waitFor(() => {
      expect(screen.getByText('Model Lab & Performance Benchmarking')).toBeInTheDocument();
    });

    // Click History
    fireEvent.click(screen.getByText('History'));
    await waitFor(() => {
      expect(screen.getByText('Analysis History')).toBeInTheDocument();
    });
  });

  it('populates subject and body when sample is clicked in Analyzer', async () => {
    render(<App />);
    fireEvent.click(screen.getByText('Email Analyzer'));

    await waitFor(() => {
      expect(screen.getByText('Phishing: Bank Alert')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Phishing: Bank Alert'));
    const subjectInput = screen.getByPlaceholderText('e.g. Account Security Verification Alert') as HTMLInputElement;
    expect(subjectInput.value).toContain('URGENT NOTICE');
  });
});
