import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./layouts/AppShell";
import Dashboard from "./pages/Dashboard";
import DataPage from "./pages/DataPage";
import Registration from "./pages/Registration";
import Correspondences from "./pages/Correspondences";
import Terrain from "./pages/Terrain";
import Temporal from "./pages/Temporal";
import Benchmarks from "./pages/Benchmarks";
import Experiments from "./pages/Experiments";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import Demo from "./pages/Demo";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/data" element={<DataPage />} />
        <Route path="/registration" element={<Registration />} />
        <Route path="/correspondences" element={<Correspondences />} />
        <Route path="/terrain" element={<Terrain />} />
        <Route path="/temporal" element={<Temporal />} />
        <Route path="/benchmarks" element={<Benchmarks />} />
        <Route path="/experiments" element={<Experiments />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/demo" element={<Demo />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
