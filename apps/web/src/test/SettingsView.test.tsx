import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { SettingsView } from '../components/SettingsView';
import { HealthStatus } from '../types';

const mockHealth: HealthStatus = {
  status: 'healthy',
  backend: true,
  database: true,
  model_loaded: true,
  active_models: ['logistic_regression', 'naive_bayes', 'linear_svm'],
  environment: 'development',
  mode: 'standard',
  version: '1.0.0',
};

describe('SettingsView Component', () => {
  const mockRefreshHealth = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    if (typeof localStorage !== 'undefined') {
      localStorage.clear();
    }
  });

  it('renders system status, engine specs, and privacy controls', () => {
    render(<SettingsView health={mockHealth} onRefreshHealth={mockRefreshHealth} />);

    expect(screen.getByText('System Settings & Privacy Preferences')).toBeInTheDocument();
    expect(screen.getByText('Privacy & Retention Controls')).toBeInTheDocument();
    expect(screen.getByText('Default Email Text Persistence')).toBeInTheDocument();
    expect(screen.getByText('Operational')).toBeInTheDocument();
  });

  it('updates privacy preferences and persists them to localStorage', async () => {
    render(<SettingsView health={mockHealth} onRefreshHealth={mockRefreshHealth} />);

    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).not.toBeChecked();

    fireEvent.click(checkbox);
    expect(checkbox).toBeChecked();

    const retentionSelect = screen.getByRole('combobox');
    fireEvent.change(retentionSelect, { target: { value: '30days' } });

    const saveButton = screen.getByRole('button', { name: /Save Preferences/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText('Preferences saved.')).toBeInTheDocument();
      expect(localStorage.getItem('mailshield_store_body')).toBe('true');
      expect(localStorage.getItem('mailshield_retention')).toBe('30days');
    });
  });

  it('triggers onRefreshHealth when Refresh Diagnostics is clicked', () => {
    render(<SettingsView health={mockHealth} onRefreshHealth={mockRefreshHealth} />);

    const refreshButton = screen.getByRole('button', { name: /Refresh/i });
    fireEvent.click(refreshButton);

    expect(mockRefreshHealth).toHaveBeenCalledTimes(1);
  });
});
