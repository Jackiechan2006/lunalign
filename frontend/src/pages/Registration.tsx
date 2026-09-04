import { FormEvent, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiPost, saveSession } from "../api/client";
import { QualityCard } from "./DataPage";
import { ActionButton, PageHeader, Panel, StatusBadge } from "../components/ui";

const STAGES = [
  "Loading",
  "Preprocessing",
  "Illumination normalization",
  "Scale estimation",
  "Feature extraction",
  "Candidate matching",
  "Geometric verification",
  "Uniform point selection",
  "Sub-pixel refinement",
  "Quality assessment",
  "DEM verification",
  "Final result",
];

export default function Registration() {
  const nav = useNavigate();
  const [step, setStep] = useState(1);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [live, setLive] = useState<any>(null);

  async function onRun(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setErr(null);
    setBusy(true);
    const form = e.currentTarget;
    const fd = new FormData(form);
    const refMeta = {
      gsd_m: num(fd.get("ref_gsd")),
      sun_azimuth_deg: num(fd.get("ref_az")),
      sun_elevation_deg: num(fd.get("ref_el")),
      acquisition: fd.get("ref_acq") || undefined,
    };
    const movMeta = {
      gsd_m: num(fd.get("mov_gsd")),
      sun_azimuth_deg: num(fd.get("mov_az")),
      sun_elevation_deg: num(fd.get("mov_el")),
      acquisition: fd.get("mov_acq") || undefined,
    };
    const demFile = fd.get("dem") as File | null;
    if (!demFile || !demFile.name || demFile.size === 0) {
      fd.delete("dem");
    }
    fd.set("ref_meta", JSON.stringify(refMeta));
    fd.set("mov_meta", JSON.stringify(movMeta));
    try {
      const created = await apiPost<{ id: string }>("/jobs", fd);
      const result = await apiPost<any>(`/jobs/${created.id}/run`);
      saveSession(created.id, result);
      setLive(result);
      nav("/correspondences");
    } catch (ex: any) {
      setErr(ex.message);
    } finally {
      setBusy(false);
    }
  }

  const deltas = useMemo(() => live, [live]);

  return (
    <div className="lunar-page lunar-registration">
      <PageHeader eyebrow="01 · ALIGNMENT WORKFLOW" title="Registration workflow" description="Seven steps. Core correspondence does not require a DEM or ML weights." action={<StatusBadge tone={busy ? "violet" : "signal"}>{busy ? "PIPELINE RUNNING" : "READY TO RUN"}</StatusBadge>} />
      <ol className="lunar-step-rail">
        {["Reference sensor", "Moving sensor", "Upload images", "Optional DEM", "Metadata", "Matching mode", "Run"].map(
          (s, i) => (
            <li key={s} className={`lunar-step ${step === i + 1 ? "lunar-step-active" : ""}`}>
              {i + 1}. {s}
            </li>
          )
        )}
      </ol>
      <form onSubmit={onRun} className="lunar-form">
        <Panel><fieldset>
          <legend className="px-2 text-dust">Sensors</legend>
          <div className="grid md:grid-cols-2 gap-4">
            <label className="text-sm">
              Reference
              <select name="ref_sensor" className="block w-full mt-1 bg-void border border-line p-2" onFocus={() => setStep(1)}>
                <option>OHRC</option>
                <option>TMC</option>
                <option>IIRS</option>
              </select>
            </label>
            <label className="text-sm">
              Moving
              <select name="mov_sensor" className="block w-full mt-1 bg-void border border-line p-2" onFocus={() => setStep(2)}>
                <option>TMC</option>
                <option>OHRC</option>
                <option>IIRS</option>
              </select>
            </label>
          </div>
        </fieldset></Panel>
        <Panel><fieldset>
          <legend className="px-2 text-dust">Uploads</legend>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <label>
              Reference image
              <input name="reference" type="file" required className="block mt-1" onFocus={() => setStep(3)} />
            </label>
            <label>
              Moving image
              <input name="moving" type="file" required className="block mt-1" onFocus={() => setStep(3)} />
            </label>
            <label>
              Optional DEM
              <input name="dem" type="file" className="block mt-1" onFocus={() => setStep(4)} />
            </label>
          </div>
          <label className="block text-sm mt-3">
            DEM kind
            <select name="dem_kind" className="bg-void border border-line p-2 ml-2">
              <option value="REAL_DEM">REAL DEM</option>
              <option value="DERIVED_DEM">DERIVED DEM</option>
              <option value="SYNTHETIC_DEM">SYNTHETIC DEM — NOT SCIENTIFIC DATA</option>
            </select>
          </label>
          <label className="block text-sm mt-3">
            Data origin
            <select name="origin" className="bg-void border border-line p-2 ml-2">
              <option value="REAL_CHANDRAYAAN2">REAL CHANDRAYAAN-2 DATA</option>
              <option value="SYNTHETIC_BENCHMARK">SYNTHETIC BENCHMARK</option>
            </select>
          </label>
        </fieldset></Panel>
        <Panel><fieldset onFocus={() => setStep(5)}>
          <legend className="px-2 text-dust">Metadata (leave blank if unknown)</legend>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <MetaBlock prefix="ref" title="REFERENCE" />
            <MetaBlock prefix="mov" title="MOVING" />
          </div>
        </fieldset></Panel>
        <label className="text-sm">
          Matching mode
          <select name="mode" className="block mt-1 bg-void border border-line p-2" onFocus={() => setStep(6)}>
            <option value="automatic">Automatic</option>
            <option value="classical">Classical</option>
            <option value="deep">Deep Learning</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </label>
        <ActionButton type="submit" disabled={busy}>{busy ? "RUNNING PIPELINE…" : "RUN REGISTRATION"}</ActionButton>
      </form>
      {busy && (
        <div className="mt-6 border border-line p-4 rounded-xl">
          <div className="text-xs tracking-widest text-dust mb-2">LIVE PIPELINE</div>
          {STAGES.map((s) => (
            <div key={s} className="text-sm py-0.5">
              ▸ {s}
            </div>
          ))}
        </div>
      )}
      {err && <pre className="mt-4 text-danger text-sm whitespace-pre-wrap">{err}</pre>}
      {deltas?.reference && <QualityCard items={deltas.reference.quality.items} />}
    </div>
  );
}

function num(v: FormDataEntryValue | null) {
  if (v === null || v === "") return undefined;
  const n = Number(v);
  return Number.isFinite(n) ? n : undefined;
}

function MetaBlock({ prefix, title }: { prefix: string; title: string }) {
  return (
    <div>
      <div className="text-signal text-xs tracking-widest">{title}</div>
      <input name={`${prefix}_gsd`} placeholder="GSD (m)" className="mt-2 w-full bg-void border border-line p-2" />
      <input name={`${prefix}_el`} placeholder="Sun elevation (deg)" className="mt-2 w-full bg-void border border-line p-2" />
      <input name={`${prefix}_az`} placeholder="Sun azimuth (deg)" className="mt-2 w-full bg-void border border-line p-2" />
      <input name={`${prefix}_acq`} placeholder="Acquisition (YYYY-MM-DD)" className="mt-2 w-full bg-void border border-line p-2" />
    </div>
  );
}
