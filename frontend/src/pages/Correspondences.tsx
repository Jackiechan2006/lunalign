import { useState } from "react";
import { fileUrl, loadSession } from "../api/client";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { PageHeader, Panel, StatusBadge } from "../components/ui";

const TABS = ["All Matches", "Ratio-Test Matches", "RANSAC Inliers", "Final Uniform Matches", "Sub-pixel Matches"];

export default function Correspondences() {
  const { jobId, result } = loadSession();
  const [tab, setTab] = useState(TABS[3]);
  const [sel, setSel] = useState<any>(null);

  if (!result) return <Empty />;

  const q = result.quality || {};
  const g = result.geometry || {};
  const chart = [
    { k: "Inlier ratio", v: (g.inlier_ratio || 0) * 100 },
    { k: "Coverage", v: (result.uniform?.coverage || 0) * 100 },
    { k: "Quality", v: (q.score || 0) * 100 },
  ];

  return (
    <div className="lunar-page">
      <PageHeader
        eyebrow={`03 · CORRESPONDENCE REVIEW · ${result.origin_label || "SESSION"}`}
        title="Correspondence analysis"
        description="Inspect registration evidence, geometric consistency, spatial coverage and algorithm transparency without hiding uncertainty."
        action={<StatusBadge tone={result.decision?.accepted ? "signal" : "warn"}>{result.decision?.status || q.band || "REVIEW"}</StatusBadge>}
      />

      <div className="mt-7 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Metric k="Matches" v={result.matching?.mutual_matches} />
        <Metric k="Inliers" v={g.inliers} />
        <Metric k="Inlier ratio" v={g.inlier_ratio != null ? `${(g.inlier_ratio * 100).toFixed(1)}%` : "—"} />
        <Metric k="RMSE" v={g.rmse != null ? `${Number(g.rmse).toFixed(2)} px` : "—"} />
        <Metric k="Coverage" v={`${((result.uniform?.coverage || 0) * 100).toFixed(0)}%`} />
      </div>

      <Panel className="mt-5">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <div className="lunar-section-label !mt-0">REGISTRATION QUALITY</div>
            <div className="mt-2 text-3xl font-light text-slate-100">{q.score ?? "—"}</div>
            <div className="mt-1 text-xs text-slate-500">Band: {q.band || "unavailable"}</div>
          </div>
          <p className="max-w-xl text-xs leading-6 text-slate-500">{q.disclaimer}</p>
        </div>
        {result.decision?.reasons?.length > 0 && (
          <div className="mt-4 border-t border-line pt-4 text-xs text-slate-400">
            {result.decision.reasons.join(" ")}
          </div>
        )}
      </Panel>

      <div className="mt-6 flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button key={t} onClick={() => setTab(t)} className={`luna-analysis-tab ${tab === t ? "active" : ""}`}>{t}</button>
        ))}
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        {["reference", "moving", "overlay", "difference", "matches", "uniform"].map((k) => (
          <figure key={k} className="luna-preview-card">
            <figcaption>{k}</figcaption>
            {jobId ? <img src={fileUrl(jobId, result.previews?.[k] || `${k === "uniform" ? "grid" : k}.png`)} alt={k} /> : null}
          </figure>
        ))}
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        <Panel>
          <div className="lunar-section-label !mt-0">QUALITY SIGNALS</div>
          <div className="mt-4 h-60">
            <ResponsiveContainer>
              <BarChart data={chart}>
                <CartesianGrid stroke="rgba(255,255,255,.07)" vertical={false} />
                <XAxis dataKey="k" stroke="#69736f" />
                <YAxis stroke="#69736f" />
                <Tooltip contentStyle={{ background: "#0d1112", border: "1px solid #2a3130", fontSize: 12 }} />
                <Bar dataKey="v" fill="#a9bdb7" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel>
          <div className="lunar-section-label !mt-0">ALGORITHM TRANSPARENCY</div>
          <div className="mt-4 divide-y divide-white/5 text-sm">
            <Row k="Feature detector" v={result.algorithm?.feature_detector} />
            <Row k="Descriptor" v={result.algorithm?.descriptor} />
            <Row k="Matcher" v={result.algorithm?.matcher} />
            <Row k="Filtering" v={result.algorithm?.filtering} />
            <Row k="Geometry" v={result.algorithm?.geometry} />
            <Row k="Refinement" v={result.algorithm?.refinement} />
            <Row k="Dimensionality reduction" v={result.algorithm?.dimensionality_reduction} />
            <Row k="Deep matcher" v={result.algorithm?.deep_model} />
            <Row k="Family" v={result.algorithm?.family} />
          </div>
          <p className="mt-4 text-xs leading-5 text-slate-500">{result.algorithm?.deep_note}</p>
        </Panel>
      </div>

      <Panel className="mt-6 overflow-hidden !p-0">
        <div className="border-b border-line p-5">
          <div className="lunar-section-label !mt-0">CORRESPONDENCE TABLE</div>
        </div>
        <div className="max-h-96 overflow-auto">
          <table className="w-full min-w-[720px] text-xs">
            <thead className="sticky top-0 bg-[#0e1213] text-slate-500">
              <tr>{["id", "ref", "mov", "NCC", "residual", "shift"].map((h) => <th key={h} className="p-3 text-left font-medium">{h}</th>)}</tr>
            </thead>
            <tbody>
              {(result.correspondences || []).map((c: any) => (
                <tr key={c.id} className="cursor-pointer border-t border-line hover:bg-white/[.025]" onClick={() => setSel(c)}>
                  <td className="p-3 text-slate-200">{c.id}</td>
                  <td className="p-3">{fmt(c.ref)}</td>
                  <td className="p-3">{fmt(c.mov)}</td>
                  <td className="p-3">{c.ncc?.toFixed?.(3)}</td>
                  <td className="p-3">{c.geometric_residual?.toFixed?.(3)}</td>
                  <td className="p-3">{c.subpixel_shift?.toFixed?.(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {sel && (
        <Panel className="mt-4">
          <div className="lunar-section-label !mt-0">SELECTED MATCH</div>
          <div className="mt-3 grid gap-2 text-sm text-slate-300 md:grid-cols-3">
            <div>Reference {fmt(sel.ref)} → Moving {fmt(sel.mov)}</div>
            <div>Distance {sel.descriptor_distance} · Lowe {sel.lowe_ratio}</div>
            <div>NCC {sel.ncc} · residual {sel.geometric_residual} · shift {sel.subpixel_shift}</div>
          </div>
        </Panel>
      )}
    </div>
  );
}

function Empty() {
  return <div className="lunar-page"><PageHeader eyebrow="03 · CORRESPONDENCES" title="No registration session" description="Run a registration first to inspect correspondence evidence." /></div>;
}
function Metric({ k, v }: { k: string; v: any }) {
  return <div className="luna-metric"><span>{k}</span><strong>{v ?? "—"}</strong></div>;
}
function Row({ k, v }: { k: string; v: any }) {
  return <div className="flex justify-between gap-5 py-2.5"><span className="text-slate-500">{k}</span><span className="text-right text-slate-200">{String(v ?? "—")}</span></div>;
}
function fmt(p?: number[]) {
  if (!p) return "—";
  return `(${p[0].toFixed(2)}, ${p[1].toFixed(2)})`;
}
