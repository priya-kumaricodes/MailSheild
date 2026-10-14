import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { AnalyzerView } from '../components/AnalyzerView';
import { api } from '../services/api';
import { PredictResponse } from '../types';

vi.mock('../services/api', () => ({
  api: {
    predict: vi.fn(),
    predictFile: vi.fn(),
    submitFeedback: vi.fn(),
  },
}));

const mockSpamPrediction: PredictResponse = {
  id: 'analysis-123',
  prediction: 'Spam',
  is_spam: true,
  score: 0.942,
  score_type: 'probability',
  calibrated: true,
  raw_decision_score: 2.85,
  confidence_level: 'High',
  model_name: 'logistic_regression',
  model_version: '1.0.0',
  threshold_used: 0.5,
  processing_time_ms: 4.8,
  created_at: new Date().toISOString(),
  explanations: {
    model_name: 'logistic_regression',
    intercept: -0.42,
    net_decision_score: 2.85,
    calibrated_probability: 0.942,
    top_spam_features: [
      {
        token: 'urgent',
        weight: 1.85,
        tfidf_value: 0.35,
        contribution: 0.6475,
        direction: 'Spam',
        relative_impact: 0.45,
        description: 'Strong spam signal',
      },
      {
        token: 'verify',
        weight: 1.42,
        tfidf_value: 0.28,
        contribution: 0.3976,
        direction: 'Spam',
        relative_impact: 0.30,
        description: 'Phishing credential request',
      },
    ],
    top_legitimate_features: [
      {
        token: 'thanks',
        weight: -1.2,
        tfidf_value: 0.15,
        contribution: -0.18,
        direction: 'Legitimate',
        relative_impact: 0.25,
        description: 'Typical legitimate closing',
      },
    ],
    all_contributions: [],
    attribution_notes: 'Linear logistic regression additive token log-odds.',
  },
};

describe('AnalyzerView Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders input fields, parameter controls and sample buttons', () => {
    render(<AnalyzerView />);
    expect(screen.getByPlaceholderText(/e\.g\. Account Security Verification Alert/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Paste the full email text, headers, or body here/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Analyze Email/i })).toBeInTheDocument();
    expect(screen.getByText('Inference Parameters')).toBeInTheDocument();
    expect(screen.getByText('Phishing: Bank Alert')).toBeInTheDocument();
  });

  it('populates fields when sample email button is clicked', () => {
    render(<AnalyzerView />);
    const sampleBtn = screen.getByText('Phishing: Bank Alert');
    fireEvent.click(sampleBtn);

    const subjectInput = screen.getByPlaceholderText(/e\.g\. Account Security Verification Alert/i) as HTMLInputElement;
    const bodyInput = screen.getByPlaceholderText(/Paste the full email text, headers, or body here/i) as HTMLTextAreaElement;

    expect(subjectInput.value).toContain('URGENT NOTICE');
    expect(bodyInput.value).toContain('unauthorized login attempt');
  });

  it('submits email for analysis and renders prediction result and feature attributions', async () => {
    vi.mocked(api.predict).mockResolvedValue(mockSpamPrediction);

    render(<AnalyzerView />);
    const subjectInput = screen.getByPlaceholderText(/e\.g\. Account Security Verification Alert/i);
    const bodyInput = screen.getByPlaceholderText(/Paste the full email text, headers, or body here/i);

    fireEvent.change(subjectInput, { target: { value: 'Suspicious invoice' } });
    fireEvent.change(bodyInput, { target: { value: 'Please verify urgent payment right now.' } });

    const submitBtn = screen.getByRole('button', { name: /Analyze Email/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(api.predict).toHaveBeenCalledWith({
        subject: 'Suspicious invoice',
        body: 'Please verify urgent payment right now.',
        model_name: 'logistic_regression',
        threshold: 0.5,
        store_content: false,
      });
    });

    await waitFor(() => {
      expect(screen.getByText('Prediction: SPAM')).toBeInTheDocument();
      expect(screen.getByText('High Confidence')).toBeInTheDocument();
      expect(screen.getByText('urgent')).toBeInTheDocument();
      expect(screen.getByText('verify')).toBeInTheDocument();
      expect(screen.getByText('thanks')).toBeInTheDocument();
    });
  });

  it('handles file upload and triggers api.predictFile', async () => {
    vi.mocked(api.predictFile).mockResolvedValue(mockSpamPrediction);

    const { container } = render(<AnalyzerView />);
    const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
    expect(fileInput).not.toBeNull();

    const file = new File(['Subject: Test\n\nSuspicious body text'], 'suspicious.eml', { type: 'message/rfc822' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(api.predictFile).toHaveBeenCalledWith(file, {
        model_name: 'logistic_regression',
        threshold: 0.5,
        store_content: false,
      });
    });

    await waitFor(() => {
      expect(screen.getByText('Prediction: SPAM')).toBeInTheDocument();
    });
  });

  it('opens feedback modal and submits user feedback', async () => {
    vi.mocked(api.predict).mockResolvedValue(mockSpamPrediction);
    vi.mocked(api.submitFeedback).mockResolvedValue({ id: 'fb-1', status: 'recorded' } as any);

    render(<AnalyzerView />);
    fireEvent.change(screen.getByPlaceholderText(/Paste the full email text, headers, or body here/i), {
      target: { value: 'Test email content for feedback' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Analyze Email/i }));

    await waitFor(() => {
      expect(screen.getByText('Report Prediction Accuracy')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Report Prediction Accuracy'));
    expect(screen.getByText('Help improve the educational benchmark by suggesting the true classification label.')).toBeInTheDocument();

    const commentInput = screen.getByPlaceholderText(/Why do you think this classification was incorrect\?/i);
    fireEvent.change(commentInput, { target: { value: 'This was an internal security test' } });

    fireEvent.click(screen.getByRole('button', { name: 'Submit Feedback' }));

    await waitFor(() => {
      expect(api.submitFeedback).toHaveBeenCalledWith(
        'analysis-123',
        'Legitimate',
        'This was an internal security test'
      );
      expect(screen.getByText('Feedback submitted. Thank you!')).toBeInTheDocument();
    });
  });

  it('displays error banner when api.predict fails', async () => {
    vi.mocked(api.predict).mockRejectedValue(new Error('Backend server unreachable'));

    render(<AnalyzerView />);
    fireEvent.change(screen.getByPlaceholderText(/Paste the full email text, headers, or body here/i), {
      target: { value: 'Test failure email' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Analyze Email/i }));

    await waitFor(() => {
      expect(screen.getByText('Backend server unreachable')).toBeInTheDocument();
    });
  });

  it('resets form when Reset Form is clicked', async () => {
    vi.mocked(api.predict).mockResolvedValue(mockSpamPrediction);

    render(<AnalyzerView />);
    const subjectInput = screen.getByPlaceholderText(/e\.g\. Account Security Verification Alert/i) as HTMLInputElement;
    fireEvent.change(subjectInput, { target: { value: 'To be cleared' } });

    fireEvent.click(screen.getByText('Reset Form'));
    expect(subjectInput.value).toBe('');
  });
});
