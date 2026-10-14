import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export type ThreatVisualState = 'idle' | 'analyzing' | 'threat_detected' | 'clean_verified';

interface CyberShieldCanvasProps {
  scrollProgress?: number;
  visualState?: ThreatVisualState;
  activeTab?: string;
}

export const CyberShieldCanvas: React.FC<CyberShieldCanvasProps> = ({
  scrollProgress = 0,
  visualState = 'idle',
  activeTab = 'dashboard',
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const stateRef = useRef<{
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    renderer: THREE.WebGLRenderer;
    particles: THREE.Points;
    grid: THREE.LineSegments;
    ambientLight: THREE.AmbientLight;
    envLight: THREE.PointLight;
    rimLight: THREE.DirectionalLight;
    redRimLight: THREE.DirectionalLight;
    targetCamPos: THREE.Vector3;
    targetLookAt: THREE.Vector3;
    currentLookAt: THREE.Vector3;
    mouseX: number;
    mouseY: number;
    animState: ThreatVisualState;
  } | null>(null);

  // Sync visualState prop with ref
  useEffect(() => {
    if (stateRef.current) {
      stateRef.current.animState = visualState;
    }
  }, [visualState]);

  const updateCameraTrajectory = (progress: number) => {
    if (!stateRef.current) return;
    const p = Math.max(0, Math.min(1, progress));

    // Define 5-chapter cinematic camera spline
    // Chapter 0 (0.00 - 0.25): Perimeter Threshold (Wide dramatic establishing angle)
    // Chapter 1 (0.25 - 0.55): Neural Gateway (Descend into defense lattice)
    // Chapter 2 (0.55 - 0.78): Threat Topography (Dynamic side inspection angle)
    // Chapter 3 (0.78 - 0.90): Zero-Leakage Sanctuary (Overhead elevated perspective)
    // Chapter 4 (0.90 - 1.00): Operational Console (Docked command view)
    let camX = 0, camY = 3.2, camZ = 13.5;
    let lookX = 0, lookY = 1.0, lookZ = 0;

    if (p < 0.25) {
      const t = p / 0.25;
      camX = THREE.MathUtils.lerp(0, 2.8, t);
      camY = THREE.MathUtils.lerp(3.2, 1.8, t);
      camZ = THREE.MathUtils.lerp(13.5, 9.2, t);
      lookX = THREE.MathUtils.lerp(0, -0.8, t);
      lookY = THREE.MathUtils.lerp(1.0, 0.9, t);
      lookZ = 0;
    } else if (p < 0.55) {
      const t = (p - 0.25) / 0.3;
      camX = THREE.MathUtils.lerp(2.8, -3.2, t);
      camY = THREE.MathUtils.lerp(1.8, 2.4, t);
      camZ = THREE.MathUtils.lerp(9.2, 7.5, t);
      lookX = THREE.MathUtils.lerp(-0.8, 0.6, t);
      lookY = THREE.MathUtils.lerp(0.9, 0.8, t);
      lookZ = 0;
    } else if (p < 0.82) {
      const t = (p - 0.55) / 0.27;
      camX = THREE.MathUtils.lerp(-3.2, 0, t);
      camY = THREE.MathUtils.lerp(2.4, 4.6, t);
      camZ = THREE.MathUtils.lerp(7.5, 5.2, t);
      lookX = THREE.MathUtils.lerp(0.6, 0, t);
      lookY = THREE.MathUtils.lerp(0.8, 0.2, t);
      lookZ = THREE.MathUtils.lerp(0, -1.5, t);
    } else {
      const t = (p - 0.82) / 0.18;
      camX = THREE.MathUtils.lerp(0, 0, t);
      camY = THREE.MathUtils.lerp(4.6, 1.2, t);
      camZ = THREE.MathUtils.lerp(5.2, 4.4, t);
      lookX = 0;
      lookY = THREE.MathUtils.lerp(0.2, 0.6, t);
      lookZ = 0;
    }

    stateRef.current.targetCamPos.set(camX, camY, camZ);
    stateRef.current.targetLookAt.set(lookX, lookY, lookZ);
  };

  // Sync camera trajectory with activeTab and authoritative scroll events
  useEffect(() => {
    if (!stateRef.current) return;

    if (activeTab && activeTab !== 'dashboard') {
      switch (activeTab) {
        case 'analyzer':
          stateRef.current.targetCamPos.set(0, 5.0, 9.0);
          stateRef.current.targetLookAt.set(0, 0.5, 0);
          break;
        case 'modellab':
          stateRef.current.targetCamPos.set(4.2, 3.2, 9.5);
          stateRef.current.targetLookAt.set(-0.5, 0.8, 0);
          break;
        case 'evaluationlab':
          stateRef.current.targetCamPos.set(-3.5, 4.5, 7.5);
          stateRef.current.targetLookAt.set(0, 0.2, -1.0);
          break;
        case 'gmail':
          stateRef.current.targetCamPos.set(1.5, 2.8, 10.5);
          stateRef.current.targetLookAt.set(0, 0.9, 0);
          break;
        case 'history':
        case 'settings':
        default:
          stateRef.current.targetCamPos.set(0, 4.2, 12.0);
          stateRef.current.targetLookAt.set(0, 0.5, 0);
          break;
      }
      return;
    }

    // Default or scrollProgress prop fallback
    updateCameraTrajectory(scrollProgress);

    const onAuthoritativeScroll = (e: any) => {
      const p = e.detail?.progress ?? 0;
      updateCameraTrajectory(p);
    };

    window.addEventListener('mailshield:scroll', onAuthoritativeScroll);
    return () => {
      window.removeEventListener('mailshield:scroll', onAuthoritativeScroll);
    };
  }, [scrollProgress, activeTab]);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // 1. Scene
    const scene = new THREE.Scene();

    // 2. Camera
    const width = window.innerWidth;
    const height = window.innerHeight;
    const camera = new THREE.PerspectiveCamera(46, width / height, 0.1, 100);
    camera.position.set(0, 3.2, 13.5);

    // 3. WebGL Renderer with full transparency & error safety
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({
        powerPreference: 'high-performance',
        antialias: true,
        alpha: true,
      });
    } catch {
      // Graceful fallback if WebGL is unavailable in environment
      return;
    }
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    container.appendChild(renderer.domElement);

    // 4. Lighting
    const ambientLight = new THREE.AmbientLight(0x0a1424, 1.4);
    scene.add(ambientLight);

    const rimLight = new THREE.DirectionalLight(0x00f0ff, 2.2);
    rimLight.position.set(5, 8, 4);
    scene.add(rimLight);

    const redRimLight = new THREE.DirectionalLight(0xe0231c, 1.2);
    redRimLight.position.set(-6, -2, -4);
    scene.add(redRimLight);

    const envLight = new THREE.PointLight(0x00f0ff, 1.2, 25, 2.0);
    envLight.position.set(0, 2.0, 0);
    scene.add(envLight);

    // 5. Procedural Cyber Perimeter Grid (Perspective Lattice Floor)
    const gridSize = 60;
    const gridDivisions = 48;
    const gridHelper = new THREE.GridHelper(gridSize, gridDivisions, 0x00f0ff, 0x0b2545);
    gridHelper.position.y = -2.2;
    if (gridHelper.material instanceof THREE.LineBasicMaterial) {
      gridHelper.material.transparent = true;
      gridHelper.material.opacity = 0.35;
      gridHelper.material.blending = THREE.AdditiveBlending;
    }
    scene.add(gridHelper);

    // 8. Cryptographic Particle Dust (Floating Neural Packets)
    const particleCount = 1200;
    const particleCoords = new Float32Array(particleCount * 3);
    const particleColors = new Float32Array(particleCount * 3);

    const baseCyan = new THREE.Color(0x00f0ff);
    const accentIndigo = new THREE.Color(0x6366f1);
    const threatRose = new THREE.Color(0xe0231c);

    for (let i = 0; i < particleCount; i++) {
      particleCoords[i * 3 + 0] = (Math.random() - 0.5) * 36;
      particleCoords[i * 3 + 1] = (Math.random() - 0.2) * 20;
      particleCoords[i * 3 + 2] = (Math.random() - 0.5) * 36;

      const mix = Math.random();
      const col = mix < 0.7 ? baseCyan.clone().lerp(accentIndigo, Math.random()) : threatRose;
      particleColors[i * 3 + 0] = col.r;
      particleColors[i * 3 + 1] = col.g;
      particleColors[i * 3 + 2] = col.b;
    }

    const particleGeom = new THREE.BufferGeometry();
    particleGeom.setAttribute('position', new THREE.BufferAttribute(particleCoords, 3));
    particleGeom.setAttribute('color', new THREE.BufferAttribute(particleColors, 3));

    const particleMat = new THREE.PointsMaterial({
      size: 0.075,
      vertexColors: true,
      transparent: true,
      opacity: 0.65,
      blending: THREE.AdditiveBlending,
    });
    const particles = new THREE.Points(particleGeom, particleMat);
    scene.add(particles);

    // Keep state
    stateRef.current = {
      scene,
      camera,
      renderer,
      particles,
      grid: gridHelper,
      ambientLight,
      envLight,
      rimLight,
      redRimLight,
      targetCamPos: new THREE.Vector3(0, 3.2, 13.5),
      targetLookAt: new THREE.Vector3(0, 1.0, 0),
      currentLookAt: new THREE.Vector3(0, 1.0, 0),
      mouseX: 0,
      mouseY: 0,
      animState: visualState,
    };

    // Mouse parallax listener
    const handlePointerMove = (e: MouseEvent) => {
      const halfW = window.innerWidth / 2;
      const halfH = window.innerHeight / 2;
      if (stateRef.current) {
        stateRef.current.mouseX = (e.clientX - halfW) / halfW;
        stateRef.current.mouseY = (e.clientY - halfH) / halfH;
      }
    };
    window.addEventListener('pointermove', handlePointerMove, { passive: true });

    // Window resize listener
    const handleResize = () => {
      if (!stateRef.current) return;
      const w = window.innerWidth;
      const h = window.innerHeight;
      stateRef.current.camera.aspect = w / h;
      stateRef.current.camera.updateProjectionMatrix();
      stateRef.current.renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    // Global custom event listeners for real-time analysis animation
    const onAnalyzing = () => {
      if (stateRef.current) stateRef.current.animState = 'analyzing';
    };
    const onResult = (e: any) => {
      if (stateRef.current) {
        const isSpam = e.detail?.isSpam;
        stateRef.current.animState = isSpam ? 'threat_detected' : 'clean_verified';
      }
    };
    const onIdle = () => {
      if (stateRef.current) stateRef.current.animState = 'idle';
    };

    window.addEventListener('mailshield:analyzing', onAnalyzing);
    window.addEventListener('mailshield:result', onResult);
    window.addEventListener('mailshield:idle', onIdle);

    // Animation Loop
    let reqId = 0;
    const clock = new THREE.Clock();

    const animate = () => {
      reqId = requestAnimationFrame(animate);
      const st = stateRef.current;
      if (!st) return;

      const dt = clock.getDelta();
      const elapsed = clock.getElapsedTime();

      // Parallax mouse offsets
      const mouseOffsetCamX = st.mouseX * 0.75;
      const mouseOffsetCamY = -st.mouseY * 0.45;

      // Smooth camera position damping
      st.camera.position.x = THREE.MathUtils.damp(
        st.camera.position.x,
        st.targetCamPos.x + mouseOffsetCamX,
        2.5,
        dt
      );
      st.camera.position.y = THREE.MathUtils.damp(
        st.camera.position.y,
        st.targetCamPos.y + mouseOffsetCamY,
        2.5,
        dt
      );
      st.camera.position.z = THREE.MathUtils.damp(
        st.camera.position.z,
        st.targetCamPos.z,
        2.5,
        dt
      );

      // Smooth lookAt damping
      st.currentLookAt.x = THREE.MathUtils.damp(st.currentLookAt.x, st.targetLookAt.x, 3.0, dt);
      st.currentLookAt.y = THREE.MathUtils.damp(st.currentLookAt.y, st.targetLookAt.y, 3.0, dt);
      st.currentLookAt.z = THREE.MathUtils.damp(st.currentLookAt.z, st.targetLookAt.z, 3.0, dt);
      st.camera.lookAt(st.currentLookAt);

      // Dynamic ambient lighting based on threat visual state
      let targetEnvColor = new THREE.Color(0x00f0ff);
      let targetIntensity = 1.2;

      if (st.animState === 'analyzing') {
        const pulse = Math.sin(elapsed * 12) * 0.5 + 0.5;
        targetEnvColor = new THREE.Color(0x00f0ff).lerp(new THREE.Color(0xffffff), pulse);
        targetIntensity = 2.4;
      } else if (st.animState === 'threat_detected') {
        targetEnvColor = new THREE.Color(0xe0231c);
        targetIntensity = 2.0;
      } else if (st.animState === 'clean_verified') {
        targetEnvColor = new THREE.Color(0x10b981);
        targetIntensity = 1.8;
      } else {
        // Idle breathing
        const breath = Math.sin(elapsed * 1.5) * 0.5 + 0.5;
        targetIntensity = 1.0 + breath * 0.3;
      }

      st.envLight.color.lerp(targetEnvColor, 0.08);
      st.envLight.intensity = THREE.MathUtils.lerp(st.envLight.intensity, targetIntensity, 0.08);

      // Slowly float particles
      const posAttr = st.particles.geometry.getAttribute('position') as THREE.BufferAttribute;
      const posArray = posAttr.array as Float32Array;
      for (let i = 0; i < particleCount; i++) {
        posArray[i * 3 + 1] -= dt * 0.45;
        if (posArray[i * 3 + 1] < -2.2) {
          posArray[i * 3 + 1] = 16.0;
        }
      }
      posAttr.needsUpdate = true;
      st.particles.rotation.y = elapsed * 0.02;

      st.renderer.render(st.scene, st.camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(reqId);
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mailshield:analyzing', onAnalyzing);
      window.removeEventListener('mailshield:result', onResult);
      window.removeEventListener('mailshield:idle', onIdle);
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className="fixed inset-0 w-full h-full pointer-events-none z-[1]"
      aria-hidden="true"
    />
  );
};
