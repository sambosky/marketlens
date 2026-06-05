"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";

type Param = { type: string; required: boolean; default: unknown };
type Tool = { name: string; description: string; parameters: Record<string, Param> };

export default function ToolsPanel() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    apiGet("/tools")
      .then((d) => setTools(d.tools))
      .catch((e) => setErr((e as Error).message));
  }, []);

  if (err) return <div className="card text-red-400">Failed to load tools: {err}</div>;

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {tools.map((t) => (
        <ToolCard key={t.name} tool={t} />
      ))}
    </div>
  );
}

function ToolCard({ tool }: { tool: Tool }) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [result, setResult] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function run() {
    setBusy(true);
    setErr("");
    setResult(null);
    const args: Record<string, unknown> = {};
    for (const [k, p] of Object.entries(tool.parameters)) {
      const v = values[k];
      if (v === undefined || v === "") continue;
      args[k] =
        p.type === "number" ? Number(v) : p.type === "integer" ? parseInt(v, 10) : v;
    }
    try {
      setResult(await apiPost(`/tools/${tool.name}`, { arguments: args }));
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card space-y-2">
      <div className="font-mono text-sm text-white">{tool.name}</div>
      <p className="text-xs text-slate-400">{tool.description}</p>
      {Object.entries(tool.parameters).map(([k, p]) => (
        <input
          key={k}
          className="input"
          placeholder={`${k}${p.required ? " *" : ""} (${p.type})`}
          value={values[k] ?? ""}
          onChange={(e) => setValues((v) => ({ ...v, [k]: e.target.value }))}
        />
      ))}
      <button className="btn" onClick={run} disabled={busy}>
        {busy ? "Running…" : "Run"}
      </button>
      {err && <div className="text-xs text-red-400">{err}</div>}
      {result != null && (
        <pre className="max-h-64 overflow-auto rounded-lg bg-ink p-2 text-xs text-slate-300">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
