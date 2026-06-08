import { API_BASE } from "./api";

export type AgentEvent =
  | { type: "routing"; tool: string; args: Record<string, unknown> }
  | { type: "tool_result"; tool: string }
  | { type: "token"; text: string }
  | { type: "sources"; items: Citation[] }
  | { type: "final"; text: string }
  | { type: "done" };

export type Citation = { source: string; url?: string | null; detail?: string | null };

function parseBlock(block: string): AgentEvent | null {
  let data = "";
  for (const line of block.split("\n")) {
    if (line.startsWith("data:")) data += line.slice(5).trim();
  }
  if (!data) return null;
  try {
    return JSON.parse(data) as AgentEvent;
  } catch {
    return null;
  }
}

export async function streamAsk(
  question: string,
  onEvent: (event: AgentEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
    signal,
  });
  if (!res.body) throw new Error("No response stream");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    // sse-starlette uses CRLF; normalize so the "\n\n" event boundary matches.
    buffer += decoder.decode(value, { stream: true }).replace(/\r/g, "");
    let idx: number;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const block = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const event = parseBlock(block);
      if (event) onEvent(event);
    }
  }
}
