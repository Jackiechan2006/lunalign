import { Suspense, useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Stars } from "@react-three/drei";
import * as THREE from "three";
import type { Group, Mesh } from "three";

function seeded(seed: number) {
  const x = Math.sin(seed * 91.173) * 10000;
  return x - Math.floor(x);
}

function LunarBody() {
  const moon = useRef<Group>(null);
  const orbit = useRef<Group>(null);

  const craters = useMemo(() => {
    const items: Array<{ p: [number, number, number]; q: [number, number, number, number]; r: number; depth: number }> = [];
    const radius = 1.72;

    for (let i = 0; i < 28; i++) {
      const theta = seeded(i + 1) * Math.PI * 2;
      const phi = Math.acos(0.25 + seeded(i + 13) * 0.7);
      const normal = new THREE.Vector3(
        Math.sin(phi) * Math.cos(theta),
        Math.cos(phi),
        Math.sin(phi) * Math.sin(theta)
      ).normalize();

      if (normal.z < -0.15) continue;

      const position = normal.clone().multiplyScalar(radius * 0.985);
      const quaternion = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal);
      items.push({
        p: [position.x, position.y, position.z],
        q: [quaternion.x, quaternion.y, quaternion.z, quaternion.w],
        r: 0.045 + seeded(i + 41) * 0.16,
        depth: 0.45 + seeded(i + 71) * 0.35,
      });
    }
    return items;
  }, []);

  useFrame((state, delta) => {
    if (moon.current) {
      moon.current.rotation.y += delta * 0.035;
      moon.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.12) * 0.018;
    }
    if (orbit.current) orbit.current.rotation.z -= delta * 0.012;
  });

  return (
    <group position={[1.45, -0.03, 0]} rotation={[0.04, -0.25, -0.04]}>
      <group ref={moon}>
        <mesh castShadow receiveShadow>
          <sphereGeometry args={[1.72, 128, 128]} />
          <meshStandardMaterial color="#8d9495" roughness={0.99} metalness={0} />
        </mesh>

        {craters.map((crater, index) => (
          <group key={index} position={crater.p} quaternion={crater.q as any}>
            <mesh scale={[1, 1, crater.depth]}>
              <sphereGeometry args={[crater.r, 24, 18, 0, Math.PI * 2, 0, Math.PI * 0.48]} />
              <meshStandardMaterial color="#555b5c" roughness={1} metalness={0} side={THREE.DoubleSide} />
            </mesh>
            <mesh position={[0, 0, crater.r * 0.028]}>
              <torusGeometry args={[crater.r * 0.82, crater.r * 0.075, 12, 36]} />
              <meshStandardMaterial color="#747b7c" roughness={1} metalness={0} />
            </mesh>
          </group>
        ))}
      </group>

      <group ref={orbit} rotation={[1.08, 0.12, 0.18]}>
        <mesh>
          <torusGeometry args={[2.5, 0.0028, 10, 220]} />
          <meshBasicMaterial color="#778285" transparent opacity={0.11} />
        </mesh>
        <mesh position={[2.46, 0.02, 0]}>
          <sphereGeometry args={[0.028, 16, 16]} />
          <meshBasicMaterial color="#d8e2e2" transparent opacity={0.62} />
        </mesh>
      </group>
    </group>
  );
}

export default function LunarHeroScene() {
  return (
    <div className="luna-hero-scene" aria-hidden="true">
      <Canvas
        dpr={[1, 1.5]}
        camera={{ position: [0, 0.06, 6.6], fov: 43 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.22} />
        <directionalLight position={[-4, 4.4, 5]} intensity={3.35} color="#f0f4f2" />
        <directionalLight position={[4, -2, -2]} intensity={0.34} color="#83918f" />
        <Suspense fallback={null}>
          <Stars radius={46} depth={30} count={760} factor={1.25} saturation={0} fade speed={0.12} />
          <LunarBody />
        </Suspense>
      </Canvas>
    </div>
  );
}
