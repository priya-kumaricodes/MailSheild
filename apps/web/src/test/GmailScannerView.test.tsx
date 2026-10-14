import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GmailScannerView } from '../components/GmailScannerView';
import { api } from '../services/api';

vi.mock('../services/api', () => ({
  api: {
    getGmailStatus: vi.fn(),
    getGmailAuthUrl: vi.fn(),
    disconnectGmail: vi.fn(),
    listGmailMessages: vi.fn(),
    scanGmailMessages: vi.fn(),
  },
}));

describe('GmailScannerView Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders disconnected state and configuration guidance when not configured', async () => {
    vi.mocked(api.getGmailStatus).mockResolvedValue({
      connected: false,
      email: null,
      scopes: [],
      connected_at: null,
      is_configured: false,
    });

    render(<GmailScannerView />);

    await waitFor(() => {
      expect(screen.getByText('Gmail Inbox Scanner')).toBeInTheDocument();
    });

    expect(screen.getByText(/Google OAuth Credentials Required/i)).toBeInTheDocument();
    expect(screen.getByText('Connect with Google')).toBeDisabled();
  });

  it('renders connect button enabled when credentials are configured', async () => {
    vi.mocked(api.getGmailStatus).mockResolvedValue({
      connected: false,
      email: null,
      scopes: [],
      connected_at: null,
      is_configured: true,
    });

    render(<GmailScannerView />);

    await waitFor(() => {
      expect(screen.getByText('Connect with Google')).not.toBeDisabled();
    });
  });

  it('renders connected account with disconnect button and fetch controls', async () => {
    vi.mocked(api.getGmailStatus).mockResolvedValue({
      connected: true,
      email: 'user@gmail.com',
      scopes: ['https://www.googleapis.com/auth/gmail.readonly'],
      connected_at: '2026-10-15T12:00:00Z',
      is_configured: true,
    });

    vi.mocked(api.listGmailMessages).mockResolvedValue({
      messages: [
        {
          id: 'msg_101',
          thread_id: 'th_101',
          snippet: 'Your statement is ready',
          sender: 'bank@example.com',
          subject: 'Monthly Bank Statement',
          date: 'Thu, 15 Oct 2026 10:00:00 GMT',
        },
      ],
      result_size_estimate: 1,
    });

    render(<GmailScannerView />);

    await waitFor(() => {
      expect(screen.getByText('user@gmail.com')).toBeInTheDocument();
    });

    expect(screen.getByText('Disconnect')).toBeInTheDocument();
    expect(screen.getByText('Fetch Recent Messages')).toBeInTheDocument();

    // Fetch messages
    fireEvent.click(screen.getByText('Fetch Recent Messages'));

    await waitFor(() => {
      expect(screen.getByText('Monthly Bank Statement')).toBeInTheDocument();
      expect(screen.getByText('bank@example.com')).toBeInTheDocument();
    });
  });

  it('executes batch scan and displays results with privacy default', async () => {
    vi.mocked(api.getGmailStatus).mockResolvedValue({
      connected: true,
      email: 'user@gmail.com',
      scopes: ['https://www.googleapis.com/auth/gmail.readonly'],
      connected_at: '2026-10-15T12:00:00Z',
      is_configured: true,
    });

    vi.mocked(api.listGmailMessages).mockResolvedValue({
      messages: [
        {
          id: 'msg_202',
          thread_id: 'th_202',
          snippet: 'Account suspended verify now',
          sender: 'security@attacker.com',
          subject: 'URGENT: Verify Account',
          date: 'Thu, 15 Oct 2026 11:00:00 GMT',
        },
      ],
      result_size_estimate: 1,
    });

    vi.mocked(api.scanGmailMessages).mockResolvedValue({
      total_scanned: 1,
      spam_count: 1,
      ham_count: 0,
      error_count: 0,
      results: [
        {
          message_id: 'msg_202',
          sender: 'security@attacker.com',
          subject: 'URGENT: Verify Account',
          date: 'Thu, 15 Oct 2026 11:00:00 GMT',
          prediction: 'spam',
          probability: 0.98,
          confidence: 0.9,
          language: 'en',
          is_mixed: false,
          phishing_risk: {
            risk_level: 'High',
            risk_score: 0.85,
            indicators_triggered: [{ name: 'credential_harvesting_threat' }],
          },
          top_tokens: [
            { token: 'urgent', weight: 1.5, direction: 'Spam', description: 'Urgency indicator' },
          ],
        },
      ],
    });

    render(<GmailScannerView />);

    await waitFor(() => {
      expect(screen.getByText('Fetch Recent Messages')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Fetch Recent Messages'));

    await waitFor(() => {
      expect(screen.getByText('URGENT: Verify Account')).toBeInTheDocument();
    });

    // Scan
    fireEvent.click(screen.getByText(/Scan Selected/i));

    await waitFor(() => {
      expect(screen.getByText('Scan Batch Summary')).toBeInTheDocument();
      expect(screen.getByText(/Processed purely in-memory/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/SPAM \(98%\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Phishing Risk: High/i)).toBeInTheDocument();
    expect(screen.getByText(/credential_harvesting_threat/i)).toBeInTheDocument();
  });
});
