import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { HistoryView } from '../components/HistoryView';
import { api } from '../services/api';
import { HistoryItem, HistoryDetail } from '../types';

vi.mock('../services/api', () => ({
  api: {
    getHistory: vi.fn(),
    getAnalysisDetail: vi.fn(),
    deleteAnalysis: vi.fn(),
    bulkDelete: vi.fn(),
    downloadExport: vi.fn(),
  },
}));

const mockItems: HistoryItem[] = [
  {
    id: 'item-1',
    timestamp: '2026-10-14T10:00:00Z',
    subject: 'Urgent Wire Transfer Request',
    prediction: 'Spam',
    is_spam: true,
    score: 0.985,
    score_type: 'probability',
    calibrated: true,
    confidence_level: 'High',
    model_name: 'logistic_regression',
    model_version: '1.0.0',
    threshold_used: 0.5,
    processing_time_ms: 5.2,
    is_content_stored: false,
    has_feedback: false,
  },
  {
    id: 'item-2',
    timestamp: '2026-10-14T09:30:00Z',
    subject: 'Sprint Planning Notes',
    prediction: 'Legitimate',
    is_spam: false,
    score: 0.05,
    score_type: 'probability',
    calibrated: true,
    confidence_level: 'High',
    model_name: 'logistic_regression',
    model_version: '1.0.0',
    threshold_used: 0.5,
    processing_time_ms: 3.1,
    is_content_stored: true,
    has_feedback: true,
  },
];

const mockDetail: HistoryDetail = {
  ...mockItems[0],
  email_hash: 'a1b2c3d4e5f6',
  email_body: '[Redacted for Privacy]',
  explanations: {
    model_name: 'logistic_regression',
    intercept: -0.4,
    net_decision_score: 3.2,
    calibrated_probability: 0.985,
    top_spam_features: [
      {
        token: 'wire',
        weight: 2.1,
        tfidf_value: 0.4,
        contribution: 0.84,
        direction: 'Spam',
        relative_impact: 0.5,
        description: 'Financial spam keyword',
      },
    ],
    top_legitimate_features: [],
    all_contributions: [],
    attribution_notes: 'Logistic regression odds.',
  },
};

describe('HistoryView Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.confirm = vi.fn().mockReturnValue(true);
  });

  it('renders history table with items and total counts', async () => {
    vi.mocked(api.getHistory).mockResolvedValue({
      items: mockItems,
      total: 2,
      page: 1,
      page_size: 10,
      total_pages: 1,
    });

    render(<HistoryView />);

    await waitFor(() => {
      expect(screen.getByText('Urgent Wire Transfer Request')).toBeInTheDocument();
      expect(screen.getByText('Sprint Planning Notes')).toBeInTheDocument();
      expect(screen.getByText(/Showing 2 of 2 records/i)).toBeInTheDocument();
    });
  });

  it('filters history by search query', async () => {
    vi.mocked(api.getHistory).mockResolvedValue({
      items: [mockItems[0]],
      total: 1,
      page: 1,
      page_size: 10,
      total_pages: 1,
    });

    render(<HistoryView />);
    const searchInput = screen.getByPlaceholderText(/Search subjects or predictions/i);
    fireEvent.change(searchInput, { target: { value: 'Wire' } });
    fireEvent.submit(searchInput.closest('form')!);

    await waitFor(() => {
      expect(api.getHistory).toHaveBeenCalledWith(
        expect.objectContaining({
          search: 'Wire',
        })
      );
    });
  });

  it('filters history by label button click', async () => {
    vi.mocked(api.getHistory).mockResolvedValue({
      items: [mockItems[0]],
      total: 1,
      page: 1,
      page_size: 10,
      total_pages: 1,
    });

    render(<HistoryView />);
    await waitFor(() => {
      expect(screen.getByText('Urgent Wire Transfer Request')).toBeInTheDocument();
    });

    const spamBtn = screen.getByRole('button', { name: /^Spam$/i });
    fireEvent.click(spamBtn);

    await waitFor(() => {
      expect(api.getHistory).toHaveBeenCalledWith(
        expect.objectContaining({
          label: 'Spam',
        })
      );
    });
  });

  it('selects multiple rows and performs bulk deletion', async () => {
    vi.mocked(api.getHistory).mockResolvedValue({
      items: mockItems,
      total: 2,
      page: 1,
      page_size: 10,
      total_pages: 1,
    });
    vi.mocked(api.bulkDelete).mockResolvedValue(2);

    const { container } = render(<HistoryView />);
    await waitFor(() => {
      expect(screen.getByText('Urgent Wire Transfer Request')).toBeInTheDocument();
    });

    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    // First checkbox is select-all
    fireEvent.click(checkboxes[0]);

    await waitFor(() => {
      expect(screen.getByText(/Delete Selected \(2\)/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Delete Selected \(2\)/i));

    await waitFor(() => {
      expect(api.bulkDelete).toHaveBeenCalledWith(['item-1', 'item-2']);
    });
  });

  it('opens detail modal and displays explanations', async () => {
    vi.mocked(api.getHistory).mockResolvedValue({
      items: mockItems,
      total: 2,
      page: 1,
      page_size: 10,
      total_pages: 1,
    });
    vi.mocked(api.getAnalysisDetail).mockResolvedValue(mockDetail);

    render(<HistoryView />);
    const rowTitle = await screen.findByText('Urgent Wire Transfer Request');
    expect(rowTitle).toBeInTheDocument();

    const viewButtons = await screen.findAllByTitle('View Feature Explanations');
    fireEvent.click(viewButtons[0]);

    await waitFor(() => {
      expect(api.getAnalysisDetail).toHaveBeenCalledWith('item-1');
      expect(screen.getByText('Feature Attribution Tokens')).toBeInTheDocument();
      expect(screen.getByText('wire')).toBeInTheDocument();
    });
  });

  it('triggers CSV and JSON downloads via api.downloadExport', async () => {
    vi.mocked(api.getHistory).mockResolvedValue({
      items: mockItems,
      total: 2,
      page: 1,
      page_size: 10,
      total_pages: 1,
    });
    vi.mocked(api.downloadExport).mockResolvedValue(undefined);

    render(<HistoryView />);
    await waitFor(() => {
      expect(screen.getByText('Export CSV')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Export CSV'));
    expect(api.downloadExport).toHaveBeenCalledWith('csv');

    fireEvent.click(screen.getByText('Export JSON'));
    expect(api.downloadExport).toHaveBeenCalledWith('json');
  });
});
