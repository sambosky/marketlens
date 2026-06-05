import ToolsPanel from "@/components/ToolsPanel";

export default function ToolsPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-white">Tools</h1>
        <p className="text-sm text-slate-400">
          The skills the agent routes between — invoke any of them directly. The
          same functions are exposed over MCP for Claude Desktop / Cursor.
        </p>
      </div>
      <ToolsPanel />
    </div>
  );
}
