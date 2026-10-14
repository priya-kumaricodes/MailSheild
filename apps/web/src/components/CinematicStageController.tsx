import React, { useEffect, useRef } from 'react';

export interface CinematicStageControllerProps {
  activeTab: string;
  heroContainerId?: string;
}

export const CinematicStageController: React.FC<CinematicStageControllerProps> = ({
  activeTab,
  heroContainerId = 'scrolly-hero-container',
}) => {
  const layer0Ref = useRef<HTMLDivElement>(null);
  const img0Ref = useRef<HTMLImageElement>(null);

  const layer1Ref = useRef<HTMLDivElement>(null);
  const img1Ref = useRef<HTMLImageElement>(null);
  const sweepRef = useRef<HTMLDivElement>(null);

  const layer2Ref = useRef<HTMLDivElement>(null);
  const img2Ref = useRef<HTMLImageElement>(null);

  const layer3Ref = useRef<HTMLDivElement>(null);
  const img3Ref = useRef<HTMLImageElement>(null);

  const stateRef = useRef({
    targetProgress: 0,
    currentProgress: 0,
    animating: false,
    reqId: 0,
    reducedMotion: false,
    activeTab: 'dashboard',
  });

  stateRef.current.activeTab = activeTab;

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Check reduced motion preference safely
    if (typeof window.matchMedia === 'function') {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      stateRef.current.reducedMotion = mediaQuery.matches;
      const handleMotionChange = (e: MediaQueryListEvent) => {
        stateRef.current.reducedMotion = e.matches;
        applyCurrentVisuals();
      };
      mediaQuery.addEventListener('change', handleMotionChange);
      return () => {
        mediaQuery.removeEventListener('change', handleMotionChange);
      };
    }
  }, []);

  const applyCurrentVisuals = () => {
    if (stateRef.current.activeTab === 'dashboard') {
      updateScrollVisuals(stateRef.current.currentProgress);
    } else {
      updateTabVisuals(stateRef.current.activeTab);
    }
  };

  const updateTabVisuals = (tab: string) => {
    const reduced = stateRef.current.reducedMotion;

    // Default: dark baseline
    let op0 = 0, op1 = 0, op2 = 0, op3 = 0;

    switch (tab) {
      case 'analyzer':
        op1 = 0.22; // Neural Gateway
        break;
      case 'modellab':
        op2 = 0.22; // Threat Radar & Calibration
        break;
      case 'evaluationlab':
        op3 = 0.20; // Zero-Leakage Sanctuary
        break;
      case 'gmail':
        op0 = 0.24; // Perimeter Shield
        break;
      case 'history':
      case 'settings':
        // Clean tactical dark stage with ambient Three.js grid
        op0 = 0.04;
        break;
      default:
        op0 = 0;
    }

    const layers = [
      { layer: layer0Ref.current, img: img0Ref.current, op: op0, origin: '50% 50%', scale: 1.08, reducedScale: 'none' },
      { layer: layer1Ref.current, img: img1Ref.current, op: op1, origin: '76% 20%', scale: 2.48, reducedScale: 'scale(2.48)' },
      { layer: layer2Ref.current, img: img2Ref.current, op: op2, origin: '25% 61%', scale: 2.70, reducedScale: 'scale(2.70)' },
      { layer: layer3Ref.current, img: img3Ref.current, op: op3, origin: '75% 61%', scale: 2.70, reducedScale: 'scale(2.70)' },
    ];

    layers.forEach(({ layer, img, op, origin, scale, reducedScale }) => {
      if (layer) {
        layer.style.transition = reduced ? 'none' : 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        layer.style.opacity = op.toFixed(4);
        layer.style.visibility = op > 0.001 ? 'visible' : 'hidden';
      }
      if (img) {
        img.style.transformOrigin = origin;
        img.style.transition = reduced ? 'none' : 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        img.style.transform = reduced ? reducedScale : `scale(${scale.toFixed(4)})`;
      }
    });

    if (sweepRef.current) {
      sweepRef.current.style.display = 'none';
    }
  };

  const updateScrollVisuals = (p: number) => {
    const reduced = stateRef.current.reducedMotion;

    // Reset transition styles for instant RAF tracking
    const imgs = [img0Ref.current, img1Ref.current, img2Ref.current, img3Ref.current];
    imgs.forEach((img) => {
      if (img) img.style.transition = 'none';
    });
    const layers = [layer0Ref.current, layer1Ref.current, layer2Ref.current, layer3Ref.current];
    layers.forEach((l) => {
      if (l) l.style.transition = 'opacity 0.15s linear';
    });

    // -------------------------------------------------------------------------
    // Chapter 00: The Perimeter Threshold (Active: 0.00 -> 0.28)
    // Continuous scale(1.15) -> scale(1.03), translateY: 0px -> -60px
    let op0 = 0;
    let sc0 = 1.0;
    let ty0 = 0;
    let tx0 = 0;

    if (p <= 0.20) {
      op0 = 1.0;
    } else if (p < 0.28) {
      const t = (p - 0.20) / 0.08;
      op0 = 1.0 - t;
    } else {
      op0 = 0;
    }

    if (!reduced) {
      const t0 = Math.min(1, p / 0.25);
      sc0 = 1.15 - t0 * 0.12; // 1.15 down to 1.03
      ty0 = -t0 * 60; // 0px to -60px upward pan
      tx0 = Math.sin(t0 * Math.PI) * 15; // Lateral camera drift
    }

    if (layer0Ref.current) {
      layer0Ref.current.style.opacity = op0.toFixed(4);
      layer0Ref.current.style.visibility = op0 > 0.001 ? 'visible' : 'hidden';
    }
    if (img0Ref.current) {
      img0Ref.current.style.transformOrigin = '50% 50%';
      img0Ref.current.style.transform = reduced
        ? 'none'
        : `scale(${sc0.toFixed(4)}) translate(${tx0.toFixed(2)}px, ${ty0.toFixed(2)}px)`;
    }

    // -------------------------------------------------------------------------
    // Chapter 01: The Neural Gateway (Active: 0.18 -> 0.54)
    // Precision quadrant framing (Top-Right): scale(2.54) -> scale(2.42)
    let op1 = 0;
    let sc1 = 2.48;
    let tx1 = 0;
    let ty1 = 0;

    if (p < 0.18) {
      op1 = 0;
    } else if (p < 0.26) {
      const t = (p - 0.18) / 0.08;
      op1 = t;
    } else if (p <= 0.44) {
      op1 = 1.0;
    } else if (p < 0.54) {
      const t = (p - 0.44) / 0.10;
      op1 = 1.0 - t;
    } else {
      op1 = 0;
    }

    if (!reduced) {
      const s1 = Math.max(0, Math.min(1, (p - 0.18) / 0.36));
      sc1 = 2.54 - s1 * 0.12; // 2.54 down to 2.42
      tx1 = (0.5 - s1) * 20; // Subtle tracking drift across neural lattice
      ty1 = (s1 - 0.5) * 10;
    }

    if (layer1Ref.current) {
      layer1Ref.current.style.opacity = op1.toFixed(4);
      layer1Ref.current.style.visibility = op1 > 0.001 ? 'visible' : 'hidden';
    }
    if (img1Ref.current) {
      img1Ref.current.style.transformOrigin = '76% 20%';
      img1Ref.current.style.transform = reduced
        ? 'scale(2.48)'
        : `scale(${sc1.toFixed(4)}) translate(${tx1.toFixed(2)}px, ${ty1.toFixed(2)}px)`;
    }
    if (sweepRef.current) {
      const sweepActive = !reduced && p >= 0.20 && p <= 0.48;
      sweepRef.current.style.display = sweepActive ? 'block' : 'none';
    }

    // -------------------------------------------------------------------------
    // Chapter 02: Threat Radar & Calibration Topography (Active: 0.44 -> 0.78)
    // Precision quadrant framing (Bottom-Left): push-in scale(2.66) -> scale(2.78)
    let op2 = 0;
    let sc2 = 2.70;
    let tx2 = 0;
    let ty2 = 0;

    if (p < 0.44) {
      op2 = 0;
    } else if (p < 0.52) {
      const t = (p - 0.44) / 0.08;
      op2 = t;
    } else if (p <= 0.68) {
      op2 = 1.0;
    } else if (p < 0.78) {
      const t = (p - 0.68) / 0.10;
      op2 = 1.0 - t;
    } else {
      op2 = 0;
    }

    if (!reduced) {
      const s2 = Math.max(0, Math.min(1, (p - 0.44) / 0.34));
      sc2 = 2.66 + s2 * 0.12; // 2.66 up to 2.78 (push in)
      ty2 = (0.5 - s2) * 10;
      tx2 = Math.sin(s2 * Math.PI) * 10;
    }

    if (layer2Ref.current) {
      layer2Ref.current.style.opacity = op2.toFixed(4);
      layer2Ref.current.style.visibility = op2 > 0.001 ? 'visible' : 'hidden';
    }
    if (img2Ref.current) {
      img2Ref.current.style.transformOrigin = '25% 61%';
      img2Ref.current.style.transform = reduced
        ? 'scale(2.70)'
        : `scale(${sc2.toFixed(4)}) translate(${tx2.toFixed(2)}px, ${ty2.toFixed(2)}px)`;
    }

    // -------------------------------------------------------------------------
    // Chapter 03: Zero-Leakage Sanctuary Defense Core (Active: 0.68 -> 1.00)
    // Precision quadrant framing (Bottom-Right): scale(2.78) -> scale(2.66)
    let op3 = 0;
    let sc3 = 2.70;
    let ty3 = 0;

    if (p < 0.68) {
      op3 = 0;
    } else if (p < 0.76) {
      const t = (p - 0.68) / 0.08;
      op3 = t;
    } else if (p <= 0.88) {
      op3 = 1.0;
    } else {
      // Approaching Chapter 04 (defense terminal): fade background to dark tactical stage
      const t = Math.min(1, (p - 0.88) / 0.12);
      op3 = 1.0 - t * 0.88; // Drops to ~0.12
    }

    if (!reduced) {
      const s3 = Math.max(0, Math.min(1, (p - 0.68) / 0.32));
      sc3 = 2.78 - s3 * 0.12; // 2.78 down to 2.66
      ty3 = (0.5 - s3) * 10;
    }

    if (layer3Ref.current) {
      layer3Ref.current.style.opacity = op3.toFixed(4);
      layer3Ref.current.style.visibility = op3 > 0.001 ? 'visible' : 'hidden';
    }
    if (img3Ref.current) {
      img3Ref.current.style.transformOrigin = '75% 61%';
      img3Ref.current.style.transform = reduced
        ? 'scale(2.70)'
        : `scale(${sc3.toFixed(4)}) translateY(${ty3.toFixed(2)}px)`;
    }
  };

  // Scroll tracking and animation loop
  useEffect(() => {
    if (typeof window === 'undefined') return;

    if (activeTab !== 'dashboard') {
      updateTabVisuals(activeTab);
      return;
    }

    const computeTargetProgress = () => {
      const hero = document.getElementById(heroContainerId);
      if (!hero) {
        const scrollY = window.scrollY || window.pageYOffset || 0;
        const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
        return Math.max(0, Math.min(1, scrollY / maxScroll));
      }
      const rect = hero.getBoundingClientRect();
      const totalScrollable = rect.height - window.innerHeight;
      if (totalScrollable <= 0) return 0;
      const current = -rect.top;
      return Math.max(0, Math.min(1, current / totalScrollable));
    };

    const step = () => {
      if (stateRef.current.activeTab !== 'dashboard') {
        stateRef.current.animating = false;
        return;
      }
      const st = stateRef.current;
      const diff = st.targetProgress - st.currentProgress;

      if (Math.abs(diff) < 0.0003) {
        st.currentProgress = st.targetProgress;
        updateScrollVisuals(st.currentProgress);
        window.dispatchEvent(
          new CustomEvent('mailshield:scroll', {
            detail: { progress: st.currentProgress },
          })
        );
        st.animating = false;
        return;
      }

      st.currentProgress += diff * 0.14; // Responsive smooth lerp
      updateScrollVisuals(st.currentProgress);
      window.dispatchEvent(
        new CustomEvent('mailshield:scroll', {
          detail: { progress: st.currentProgress },
        })
      );
      st.reqId = requestAnimationFrame(step);
    };

    const wakeAnimation = () => {
      if (stateRef.current.activeTab !== 'dashboard') return;
      const target = computeTargetProgress();
      stateRef.current.targetProgress = target;
      if (!stateRef.current.animating) {
        stateRef.current.animating = true;
        stateRef.current.reqId = requestAnimationFrame(step);
      }
    };

    const initialTarget = computeTargetProgress();
    stateRef.current.targetProgress = initialTarget;
    stateRef.current.currentProgress = initialTarget;
    updateScrollVisuals(initialTarget);
    window.dispatchEvent(
      new CustomEvent('mailshield:scroll', {
        detail: { progress: initialTarget },
      })
    );

    window.addEventListener('scroll', wakeAnimation, { passive: true });
    window.addEventListener('resize', wakeAnimation, { passive: true });

    return () => {
      window.removeEventListener('scroll', wakeAnimation);
      window.removeEventListener('resize', wakeAnimation);
      if (stateRef.current.reqId) {
        cancelAnimationFrame(stateRef.current.reqId);
      }
    };
  }, [activeTab, heroContainerId]);

  return (
    <div
      className="fixed inset-0 w-full h-full overflow-hidden pointer-events-none z-0"
      aria-hidden="true"
    >
      {/* ============================================================ CHAPTER 00 IMAGE STAGE */}
      <div
        ref={layer0Ref}
        className="absolute inset-0 w-full h-full will-change-[opacity,transform]"
      >
        <img
          ref={img0Ref}
          src="/cinematic/hero-perimeter-shield.jpg"
          alt=""
          width="1920"
          height="1080"
          loading="eager"
          decoding="async"
          style={{ transformOrigin: '50% 50%' }}
          className="w-full h-full object-cover object-center will-change-transform"
        />
        {/* Editorial Readability Gradient & Atmospheric Vignette */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#04070c]/90 via-[#04070c]/70 to-[#04070c]/55" />
        <div className="absolute inset-0 bg-radial-vignette opacity-70" />
        <div className="cinematic-scanline opacity-30" />
      </div>

      {/* ============================================================ CHAPTER 01 IMAGE STAGE */}
      <div
        ref={layer1Ref}
        className="absolute inset-0 w-full h-full will-change-[opacity,transform]"
        style={{ opacity: 0 }}
      >
        <img
          ref={img1Ref}
          src="/cinematic/neural-token-analysis.jpg"
          alt=""
          width="1920"
          height="1080"
          loading="lazy"
          decoding="async"
          style={{ transformOrigin: '76% 20%' }}
          className="w-full h-full object-cover object-center will-change-transform"
        />
        {/* Editorial Readability Gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#04070c]/92 via-[#04070c]/75 to-[#04070c]/50" />
        <div className="absolute inset-0 bg-radial-vignette opacity-75" />
        <div className="cinematic-scanline opacity-35" />
        {/* Laser Sweep across Chapter 01 reveal */}
        <div ref={sweepRef} className="cinematic-laser-sweep" style={{ display: 'none' }} />
      </div>

      {/* ============================================================ CHAPTER 02 IMAGE STAGE */}
      <div
        ref={layer2Ref}
        className="absolute inset-0 w-full h-full will-change-[opacity,transform]"
        style={{ opacity: 0 }}
      >
        <img
          ref={img2Ref}
          src="/cinematic/threat-calibration-radar.jpg"
          alt=""
          width="1920"
          height="1080"
          loading="lazy"
          decoding="async"
          style={{ transformOrigin: '25% 61%' }}
          className="w-full h-full object-cover object-center will-change-transform"
        />
        {/* Central Topography Darkening & Editorial Gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#04070c]/85 via-[#04070c]/65 to-[#04070c]/90" />
        <div className="absolute inset-0 bg-radial-vignette opacity-80" />
        <div className="cinematic-scanline opacity-30" />
      </div>

      {/* ============================================================ CHAPTER 03 IMAGE STAGE */}
      <div
        ref={layer3Ref}
        className="absolute inset-0 w-full h-full will-change-[opacity,transform]"
        style={{ opacity: 0 }}
      >
        <img
          ref={img3Ref}
          src="/cinematic/sanctuary-defense-core.jpg"
          alt=""
          width="1920"
          height="1080"
          loading="lazy"
          decoding="async"
          style={{ transformOrigin: '75% 61%' }}
          className="w-full h-full object-cover object-center will-change-transform"
        />
        {/* Zero-Leakage Sanctuary Atmosphere */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#04070c]/90 via-[#04070c]/70 to-[#04070c]/60" />
        <div className="absolute inset-0 bg-radial-vignette opacity-80" />
        <div className="cinematic-scanline opacity-30" />
      </div>
    </div>
  );
};
