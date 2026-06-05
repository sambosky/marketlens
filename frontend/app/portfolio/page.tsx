"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

type Pos = {
  ticker: string;
  quantity: number;
  cost_basis: number;
  price: number | null;
  market_value: number | null;
  unrealized_pnl: number | null;
  unrealized_pnl_pct: number | null;
};

const fmt = (n: number | null, d = 2) => (n == null ? "—" : n.toFixed(d));

export default function PortfolioPage() {
  const [rows, setRows] = useState<Pos[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    apiGet("/portfolio")
      .then((d) => setRows(d.data?.positions ?? []))
      .catch((e) => setErr((e as Error).message));
  }, []);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-white">Portfolio</h1>
        <p className="text-sm text-slate-400">Seeded demo holdings, marked to live prices.</p>
      </div>
      {err && <div className="card text-red-400">{err}</div>}
      <div className="card overflow-x-auto">
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Qty</th>
              <th>Cost</th>
              <th>Price</th>
              <th>Value</th>
              <th>P&amp;L</th>
              <th>P&amp;L %</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.ticker}>
                <td className="font-medium text-white">{r.ticker}</td>
                <td>{fmt(r.quantity, 0)}</td>
                <td>{fmt(r.cost_basis)}</td>
                <td>{fmt(r.price)}</td>
                <td>{fmt(r.market_value)}</td>
                <td className={(r.unrealized_pnl ?? 0) >= 0 ? "text-emerald-400" : "text-red-400"}>
                  {fmt(r.unrealized_pnl)}
                </td>
                <td className={(r.unrealized_pnl_pct ?? 0) >= 0 ? "text-emerald-400" : "text-red-400"}>
                  {fmt(r.unrealized_pnl_pct)}%
                </td>
              </tr>
            ))}
            {rows.length === 0 && !err && (
              <tr>
                <td colSpan={7} className="text-slate-500">
                  No positions. Run the ingest/seed step.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
