import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiPost, saveSession } from "../api/client";

export default function Demo() {
  const nav = useNavigate();
  const [i, setI] = useState(0);
  const [busy, setBusy] = useState(false);
  const [payload, setPayload] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);
  const steps = payload?.steps || payload?.result?.demo_steps || [];

  async function start() {
    setBusy(true);
    setErr(null);
    try {
      const r = await apiPost<any>("/demo/sih");
      setPayload(r);
      saveSession(r.id, r.result);
      setI(0);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="lunar-page max-w-4xl">
      <h1 className="text-3xl">SIH Demo Mode</h1>
      <p className="text-slate-400 mt-2">
        Storytelling for judges. Metrics come from the real pipeline on a synthetic crater pair, labeled
        SYNTHETIC BENCHMARK.
      </p>
      <button onClick={start} disabled={busy} className="mt-4 px-5 py-3 bg-dust text-void rounded">
        {busy ? "Running demonstration pipeline…" : "Play demonstration"}
      </button>
      {err && <pre className="text-danger text-sm mt-3 whitespace-pre-wrap">{err}</pre>}
      {payload && (
        <>
          <p className="mt-4 text-sm text-warn">{payload.result?.demo_story}</p>
          <div className="mt-6 border border-line p-6 rounded-xl min-h-48">
            <div className="text-dust text-xs tracking-[0.3em]">{steps[i]?.title}</div>
            <p className="mt-3 text-lg">{steps[i]?.body}</p>
            <div className="mt-6 flex gap-2">
              <button className="border border-line px-3 py-1" onClick={() => setI((x) => Math.max(0, x - 1))}>
                Back
              </button>
              <button className="border border-signal text-signal px-3 py-1" onClick={() => setI((x) => Math.min(steps.length - 1, x + 1))}>
                Next
              </button>
              <button className="ml-auto text-signal" onClick={() => nav("/correspondences")}>
                Open results
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
