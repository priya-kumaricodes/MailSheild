import React, { useEffect, useRef } from 'react';

interface CinematicBackgroundStageProps {
  containerRef: React.RefObject<HTMLDivElement | null>;
}

export const CinematicBackgroundStage: React.FC<CinematicBackgroundStageProps> = ({ containerRef }) => {
  // DOM element refs for GPU-accelerated direct style updates (zero React re-renders during scroll)
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
  });

  useEffect(() => {
    // Check reduced motion preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    stateRef.current.reducedMotion = mediaQuery.matches;
    const handleMotionChange = (e: MediaQueryListEvent) => {
      stateRef.current.reducedMotion = e.matches;
      updateVisuals(stateRef.current.currentProgress);
    };
    mediaQuery.addEventListener('change', handleMotionChange);

    const computeTargetProgress = () => {
      const container = containerRef.current;
      if (!container) return 0;
      const rect = container.getBoundingClientRect();
      const totalScrollable = rect.height - window.innerHeight;
      if (totalScrollable <= 0) return 0;
      const current = -rect.top;
      return Math.max(0, Math.min(1, current / totalScrollable));
    };

    const updateVisuals = (p: number) => {
      const reduced = stateRef.current.reducedMotion;

      // -------------------------------------------------------------
      // 1. Chapter 00: The Perimeter Threshold
      // Active: 0.00 -> 0.28
      let op0 = 0;
      let sc0 = 1.0;
      let ty0 = 0;

      if (p <= 0.20) {
        op0 = 1.0;
      } else if (p < 0.28) {
        const t = (p - 0.20) / 0.08;
        op0 = 1.0 - t;
      } else {
        op0 = 0;
      }

      if (!reduced) {
        // Starts at scale(1.12), smoothly moves toward scale(1.00)
        const t0 = Math.min(1, p / 0.25);
        sc0 = 1.12 - t0 * 0.12;
        ty0 = -t0 * 24; // Subtle upward camera drift
      }

      if (layer0Ref.current) {
        layer0Ref.current.style.opacity = op0.toFixed(4);
        layer0Ref.current.style.visibility = op0 > 0.001 ? 'visible' : 'hidden';
      }
      if (img0Ref.current) {
        img0Ref.current.style.transform = reduced
          ? 'none'
          : `scale(${sc0.toFixed(4)}) translateY(${ty0.toFixed(2)}px)`;
      }

      // -------------------------------------------------------------
      // 2. Chapter 01: The Neural Gateway
      // Active: 0.18 -> 0.54
      let op1 = 0;
      let sc1 = 1.0;
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
        // Starts at scale(1.10), moves toward scale(1.02)
        const s1 = Math.max(0, Math.min(1, (p - 0.18) / 0.36));
        sc1 = 1.10 - s1 * 0.08;
        tx1 = (1 - s1 * 2) * 14; // Horizontal camera pan across token scene (+14px -> -14px)
        ty1 = (s1 - 0.5) * 18;
      }

      if (layer1Ref.current) {
        layer1Ref.current.style.opacity = op1.toFixed(4);
        layer1Ref.current.style.visibility = op1 > 0.001 ? 'visible' : 'hidden';
      }
      if (img1Ref.current) {
        img1Ref.current.style.transform = reduced
          ? 'none'
          : `scale(${sc1.toFixed(4)}) translate(${tx1.toFixed(2)}px, ${ty1.toFixed(2)}px)`;
      }
      if (sweepRef.current) {
        // Laser sweep only visible during Chapter 01 reveal zone (0.20 - 0.46)
        const sweepActive = !reduced && p >= 0.20 && p <= 0.48;
        sweepRef.current.style.display = sweepActive ? 'block' : 'none';
      }

      // -------------------------------------------------------------
      // 3. Chapter 02: Threat Radar & Calibration Topography
      // Active: 0.44 -> 0.78
      let op2 = 0;
      let sc2 = 1.0;
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
        // Restrained push-in: scale(1.02) -> scale(1.08)
        const s2 = Math.max(0, Math.min(1, (p - 0.44) / 0.34));
        sc2 = 1.02 + s2 * 0.06;
        ty2 = (1 - s2) * 16 - 8;
      }

      if (layer2Ref.current) {
        layer2Ref.current.style.opacity = op2.toFixed(4);
        layer2Ref.current.style.visibility = op2 > 0.001 ? 'visible' : 'hidden';
      }
      if (img2Ref.current) {
        img2Ref.current.style.transform = reduced
          ? 'none'
          : `scale(${sc2.toFixed(4)}) translateY(${ty2.toFixed(2)}px)`;
      }

      // -------------------------------------------------------------
      // 4. Chapter 03: Zero-Leakage Sanctuary Defense Core
      // Active: 0.68 -> 1.00
      let op3 = 0;
      let sc3 = 1.0;
      let ty3 = 0;

      if (p < 0.68) {
        op3 = 0;
      } else if (p < 0.76) {
        const t = (p - 0.68) / 0.08;
        op3 = t;
      } else if (p <= 0.88) {
        op3 = 1.0;
      } else {
        // Approaching Chapter 04: fade background atmosphere to dark tactical stage
        const t = Math.min(1, (p - 0.88) / 0.12);
        op3 = 1.0 - t * 0.85; // Gently drops down to ~0.15
      }

      if (!reduced) {
        // Controlled zoom reduction: scale(1.06) -> scale(1.00)
        const s3 = Math.max(0, Math.min(1, (p - 0.68) / 0.32));
        sc3 = 1.06 - s3 * 0.06;
        ty3 = (1 - s3) * 14;
      }

      if (layer3Ref.current) {
        layer3Ref.current.style.opacity = op3.toFixed(4);
        layer3Ref.current.style.visibility = op3 > 0.001 ? 'visible' : 'hidden';
      }
      if (img3Ref.current) {
        img3Ref.current.style.transform = reduced
          ? 'none'
          : `scale(${sc3.toFixed(4)}) translateY(${ty3.toFixed(2)}px)`;
      }
    };

    // Animation loop using lerp for silky smooth 60fps tracking without jitter
    const step = () => {
      const st = stateRef.current;
      const diff = st.targetProgress - st.currentProgress;

      if (Math.abs(diff) < 0.0004) {
        st.currentProgress = st.targetProgress;
        updateVisuals(st.currentProgress);
        st.animating = false;
        return; // Pause loop when stationary - no permanent idle loop
      }

      st.currentProgress += diff * 0.14; // Responsive smooth lerp
      updateVisuals(st.currentProgress);
      st.reqId = requestAnimationFrame(step);
    };

    const wakeAnimation = () => {
      const target = computeTargetProgress();
      stateRef.current.targetProgress = target;
      if (!stateRef.current.animating) {
        stateRef.current.animating = true;
        stateRef.current.reqId = requestAnimationFrame(step);
      }
    };

    // Initialize immediate state
    const initialTarget = computeTargetProgress();
    stateRef.current.targetProgress = initialTarget;
    stateRef.current.currentProgress = initialTarget;
    updateVisuals(initialTarget);

    window.addEventListener('scroll', wakeAnimation, { passive: true });
    window.addEventListener('resize', wakeAnimation, { passive: true });

    return () => {
      mediaQuery.removeEventListener('change', handleMotionChange);
      window.removeEventListener('scroll', wakeAnimation);
      window.removeEventListener('resize', wakeAnimation);
      if (stateRef.current.reqId) {
        cancelAnimationFrame(stateRef.current.reqId);
      }
    };
  }, [containerRef]);

  return (
    <div
      className="sticky top-0 left-0 w-full h-screen overflow-hidden pointer-events-none z-0"
      aria-hidden="true"
    >
      {/* ============================================================ CHAPTER 00 IMAGE STAGE */}
      <div
        ref={layer0Ref}
        className="absolute inset-0 w-full h-full will-change-[opacity,transform] transition-opacity duration-150"
      >
        <img
          ref={img0Ref}
          src="/cinematic/hero-perimeter-shield.jpg"
          alt=""
          width="1920"
          height="1080"
          loading="eager"
          decoding="async"
          className="w-full h-full object-cover object-[center_35%] will-change-transform"
        />
        {/* Editorial Readability Gradient & Atmospheric Vignette */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#04070c]/90 via-[#04070c]/70 to-[#04070c]/55" />
        <div className="absolute inset-0 bg-radial-vignette opacity-70" />
        <div className="cinematic-scanline opacity-30" />
      </div>

      {/* ============================================================ CHAPTER 01 IMAGE STAGE */}
      <div
        ref={layer1Ref}
        className="absolute inset-0 w-full h-full will-change-[opacity,transform] transition-opacity duration-150"
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
          className="w-full h-full object-cover object-[center_40%] will-change-transform"
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
        className="absolute inset-0 w-full h-full will-change-[opacity,transform] transition-opacity duration-150"
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
          className="w-full h-full object-cover object-[center_45%] will-change-transform"
        />
        {/* Central Topography Darkening & Editorial Gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#04070c]/85 via-[#04070c]/65 to-[#04070c]/90" />
        <div className="absolute inset-0 bg-radial-vignette opacity-80" />
        <div className="cinematic-scanline opacity-30" />
      </div>

      {/* ============================================================ CHAPTER 03 IMAGE STAGE */}
      <div
        ref={layer3Ref}
        className="absolute inset-0 w-full h-full will-change-[opacity,transform] transition-opacity duration-150"
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
          className="w-full h-full object-cover object-[center_40%] will-change-transform"
        />
        {/* Zero-Leakage Sanctuary Atmosphere */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#04070c]/90 via-[#04070c]/70 to-[#04070c]/60" />
        <div className="absolute inset-0 bg-radial-vignette opacity-80" />
        <div className="cinematic-scanline opacity-30" />
      </div>
    </div>
  );
};
