import { PageHeader, Panel, StatusBadge } from "../components/ui";

export default function Experiments() {
  return (
    <div className="lunar-page">
      <PageHeader eyebrow="07 · VALIDATION" title="Experiments" description="Keep synthetic ground truth and real mission validation scientifically separate. LunaAlign never presents synthetic performance as mission accuracy." action={<StatusBadge tone="warn">EVIDENCE BOUNDARY</StatusBadge>} />
      <div className="grid md:grid-cols-2 gap-4 mt-8">
        <Panel>
          <div className="lunar-section-label !mt-0">SYNTHETIC GROUND TRUTH</div>
          <ul className="mt-5 text-sm space-y-3 text-slate-400">
            <li>Known similarity and affine transforms</li><li>Controlled scale at 1×, 2×, 4× and 8×</li><li>Synthetic illumination, explicitly labeled</li><li>Validates software behavior, not mission accuracy</li>
          </ul>
        </Panel>
        <Panel>
          <div className="lunar-section-label !mt-0">REAL DATA VALIDATION</div>
          <ul className="mt-5 text-sm space-y-3 text-slate-400">
            <li>OHRC ↔ OHRC / TMC / IIRS mission products</li><li>Manual control points or geospatial references</li><li>Real lunar DEM when supplied</li><li>Mission data required for scientific validation</li>
          </ul>
        </Panel>
      </div>
      <Panel className="mt-5">
        <div className="lunar-section-label !mt-0">REPRODUCIBILITY RECORD</div>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-400">Every experiment records dataset, sensors, GSD, sun angles, matcher, model, thresholds, seed, metrics and runtime under <code className="text-slate-200">data/processed/</code> and <code className="text-slate-200">configs/default.yaml</code>.</p>
      </Panel>
    </div>
  );
}
