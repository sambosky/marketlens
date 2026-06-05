"use client";

import { useState } from "react";
import { streamAsk, type AgentEvent, type Citation } from "@/lib/sse";

type Msg = {
  role: "user" | "assistant";
  text: string;
  routing: string[];
  sources: Citation[];
  busy?: boolean;
};

const EXAMPLES = [
  "What were NVDA's latest reported margins?",
  "Why did TSLA move recently?",
  "What's AAPL's current price and P/E?",
  "How is my MSFT position doing?",
  "Add NVDA to my watchlist",
];

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  function patchLast(fn: (m: Msg) => Msg) {
    setMessages((prev) => {
      const copy = [...prev];
      copy[copy.length - 1] = fn(copy[copy.length - 1]);
      return copy;
    });
  }

  async function ask(question: string) {
    const q = question.trim();
    if (!q || busy) return;
    setInput("");
    setBusy(true);
    setMessages((m) => [
      ...m,
      { role: "user", text: q, routing: [], sources: [] },
      { role: "assistant", text: "", routing: [], sources: [], busy: true },
    ]);
    try {
      await streamAsk(q, (ev: AgentEvent) => {
        if (ev.type === "routing")
          patchLast((m) => ({
            ...m,
            routing: m.routing.includes(ev.tool) ? m.routing : [...m.routing, ev.tool],
          }));
        else if (ev.type === "token") patchLast((m) => ({ ...m, text: m.text + ev.text }));
        else if (ev.type === "final") patchLast((m) => ({ ...m, text: ev.text }));
        else if (ev.type === "sources") patchLast((m) => ({ ...m, sources: ev.items }));
      });
    } catch (e) {
      patchLast((m) => ({ ...m, text: `⚠️ ${(e as Error).message}` }));
    } finally {
      patchLast((m) => ({ ...m, busy: false }));
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      {messages.length === 0 && (
        <div className="card">
          <p className="mb-3 text-sm text-slate-400">
            Ask about fundamentals, news, live prices, or your portfolio. Try:
          </p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map((ex) => (
              <button key={ex} className="chip hover:border-accent" onClick={() => ask(ex)}>
                {ex}
              </button>
            ))}
          </div>
        </div>
      )}

      {messages.map((m, i) => (
        <div key={i} className={m.role === "user" ? "text-right" : ""}>
          {m.role === "user" ? (
            <span className="inline-block rounded-2xl bg-accent px-4 py-2 text-sm text-white">
              {m.text}
            </span>
          ) : (
            <div className="card">
              {m.routing.length > 0 && (
                <div className="mb-2 flex flex-wrap gap-2">
                  <span className="text-xs text-slate-500">Routing →</span>
                  {m.routing.map((t) => (
                    <span key={t} className="chip">
                      {t}
                    </span>
                  ))}
                </div>
              )}
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {m.text || (m.busy ? "Thinking…" : "")}
              </div>
              {m.sources.length > 0 && (
                <div className="mt-3 border-t border-edge pt-2">
                  <div className="mb-1 text-xs uppercase tracking-wide text-slate-500">
                    Cited sources
                  </div>
                  <ol className="list-decimal space-y-1 pl-5 text-xs text-slate-400">
                    {m.sources.map((c, j) => (
                      <li key={j}>
                        {c.url ? (
                          <a
                            className="text-accent hover:underline"
                            href={c.url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {c.source}
                          </a>
                        ) : (
                          c.source
                        )}
                        {c.detail ? ` — ${c.detail}` : ""}
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          )}
        </div>
      ))}

      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
      >
        <input
          className="input"
          placeholder="Ask about a stock…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className="btn" disabled={busy}>
          {busy ? "…" : "Ask"}
        </button>
      </form>
    </div>
  );
}
