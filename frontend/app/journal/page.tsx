"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";

type Entry = {
  id: number;
  ticker: string;
  action: string | null;
  note: string;
  rationale: string | null;
  created_at: string | null;
};

export default function JournalPage() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [ticker, setTicker] = useState("");
  const [note, setNote] = useState("");
  const [err, setErr] = useState("");

  async function refresh() {
    try {
      const d = await apiGet("/journal");
      setEntries(d.data?.entries ?? []);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!ticker.trim() || !note.trim()) return;
    await apiPost("/journal", { ticker, note });
    setTicker("");
    setNote("");
    refresh();
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-white">Trade journal</h1>
        <p className="text-xs text-slate-500">A research log — nothing is executed.</p>
      </div>
      {err && <div className="card text-red-400">{err}</div>}
      <form className="flex flex-wrap gap-2" onSubmit={add}>
        <input
          className="input max-w-[10rem]"
          placeholder="Ticker"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
        />
        <input
          className="input flex-1"
          placeholder="Note / rationale"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
        <button className="btn">Log</button>
      </form>
      <div className="space-y-2">
        {entries.map((e) => (
          <div key={e.id} className="card">
            <div className="flex items-center justify-between">
              <span className="font-medium text-white">{e.ticker}</span>
              <span className="text-xs text-slate-500">
                {e.created_at ? new Date(e.created_at).toLocaleString() : ""}
              </span>
            </div>
            <div className="text-sm text-slate-300">{e.note}</div>
          </div>
        ))}
        {entries.length === 0 && (
          <div className="card text-sm text-slate-500">No journal entries yet.</div>
        )}
      </div>
    </div>
  );
}
