import { useEffect, useState } from "react";
import { apiGet } from "../api/client";
import { PageHeader, Panel, StatusBadge } from "../components/ui";

export default function Settings() {
  const [cfg, setCfg] = useState<any>(null);
  useEffect(() => { apiGet("/config").then(setCfg).catch(() => setCfg({ error: "Backend offline" })); }, []);
  const offline = Boolean(cfg?.error);
  return (
    <div className="lunar-page">
      <PageHeader eyebrow="09 · SYSTEM" title="Configuration" description="Runtime configuration loaded from configs/default.yaml. Scientific defaults remain explicit and inspectable." action={<StatusBadge tone={offline ? "danger" : "signal"}>{offline ? "BACKEND OFFLINE" : "CONFIG LOADED"}</StatusBadge>} />
      <div className="grid gap-5 lg:grid-cols-[.7fr_1.3fr] mt-8">
        <Panel>
          <div className="lunar-section-label !mt-0">GUARDRAILS</div>
          <dl className="mt-5 space-y-5 text-sm">
            <div><dt className="text-slate-500">Random seed</dt><dd className="mt-1 text-slate-200">42 by default</dd></div>
            <div><dt className="text-slate-500">Deep model downloads</dt><dd className="mt-1 text-slate-200">Disabled</dd></div>
            <div><dt className="text-slate-500">Pipeline philosophy</dt><dd className="mt-1 text-slate-200">Local-first · evidence-first</dd></div>
          </dl>
        </Panel>
        <Panel>
          <div className="lunar-section-label !mt-0">ACTIVE CONFIGURATION</div>
          <pre className="mt-4 max-h-[600px] overflow-auto border border-line bg-black/30 p-5 text-xs leading-6 text-slate-300">{JSON.stringify(cfg, null, 2)}</pre>
        </Panel>
      </div>
    </div>
  );
}
