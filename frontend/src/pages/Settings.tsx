import { useEffect, useState } from "react";
import { apiGet } from "../api/client";

export default function Settings() {
  const [cfg, setCfg] = useState<any>(null);
  useEffect(() => {
    apiGet("/config").then(setCfg).catch(() => setCfg({ error: "Backend offline" }));
  }, []);
  return (
    <div className="lunar-page max-w-3xl">
      <h1 className="text-3xl">Settings</h1>
      <p className="text-slate-400 mt-2">
        Loaded from <code>configs/default.yaml</code>. random_seed defaults to 42. Deep auto_download is false.
      </p>
      <pre className="mt-6 text-xs bg-black/40 border border-line p-4 overflow-auto">{JSON.stringify(cfg, null, 2)}</pre>
    </div>
  );
}
