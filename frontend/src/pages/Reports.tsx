import { fileUrl, loadSession } from "../api/client";

export default function Reports() {
  const { jobId, result } = loadSession();
  if (!result) return <div className="p-10 text-slate-400">Generate a registration first.</div>;
  const reports = result.reports || {};
  return (
    <div className="lunar-page max-w-3xl">
      <h1 className="text-3xl">Reports</h1>
      <p className="text-slate-400 mt-2">HTML, JSON, CSV and PDF written by the backend from computed metrics only.</p>
      <div className="mt-6 flex flex-col gap-2">
        {Object.entries(reports).map(([k, v]) => (
          <a key={k} className="text-signal underline" href={jobId ? fileUrl(jobId, String(v)) : "#"} target="_blank" rel="noreferrer">
            {k.toUpperCase()} — {String(v)}
          </a>
        ))}
      </div>
      <ol className="mt-8 text-sm text-slate-300 list-decimal ml-5 space-y-1">
        <li>Problem</li>
        <li>Input data and sensors</li>
        <li>Preprocessing and matching algorithm</li>
        <li>Correspondence, geometry, sub-pixel, quality</li>
        <li>DEM / 3D / 4D if used</li>
        <li>Limitations</li>
      </ol>
    </div>
  );
}
