"use client";

import { Canvas, useFrame, useLoader } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import { useRef, useMemo, Suspense } from "react";
import * as THREE from "three";

function seededUnit(seed: number) {
  const value = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return value - Math.floor(value);
}

/* ----------------------------------------------------------------
   Bridge as a 3D plane that lives in space, tilts with the mouse,
   and recedes on scroll. Gives the flat image real depth.
-----------------------------------------------------------------*/
function BridgePlane({ scroll }: { scroll: React.MutableRefObject<number> }) {
  const texture = useLoader(THREE.TextureLoader, "/assets/ctf-bridge.webp");
  const groupRef = useRef<THREE.Group>(null);
  const matRef = useRef<THREE.MeshBasicMaterial>(null);

  // keep aspect ratio of the bridge (1568x926)
  const aspect = 1568 / 926;
  const h = 7.5;
  const w = h * aspect;

  useFrame((state) => {
    if (!groupRef.current) return;
    const px = state.pointer.x;
    const py = state.pointer.y;
    // smooth tilt toward pointer
    groupRef.current.rotation.y += (px * 0.25 - groupRef.current.rotation.y) * 0.05;
    groupRef.current.rotation.x += (-py * 0.12 - groupRef.current.rotation.x) * 0.05;
    // recede + fade on scroll
    const s = scroll.current;
    groupRef.current.position.z = -s * 6;
    groupRef.current.position.x = 3.2 + s * 2;
    if (matRef.current) matRef.current.opacity = 1 - s * 0.9;
  });

  return (
    <group ref={groupRef} position={[3.2, 0, 0]}>
      <mesh>
        <planeGeometry args={[w, h]} />
        <meshBasicMaterial
          ref={matRef}
          map={texture}
          transparent
          toneMapped={false}
        />
      </mesh>
    </group>
  );
}

/* Glossy floating brand balls */
function Ball({
  position,
  color,
  scale = 1,
  speed = 1,
}: {
  position: [number, number, number];
  color: string;
  scale?: number;
  speed?: number;
}) {
  return (
    <Float speed={speed} rotationIntensity={1.2} floatIntensity={2.4}>
      <mesh position={position} scale={scale}>
        <sphereGeometry args={[1, 48, 48]} />
        <meshStandardMaterial
          color={color}
          roughness={0.12}
          metalness={0.2}
          emissive={color}
          emissiveIntensity={0.25}
        />
      </mesh>
    </Float>
  );
}

function Particles({ count = 500 }: { count?: number }) {
  const ref = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const p = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      p[i * 3] = (seededUnit(i * 3) - 0.5) * 22;
      p[i * 3 + 1] = (seededUnit(i * 3 + 1) - 0.5) * 14;
      p[i * 3 + 2] = (seededUnit(i * 3 + 2) - 0.5) * 10;
    }
    return p;
  }, [count]);
  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    return g;
  }, [positions]);
  useFrame((state) => {
    if (ref.current) ref.current.rotation.y = state.clock.elapsedTime * 0.02;
  });
  return (
    <points ref={ref} geometry={geo}>
      <pointsMaterial
        size={0.03}
        color="#ffffff"
        transparent
        opacity={0.45}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
}

function Rig() {
  useFrame((state) => {
    // subtle camera drift toward pointer
    state.camera.position.x += (state.pointer.x * 0.6 - state.camera.position.x) * 0.04;
    state.camera.position.y += (state.pointer.y * 0.4 - state.camera.position.y) * 0.04;
    state.camera.lookAt(0, 0, 0);
  });
  return null;
}

export function HeroScene({
  scroll,
}: {
  scroll: React.MutableRefObject<number>;
}) {
  return (
    <Canvas
      camera={{ position: [0, 0, 9], fov: 50 }}
      gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
      dpr={[1, 1.75]}
    >
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 5, 5]} intensity={2.2} color="#ff7a18" />
      <pointLight position={[-5, -2, 3]} intensity={3.5} color="#5b2eff" />
      <pointLight position={[3, 3, -4]} intensity={3} color="#ff0a9c" />
      <pointLight position={[0, -4, 2]} intensity={2} color="#ffc400" />

      <Suspense fallback={null}>
        <BridgePlane scroll={scroll} />
      </Suspense>

      <Ball position={[-3.4, -1.8, 1]} color="#ff2d4f" scale={0.5} speed={1.3} />
      <Ball position={[-4.2, 1.6, 0.5]} color="#ffc400" scale={0.4} speed={1.5} />
      <Ball position={[-2.4, -2.4, 1.5]} color="#5b2eff" scale={0.55} speed={1} />
      <Ball position={[0.5, 2.6, -1]} color="#ff0a9c" scale={0.35} speed={1.6} />

      <Particles />
      <Rig />
    </Canvas>
  );
}
