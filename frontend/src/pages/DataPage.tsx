import { FormEvent, useState } from "react";
import { apiPost } from "../api/client";

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
    <div className="lunar-page max-w-4xl">
      <h1 className="text-3xl">Data intake</h1>
      <p className="text-slate-400 mt-2">
        PNG, JPEG, TIFF/GeoTIFF, NPY hyperspectral cubes. Missing metadata is shown as missing — never invented.
      </p>
      <form onSubmit={onSubmit} className="mt-6 space-y-4 border border-line bg-panel p-6 rounded-xl">
        <label className="block text-sm">
          Sensor hint
          <select name="sensor" value={sensor} onChange={(e) => setSensor(e.target.value)} className="mt-1 w-full bg-void border border-line p-2 rounded">
            <option>OHRC</option>
            <option>TMC</option>
            <option>IIRS</option>
          </select>
        </label>
        <label className="block text-sm">
          Image / cube
          <input name="image" type="file" required className="mt-1 block" />
        </label>
        <button className="px-4 py-2 bg-signal text-void rounded">Inspect</button>
      </form>
      {err && <pre className="mt-4 text-danger text-sm whitespace-pre-wrap">{err}</pre>}
      {info && (
        <div className="mt-6 grid gap-4">
          <QualityCard items={info.quality?.items || []} />
          <pre className="text-xs bg-black/40 p-4 rounded border border-line overflow-auto">
            {JSON.stringify(info.metadata, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export function QualityCard({ items }: { items: any[] }) {
  return (
    <div className="border border-line rounded-xl p-4 bg-black/30">
      <div className="text-xs tracking-widest text-dust mb-2">DATA QUALITY</div>
      {items.map((it) => (
        <div key={it.key} className="flex gap-2 text-sm py-1">
          <span>{it.warn ? "⚠" : it.ok ? "✓" : "✕"}</span>
          <span>{it.label}</span>
          {it.detail && <span className="text-slate-500">{it.detail}</span>}
        </div>
      ))}
    </div>
  );
}
