import React, { useEffect, useState, useRef } from 'react';

export interface CinematicViewTransitionProps {
  activeKey: string;
  children: React.ReactNode;
  className?: string;
}

export const CinematicViewTransition: React.FC<CinematicViewTransitionProps> = ({
  activeKey,
  children,
  className = '',
}) => {
  const [displayedKey, setDisplayedKey] = useState(activeKey);
  const [animState, setAnimState] = useState<'entering' | 'active'>('active');
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    if (activeKey !== displayedKey) {
      if (timerRef.current) {
        window.clearTimeout(timerRef.current);
      }
      setDisplayedKey(activeKey);
      setAnimState('entering');

      // Check reduced motion safely
      const reducedMotion =
        typeof window !== 'undefined' &&
        typeof window.matchMedia === 'function' &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      if (reducedMotion) {
        setAnimState('active');
      } else {
        timerRef.current = window.setTimeout(() => {
          setAnimState('active');
        }, 360);
      }
    }

    return () => {
      if (timerRef.current) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, [activeKey, displayedKey]);

  return (
    <div
      key={displayedKey}
      data-cinematic-state={animState}
      className={`cinematic-view-transition ${animState === 'entering' ? 'cinematic-view-enter' : 'cinematic-view-active'} ${className}`}
    >
      {children}
    </div>
  );
};
