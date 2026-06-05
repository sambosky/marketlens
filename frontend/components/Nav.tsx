import Link from "next/link";

const LINKS: [string, string][] = [
  ["/", "Chat"],
  ["/tools", "Tools"],
  ["/portfolio", "Portfolio"],
  ["/watchlist", "Watchlist"],
  ["/alerts", "Alerts"],
  ["/journal", "Journal"],
];

export default function Nav() {
  return (
    <header className="border-b border-edge bg-panel">
      <div className="mx-auto flex max-w-5xl items-center gap-6 px-4 py-3">
        <span className="font-semibold text-white">📈 MarketLens</span>
        <nav className="flex flex-wrap gap-4 text-sm">
          {LINKS.map(([href, label]) => (
            <Link key={href} href={href} className="text-slate-300 hover:text-white">
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
