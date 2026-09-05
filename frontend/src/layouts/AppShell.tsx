import { useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

const NAV = [
  ["/data", "Data", "01"],
  ["/registration", "Registration", "02"],
  ["/correspondences", "Correspondences", "03"],
  ["/terrain", "3D Terrain", "04"],
  ["/temporal", "4D Analysis", "05"],
  ["/benchmarks", "Benchmarks", "06"],
  ["/experiments", "Experiments", "07"],
  ["/reports", "Reports", "08"],
  ["/settings", "Settings", "09"],
];

export default function AppShell() {
  const [navOpen, setNavOpen] = useState(false);
  const location = useLocation();
  const isLanding = location.pathname === "/";

  if (isLanding) return <main className="luna-public"><Outlet /></main>;

  return (
    <div className="luna-workspace-shell">
      <button
        type="button"
        className="luna-mobile-menu"
        onClick={() => setNavOpen((open) => !open)}
        aria-expanded={navOpen}
        aria-controls="mission-navigation"
      >
        {navOpen ? "CLOSE" : "MENU"}
      </button>

      <aside id="mission-navigation" className={`luna-sidebar ${navOpen ? "is-open" : ""}`}>
        <NavLink className="luna-sidebar-brand" to="/" onClick={() => setNavOpen(false)}>
          <span className="luna-mark"><span /></span>
          <span><strong>LUNAALIGN</strong><small>MISSION WORKSPACE</small></span>
        </NavLink>

        <div className="luna-sidebar-label">ANALYSIS MODULES</div>
        <nav aria-label="Mission navigation">
          {NAV.map(([to, label, index]) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setNavOpen(false)}
              className={({ isActive }) => isActive ? "active" : ""}
            >
              <span className="luna-nav-index">{index}</span>
              <span>{label}</span>
              <b>↗</b>
            </NavLink>
          ))}
        </nav>

        <div className="luna-sidebar-footer">
          <span><i /> SYSTEM ONLINE</span>
          <p>Local-first scientific pipeline<br />Deep models remain optional</p>
        </div>
      </aside>

      {navOpen && <button className="luna-nav-scrim" aria-label="Close navigation" onClick={() => setNavOpen(false)} />}

      <div className="luna-workspace-main">
        <header className="luna-workspace-topbar">
          <span>CHANDRAYAAN-2 / LUNAR CORRESPONDENCE</span>
          <NavLink to="/">MISSION OVERVIEW ↗</NavLink>
        </header>
        <main className="lunar-grid"><Outlet /></main>
      </div>
    </div>
  );
}
