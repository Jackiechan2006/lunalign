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
    <div className="luna-landing luna-journey">
      <div className="luna-story-stage" aria-hidden="true">
        <LunarHeroScene />
        <div className="luna-story-vignette" />
        <div className="luna-story-grid" />
      </div>

      <header className="luna-landing-nav luna-journey-nav">
        <Link className="luna-wordmark" to="/" aria-label="LunaAlign home">
          <span className="luna-mark"><span /></span>
          <span><strong>LUNAALIGN</strong><small>LUNAR CORRESPONDENCE SYSTEM</small></span>
        </Link>
        <div className="luna-nav-meta">
          <span><i /> MISSION SYSTEM ONLINE</span>
          <a href="#pipeline">VIEW PIPELINE <b>↓</b></a>
        </div>
      </header>

      <section className="luna-story-panel luna-story-hero">
        <div className="luna-story-copy">
          <div className="luna-kicker"><span>CHANDRAYAAN-2</span><span>IMAGE INTELLIGENCE</span></div>
          <h1>See the lunar surface<br /><em>as one.</em></h1>
          <p>
            Multi-modal, sun-angle and scale-invariant lunar image correspondence for rigorous
            planetary analysis across OHRC, TMC-2 and IIRS observations.
          </p>
          <a className="luna-story-next" href="#problem">EXPLORE THE MISSION <span>↓</span></a>
        </div>
        <div className="luna-hero-readout luna-journey-readout">
          <span>12.42° S</span><span>46.18° E</span><span>ALT 100 KM</span>
        </div>
      </section>

      <section className="luna-story-panel luna-story-problem" id="problem">
        <div className="luna-story-copy luna-story-copy-right">
          <span className="luna-story-index">01 / PROBLEM</span>
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

      <section className="luna-story-panel luna-story-pipeline" id="pipeline">
        <div className="luna-story-wide">
          <div className="luna-story-heading">
            <span className="luna-story-index">02 / PIPELINE</span>
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
        </div>
      </section>

      <section className="luna-story-panel luna-story-evidence">
        <div className="luna-story-wide">
          <div className="luna-story-heading luna-story-heading-split">
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

      <section className="luna-story-panel luna-story-ready">
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
    </div>
  );
}
