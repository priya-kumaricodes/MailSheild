import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { ModelLabView } from '../components/ModelLabView';
import { api } from '../services/api';
import { ModelListResponse, ThresholdSimulationResponse } from '../types';

vi.mock('../services/api', () => ({
  api: {
    getModels: vi.fn(),
    getThresholdSimulation: vi.fn(),
  },
}));

const mockModelList: ModelListResponse = {
  models: [
    {
      name: 'logistic_regression',
      display_name: 'Logistic Regression',
      version: '1.0.0',
      score_type: 'probability',
      calibrated: true,
      optimal_threshold: 0.4,
      test_metrics: {
        accuracy: 1.0,
        precision: 1.0,
        recall: 1.0,
        f1_score: 1.0,
        false_positive_rate: 0.0,
        pr_auc: 1.0,
        roc_auc: 1.0,
        num_samples: 28,
        threshold: 0.4,
        confusion_matrix: { tn: 13, fp: 0, fn: 0, tp: 15 },
      },
      validation_metrics: {
        accuracy: 1.0,
        precision: 1.0,
        recall: 1.0,
        f1_score: 1.0,
        false_positive_rate: 0.0,
        pr_auc: 1.0,
        roc_auc: 1.0,
        num_samples: 28,
        threshold: 0.4,
        confusion_matrix: { tn: 13, fp: 0, fn: 0, tp: 15 },
      },
    },
    {
      name: 'naive_bayes',
      display_name: 'Multinomial Naive Bayes',
      version: '1.0.0',
      score_type: 'probability',
      calibrated: false,
      optimal_threshold: 0.05,
      test_metrics: {
        accuracy: 1.0,
        precision: 1.0,
        recall: 1.0,
        f1_score: 1.0,
        false_positive_rate: 0.0,
        pr_auc: 1.0,
        roc_auc: 1.0,
        num_samples: 28,
        threshold: 0.05,
        confusion_matrix: { tn: 13, fp: 0, fn: 0, tp: 15 },
      },
      validation_metrics: {
        accuracy: 1.0,
        precision: 1.0,
        recall: 1.0,
        f1_score: 1.0,
        false_positive_rate: 0.0,
        pr_auc: 1.0,
        roc_auc: 1.0,
        num_samples: 28,
        threshold: 0.05,
        confusion_matrix: { tn: 13, fp: 0, fn: 0, tp: 15 },
      },
    },
    {
      name: 'linear_svm',
      display_name: 'Linear SVM',
      version: '1.0.0',
      score_type: 'probability',
      calibrated: true,
      optimal_threshold: 0.25,
      test_metrics: {
        accuracy: 1.0,
        precision: 1.0,
        recall: 1.0,
        f1_score: 1.0,
        false_positive_rate: 0.0,
        pr_auc: 1.0,
        roc_auc: 1.0,
        num_samples: 28,
        threshold: 0.25,
        confusion_matrix: { tn: 13, fp: 0, fn: 0, tp: 15 },
      },
      validation_metrics: {
        accuracy: 1.0,
        precision: 1.0,
        recall: 1.0,
        f1_score: 1.0,
        false_positive_rate: 0.0,
        pr_auc: 1.0,
        roc_auc: 1.0,
        num_samples: 28,
        threshold: 0.25,
        confusion_matrix: { tn: 13, fp: 0, fn: 0, tp: 15 },
      },
    },
  ],
  active_model: 'logistic_regression',
  vocab_size: 696,
  dataset_info: {
    total_samples: 184,
  },
};

const mockSimulation: ThresholdSimulationResponse = {
  model_name: 'logistic_regression',
  current_metrics: {
    threshold: 0.5,
    accuracy: 1.0,
    precision: 1.0,
    recall: 1.0,
    f1_score: 1.0,
    false_positive_rate: 0.0,
    confusion_matrix: [
      [13, 0],
      [0, 15],
    ],
  },
  sweep_curve: [
    {
      threshold: 0.1,
      accuracy: 0.95,
      precision: 0.92,
      recall: 1.0,
      f1_score: 0.96,
      false_positive_rate: 0.05,
      confusion_matrix: [
        [12, 1],
        [0, 15],
      ],
    },
    {
      threshold: 0.5,
      accuracy: 1.0,
      precision: 1.0,
      recall: 1.0,
      f1_score: 1.0,
      false_positive_rate: 0.0,
      confusion_matrix: [
        [13, 0],
        [0, 15],
      ],
    },
  ],
};

describe('ModelLabView Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders model cards and benchmark metrics', async () => {
    vi.mocked(api.getModels).mockResolvedValue(mockModelList);
    vi.mocked(api.getThresholdSimulation).mockResolvedValue(mockSimulation);

    render(<ModelLabView />);

    await waitFor(() => {
      expect(screen.getByText('Model Lab & Performance Benchmarking')).toBeInTheDocument();
      expect(screen.getAllByText('Logistic Regression').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Multinomial Naive Bayes').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Linear SVM').length).toBeGreaterThan(0);
    });
  });

  it('changes selected model when card is clicked and fetches new simulation data', async () => {
    vi.mocked(api.getModels).mockResolvedValue(mockModelList);
    vi.mocked(api.getThresholdSimulation).mockResolvedValue(mockSimulation);

    render(<ModelLabView />);

    const nbCards = await screen.findAllByText('Multinomial Naive Bayes');
    expect(nbCards.length).toBeGreaterThan(0);

    fireEvent.click(nbCards[0]);

    await waitFor(() => {
      expect(api.getThresholdSimulation).toHaveBeenCalledWith('naive_bayes', 0.5);
    });
  });

  it('adjusts decision threshold slider and updates simulation metrics', async () => {
    vi.mocked(api.getModels).mockResolvedValue(mockModelList);
    vi.mocked(api.getThresholdSimulation).mockResolvedValue(mockSimulation);

    render(<ModelLabView />);

    await waitFor(() => {
      expect(screen.getByText('DYNAMIC VALIDATION SIMULATOR')).toBeInTheDocument();
    });

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '0.70' } });

    await waitFor(() => {
      expect(api.getThresholdSimulation).toHaveBeenCalledWith('logistic_regression', 0.7);
    });
  });

  it('displays confusion matrix metrics (TN, FP, FN, TP)', async () => {
    vi.mocked(api.getModels).mockResolvedValue(mockModelList);
    vi.mocked(api.getThresholdSimulation).mockResolvedValue(mockSimulation);

    render(<ModelLabView />);

    await waitFor(() => {
      expect(screen.getByText(/Validation Confusion Matrix at/i)).toBeInTheDocument();
      expect(screen.getByText('True Negative (TN)')).toBeInTheDocument();
      expect(screen.getByText('True Positive (TP)')).toBeInTheDocument();
      expect(screen.getByText('False Positive (FP)')).toBeInTheDocument();
      expect(screen.getByText('False Negative (FN)')).toBeInTheDocument();
    });
  });
});
