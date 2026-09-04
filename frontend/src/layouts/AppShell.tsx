import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";

const NAV = [
  ["/workspace", "Overview", "01"],
  ["/data", "Data", "02"],
  ["/registration", "Registration", "03"],
  ["/correspondences", "Correspondences", "04"],
  ["/terrain", "3D Terrain", "05"],
  ["/temporal", "4D Analysis", "06"],
  ["/benchmarks", "Benchmarks", "07"],
  ["/experiments", "Experiments", "08"],
  ["/reports", "Reports", "09"],
  ["/settings", "Settings", "10"],
];

export default function AppShell() {
  const [navOpen, setNavOpen] = useState(false);

  return (
    <div className="workspace-shell">
      {navOpen && <button className="workspace-scrim" aria-label="Close navigation" onClick={() => setNavOpen(false)} />}
      <aside id="mission-navigation" className={`workspace-sidebar ${navOpen ? "is-open" : ""}`}>
        <Link className="workspace-brand" to="/">
          <span className="workspace-brand-mark"><span /></span>
          <span><strong>LUNAALIGN</strong><small>MISSION WORKSPACE</small></span>
        </Link>

        <div className="workspace-nav-label">OPERATIONS</div>
        <nav className="workspace-nav" aria-label="Mission navigation">
          {NAV.map(([to, label, index]) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setNavOpen(false)}
              className={({ isActive }) => `workspace-nav-item ${isActive ? "is-active" : ""}`}
            >
              <span className="workspace-nav-index">{index}</span>
              <span>{label}</span>
              <span className="workspace-nav-arrow">↗</span>
            </NavLink>
          ))}
        </nav>

        <div className="workspace-system">
          <div><span className="workspace-online" /> PIPELINE READY</div>
          <p>Local-first correspondence workflow. Deep models remain optional.</p>
        </div>
      </aside>

      <section className="workspace-main">
        <header className="workspace-topbar">
          <button
            type="button"
            className="workspace-menu"
            onClick={() => setNavOpen((open) => !open)}
            aria-expanded={navOpen}
            aria-controls="mission-navigation"
          >
            <span /> <span />
            <b>Menu</b>
          </button>
          <div className="workspace-topbar-context">
            <span>CHANDRAYAAN-2</span>
            <i />
            <span>LUNAR IMAGE CORRESPONDENCE</span>
          </div>
          <Link className="workspace-exit" to="/">Mission view ↗</Link>
        </header>
        <main className="workspace-content"><Outlet /></main>
      </section>
    </div>
  );
}
