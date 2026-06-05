export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function handle(res: Response) {
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json();
}

export async function apiGet(path: string) {
  return handle(await fetch(`${API_BASE}/api${path}`, { cache: "no-store" }));
}

export async function apiPost(path: string, body: unknown) {
  return handle(
    await fetch(`${API_BASE}/api${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

export async function apiDelete(path: string) {
  return handle(await fetch(`${API_BASE}/api${path}`, { method: "DELETE" }));
}
