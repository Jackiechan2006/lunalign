import { Suspense, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Stars } from "@react-three/drei";
import type { Group, Mesh } from "three";

function LunarBody() {
  const moon = useRef<Mesh>(null);
  const orbit = useRef<Group>(null);

  useFrame((state, delta) => {
    if (moon.current) {
      moon.current.rotation.y += delta * 0.045;
      moon.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.16) * 0.025;
    }
    if (orbit.current) orbit.current.rotation.z -= delta * 0.035;
  });

  return (
    <group position={[1.45, -0.08, 0]} rotation={[0.08, -0.2, -0.08]}>
      <Float speed={0.65} rotationIntensity={0.08} floatIntensity={0.16}>
        <mesh ref={moon} castShadow receiveShadow>
          <sphereGeometry args={[1.72, 96, 96]} />
          <meshStandardMaterial color="#92989a" roughness={0.94} metalness={0.02} />
        </mesh>
        <mesh position={[-0.48, 0.7, 1.54]} rotation={[0.34, 0.1, -0.25]}>
          <torusGeometry args={[0.26, 0.025, 18, 80]} />
          <meshStandardMaterial color="#555c5e" roughness={1} />
        </mesh>
        <mesh position={[0.58, -0.5, 1.5]} rotation={[0.1, 0.35, 0.16]}>
          <torusGeometry args={[0.34, 0.035, 18, 80]} />
          <meshStandardMaterial color="#4b5254" roughness={1} />
        </mesh>
        <mesh position={[0.7, 0.58, 1.45]} rotation={[-0.18, 0.32, 0.12]}>
          <torusGeometry args={[0.18, 0.022, 18, 72]} />
          <meshStandardMaterial color="#5f6668" roughness={1} />
        </mesh>
      </Float>

      <group ref={orbit} rotation={[1.12, 0.1, 0.18]}>
        <mesh>
          <torusGeometry args={[2.52, 0.003, 10, 240]} />
          <meshBasicMaterial color="#7f8f92" transparent opacity={0.24} />
        </mesh>
        <mesh position={[2.48, 0.02, 0]}>
          <sphereGeometry args={[0.035, 18, 18]} />
          <meshBasicMaterial color="#d7e7e9" />
        </mesh>
      </group>
    </group>
  );
}

export default function LunarHeroScene() {
  return (
    <div className="luna-hero-scene" aria-hidden="true">
      <Canvas
        dpr={[1, 1.6]}
        camera={{ position: [0, 0.08, 6.6], fov: 43 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.36} />
        <directionalLight position={[-4, 4, 5]} intensity={3.2} color="#f2f6f5" />
        <pointLight position={[3, -1, 4]} intensity={1.2} color="#8da7aa" />
        <Suspense fallback={null}>
          <Stars radius={45} depth={28} count={680} factor={1.45} saturation={0} fade speed={0.18} />
          <LunarBody />
        </Suspense>
      </Canvas>
    </div>
  );
}
