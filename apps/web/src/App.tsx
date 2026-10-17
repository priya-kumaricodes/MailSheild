import React, { useEffect, useState } from 'react';
import { Header } from './components/Header';
import { CyberShieldCanvas } from './components/CyberShieldCanvas';
import { CinematicHero } from './components/CinematicHero';
import { CinematicStageController } from './components/CinematicStageController';
import { CinematicViewTransition } from './components/CinematicViewTransition';
import { DashboardView } from './components/DashboardView';
import { AnalyzerView } from './components/AnalyzerView';
import { GmailScannerView } from './components/GmailScannerView';
import { HistoryView } from './components/HistoryView';
import { ModelLabView } from './components/ModelLabView';
import { EvaluationLabView } from './components/EvaluationLabView';
import { SettingsView } from './components/SettingsView';
import { api } from './services/api';
import { HealthStatus } from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [health, setHealth] = useState<HealthStatus | null>(null);

  const fetchHealth = async () => {
    try {
      const res = await api.getHealth();
      setHealth(res);
    } catch (err) {
      console.warn('Backend currently unreachable');
      setHealth({
        status: 'degraded',
        backend: false,
        database: false,
        model_loaded: false,
        active_models: [],
        environment: 'offline',
        mode: 'standard',
        version: '2.1.0',
      });
    }
  };

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, [currentTab]);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);

    // Handle OAuth callback redirects in web mode
    if (typeof window !== 'undefined' && window.location.search) {
      const params = new URLSearchParams(window.location.search);
      const code = params.get('code');
      const state = params.get('state');
      if (code && state) {
        setCurrentTab('gmail');
        api
          .submitGmailCallback(code, state)
          .then(() => {
            window.history.replaceState({}, document.title, window.location.pathname);
          })
          .catch((err) => {
            console.error('Failed to submit OAuth callback:', err);
          });
      }
    }

    return () => {
      clearInterval(interval);
    };
  }, []);

  const handleEnterConsole = () => {
    const el = document.getElementById('defense-terminal');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    } else {
      setCurrentTab('analyzer');
    }
  };

  const handleNavigateSection = (secId: string) => {
    const el = document.getElementById(secId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-transparent text-slate-100 flex flex-col relative selection:bg-cyan-500 selection:text-slate-950">
      {/* Application-Wide Cinematic Background Stage Controller */}
      <CinematicStageController activeTab={currentTab} heroContainerId="scrolly-hero-container" />

      {/* Three.js Procedural Environmental Layer with Tab Waypoints */}
      <CyberShieldCanvas activeTab={currentTab} />

      {/* Atmospheric Vignette & Film Depth Overlay */}
      <div id="vignette" aria-hidden="true" />

      {/* Fixed Sticky Header Navigation */}
      <Header currentTab={currentTab} onTabChange={setCurrentTab} health={health} />

      {/* Main Content Stage with Cinematic View Transitions */}
      <main className="flex-1 w-full relative z-10">
        <CinematicViewTransition activeKey={currentTab}>
          {currentTab === 'dashboard' && (
            <div className="space-y-4">
              <CinematicHero
                onEnterConsole={handleEnterConsole}
                onNavigateSection={handleNavigateSection}
                activeModelF1="100.0%"
              />

              <div id="defense-terminal" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24 border-t border-shield-border/40">
                <div className="flex items-center gap-3 mb-6 text-xs font-mono tracking-widest text-shield-cyan uppercase">
                  <span>04 &mdash; Operational Defense Terminal</span>
                  <span className="w-12 h-px bg-shield-cyan/40" />
                  <span className="text-slate-500">Live Telemetry &amp; System Health</span>
                </div>
                <DashboardView onNavigate={setCurrentTab} />
              </div>
            </div>
          )}

          {currentTab !== 'dashboard' && (
            <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {currentTab === 'analyzer' && (
                <AnalyzerView backendReady={health !== null ? health.backend : false} />
              )}
              {currentTab === 'gmail' && <GmailScannerView />}
              {currentTab === 'history' && <HistoryView />}
              {currentTab === 'modellab' && <ModelLabView />}
              {currentTab === 'evaluationlab' && <EvaluationLabView />}
              {currentTab === 'settings' && (
                <SettingsView health={health} onRefreshHealth={fetchHealth} />
              )}
            </div>
          )}
        </CinematicViewTransition>
      </main>

      {/* Footer Colophon */}
      <footer className="relative z-10 border-t border-shield-border/60 py-8 text-center text-xs text-slate-500 font-mono backdrop-blur-md bg-slate-950/80">
        <p>MailShield v2.1.0 &bull; Multilingual Spam Defense &bull; Three.js Neural Radar &bull; Decoupled Phishing Risk</p>
      </footer>
    </div>
  );
};

export default App;
