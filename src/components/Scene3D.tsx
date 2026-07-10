"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import { useRef, useMemo } from "react";
import * as THREE from "three";

function seededUnit(seed: number) {
  const value = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return value - Math.floor(value);
}

/* Glossy floating sphere — like the brand's color balls */
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
    <Float speed={speed} rotationIntensity={1} floatIntensity={2}>
      <mesh position={position} scale={scale}>
        <sphereGeometry args={[1, 64, 64]} />
        <meshStandardMaterial
          color={color}
          roughness={0.15}
          metalness={0.1}
          emissive={color}
          emissiveIntensity={0.15}
        />
      </mesh>
    </Float>
  );
}

/* Twisted ribbon (echoes the brand Z mark) */
function Ribbon() {
  const ref = useRef<THREE.Mesh>(null);

  const geometry = useMemo(() => {
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(-2, 2.5, 0),
      new THREE.Vector3(1.2, 1.2, -1),
      new THREE.Vector3(-1, 0, 1),
      new THREE.Vector3(1.2, -1.2, -1),
      new THREE.Vector3(-2, -2.5, 0),
    ]);
    return new THREE.TubeGeometry(curve, 120, 0.42, 24, false);
  }, []);

  useFrame((state) => {
    if (!ref.current) return;
    const t = state.clock.elapsedTime;
    ref.current.rotation.y = t * 0.25;
    ref.current.rotation.z = Math.sin(t * 0.3) * 0.15;
    ref.current.position.x += (state.pointer.x * 0.6 - ref.current.position.x) * 0.04;
    ref.current.position.y += (state.pointer.y * 0.4 - ref.current.position.y) * 0.04;
  });

  return (
    <mesh ref={ref} geometry={geometry}>
      <meshStandardMaterial
        color="#ff0a9c"
        roughness={0.1}
        metalness={0.3}
        emissive="#5b2eff"
        emissiveIntensity={0.3}
      />
    </mesh>
  );
}

function Particles({ count = 600 }: { count?: number }) {
  const ref = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const p = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 6 + seededUnit(i * 3) * 8;
      const t = seededUnit(i * 3 + 1) * Math.PI * 2;
      const ph = Math.acos(2 * seededUnit(i * 3 + 2) - 1);
      p[i * 3] = r * Math.sin(ph) * Math.cos(t);
      p[i * 3 + 1] = r * Math.sin(ph) * Math.sin(t);
      p[i * 3 + 2] = r * Math.cos(ph);
    }
    return p;
  }, [count]);

  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    return g;
  }, [positions]);

  useFrame((state) => {
    if (ref.current) ref.current.rotation.y = state.clock.elapsedTime * 0.03;
  });

  return (
    <points ref={ref} geometry={geo}>
      <pointsMaterial
        size={0.035}
        color="#ffffff"
        transparent
        opacity={0.5}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
}

export function Scene3D() {
  return (
    <Canvas
      camera={{ position: [0, 0, 8], fov: 50 }}
      gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
      dpr={[1, 1.75]}
    >
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 5, 5]} intensity={2.5} color="#ff7a18" />
      <pointLight position={[-5, -2, 3]} intensity={3.5} color="#5b2eff" />
      <pointLight position={[3, 3, -4]} intensity={3} color="#ff0a9c" />
      <pointLight position={[0, -4, 2]} intensity={2} color="#ffc400" />

      <Ribbon />
      <Ball position={[3.2, 1.8, -1]} color="#ff2d4f" scale={0.7} speed={1.2} />
      <Ball position={[-3.4, -1.2, -0.5]} color="#5b2eff" scale={0.9} speed={0.9} />
      <Ball position={[3, -2, 0.5]} color="#ffc400" scale={0.55} speed={1.4} />
      <Ball position={[-2.8, 2.4, -1.5]} color="#ff0a9c" scale={0.5} speed={1.1} />

      <Particles />
    </Canvas>
  );
}
