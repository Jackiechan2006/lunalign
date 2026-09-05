import { useState } from "react";
import { apiPost } from "../api/client";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ActionButton, PageHeader, Panel, StatusBadge } from "../components/ui";

export default function Benchmarks() {
  const [data, setData] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function run() {
    setBusy(true);
    setErr(null);
    try {
      setData(await apiPost("/benchmarks/synthetic"));
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="lunar-page">
      <PageHeader
        eyebrow="06 · VALIDATION"
        title="Benchmark analysis"
        description="Synthetic robustness evaluation remains clearly separated from real mission-data validation. Optional deep models only appear when local checkpoints already exist."
        action={<StatusBadge tone={busy ? "violet" : "signal"}>{busy ? "RUNNING" : "READY"}</StatusBadge>}
      />

      <div className="mt-7 flex flex-wrap items-center justify-between gap-4">
        <div className="max-w-2xl text-sm text-slate-500">Measure scale robustness, inlier quality, geometric error, spatial coverage, NCC and runtime without mixing synthetic results with mission claims.</div>
        <ActionButton onClick={run as any} disabled={busy}>{busy ? "RUNNING SUITE…" : "RUN SYNTHETIC SUITE"}</ActionButton>
      </div>

      {err && <pre className="mt-4 border border-line p-4 text-sm text-danger whitespace-pre-wrap">{err}</pre>}

      {data && (
        <div className="mt-8 space-y-5">
          <Panel>
            <div className="lunar-section-label !mt-0">RESULT SUMMARY</div>
            <p className="mt-3 text-sm text-warn">{data.disclaimer}</p>
            <div className="mt-6 h-72">
              <ResponsiveContainer>
                <BarChart data={data.rows || []}>
                  <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false} />
                  <XAxis dataKey="experiment" stroke="#6f7976" hide />
                  <YAxis stroke="#6f7976" />
                  <Tooltip contentStyle={{ background: "#0d1112", border: "1px solid #2a3130", fontSize: 12 }} />
                  <Legend />
                  <Bar dataKey="inlier_ratio" fill="#a9bdb7" name="Inlier ratio" />
                  <Bar dataKey="quality_score" fill="#747f7b" name="Quality score" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Panel>

          <Panel className="overflow-hidden !p-0">
            <div className="p-5 border-b border-line">
              <div className="lunar-section-label !mt-0">EXPERIMENT TABLE</div>
            </div>
            <div className="overflow-auto">
              <table className="text-xs w-full min-w-[860px]">
                <thead className="bg-black/20 text-slate-500">
                  <tr>
                    {["experiment", "inliers", "inlier_ratio", "rmse", "spatial_coverage", "ncc", "runtime_s", "quality_score"].map((h) => (
                      <th key={h} className="p-3 text-left font-medium tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(data.rows || []).map((r: any) => (
                    <tr key={r.experiment} className="border-t border-line hover:bg-white/[.025]">
                      <td className="p-3 text-slate-200">{r.experiment}</td>
                      <td className="p-3">{r.inliers}</td>
                      <td className="p-3">{r.inlier_ratio?.toFixed?.(3)}</td>
                      <td className="p-3">{r.rmse?.toFixed?.(3)}</td>
                      <td className="p-3">{r.spatial_coverage?.toFixed?.(3)}</td>
                      <td className="p-3">{r.ncc?.toFixed?.(3)}</td>
                      <td className="p-3">{r.runtime_s?.toFixed?.(2)}</td>
                      <td className="p-3">{r.quality_score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>

          {(data.missing || []).length > 0 && (
            <Panel>
              <div className="lunar-section-label !mt-0">NOT AVAILABLE IN THIS RUN</div>
              <ul className="mt-4 grid gap-2 text-sm text-slate-500 md:grid-cols-2">
                {(data.missing || []).map((m: string) => <li key={m}>— {m}</li>)}
              </ul>
            </Panel>
          )}
        </div>
      )}
    </div>
  );
}
