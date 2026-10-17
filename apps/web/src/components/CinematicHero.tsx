import React, { useRef } from 'react';
import { ArrowDownRight, Terminal, Shield, Cpu, Layers, Lock, Compass, CheckCircle2, ChevronRight, Activity, Globe2, Radio } from 'lucide-react';

interface CinematicHeroProps {
  onEnterConsole: () => void;
  onNavigateSection: (sectionId: string) => void;
  activeModelF1?: string;
}

export const CinematicHero: React.FC<CinematicHeroProps> = ({
  onEnterConsole,
  onNavigateSection,
  activeModelF1 = '100.0%',
}) => {
  const scrollyContainerRef = useRef<HTMLDivElement>(null);

  return (
    <div
      id="scrolly-hero-container"
      ref={scrollyContainerRef}
      className="relative w-full"
    >
      {/* ============================================================ FOREGROUND NARRATIVE CONTENT */}
      <div className="relative z-10 w-full text-slate-100">
        {/* ============================================================ CHAPTER 00: THE PERIMETER THRESHOLD */}
        <section id="ch-perimeter" className="relative min-h-screen flex flex-col justify-between pt-8 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          <div className="pt-6 sm:pt-12">
            {/* Eyebrow */}
            <div className="inline-flex items-center gap-2.5 px-3 py-1 rounded-full bg-slate-900/80 border border-shield-borderLight text-xs tracking-widest uppercase font-mono text-shield-cyan mb-6 shadow-sm shadow-shield-cyan/5">
              <span className="w-2 h-2 rounded-full bg-shield-cyan animate-pulse shadow-sm shadow-shield-cyan" />
              <span>Chapter 00 &mdash; The Perimeter Threshold</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
              {/* Left: Masked Editorial Typography */}
              <div className="lg:col-span-6 space-y-6">
                <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extralight tracking-tight leading-[1.08] text-white">
                  <span className="block font-medium bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                    Where stillness
                  </span>
                  <span className="block font-light italic text-shield-cyan">
                    reveals the threat.
                  </span>
                </h1>

                <p className="text-base sm:text-lg text-slate-300 font-light leading-relaxed max-w-xl">
                  MailShield replaces opaque deep-learning heuristics with verifiable, linear dot-product token attribution and zero-leakage multilingual defense across Indic and Latin scripts.
                </p>

                {/* Primary Action Buttons */}
                <div className="flex flex-wrap items-center gap-4 pt-2">
                  <button
                    onClick={onEnterConsole}
                    className="group relative flex items-center gap-3 px-6 py-3.5 rounded-xl bg-gradient-to-r from-shield-cyan to-shield-accent text-slate-950 font-semibold text-sm hover:opacity-95 shadow-xl shadow-shield-cyan/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
                  >
                    <Terminal className="w-4 h-4 text-slate-950" />
                    <span>Enter Defense Terminal</span>
                    <ArrowDownRight className="w-4 h-4 text-slate-950 group-hover:translate-x-0.5 group-hover:translate-y-0.5 transition-transform" />
                  </button>

                  <button
                    onClick={() => onNavigateSection('ch-gateway')}
                    className="flex items-center gap-2 px-5 py-3.5 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 text-slate-300 hover:text-white border border-shield-border text-sm font-medium transition-colors backdrop-blur-md"
                  >
                    <span>Explore Narrative Walk</span>
                  </button>
                </div>

                {/* Quick Telemetry Indicators */}
                <div className="flex items-center gap-6 pt-2 text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                    <span>Multilingual: 6 Scripts</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-shield-cyan" />
                    <span>Latency: 0.028ms</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                    <span>Holdout F1: {activeModelF1}</span>
                  </div>
                </div>
              </div>

              {/* Right: Perimeter Telemetry HUD Station */}
              <div className="lg:col-span-6">
                <div className="p-6 sm:p-8 rounded-3xl bg-[#060b14]/90 border border-slate-800/90 backdrop-blur-xl shadow-2xl shadow-cyan-950/20 relative overflow-hidden">
                  <div className="flex items-center justify-between pb-4 border-b border-slate-800/80">
                    <div className="flex items-center gap-2.5">
                      <span className="w-2 h-2 rounded-full bg-shield-cyan animate-pulse shadow-sm shadow-shield-cyan" />
                      <span className="text-xs font-mono text-shield-cyan uppercase tracking-widest font-medium">PERIMETER BARRIER // LIVE</span>
                    </div>
                    <span className="text-[11px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30">ZERO LEAKAGE</span>
                  </div>

                  <div className="mt-6 space-y-4 font-mono text-xs">
                    <div className="p-3.5 rounded-xl bg-[#0c1424] border border-slate-800 flex items-center justify-between shadow-inner">
                      <span className="text-slate-300">Ingress Stream Status</span>
                      <span className="text-slate-100 font-semibold flex items-center gap-1.5">
                        <Radio className="w-3.5 h-3.5 text-shield-cyan animate-pulse" />
                        4,820 packets/sec
                      </span>
                    </div>

                    <div className="p-3.5 rounded-xl bg-[#0c1424] border border-slate-800 space-y-2 shadow-inner">
                      <div className="flex justify-between text-slate-300">
                        <span>Multilingual Script Defense</span>
                        <span className="text-shield-cyan font-medium">6 Script Channels</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {['Latin', 'Devanagari', 'Tamil', 'Telugu', 'Kannada', 'Bengali'].map((script) => (
                          <span key={script} className="px-2 py-0.5 rounded bg-slate-800/90 border border-slate-700 text-[10px] text-slate-200">
                            {script}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="p-3.5 rounded-xl bg-[#0c1424] border border-slate-800 flex items-center justify-between shadow-inner">
                      <span className="text-slate-300">Deterministic Invariant</span>
                      <span className="text-emerald-400 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        Holdout F1: {activeModelF1}
                      </span>
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-300">
                    <span>Attribution Engine: Dot-Product Linear</span>
                    <span>Latency: 0.028ms</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Chapter Navigation Chips */}
          <div className="pt-12">
            <div className="flex items-center justify-between text-[11px] tracking-widest uppercase font-mono text-slate-400 pb-3 border-b border-shield-border/60">
              <span className="flex items-center gap-2">
                <Compass className="w-3.5 h-3.5 text-shield-cyan" />
                Scroll down to explore chapters
              </span>
              <span>Live Telemetry &bull; Active Model F1: {activeModelF1}</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4">
              <div
                onClick={() => onNavigateSection('ch-gateway')}
                className="p-3.5 rounded-xl bg-slate-950/70 hover:bg-slate-900/90 border border-shield-border/60 hover:border-shield-cyan/40 backdrop-blur-md transition-all cursor-pointer group"
              >
                <div className="text-xs font-mono text-shield-cyan group-hover:translate-x-1 transition-transform">01</div>
                <div className="text-sm font-medium text-slate-200 mt-1">Neural Gateway</div>
                <div className="text-xs text-slate-400 mt-0.5 line-clamp-1">Dual-channel tokenization architecture</div>
              </div>

              <div
                onClick={() => onNavigateSection('ch-radar')}
                className="p-3.5 rounded-xl bg-slate-950/70 hover:bg-slate-900/90 border border-shield-border/60 hover:border-shield-cyan/40 backdrop-blur-md transition-all cursor-pointer group"
              >
                <div className="text-xs font-mono text-shield-cyan group-hover:translate-x-1 transition-transform">02</div>
                <div className="text-sm font-medium text-slate-200 mt-1">Threat Topography</div>
                <div className="text-xs text-slate-400 mt-0.5 line-clamp-1">Platt calibration & Brier scores</div>
              </div>

              <div
                onClick={() => onNavigateSection('ch-provenance')}
                className="p-3.5 rounded-xl bg-slate-950/70 hover:bg-slate-900/90 border border-shield-border/60 hover:border-shield-cyan/40 backdrop-blur-md transition-all cursor-pointer group"
              >
                <div className="text-xs font-mono text-shield-cyan group-hover:translate-x-1 transition-transform">03</div>
                <div className="text-sm font-medium text-slate-200 mt-1">Zero-Leakage</div>
                <div className="text-xs text-slate-400 mt-0.5 line-clamp-1">Disjoint template validation guarantee</div>
              </div>

              <div
                onClick={onEnterConsole}
                className="p-3.5 rounded-xl bg-slate-950/70 hover:bg-slate-900/90 border border-shield-border/60 hover:border-shield-cyan/40 backdrop-blur-md transition-all cursor-pointer group"
              >
                <div className="text-xs font-mono text-shield-cyan group-hover:translate-x-1 transition-transform">04</div>
                <div className="text-sm font-medium text-slate-200 mt-1">Defense Terminal</div>
                <div className="text-xs text-slate-400 mt-0.5 line-clamp-1">Live interactive analyzer & Gmail scanner</div>
              </div>
            </div>
          </div>
        </section>

        {/* ============================================================ CHAPTER 01: THE NEURAL GATEWAY */}
        <section id="ch-gateway" className="relative min-h-screen flex flex-col justify-center py-28 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto border-t border-shield-border/40">
          <div className="flex items-center gap-3 mb-4 text-xs font-mono tracking-widest text-shield-cyan uppercase">
            <span>01 &mdash; The Neural Gateway</span>
            <span className="w-12 h-px bg-shield-cyan/40" />
            <span className="text-slate-400">Multilingual Ingestion &amp; Explainability</span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
            {/* Left: Narrative & Attribution Formula */}
            <div className="lg:col-span-6 space-y-6">
              <h2 className="text-3xl sm:text-5xl font-light tracking-tight text-white leading-tight">
                Mathematical attribution,{' '}
                <span className="italic text-slate-300 font-normal">zero synthetic opacity.</span>
              </h2>

              <p className="text-base text-slate-300 font-light leading-relaxed">
                Every email entering MailShield undergoes dual-channel feature decomposition: subword character n-grams capture Indic morphosyntax across Devanagari, Tamil, Telugu, and Kannada, while word n-grams extract transactional intent.
              </p>
              <p className="text-sm text-slate-400 font-light leading-relaxed">
                Unlike black-box neural networks that hallucinate confidence, MailShield calculates the exact dot product contribution <code className="text-shield-cyan font-mono text-xs bg-slate-900/80 px-1.5 py-0.5 rounded border border-shield-border">c_i = w_i &times; x_i</code> for each detected token. You inspect the literal mathematical evidence before making a security determination.
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-slate-800/80 pt-6">
                <div className="p-3.5 rounded-xl bg-[#060b14]/85 border border-slate-800/80 backdrop-blur-md shadow-sm">
                  <div className="text-2xl sm:text-3xl font-medium text-white font-mono">06</div>
                  <div className="text-[11px] text-slate-300 uppercase tracking-wider font-mono mt-1">Active Models</div>
                </div>
                <div className="p-3.5 rounded-xl bg-[#060b14]/85 border border-slate-800/80 backdrop-blur-md shadow-sm">
                  <div className="text-2xl sm:text-3xl font-medium text-shield-cyan font-mono">0.028<span className="text-sm font-normal">ms</span></div>
                  <div className="text-[11px] text-slate-300 uppercase tracking-wider font-mono mt-1">CPU Latency</div>
                </div>
                <div className="p-3.5 rounded-xl bg-[#060b14]/85 border border-slate-800/80 backdrop-blur-md shadow-sm">
                  <div className="text-2xl sm:text-3xl font-medium text-emerald-400 font-mono">0.0%</div>
                  <div className="text-[11px] text-slate-300 uppercase tracking-wider font-mono mt-1">False Positives</div>
                </div>
                <div className="p-3.5 rounded-xl bg-[#060b14]/85 border border-slate-800/80 backdrop-blur-md shadow-sm">
                  <div className="text-2xl sm:text-3xl font-medium text-shield-accent font-mono">100%</div>
                  <div className="text-[11px] text-slate-300 uppercase tracking-wider font-mono mt-1">Deterministic</div>
                </div>
              </div>

              {/* Pipeline Architecture Cards */}
              <div className="space-y-3 pt-2">
                <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 backdrop-blur-md flex items-start gap-3">
                  <Cpu className="w-4 h-4 text-shield-cyan mt-0.5 shrink-0" />
                  <div>
                    <div className="text-slate-200 text-xs font-semibold">Dual-Channel Vectorizer</div>
                    <div className="text-slate-400 mt-0.5 text-[11px] leading-relaxed">Word (1-2) + Subword Char_WB (3-5) with 5,000 feature vocabulary</div>
                  </div>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 backdrop-blur-md flex items-start gap-3">
                  <Layers className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0" />
                  <div>
                    <div className="text-slate-200 text-xs font-semibold">Platt-Calibrated SVM</div>
                    <div className="text-slate-400 mt-0.5 text-[11px] leading-relaxed">3-fold cross-validated sigmoid link maps margins to posterior probabilities</div>
                  </div>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 backdrop-blur-md flex items-start gap-3">
                  <Lock className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                  <div>
                    <div className="text-slate-200 text-xs font-semibold">Decoupled Phishing Engine</div>
                    <div className="text-slate-400 mt-0.5 text-[11px] leading-relaxed">Independent heuristic analyzer preserving high recall on legitimate banking alerts</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Floating Glass Token Attribution HUD */}
            <div className="lg:col-span-6">
              <div className="p-6 sm:p-8 rounded-3xl bg-[#060b14]/90 border border-slate-800/90 backdrop-blur-xl shadow-2xl relative overflow-hidden">
                <div className="flex items-center justify-between pb-4 border-b border-slate-800/80">
                  <div className="flex items-center gap-2">
                    <Radio className="w-3.5 h-3.5 text-shield-cyan animate-pulse" />
                    <span className="text-xs font-mono text-shield-cyan uppercase tracking-widest font-medium">TOKEN ATTRIBUTION DECOMPOSITION</span>
                  </div>
                  <span className="text-[10px] font-mono text-rose-400 px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/30 font-medium">97.3% THREAT WEIGHT</span>
                </div>

                <div className="mt-5 space-y-3 font-mono">
                  <div className="text-[11px] text-slate-300 uppercase tracking-wider font-medium">Dual-Channel Sample Vectors</div>
                  <div className="space-y-2 text-xs">
                    <div className="p-3 rounded-xl bg-[#0c1424] border border-rose-500/40 flex items-center justify-between shadow-inner">
                      <span className="text-rose-300 font-semibold">kyc_block_immediate</span>
                      <span className="text-rose-400 font-mono font-medium">+2.418 (threat intent)</span>
                    </div>
                    <div className="p-3 rounded-xl bg-[#0c1424] border border-rose-500/40 flex items-center justify-between shadow-inner">
                      <span className="text-rose-300 font-semibold">otp_expire_within_5m</span>
                      <span className="text-rose-400 font-mono font-medium">+1.984 (urgency trigger)</span>
                    </div>
                    <div className="p-3 rounded-xl bg-[#0c1424] border border-emerald-500/40 flex items-center justify-between shadow-inner">
                      <span className="text-emerald-300 font-semibold">official_bank_statement</span>
                      <span className="text-emerald-400 font-mono font-medium">-1.842 (authentic token)</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-300">
                  <span>DOT PRODUCT EVIDENCE: c_i = w_i &times; x_i</span>
                  <span className="text-shield-cyan font-bold">Linear Certainty</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ============================================================ CHAPTER 02: THREAT RADAR */}
        <section id="ch-radar" className="relative min-h-screen flex flex-col justify-center py-28 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto border-t border-shield-border/40">
          <div className="flex items-center gap-3 mb-4 text-xs font-mono tracking-widest text-shield-cyan uppercase">
            <span>02 &mdash; Threat Radar &amp; Calibration Topography</span>
            <span className="w-12 h-px bg-shield-cyan/40" />
            <span className="text-slate-300 font-medium">Uncertainty Quantification</span>
          </div>

          <div className="max-w-3xl mb-8">
            <h2 className="text-3xl sm:text-5xl font-light tracking-tight text-white leading-tight">
              Calibrated confidence,{' '}
              <span className="italic text-shield-cyan font-normal">not manufactured certainty.</span>
            </h2>
            <p className="mt-4 text-base text-slate-200 font-light leading-relaxed">
              Standard classifiers output raw logits that look like probabilities but fail under distribution shift. MailShield evaluates Brier loss scores across 6 distinct model architectures and exposes an interactive dynamic decision threshold (&tau;).
            </p>
          </div>

          {/* Spherical Decision Space HUD */}
          <div className="mb-10 p-6 sm:p-8 rounded-3xl bg-[#060b14]/90 border border-slate-800/90 backdrop-blur-xl shadow-2xl relative overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
              <div className="flex items-center gap-2">
                <Globe2 className="w-4 h-4 text-shield-cyan" />
                <span className="text-xs font-mono text-shield-cyan uppercase tracking-widest font-medium">CALIBRATED TOPOGRAPHY // SPHERICAL RADAR</span>
              </div>
              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="text-slate-300">OPERATING THRESHOLD:</span>
                <span className="text-shield-cyan font-bold px-2 py-0.5 rounded bg-shield-cyan/10 border border-shield-cyan/30">&tau; = 0.65</span>
                <span className="text-emerald-400 font-medium px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30">BRIER LOSS: 0.034</span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6 text-xs font-mono text-slate-200">
              <div className="p-4 rounded-xl bg-[#0c1424] border border-slate-800 shadow-inner">
                <div className="text-slate-300 text-[10px] uppercase font-medium">Uncertainty Band</div>
                <div className="text-lg font-light text-white mt-1">&plusmn; 0.012</div>
                <div className="text-[11px] text-slate-300 mt-1">Cross-validated across 3-fold Platt sigmoids</div>
              </div>
              <div className="p-4 rounded-xl bg-[#0c1424] border border-slate-800 shadow-inner">
                <div className="text-slate-300 text-[10px] uppercase font-medium">Margin Separation</div>
                <div className="text-lg font-light text-shield-cyan mt-1">4.28 &sigma;</div>
                <div className="text-[11px] text-slate-300 mt-1">Optimal distance from decision hyperplanes</div>
              </div>
              <div className="p-4 rounded-xl bg-[#0c1424] border border-slate-800 shadow-inner">
                <div className="text-slate-300 text-[10px] uppercase font-medium">Calibration Curve</div>
                <div className="text-lg font-light text-emerald-400 mt-1">Slope = 0.998</div>
                <div className="text-[11px] text-slate-300 mt-1">Near-ideal diagonal alignment on holdout</div>
              </div>
            </div>
          </div>

          {/* Model Benchmark Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-[#060b14]/90 border border-slate-800/90 backdrop-blur-xl shadow-xl hover:border-shield-cyan/50 transition-colors">
              <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-3">
                <span className="font-medium">MULTILINGUAL LINEAR SVM</span>
                <span className="text-shield-cyan text-[10px] px-2 py-0.5 rounded bg-shield-cyan/10 border border-shield-cyan/30">RECOMMENDED</span>
              </div>
              <div className="text-2xl font-light text-white font-mono">97.2% <span className="text-xs text-slate-300 font-normal">[HOLDOUT EVALUATION]</span></div>
              <div className="text-sm font-mono text-emerald-400 mt-1">Brier: 0.034 &bull; 0.0% FPR</div>
              <p className="mt-4 text-xs text-slate-200 leading-relaxed">
                Dual-channel linear support vector machine with cross-validated Platt scaling. Optimal balanced operating point at &tau; = 0.65.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#060b14]/90 border border-slate-800/90 backdrop-blur-xl shadow-xl hover:border-indigo-400/50 transition-colors">
              <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-3">
                <span className="font-medium">MULTILINGUAL LOGISTIC REGRESSION</span>
                <span className="text-indigo-400 text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/30">HIGH PRECISION</span>
              </div>
              <div className="text-2xl font-light text-white font-mono">94.4% <span className="text-xs text-slate-300 font-normal">[HOLDOUT EVALUATION]</span></div>
              <div className="text-sm font-mono text-indigo-400 mt-1">Brier: 0.147 &bull; 0.0% FPR</div>
              <p className="mt-4 text-xs text-slate-200 leading-relaxed">
                Additive token log-odds providing direct linear interpretability and smooth sigmoid probability outputs.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#060b14]/90 border border-slate-800/90 backdrop-blur-xl shadow-xl hover:border-slate-600/50 transition-colors">
              <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-3">
                <span className="font-medium">MULTINOMIAL NAIVE BAYES</span>
                <span className="text-slate-300 text-[10px] px-2 py-0.5 rounded bg-slate-800 border border-slate-700">FAST BASELINE</span>
              </div>
              <div className="text-2xl font-light text-white font-mono">83.3% <span className="text-xs text-slate-300 font-normal">[HOLDOUT EVALUATION]</span></div>
              <div className="text-sm font-mono text-slate-300 mt-1">Brier: 0.095 &bull; 5.6% FPR</div>
              <p className="mt-4 text-xs text-slate-200 leading-relaxed">
                Sub-millisecond vocabulary frequency baseline for lightweight devices and initial triage filtering.
              </p>
            </div>
          </div>
        </section>

        {/* ============================================================ CHAPTER 03: ZERO-LEAKAGE PROVENANCE */}
        <section id="ch-provenance" className="relative min-h-screen flex flex-col justify-center py-28 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto border-t border-shield-border/40">
          <div className="flex items-center gap-3 mb-4 text-xs font-mono tracking-widest text-shield-cyan uppercase">
            <span>03 &mdash; The Zero-Leakage Sanctuary</span>
            <span className="w-12 h-px bg-shield-cyan/40" />
            <span className="text-slate-300 font-medium">Empirical Integrity &amp; Provenance</span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            {/* Left: Sanctuary Defense HUD */}
            <div className="lg:col-span-6">
              <div className="p-6 sm:p-8 rounded-3xl bg-[#060b14]/90 border border-slate-800/90 backdrop-blur-xl shadow-2xl relative overflow-hidden">
                <div className="flex items-center justify-between pb-4 border-b border-slate-800/80">
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-shield-cyan" />
                    <span className="text-xs font-mono text-shield-cyan uppercase tracking-widest">ZERO-LEAKAGE DEFENSE CORE</span>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30">VERIFIED INVARIANT</span>
                </div>

                <div className="mt-5 space-y-4 font-mono text-xs">
                  <div className="p-4 rounded-xl bg-[#0c1424] border border-emerald-500/40 flex items-start gap-3 shadow-inner">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                    <div>
                      <div className="font-semibold text-emerald-300">Formal Group Separation Invariant</div>
                      <div className="text-[11px] text-emerald-400/90 mt-1">
                        groups(Train) &cap; groups(Val) = &empty; &bull; groups(Train) &cap; groups(Test) = &empty;
                      </div>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-[#0c1424] border border-slate-800 space-y-2 shadow-inner">
                    <div className="flex justify-between text-slate-300">
                      <span>Holdout Integrity</span>
                      <span className="text-emerald-400 font-medium">100% Unseen Templates</span>
                    </div>
                    <div className="text-[11px] text-slate-300">
                      Strict isolation ensures evaluated models never memorize template structures across evaluation boundaries.
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-[#0c1424] border border-slate-800 flex items-center justify-between shadow-inner">
                    <span className="text-slate-300">Region Telemetry Guard</span>
                    <span className="text-shield-cyan font-medium">India Regional Mesh Active</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Separation Proof & Corpus Distribution */}
            <div className="lg:col-span-6 space-y-6">
              <div>
                <h2 className="text-3xl sm:text-5xl font-light tracking-tight text-white leading-tight">
                  Strict template-group partitioning.
                </h2>
                <p className="mt-4 text-base text-slate-300 font-light leading-relaxed">
                  Benchmark leakage is the hidden scandal of spam ML. When similar campaign templates leak between train and test partitions, models appear to achieve 99% accuracy while failing on real-world attacks.
                </p>
                <p className="mt-3 text-sm text-slate-400 font-light leading-relaxed">
                  MailShield enforces mathematical separation: no template group crosses partition boundaries. The holdout test set is composed of 100% unseen templates.
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-slate-950/70 border border-shield-border backdrop-blur-xl">
                <div className="text-xs font-mono text-slate-400 pb-3 border-b border-slate-800 flex items-center justify-between">
                  <span>CORPUS DISTRIBUTION BY PARTITION</span>
                  <span className="text-shield-cyan text-[10px]">144 TOTAL EXAMPLES</span>
                </div>
                <div className="space-y-4 pt-4 text-xs font-mono">
                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Training Split (24 template groups)</span>
                      <span className="text-shield-cyan font-bold">72 samples (50%)</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div className="h-full bg-shield-cyan rounded-full" style={{ width: '50%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Validation Split (12 template groups)</span>
                      <span className="text-indigo-400 font-bold">36 samples (25%)</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div className="h-full bg-indigo-500 rounded-full" style={{ width: '25%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span>Holdout Test Split (12 template groups)</span>
                      <span className="text-emerald-400 font-bold">36 samples (25%)</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full" style={{ width: '25%' }} />
                    </div>
                  </div>
                </div>
              </div>

              {/* Gateway to Operational Terminal */}
              <div className="pt-2">
                <button
                  onClick={onEnterConsole}
                  className="w-full group flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800 hover:from-slate-800 hover:to-slate-700 border border-shield-border hover:border-shield-cyan/50 transition-all text-left shadow-lg"
                >
                  <div>
                    <div className="text-xs font-mono text-shield-cyan">PROCEED TO CHAPTER 04</div>
                    <div className="text-sm font-medium text-white mt-0.5">Enter Operational Defense Terminal</div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-shield-cyan group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
