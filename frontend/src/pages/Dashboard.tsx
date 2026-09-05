import { Link } from "react-router-dom";
import LunarHeroScene from "../components/LunarHeroScene";

const pipeline = [
  ["01", "INGEST", "OHRC · TMC-2 · IIRS", "Bring heterogeneous lunar observations into one controlled scientific pipeline."],
  ["02", "NORMALIZE", "SCALE · CONTRAST · MODALITY", "Prepare imagery without inventing mission metadata or hiding missing information."],
  ["03", "MATCH", "CLASSICAL · DEEP OPTIONAL", "Generate candidate correspondences across scale, modality and illumination differences."],
  ["04", "VERIFY", "RANSAC · UNIFORMITY · RMSE", "Reject weak geometry and retain inspectable, spatially defensible evidence."],
  ["05", "INTERPRET", "3D · 4D · REPORT", "Move from registration to terrain, temporal analysis and exportable scientific reporting."],
];

const evidence = [
  ["01", "Registration", "Cross-sensor alignment with explicit geometric verification."],
  ["02", "Correspondence", "Inspect matches, inliers, coverage and uncertainty directly."],
  ["03", "Terrain", "Use DEM context to understand spatial relationships on the lunar surface."],
  ["04", "Temporal", "Separate illumination effects from candidate physical change across epochs."],
];

export default function Dashboard() {
  return (
    <main className="landing-shell luna-landing luna-journey">
      <div className="hero-backdrop luna-story-stage" aria-hidden="true">
        <LunarHeroScene />
        <div className="luna-story-vignette" />
      </div>
      <div className="hero-grid luna-story-grid" aria-hidden="true" />

      <header className="landing-nav luna-landing-nav luna-journey-nav">
        <Link className="reference-brand" to="/" aria-label="LunaAlign home">
          <span className="reference-brand-mark"><i /><b /></span>
          <span><strong>LUNAALIGN</strong><small>LUNAR CORRESPONDENCE SYSTEM</small></span>
        </Link>
        <nav className="reference-nav-links" aria-label="Landing navigation">
          <a href="#technology">RIGHT ALIGNED</a>
          <a href="#validation">BADGES</a>
          <a href="#about">+ REGISTER</a>
        </nav>
        <div className="reference-status"><i /> MISSION SYSTEM ONLINE</div>
      </header>

      <section id="top" className="hero-section luna-story-panel luna-story-hero reference-hero">
        <div className="reference-hero-copy">
          <div className="reference-kicker">CHANDRAYAAN-2 · IMAGE INTELLIGENCE</div>
          <h1>LUNAR ALIGNMENT<br /><em>ACROSS LIGHT</em></h1>
          <p>Multi-modal, sun-angle and scale-invariant lunar image correspondence for rigorous planetary analysis.</p>
          <div className="reference-hero-actions">
            <a href="#technology" className="reference-primary-cta">EXPLORE TECH <span>→</span></a>
            <a href="#validation" className="reference-secondary-cta">WATCH PIPELINE ↗</a>
          </div>
        </div>

        <div className="reference-moon-overlay" aria-hidden="true">
          <div className="reference-reticle"><span /><i /></div>
          <div className="reference-orbit reference-orbit-a" />
          <div className="reference-orbit reference-orbit-b" />
          <div className="reference-metric reference-metric-a"><strong>52</strong><small>INLIER</small></div>
          <div className="reference-metric reference-metric-b"><strong>28</strong><small>RMSE</small></div>
          <div className="reference-metric reference-metric-c"><strong>91%</strong><small>VALID</small></div>
          <div className="reference-axis-label">LUNA / 01</div>
        </div>

        <div className="reference-scroll-cue"><span /> SCROLL TO EXPLORE</div>
      </section>

      <section id="technology" className="prelaunch-sequence luna-story-panel luna-story-problem">
        <div className="luna-story-copy luna-story-copy-right">
          <span className="luna-story-index">01 / TECHNOLOGY</span>
          <h2>Different sensors.<br />Different light.<br /><em>One lunar surface.</em></h2>
          <p>
            Lunar observations rarely arrive in the same scale, modality or illumination. LunaAlign
            treats those differences as part of the scientific problem instead of hiding them behind
            a single black-box score.
          </p>
          <div className="luna-story-sensors">
            <span><b>OHRC</b><small>HIGH RESOLUTION</small></span>
            <span><b>TMC-2</b><small>TERRAIN MAPPING</small></span>
            <span><b>IIRS</b><small>HYPERSPECTRAL</small></span>
          </div>
        </div>
      </section>

      <section id="validation" className="pipeline-ribbon enhanced-ribbon luna-story-panel luna-story-pipeline">
        <div className="luna-story-wide">
          <div className="luna-story-heading">
            <span className="luna-story-index">02 / VALIDATION PIPELINE</span>
            <h2>From observation<br />to correspondence.</h2>
            <p>Every stage remains inspectable, reproducible and evidence-first.</p>
          </div>

          <div className="luna-pipeline-rail">
            {pipeline.map(([index, title, meta, copy]) => (
              <article className="luna-pipeline-step" key={index}>
                <div className="luna-pipeline-top"><span>{index}</span><i /></div>
                <h3>{title}</h3>
                <small>{meta}</small>
                <p>{copy}</p>
              </article>
            ))}
          </div>

          <div className="luna-story-heading luna-story-heading-split luna-evidence-heading">
            <div>
              <span className="luna-story-index">03 / SCIENTIFIC EVIDENCE</span>
              <h2>Do not just align.<br /><em>Explain the alignment.</em></h2>
            </div>
            <p>
              The workspace is built around evidence: geometry, spatial coverage, terrain context,
              temporal context and explicit limitations.
            </p>
          </div>

          <div className="luna-evidence-grid">
            {evidence.map(([index, title, copy]) => (
              <article key={index}>
                <span>{index}</span>
                <h3>{title}</h3>
                <p>{copy}</p>
                <b>↗</b>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="about" className="final-cta luna-story-panel luna-story-ready">
        <div className="luna-ready-orbit" aria-hidden="true"><span /><i /></div>
        <div className="luna-ready-content">
          <span className="luna-story-index">04 / MISSION WORKSPACE</span>
          <h2>The pipeline is clear.<br />Now enter the workspace.</h2>
          <p>
            Run the real LunaAlign workflow: data intake, registration, correspondence review,
            terrain analysis, temporal analysis, benchmarks and reporting.
          </p>
          <div className="luna-ready-actions">
            <Link className="luna-launch luna-launch-light" to="/registration">LAUNCH WORKSPACE <span>→</span></Link>
            <Link className="luna-demo-link luna-demo-dark" to="/demo">VIEW GUIDED DEMO <span>↗</span></Link>
          </div>
        </div>
      </section>

      <footer className="luna-reference-footer">
        <span>LUNAALIGN · CHANDRAYAAN-2 LUNAR CORRESPONDENCE</span>
        <a href="#top">BACK TO TOP ↑</a>
      </footer>
    </main>
  );
}
