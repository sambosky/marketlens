"use client";

import { useEffect, useState } from "react";
import { apiDelete, apiGet, apiPost } from "@/lib/api";

type Item = { ticker: string; note: string | null };

export default function WatchlistPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [ticker, setTicker] = useState("");
  const [err, setErr] = useState("");

  async function refresh() {
    try {
      const d = await apiGet("/watchlist");
      setItems(d.data?.watchlist ?? []);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!ticker.trim()) return;
    await apiPost("/watchlist", { ticker });
    setTicker("");
    refresh();
  }
  async function remove(t: string) {
    await apiDelete(`/watchlist/${t}`);
    refresh();
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold text-white">Watchlist</h1>
      {err && <div className="card text-red-400">{err}</div>}
      <form className="flex gap-2" onSubmit={add}>
        <input
          className="input"
          placeholder="Ticker (e.g. NVDA)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
        />
        <button className="btn">Add</button>
      </form>
      <div className="card">
        {items.length === 0 ? (
          <div className="text-sm text-slate-500">Nothing watched yet.</div>
        ) : (
          <ul className="space-y-2">
            {items.map((i) => (
              <li key={i.ticker} className="flex items-center justify-between">
                <span className="font-medium text-white">{i.ticker}</span>
                <button
                  className="text-xs text-slate-400 hover:text-red-400"
                  onClick={() => remove(i.ticker)}
                >
                  remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
