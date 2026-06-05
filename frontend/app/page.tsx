import Chat from "@/components/Chat";

export default function HomePage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-white">Ask MarketLens</h1>
        <p className="text-sm text-slate-400">
          Questions route to SEC filings, news, live prices, or your portfolio —
          answers come back cited.
        </p>
      </div>
      <Chat />
    </div>
  );
}
