import { fileUrl, loadSession } from "../api/client";
import { PageHeader, Panel, StatusBadge } from "../components/ui";

export default function Reports() {
  const { jobId, result } = loadSession();
  if (!result) return <div className="lunar-page"><PageHeader eyebrow="08 · REPORTING" title="Reports" description="Run a registration first to generate evidence-backed outputs." /></div>;
  const reports = result.reports || {};
  return (
    <div className="lunar-page">
      <PageHeader eyebrow="08 · REPORTING" title="Scientific reports" description="Backend-generated HTML, JSON, CSV and PDF outputs derived only from computed registration metrics." action={<StatusBadge>{Object.keys(reports).length} OUTPUTS</StatusBadge>} />
      <div className="grid gap-5 lg:grid-cols-[1.1fr_.9fr] mt-8">
        <Panel>
          <div className="lunar-section-label !mt-0">AVAILABLE ARTIFACTS</div>
          <div className="mt-4 divide-y divide-white/5">
            {Object.entries(reports).map(([k, v]) => (
              <a key={k} className="group flex items-center justify-between py-4 no-underline" href={jobId ? fileUrl(jobId, String(v)) : "#"} target="_blank" rel="noreferrer">
                <span><strong className="block text-sm font-medium text-slate-200">{k.toUpperCase()}</strong><small className="mt-1 block text-xs text-slate-500">{String(v)}</small></span>
                <span className="text-slate-500 transition group-hover:text-slate-200">↗</span>
              </a>
            ))}
          </div>
        </Panel>
        <Panel>
          <div className="lunar-section-label !mt-0">REPORT STRUCTURE</div>
          <ol className="mt-5 space-y-3 text-sm text-slate-400">
            {["Problem definition", "Input data and sensors", "Preprocessing and matching algorithm", "Correspondence, geometry and quality", "DEM / 3D / 4D evidence when used", "Limitations and scientific caveats"].map((x,i)=><li key={x} className="flex gap-3"><span className="font-mono text-slate-600">0{i+1}</span><span>{x}</span></li>)}
          </ol>
        </Panel>
      </div>
    </div>
  );
}
