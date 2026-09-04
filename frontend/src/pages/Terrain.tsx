import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useMemo, useState } from "react";
import * as THREE from "three";
import { loadSession } from "../api/client";

export default function Terrain() {
  const { result } = loadSession();
  const [showPts, setShowPts] = useState(true);
  const [wireframe, setWireframe] = useState(false);
  const [picked, setPicked] = useState<{ x: number; y: number; z: number } | null>(null);

  if (!result) {
    return (
      <div className="p-10 text-slate-400">
        <h1 className="text-2xl text-signal mb-2">No Registration Session Found</h1>
        <p>Please run a registration job first from the Registration tab.</p>
      </div>
    );
  }

  const dem = result.dem;
  const mesh = result.mesh;

  return (
    <div className="p-8 h-[calc(100vh-2rem)] flex flex-col">
      {/* Header Bar */}
      <div className="flex flex-wrap justify-between items-center gap-4 bg-panel p-4 rounded-xl border border-line mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100">3D Interactive Lunar Terrain</h1>
            <span className="px-2 py-0.5 text-xs bg-signal/20 text-signal rounded-full border border-signal/40 font-mono">
              {dem?.kind || "DERIVED DEM"}
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Topographic 3D surface mesh derived from image illumination & elevation geometry.
          </p>
        </div>

        {/* View Controls */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <label className="flex items-center gap-1.5 cursor-pointer bg-void px-3 py-1.5 rounded border border-line hover:border-signal/50">
            <input
              type="checkbox"
              checked={showPts}
              onChange={(e) => setShowPts(e.target.checked)}
              className="accent-signal"
            />
            Show 3D Inliers ({result.correspondences?.length || 0})
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer bg-void px-3 py-1.5 rounded border border-line hover:border-signal/50">
            <input
              type="checkbox"
              checked={wireframe}
              onChange={(e) => setWireframe(e.target.checked)}
              className="accent-signal"
            />
            Wireframe Mesh
          </label>
        </div>
      </div>

      {/* Main 3D Canvas Area */}
      <div className="relative flex-1 border border-line rounded-xl overflow-hidden bg-gradient-to-b from-slate-950 to-black">
        {/* Telemetry Overlay Panel */}
        <div className="absolute top-4 left-4 z-10 bg-slate-900/80 backdrop-blur-md p-4 rounded-xl border border-slate-700/50 text-xs w-64 shadow-2xl">
          <div className="text-signal tracking-widest font-mono font-bold mb-2 uppercase text-[10px]">
            Terrain Telemetry
          </div>
          <div className="space-y-1.5 font-mono text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-500">Source:</span>
              <span className="text-signal font-semibold">{dem?.kind || "DERIVED"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Grid Resolution:</span>
              <span>{mesh?.width || 0} × {mesh?.height || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Min Elevation:</span>
              <span className="text-cyan-400">{mesh?.z_min?.toFixed(1) || 0} m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Max Elevation:</span>
              <span className="text-amber-400">{mesh?.z_max?.toFixed(1) || 0} m</span>
            </div>
            <div className="flex justify-between border-t border-slate-700/60 pt-1 mt-1">
              <span className="text-slate-500">Total Relief:</span>
              <span className="text-emerald-400">
                {((mesh?.z_max || 0) - (mesh?.z_min || 0)).toFixed(1)} m
              </span>
            </div>
          </div>
        </div>

        {/* Selected Point HUD */}
        {picked ? (
          <div className="absolute bottom-4 left-4 z-10 bg-signal/10 backdrop-blur-md border border-signal/40 p-3 rounded-xl text-xs font-mono text-signal shadow-lg flex items-center gap-4">
            <div className="font-bold">PROBED SURFACE POINT:</div>
            <div>X: <span className="text-slate-100 font-semibold">{picked.x.toFixed(2)}</span></div>
            <div>Y: <span className="text-slate-100 font-semibold">{picked.y.toFixed(2)}</span></div>
            <div>Elevation Z: <span className="text-amber-300 font-semibold">{picked.z.toFixed(2)}m</span></div>
          </div>
        ) : (
          <div className="absolute bottom-4 left-4 z-10 bg-slate-900/60 backdrop-blur-sm border border-slate-800 p-2.5 rounded-lg text-xs font-mono text-slate-400">
            💡 Click anywhere on the 3D terrain surface to probe elevation coordinates.
          </div>
        )}

        {/* Legend */}
        <div className="absolute bottom-4 right-4 z-10 bg-slate-900/80 backdrop-blur-md p-3 rounded-xl border border-slate-700/50 text-[11px] font-mono flex items-center gap-3">
          <span className="text-slate-400">Elevation:</span>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-cyan-600 inline-block"></span> Low
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span> Mid
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-amber-400 inline-block"></span> High
          </div>
        </div>

        {/* 3D R3F Canvas */}
        <Canvas camera={{ position: [35, 45, 60], fov: 45 }}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[30, 50, 20]} intensity={1.5} castShadow />
          <pointLight position={[-20, -20, 20]} intensity={0.5} color="#00e5ff" />

          {mesh && <TerrainMesh mesh={mesh} wireframe={wireframe} onPick={setPicked} />}

          {showPts &&
            result.correspondences?.map((c: any) => {
              const cx = (c.ref[0] / (result.scale?.image_shape_ref?.[1] || 384) - 0.5) * 40;
              const cy = (c.ref[1] / (result.scale?.image_shape_ref?.[0] || 384) - 0.5) * 40;
              const cz = ((c.ncc || 0.5) * 8);
              return (
                <mesh key={c.id} position={[cx, cz + 1, cy]}>
                  <sphereGeometry args={[0.4, 16, 16]} />
                  <meshStandardMaterial
                    color="#00ffcc"
                    emissive="#00ffcc"
                    emissiveIntensity={0.6}
                    roughness={0.2}
                  />
                </mesh>
              );
            })}

          <OrbitControls makeDefault enableDamping dampingFactor={0.05} minDistance={10} maxDistance={150} />
        </Canvas>
      </div>
    </div>
  );
}

function TerrainMesh({
  mesh,
  wireframe,
  onPick,
}: {
  mesh: any;
  wireframe: boolean;
  onPick: (p: any) => void;
}) {
  const { geometry } = useMemo(() => {
    const w = mesh.width;
    const h = mesh.height;
    const pos = mesh.positions as number[][];
    const geom = new THREE.PlaneGeometry(40, 40, w - 1, h - 1);

    const positions = geom.attributes.position;
    const zMin = mesh.z_min ?? 0;
    const zMax = mesh.z_max ?? 1;
    const zRange = Math.max(zMax - zMin, 1e-6);

    const colors = new Float32Array(pos.length * 3);

    for (let i = 0; i < pos.length; i++) {
      const zRaw = pos[i][2];
      const normZ = (zRaw - zMin) / zRange;
      const heightVal = normZ * 8; // Displace height

      // Set Z coordinate in PlaneGeometry
      positions.setZ(i, heightVal);

      // Color mapping: Low (cyan/navy) -> Mid (emerald/gold) -> High (amber/white)
      const color = new THREE.Color();
      if (normZ < 0.35) {
        color.setHSL(0.55, 0.8, 0.2 + normZ * 0.4); // Deep Cyan
      } else if (normZ < 0.7) {
        color.setHSL(0.35, 0.7, 0.3 + normZ * 0.4); // Emerald Gold
      } else {
        color.setHSL(0.12, 0.9, 0.5 + normZ * 0.4); // Amber White
      }

      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    geom.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geom.computeVertexNormals();

    return { geometry: geom };
  }, [mesh]);

  return (
    <mesh
      geometry={geometry}
      rotation={[-Math.PI / 2, 0, 0]}
      onClick={(e) => {
        e.stopPropagation();
        onPick({ x: e.point.x, y: e.point.z, z: e.point.y });
      }}
    >
      <meshStandardMaterial
        vertexColors
        wireframe={wireframe}
        roughness={0.4}
        metalness={0.1}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

