export type Sensor = "OHRC" | "TMC" | "IIRS";

const API = "/api";

export async function apiGet<T>(path: string): Promise<T> {
  const r = await fetch(`${API}${path}`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function apiPost<T>(path: string, body?: BodyInit, headers?: HeadersInit): Promise<T> {
  const r = await fetch(`${API}${path}`, { method: "POST", body, headers });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export function fileUrl(jobId: string, name: string) {
  return `${API}/jobs/${jobId}/files/${name}`;
}

export function saveSession(jobId: string, result: unknown) {
  sessionStorage.setItem("lunaalign_job", jobId);
  sessionStorage.setItem("lunaalign_result", JSON.stringify(result));
}

export function loadSession(): { jobId: string | null; result: any } {
  return {
    jobId: sessionStorage.getItem("lunaalign_job"),
    result: JSON.parse(sessionStorage.getItem("lunaalign_result") || "null"),
  };
}
