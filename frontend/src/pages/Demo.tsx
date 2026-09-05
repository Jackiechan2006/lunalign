import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiPost, saveSession } from "../api/client";
import { ActionButton, PageHeader, Panel, StatusBadge } from "../components/ui";

export default function Demo() {
  const nav = useNavigate();
  const [i, setI] = useState(0);
  const [busy, setBusy] = useState(false);
  const [payload, setPayload] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);
  const steps = payload?.steps || payload?.result?.demo_steps || [];

  async function start() {
    setBusy(true); setErr(null);
    try { const r = await apiPost<any>("/demo/sih"); setPayload(r); saveSession(r.id, r.result); setI(0); }
    catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  }

  return (
    <div className="lunar-page">
      <PageHeader eyebrow="DEMONSTRATION · JUDGE MODE" title="Guided mission demo" description="A concise walkthrough of LunaAlign using the real pipeline on an explicitly labeled synthetic crater pair." action={<StatusBadge tone="warn">SYNTHETIC BENCHMARK</StatusBadge>} />
      <div className="mt-8 grid gap-5 lg:grid-cols-[.7fr_1.3fr]">
        <Panel>
          <div className="lunar-section-label !mt-0">DEMO CONTROL</div>
          <p className="mt-4 text-sm leading-7 text-slate-400">Run the benchmark pipeline, then step through the scientific story and open the generated correspondence evidence.</p>
          <div className="mt-6"><ActionButton disabled={busy} onClick={undefined as never}>{busy ? "RUNNING PIPELINE…" : "PLAY DEMONSTRATION"}</ActionButton></div>
          <button onClick={start} disabled={busy} className="absolute h-0 w-0 overflow-hidden" aria-label="Start demonstration" />
          {!busy && !payload && <button onClick={start} className="mt-3 border border-line px-4 py-2 text-[9px] tracking-widest text-slate-400 hover:text-white">RUN DEMO PIPELINE</button>}
          {err && <pre className="text-danger text-sm mt-4 whitespace-pre-wrap">{err}</pre>}
        </Panel>
        <Panel>
          <div className="flex items-center justify-between"><div className="lunar-section-label !mt-0">MISSION STORY</div><span className="font-mono text-[9px] text-slate-600">{steps.length ? `${String(i+1).padStart(2,"0")} / ${String(steps.length).padStart(2,"0")}` : "WAITING"}</span></div>
          {payload ? <>
            <p className="mt-5 text-xs leading-6 text-warn">{payload.result?.demo_story}</p>
            <div className="mt-8 min-h-36 border-t border-line pt-6"><div className="text-[9px] tracking-[.25em] text-slate-500">{steps[i]?.title}</div><p className="mt-3 max-w-2xl font-serif text-2xl leading-snug text-slate-200">{steps[i]?.body}</p></div>
            <div className="mt-6 flex gap-2"><button className="border border-line px-3 py-2 text-xs" onClick={() => setI(x=>Math.max(0,x-1))}>← BACK</button><button className="border border-line px-3 py-2 text-xs" onClick={() => setI(x=>Math.min(steps.length-1,x+1))}>NEXT →</button><button className="ml-auto text-xs text-slate-300" onClick={()=>nav("/correspondences")}>OPEN RESULTS ↗</button></div>
          </> : <div className="grid min-h-64 place-items-center text-center"><div><span className="luna-mark mx-auto"><span /></span><p className="mt-5 text-xs tracking-widest text-slate-600">READY FOR DEMONSTRATION</p></div></div>}
        </Panel>
      </div>
    </div>
  );
}
