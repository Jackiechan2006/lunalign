import { Canvas, useFrame } from "@react-three/fiber";
import { Stars } from "@react-three/drei";
import { Link } from "react-router-dom";
import { useRef } from "react";
import type { Mesh } from "three";

function Moon() {
  const moon = useRef<Mesh>(null);
  useFrame((state, delta) => {
    if (!moon.current) return;
    moon.current.rotation.y += delta * 0.035;
    moon.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.12) * 0.04;
  });

  return (
    <mesh ref={moon} position={[2.6, -0.25, -1.4]} scale={2.35}>
      <sphereGeometry args={[1, 128, 128]} />
      <meshStandardMaterial color="#7d8587" roughness={0.94} metalness={0.02} />
    </mesh>
  );
}

function OrbitalScene() {
  return (
    <Canvas camera={{ position: [0, 0, 7], fov: 42 }} dpr={[1, 1.7]}>
      <ambientLight intensity={0.48} />
      <directionalLight position={[-4, 3, 5]} intensity={3.2} color="#edf7f4" />
      <pointLight position={[4, -2, 2]} intensity={0.8} color="#7fcbb7" />
      <Stars radius={90} depth={32} count={1100} factor={1.8} saturation={0} fade speed={0.15} />
      <Moon />
    </Canvas>
  );
}

export default function Landing() {
  return (
    <main className="landing-shell">
      <div className="landing-scene" aria-hidden="true"><OrbitalScene /></div>
      <div className="landing-vignette" />
      <header className="landing-nav">
        <Link className="landing-brand" to="/" aria-label="LunaAlign home">
          <span className="landing-brand-mark"><span /></span>
          <span>
            <strong>LUNAALIGN</strong>
            <small>LUNAR CORRESPONDENCE SYSTEM</small>
          </span>
        </Link>
        <div className="landing-nav-meta">
          <span>CHANDRAYAAN-2</span>
          <span className="landing-status-dot">SYSTEM READY</span>
        </div>
      </header>

      <section className="landing-hero">
        <div className="landing-copy">
          <p className="landing-kicker">MULTI-MODAL LUNAR IMAGE INTELLIGENCE</p>
          <h1>Align the Moon.<br /><em>Reveal the signal.</em></h1>
          <p className="landing-summary">
            A precision correspondence workspace for Chandrayaan-2 imagery — engineered to remain reliable across sensor, scale, illumination and temporal variation.
          </p>
          <div className="landing-actions">
            <Link className="landing-primary" to="/workspace">Launch workspace <span>↗</span></Link>
            <a className="landing-secondary" href="#mission">Explore system</a>
          </div>
          <div className="landing-metrics" aria-label="System capabilities">
            <div><strong>03</strong><span>Sensor families</span></div>
            <div><strong>4D</strong><span>Spatial-temporal analysis</span></div>
            <div><strong>Sub-px</strong><span>Refinement capability</span></div>
          </div>
        </div>

        <aside className="landing-orbit-card">
          <span className="orbit-card-label">CURRENT MISSION PROFILE</span>
          <div className="orbit-card-row"><span>Primary objective</span><strong>Cross-sensor correspondence</strong></div>
          <div className="orbit-card-row"><span>Supported imagery</span><strong>OHRC · TMC-2 · IIRS</strong></div>
          <div className="orbit-card-row"><span>Pipeline</span><strong>Evidence-first CV</strong></div>
          <div className="orbit-card-rule" />
          <p>Built for rigorous comparison, geometric verification and judge-ready interpretability.</p>
        </aside>
      </section>

      <section id="mission" className="landing-lower">
        <p>Precision before spectacle. Every visual decision serves scientific readability.</p>
        <span>Scroll to inspect ↓</span>
      </section>
    </main>
  );
}
