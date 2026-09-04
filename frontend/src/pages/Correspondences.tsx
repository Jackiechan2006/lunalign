import { useMemo, useState } from "react";
import { fileUrl, loadSession } from "../api/client";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const TABS = ["All Matches", "Ratio-Test Matches", "RANSAC Inliers", "Final Uniform Matches", "Sub-pixel Matches"];

export default function Correspondences() {
  const { jobId, result } = loadSession();
  const [tab, setTab] = useState(TABS[3]);
  const [sel, setSel] = useState<any>(null);
  if (!result) {
    return <Empty />;
  }
  const q = result.quality || {};
  const g = result.geometry || {};
  const preview = (name: string) => (jobId && result.previews?.[name === "uniform" ? "uniform" : name] ? fileUrl(jobId, result.previews[name] || result.previews.matches) : "");
  const chart = useMemo(
    () => [
      { k: "Inlier ratio", v: (g.inlier_ratio || 0) * 100 },
      { k: "Coverage %", v: (result.uniform?.coverage || 0) * 100 },
      { k: "Quality ×100", v: (q.score || 0) * 100 },
    ],
    [result]
  );
  return (
    <div className="lunar-page">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-xs tracking-[0.25em] text-dust">{result.origin_label}</div>
          <h1 className="text-3xl mt-1">Correspondences</h1>
        </div>
        <div className="text-right">
          <div className="text-signal text-sm">Registration Quality: {q.band}</div>
          <div className="text-2xl">Score: {q.score}</div>
          <div className="text-[11px] text-slate-500 max-w-sm">{q.disclaimer}</div>
        </div>
      </div>
      <div className={`mt-3 text-sm ${result.decision?.accepted ? "text-signal" : "text-warn"}`}>
        {result.decision?.status}
        {result.decision?.reasons?.length ? ` — ${result.decision.reasons.join(" ")}` : ""}
      </div>
      <div className="grid md:grid-cols-5 gap-3 mt-6 text-sm">
        <Metric k="Matches" v={result.matching?.mutual_matches} />
        <Metric k="Inliers" v={g.inliers} />
        <Metric k="Inlier ratio" v={g.inlier_ratio != null ? `${(g.inlier_ratio * 100).toFixed(1)}%` : "—"} />
        <Metric k="RMSE" v={g.rmse != null ? `${Number(g.rmse).toFixed(2)} px` : "—"} />
        <Metric k="Coverage" v={`${((result.uniform?.coverage || 0) * 100).toFixed(0)}%`} />
      </div>
      <div className="flex gap-2 mt-6 text-xs flex-wrap">
        {TABS.map((t) => (
          <button key={t} onClick={() => setTab(t)} className={`px-3 py-1 border rounded ${tab === t ? "border-signal text-signal" : "border-line"}`}>
            {t}
          </button>
        ))}
      </div>
      <div className="grid md:grid-cols-2 gap-4 mt-4">
        {["reference", "moving", "overlay", "difference", "matches", "uniform"].map((k) => (
          <figure key={k} className="border border-line bg-black/40 p-2 rounded">
            <figcaption className="text-xs text-dust mb-2 uppercase tracking-widest">{k}</figcaption>
            {jobId ? (
              <img src={fileUrl(jobId, result.previews?.[k] || `${k === "uniform" ? "grid" : k}.png`)} alt={k} className="w-full" />
            ) : null}
          </figure>
        ))}
      </div>
      <div className="grid md:grid-cols-2 gap-6 mt-8">
        <div className="h-56 border border-line p-3 rounded">
          <ResponsiveContainer>
            <BarChart data={chart}>
              <CartesianGrid stroke="#243044" />
              <XAxis dataKey="k" stroke="#9aa" />
              <YAxis stroke="#9aa" />
              <Tooltip />
              <Bar dataKey="v" fill="#7fd1c7" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="border border-line p-4 rounded text-sm space-y-1">
          <div className="text-dust text-xs tracking-widest">ALGORITHM TRANSPARENCY</div>
          <Row k="Feature detector" v={result.algorithm?.feature_detector} />
          <Row k="Descriptor" v={result.algorithm?.descriptor} />
          <Row k="Matcher" v={result.algorithm?.matcher} />
          <Row k="Filtering" v={result.algorithm?.filtering} />
          <Row k="Geometry" v={result.algorithm?.geometry} />
          <Row k="Refinement" v={result.algorithm?.refinement} />
          <Row k="Dimensionality reduction" v={result.algorithm?.dimensionality_reduction} />
          <Row k="Deep matcher" v={result.algorithm?.deep_model} />
          <Row k="Family" v={result.algorithm?.family} />
          <p className="text-slate-500 text-xs pt-2">{result.algorithm?.deep_note}</p>
        </div>
      </div>
      <div className="mt-6 overflow-auto max-h-80 border border-line rounded">
        <table className="w-full text-xs">
          <thead className="bg-panel text-dust">
            <tr>
              {["id", "ref", "mov", "NCC", "residual", "shift"].map((h) => (
                <th key={h} className="p-2 text-left">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(result.correspondences || []).map((c: any) => (
              <tr key={c.id} className="border-t border-line hover:bg-white/5 cursor-pointer" onClick={() => setSel(c)}>
                <td className="p-2">{c.id}</td>
                <td className="p-2">{fmt(c.ref)}</td>
                <td className="p-2">{fmt(c.mov)}</td>
                <td className="p-2">{c.ncc?.toFixed?.(3)}</td>
                <td className="p-2">{c.geometric_residual?.toFixed?.(3)}</td>
                <td className="p-2">{c.subpixel_shift?.toFixed?.(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {sel && (
        <div className="mt-4 text-sm border border-signal/40 p-4 rounded">
          <div>Reference {fmt(sel.ref)} → Moving {fmt(sel.mov)}</div>
          <div>Descriptor distance {sel.descriptor_distance} · Lowe ratio {sel.lowe_ratio}</div>
          <div>NCC {sel.ncc} · geometric residual {sel.geometric_residual} · subpixel shift {sel.subpixel_shift}</div>
        </div>
      )}
    </div>
  );
}

function Empty() {
  return <div className="p-10 text-slate-400">Run a registration first.</div>;
}
function Metric({ k, v }: { k: string; v: any }) {
  return (
    <div className="border border-line bg-panel p-3 rounded">
      <div className="text-[11px] text-slate-500">{k}</div>
      <div className="text-lg">{v ?? "—"}</div>
    </div>
  );
}
function Row({ k, v }: { k: string; v: any }) {
  return (
    <div>
      <span className="text-slate-500">{k}: </span>
      {String(v ?? "—")}
    </div>
  );
}
function fmt(p?: number[]) {
  if (!p) return "—";
  return `(${p[0].toFixed(2)}, ${p[1].toFixed(2)})`;
}
