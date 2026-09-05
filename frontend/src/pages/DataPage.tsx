import { FormEvent, useState } from "react";
import { apiPost } from "../api/client";
import { ActionButton, PageHeader, Panel, StatusBadge } from "../components/ui";

export default function DataPage() {
  const [sensor, setSensor] = useState("OHRC");
  const [info, setInfo] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setErr(null);
    const fd = new FormData(e.currentTarget);
    try {
      const r = await apiPost<any>("/inspect", fd);
      setInfo(r);
    } catch (ex: any) {
      setErr(ex.message);
    }
  }

  return (
    <div className="lunar-page lunar-data-page">
      <PageHeader
        eyebrow="01 · DATA INTAKE"
        title="Inspect lunar data"
        description="Validate imagery and metadata before registration. Missing metadata remains explicitly missing — LunaAlign never fabricates mission values."
        action={<StatusBadge tone="violet">PNG · JPEG · TIFF · NPY</StatusBadge>}
      />

      <div className="grid gap-5 lg:grid-cols-[1.05fr_.95fr] mt-8">
        <Panel>
          <div className="lunar-section-label !mt-0">INPUT / SENSOR CONTEXT</div>
          <form onSubmit={onSubmit} className="lunar-form mt-5">
            <label className="text-sm">
              Sensor hint
              <select name="sensor" value={sensor} onChange={(e) => setSensor(e.target.value)} className="mt-2 w-full border p-3">
                <option>OHRC</option>
                <option>TMC</option>
                <option>IIRS</option>
              </select>
            </label>
            <label className="text-sm">
              Image / hyperspectral cube
              <input name="image" type="file" required className="mt-3 block" />
            </label>
            <div className="pt-2">
              <ActionButton type="submit">INSPECT DATASET</ActionButton>
            </div>
          </form>
        </Panel>

        <Panel>
          <div className="lunar-section-label !mt-0">SUPPORTED SCIENTIFIC INPUT</div>
          <div className="mt-5 grid gap-4 text-sm text-slate-400">
            <div><span className="text-slate-200">OHRC</span><p className="mt-1 text-xs leading-6">High-resolution panchromatic imagery for fine geometric correspondence.</p></div>
            <div><span className="text-slate-200">TMC-2</span><p className="mt-1 text-xs leading-6">Terrain mapping observations suitable for broader-scale alignment and DEM workflows.</p></div>
            <div><span className="text-slate-200">IIRS</span><p className="mt-1 text-xs leading-6">Hyperspectral cubes handled through explicit dimensionality reduction before matching.</p></div>
          </div>
        </Panel>
      </div>

      {err && <pre className="mt-5 text-danger text-sm whitespace-pre-wrap border border-line p-4">{err}</pre>}
      {info && (
        <div className="mt-6 grid gap-4 lg:grid-cols-[.8fr_1.2fr]">
          <QualityCard items={info.quality?.items || []} />
          <Panel>
            <div className="lunar-section-label !mt-0">EXTRACTED METADATA</div>
            <pre className="mt-4 text-xs bg-black/30 p-4 border border-line overflow-auto max-h-[420px]">
              {JSON.stringify(info.metadata, null, 2)}
            </pre>
          </Panel>
        </div>
      )}
    </div>
  );
}

export function QualityCard({ items }: { items: any[] }) {
  return (
    <Panel>
      <div className="lunar-section-label !mt-0">DATA QUALITY</div>
      <div className="mt-4 divide-y divide-white/5">
        {items.map((it) => (
          <div key={it.key} className="flex items-start gap-3 py-3 text-sm">
            <span className={it.warn ? "text-warn" : it.ok ? "text-signal" : "text-danger"}>{it.warn ? "△" : it.ok ? "✓" : "×"}</span>
            <div><div className="text-slate-200">{it.label}</div>{it.detail && <div className="mt-1 text-xs text-slate-500">{it.detail}</div>}</div>
          </div>
        ))}
      </div>
    </Panel>
  );
}
