import { useState } from "react";
import { apiPost } from "../api/client";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

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
      <h1 className="text-3xl">Benchmarks</h1>
      <p className="text-slate-400 mt-2 max-w-3xl">
        SYNTHETIC BENCHMARK only unless you supply mission products. LoFTR and SuperPoint+SuperGlue appear when local
        checkpoints exist; they are never downloaded.
      </p>
      <button onClick={run} disabled={busy} className="mt-4 px-4 py-2 bg-signal text-void rounded">
        {busy ? "Running…" : "Run synthetic scale robustness suite"}
      </button>
      {err && <pre className="text-danger text-sm mt-3">{err}</pre>}
      {data && (
        <>
          <p className="mt-4 text-warn text-sm">{data.disclaimer}</p>
          <div className="h-64 mt-6">
            <ResponsiveContainer>
              <BarChart data={data.rows || []}>
                <CartesianGrid stroke="#243044" />
                <XAxis dataKey="experiment" stroke="#9aa" hide />
                <YAxis stroke="#9aa" />
                <Tooltip />
                <Legend />
                <Bar dataKey="inlier_ratio" fill="#7fd1c7" name="Inlier ratio" />
                <Bar dataKey="quality_score" fill="#c9b896" name="Quality score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="overflow-auto mt-4 border border-line">
            <table className="text-xs w-full">
              <thead className="bg-panel">
                <tr>
                  {["experiment", "inliers", "inlier_ratio", "rmse", "spatial_coverage", "ncc", "runtime_s", "quality_score"].map((h) => (
                    <th key={h} className="p-2 text-left">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(data.rows || []).map((r: any) => (
                  <tr key={r.experiment} className="border-t border-line">
                    <td className="p-2">{r.experiment}</td>
                    <td className="p-2">{r.inliers}</td>
                    <td className="p-2">{r.inlier_ratio?.toFixed?.(3)}</td>
                    <td className="p-2">{r.rmse?.toFixed?.(3)}</td>
                    <td className="p-2">{r.spatial_coverage?.toFixed?.(3)}</td>
                    <td className="p-2">{r.ncc?.toFixed?.(3)}</td>
                    <td className="p-2">{r.runtime_s?.toFixed?.(2)}</td>
                    <td className="p-2">{r.quality_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <ul className="text-slate-500 text-sm mt-4 list-disc ml-5">
            {(data.missing || []).map((m: string) => (
              <li key={m}>{m}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
