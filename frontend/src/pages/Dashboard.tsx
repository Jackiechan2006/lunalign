import { Link } from "react-router-dom";
import LunarHeroScene from "../components/LunarHeroScene";

const capabilities = [
  ["01", "Cross-sensor registration", "Align OHRC, TMC-2 and IIRS observations across scale, modality and illumination."],
  ["02", "Evidence-first matching", "Classical and optional deep correspondence with robust geometric verification."],
  ["03", "Spatial intelligence", "Explore terrain constraints, uniform matches and temporal evidence in one workspace."],
];

export default function Dashboard() {
  return (
    <div className="luna-landing">
      <section className="luna-hero">
        <LunarHeroScene />
        <div className="luna-hero-vignette" />

        <header className="luna-landing-nav">
          <Link className="luna-wordmark" to="/" aria-label="LunaAlign home">
            <span className="luna-mark"><span /></span>
            <span><strong>LUNAALIGN</strong><small>LUNAR CORRESPONDENCE SYSTEM</small></span>
          </Link>
          <div className="luna-nav-meta">
            <span><i /> MISSION SYSTEM ONLINE</span>
            <Link to="/registration">ENTER WORKSPACE <b>↗</b></Link>
          </div>
        </header>

        <div className="luna-hero-content">
          <div className="luna-kicker"><span>CHANDRAYAAN-2</span><span>IMAGE INTELLIGENCE</span></div>
          <h1>See the lunar surface<br /><em>as one.</em></h1>
          <p>
            Multi-modal, sun-angle and scale-invariant lunar image correspondence for rigorous
            planetary analysis across OHRC, TMC-2 and IIRS observations.
          </p>
          <div className="luna-hero-actions">
            <Link className="luna-launch" to="/registration">LAUNCH WORKSPACE <span>→</span></Link>
            <Link className="luna-demo-link" to="/demo">VIEW DEMONSTRATION <span>↗</span></Link>
          </div>
        </div>

        <div className="luna-hero-readout">
          <span>12.42° S</span><span>46.18° E</span><span>ALT 100 KM</span>
        </div>
        <div className="luna-scroll-cue"><span /> EXPLORE SYSTEM</div>
      </section>

      <section className="luna-intro">
        <div className="luna-intro-heading">
          <span className="luna-section-index">01 / SYSTEM</span>
          <h2>One scientific workspace.<br />Multiple views of the Moon.</h2>
        </div>
        <div className="luna-intro-copy">
          <p>
            LunaAlign brings heterogeneous lunar observations into a common geometric frame,
            making correspondence inspectable rather than opaque.
          </p>
          <div className="luna-sensor-row"><span>OHRC</span><span>TMC-2</span><span>IIRS</span><span>DEM</span></div>
        </div>
      </section>

      <section className="luna-capabilities">
        {capabilities.map(([index, title, copy]) => (
          <article key={index}>
            <span>{index}</span>
            <div><h3>{title}</h3><p>{copy}</p></div>
            <b>↗</b>
          </article>
        ))}
      </section>

      <section className="luna-workspace-cta">
        <span className="luna-section-index">READY FOR ANALYSIS</span>
        <h2>From raw observation<br />to defensible correspondence.</h2>
        <Link className="luna-launch luna-launch-light" to="/registration">LAUNCH WORKSPACE <span>→</span></Link>
      </section>
    </div>
  );
}
