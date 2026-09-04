import { Link } from "react-router-dom";
import { ActionButton, PageHeader, Panel, StatusBadge } from "../components/ui";

const sensors = [
  { k: "OHRC", d: "Orbiter High Resolution Camera · panchromatic imagery and high-GSD surface detail." },
  { k: "TMC-2", d: "Terrain Mapping Camera · stereo-capable imagery supporting terrain and DEM workflows." },
  { k: "IIRS", d: "Imaging Infrared Spectrometer · hyperspectral observations with PCA dimensionality reduction." },
];

const methods = [
  { k: "Classical CV", d: "SIFT, RootSIFT, NCC, pyramids and phase correlation." },
  { k: "Deep Matching", d: "Optional LoFTR or SuperPoint + SuperGlue using local checkpoints." },
  { k: "Geometry", d: "Optional X, Y, Z constraints for spatially credible verification." },
  { k: "4D Analysis", d: "X, Y, Z, T comparison for evidence-led potential change analysis." },
];

export default function Dashboard() {
  return (
    <div className="lunar-page lunar-dashboard">
      <PageHeader
        eyebrow="MISSION WORKSPACE · OVERVIEW"
        title="Lunar correspondence, under control."
        description="A focused operational view of the LunaAlign processing pipeline."
        action={<StatusBadge>PIPELINE READY</StatusBadge>}
      />

      <p className="lunar-lead">
        Register and interrogate Chandrayaan-2 imagery across OHRC, TMC-2 and IIRS while preserving geometric evidence, illumination robustness and scientific traceability.
      </p>
      <div className="lunar-actions">
        <Link to="/registration"><ActionButton>New registration</ActionButton></Link>
        <Link to="/demo"><ActionButton variant="secondary">Demo sequence</ActionButton></Link>
      </div>

      <div className="lunar-section-label">AVAILABLE SENSOR FAMILIES</div>
      <div className="lunar-card-grid lunar-card-grid-three">
        {sensors.map((sensor) => (
          <Panel key={sensor.k}>
            <StatusBadge tone="violet">{sensor.k}</StatusBadge>
            <p className="lunar-card-copy">{sensor.d}</p>
          </Panel>
        ))}
      </div>

      <div className="lunar-section-label">PROCESSING CAPABILITIES</div>
      <div className="lunar-card-grid lunar-card-grid-four">
        {methods.map((method) => (
          <Panel key={method.k}>
            <StatusBadge>{method.k}</StatusBadge>
            <p className="lunar-card-copy">{method.d}</p>
          </Panel>
        ))}
      </div>
    </div>
  );
}
