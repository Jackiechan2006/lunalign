export default function Experiments() {
  return (
    <div className="lunar-page max-w-4xl">
      <h1 className="text-3xl">Experiments</h1>
      <p className="text-slate-400 mt-2">
        Separate SYNTHETIC GROUND TRUTH from REAL DATA VALIDATION. Do not mix them in a SIH performance slide.
      </p>
      <div className="grid md:grid-cols-2 gap-4 mt-6">
        <div className="border border-line p-5 rounded-xl">
          <div className="text-dust text-xs tracking-widest">SYNTHETIC GROUND TRUTH</div>
          <ul className="mt-3 text-sm space-y-2 text-slate-300">
            <li>Known similarity/affine transforms</li>
            <li>Controlled scale 1×, 2×, 4×, 8×</li>
            <li>Synthetic illumination (labeled as synthetic)</li>
            <li>Used to validate software, not mission accuracy</li>
          </ul>
        </div>
        <div className="border border-line p-5 rounded-xl">
          <div className="text-dust text-xs tracking-widest">REAL DATA VALIDATION</div>
          <ul className="mt-3 text-sm space-y-2 text-slate-300">
            <li>OHRC ↔ OHRC / TMC / IIRS mission products</li>
            <li>Manual control points or geospatial references</li>
            <li>Real lunar DEM when supplied</li>
            <li>Real mission data required for this validation.</li>
          </ul>
        </div>
      </div>
      <p className="text-xs text-slate-500 mt-6">
        Every experiment records dataset, sensors, GSD, sun angles, matcher, model, thresholds, seed, metrics and runtime
        under <code>data/processed/</code> and <code>configs/default.yaml</code>.
      </p>
    </div>
  );
}
