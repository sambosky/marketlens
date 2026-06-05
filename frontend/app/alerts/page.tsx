"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";

type Alert = {
  id: number;
  ticker: string;
  threshold: number;
  direction: string;
  status: string;
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [ticker, setTicker] = useState("");
  const [threshold, setThreshold] = useState("");
  const [direction, setDirection] = useState("below");
  const [err, setErr] = useState("");

  async function refresh() {
    try {
      const d = await apiGet("/alerts");
      setAlerts(d.data?.alerts ?? []);
    } catch (e) {
      setErr((e as Error).message);
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!ticker.trim() || !threshold) return;
    await apiPost("/alerts", { ticker, threshold: Number(threshold), direction });
    setTicker("");
    setThreshold("");
    refresh();
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-white">Price alerts</h1>
        <p className="text-xs text-slate-500">Local reminders — no brokerage orders.</p>
      </div>
      {err && <div className="card text-red-400">{err}</div>}
      <form className="flex flex-wrap gap-2" onSubmit={add}>
        <input
          className="input max-w-[10rem]"
          placeholder="Ticker"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
        />
        <select
          className="input max-w-[8rem]"
          value={direction}
          onChange={(e) => setDirection(e.target.value)}
        >
          <option value="below">below</option>
          <option value="above">above</option>
        </select>
        <input
          className="input max-w-[10rem]"
          placeholder="Threshold"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
        />
        <button className="btn">Set alert</button>
      </form>
      <div className="card overflow-x-auto">
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Direction</th>
              <th>Threshold</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => (
              <tr key={a.id}>
                <td className="font-medium text-white">{a.ticker}</td>
                <td>{a.direction}</td>
                <td>{a.threshold}</td>
                <td>{a.status}</td>
              </tr>
            ))}
            {alerts.length === 0 && (
              <tr>
                <td colSpan={4} className="text-slate-500">
                  No alerts set.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
