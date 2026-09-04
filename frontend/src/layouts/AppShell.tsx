import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

const NAV = [
  ["/", "Dashboard"],
  ["/data", "Data"],
  ["/registration", "Registration"],
  ["/correspondences", "Correspondences"],
  ["/terrain", "3D Terrain"],
  ["/temporal", "4D Analysis"],
  ["/benchmarks", "Benchmarks"],
  ["/experiments", "Experiments"],
  ["/reports", "Reports"],
  ["/settings", "Settings"],
];

export default function AppShell() {
  const [navOpen, setNavOpen] = useState(false);

  return (
    <div className="min-h-screen flex bg-void text-slate-100">
      <button
        type="button"
        className="fixed right-4 top-4 z-30 border border-line bg-panel px-3 py-2 text-xs uppercase tracking-[0.18em] text-signal md:hidden"
        onClick={() => setNavOpen((open) => !open)}
        aria-expanded={navOpen}
        aria-controls="mission-navigation"
      >
        {navOpen ? "Close" : "Menu"}
      </button>
      <aside
        id="mission-navigation"
        className={`fixed inset-y-0 left-0 z-20 flex w-72 shrink-0 flex-col border-r border-line bg-[#081211]/95 px-5 py-6 backdrop-blur-xl transition-transform duration-300 md:sticky md:top-0 md:h-screen md:translate-x-0 ${
          navOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="mb-9 border-b border-line pb-6">
          <div className="mb-3 flex items-center gap-3">
            <span className="relative grid h-8 w-8 place-items-center rounded-full border border-dust/60 text-signal before:absolute before:inset-1 before:rounded-full before:border before:border-signal/50">
              <span className="h-1.5 w-1.5 rounded-full bg-signal shadow-[0_0_12px_#53e0b0]" />
            </span>
            <div>
              <div className="text-[10px] tracking-[0.28em] text-dust">CHANDRAYAAN-2</div>
              <div className="font-display text-xl tracking-[0.12em] text-white">LUNAALIGN</div>
            </div>
          </div>
          <p className="max-w-[210px] text-xs leading-relaxed text-slate-400">
            Multi-modal lunar image correspondence
          </p>
        </div>
        <div className="mb-3 text-[10px] tracking-[0.24em] text-slate-500">MISSION CONSOLE</div>
        <nav className="flex flex-col gap-1 text-sm" aria-label="Mission navigation">
          {NAV.map(([to, label]) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              onClick={() => setNavOpen(false)}
              className={({ isActive }) =>
                `group flex items-center justify-between border-l-2 px-3 py-2.5 transition-colors ${
                  isActive
                    ? "border-signal bg-signal/10 text-signal"
                    : "border-transparent text-slate-300 hover:border-dust/60 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              <span>{label}</span>
              <span className="text-[10px] text-slate-600 group-[.active]:text-signal">↗</span>
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto border-t border-line pt-5 text-[10px] leading-relaxed text-slate-500">
          <div className="mb-2 flex items-center gap-2 text-signal">
            <span className="h-1.5 w-1.5 rounded-full bg-signal shadow-[0_0_8px_#53e0b0]" />
            SYSTEM ONLINE
          </div>
          Core pipeline is offline classical computer vision. Deep models are optional and never auto-downloaded.
        </div>
      </aside>
      <main className="min-h-screen min-w-0 flex-1 lunar-grid">
        <Outlet />
      </main>
    </div>
  );
}
