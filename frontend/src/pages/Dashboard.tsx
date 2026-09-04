import { Link } from "react-router-dom";
import { ActionButton, PageHeader, Panel, StatusBadge } from "../components/ui";

const sensors = [
  { k: "OHRC", d: "Orbiter High Resolution Camera — panchromatic, high GSD contrast." },
  { k: "TMC-2", d: "Terrain Mapping Camera — stereo-capable, coarser scale, DEM path." },
  { k: "IIRS", d: "Imaging Infrared Spectrometer — X×Y×bands, PCA dimensionality reduction." },
];

const methods = [
  { k: "Classical CV", d: "SIFT, RootSIFT, NCC, pyramids, phase correlation." },
  { k: "Deep Learning", d: "Optional LoFTR / SuperPoint+SuperGlue with local checkpoints only." },
  { k: "DEM", d: "Optional X,Y,Z geometric constraint. Never fabricated as mission DEM." },
  { k: "4D Analysis", d: "Optional X,Y,Z,T potential change — not confirmed physical change." },
];

export default function Dashboard() {
  return (
    <div className="lunar-page lunar-dashboard">
      <PageHeader
        eyebrow="ISRO · SMART INDIA HACKATHON · MISSION CONSOLE"
        title="LUNAALIGN-X"
        description="Multi-Modal, Sun-Angle and Scale-Invariant Lunar Image Correspondence"
        action={<StatusBadge>SYSTEM ONLINE</StatusBadge>}
      />
      <p className="lunar-lead max-w-3xl">
        Chandrayaan-2 multi-modal image correspondence across OHRC, TMC-2 and IIRS. Illumination-robust
        classical computer vision, optional deep-learning correspondence, robust geometric verification,
        spatially uniform matches and sub-pixel refinement.
      </p>
      <div className="lunar-actions">
        <Link to="/registration"><ActionButton>START NEW REGISTRATION</ActionButton></Link>
        <Link to="/demo"><ActionButton variant="secondary">SIH DEMO MODE</ActionButton></Link>
      </div>
      <div className="lunar-section-label">SENSOR FAMILIES / AVAILABLE INPUTS</div>
      <div className="lunar-card-grid lunar-card-grid-three">
        {sensors.map((s) => (
          <Panel key={s.k}><StatusBadge tone="violet">{s.k}</StatusBadge><p className="lunar-card-copy">{s.d}</p></Panel>
        ))}
      </div>
      <div className="lunar-section-label">PROCESSING CAPABILITIES / EVIDENCE FIRST</div>
      <div className="lunar-card-grid lunar-card-grid-four">
        {methods.map((s) => (
          <Panel key={s.k}><StatusBadge>{s.k}</StatusBadge><p className="lunar-card-copy">{s.d}</p></Panel>
        ))}
      </div>
    </div>
  );
}
