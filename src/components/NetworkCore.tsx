"use client";

import { Canvas, useFrame, useLoader } from "@react-three/fiber";
import { Suspense, useEffect, useMemo, useRef } from "react";
import type { MutableRefObject } from "react";
import * as THREE from "three";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

type ScrollRef = MutableRefObject<number>;

const COLORS = {
  magenta: "#ff0a9c",
  blue: "#5b2eff",
  orange: "#ff7a18",
  yellow: "#ffc400",
  red: "#ff2d4f",
};

const NODE_POSITIONS: [number, number, number][] = [
  [-3.8, 1.9, 0.1],
  [-2.6, -1.2, 0.7],
  [-1.2, 1.0, -0.6],
  [-0.2, -2.0, 0.2],
  [1.0, 1.6, 0.8],
  [2.4, -0.4, -0.5],
  [3.7, 1.1, 0.3],
  [3.2, -2.0, 0.9],
  [0.0, 0.0, 1.2],
  [-4.4, -2.2, -0.4],
  [4.4, 2.3, -0.7],
  [1.5, -2.9, -0.2],
];

const EDGES: [number, number][] = [
  [0, 2],
  [2, 4],
  [4, 6],
  [1, 3],
  [3, 5],
  [5, 7],
  [2, 8],
  [8, 5],
  [8, 3],
  [0, 1],
  [6, 10],
  [7, 11],
  [9, 1],
  [4, 8],
];

function smoothstep(edge0: number, edge1: number, x: number) {
  const t = Math.min(1, Math.max(0, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
}

function usePageScrollProgress(enabled: boolean) {
  const scroll = useRef(0);

  useEffect(() => {
    if (!enabled) return;

    let frame = 0;
    const update = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      scroll.current = max > 0 ? window.scrollY / max : 0;
      frame = requestAnimationFrame(update);
    };

    update();
    return () => cancelAnimationFrame(frame);
  }, [enabled]);

  return scroll;
}

function BridgePortal({ scroll }: { scroll: ScrollRef }) {
  const texture = useLoader(THREE.TextureLoader, "/assets/ctf-bridge.webp");
  const groupRef = useRef<THREE.Group>(null);
  const matRef = useRef<THREE.MeshBasicMaterial>(null);
  const aspect = 1568 / 926;
  const height = 7.2;

  useFrame((state) => {
    if (!groupRef.current || !matRef.current) return;
    const progress = scroll.current;
    const exit = smoothstep(0.02, 0.18, progress);
    const pointerX = state.pointer.x;
    const pointerY = state.pointer.y;

    groupRef.current.position.x = 2.9 + exit * 1.5;
    groupRef.current.position.z = -exit * 5.5;
    groupRef.current.rotation.y += (pointerX * 0.18 - groupRef.current.rotation.y) * 0.04;
    groupRef.current.rotation.x += (-pointerY * 0.1 - groupRef.current.rotation.x) * 0.04;
    matRef.current.opacity = 0.82 * (1 - exit);
  });

  return (
    <group ref={groupRef} position={[2.9, 0, 0]}>
      <mesh>
        <planeGeometry args={[height * aspect, height]} />
        <meshBasicMaterial
          ref={matRef}
          map={texture}
          transparent
          toneMapped={false}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
}

function NetworkMap({
  scroll,
  reducedMotion,
}: {
  scroll: ScrollRef;
  reducedMotion: boolean;
}) {
  const groupRef = useRef<THREE.Group>(null);
  const lineRef = useRef<THREE.LineSegments>(null);
  const packetRef = useRef<THREE.InstancedMesh>(null);
  const pulseMatRef = useRef<THREE.MeshBasicMaterial>(null);
  const packetMatrix = useMemo(() => new THREE.Object3D(), []);
  const nodeColors = [
    COLORS.magenta,
    COLORS.blue,
    COLORS.orange,
    COLORS.yellow,
    COLORS.red,
  ];

  const lineGeometry = useMemo(() => {
    const points: number[] = [];
    EDGES.forEach(([a, b]) => {
      points.push(...NODE_POSITIONS[a], ...NODE_POSITIONS[b]);
    });
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.Float32BufferAttribute(points, 3));
    return geometry;
  }, []);

  useFrame((state) => {
    const progress = scroll.current;
    const time = reducedMotion ? 0 : state.clock.elapsedTime;
    const portal = 1 - smoothstep(0.02, 0.18, progress);
    const attack = smoothstep(0.26, 0.58, progress);
    const capture = smoothstep(0.68, 0.94, progress);

    if (groupRef.current) {
      groupRef.current.visible = portal < 0.98;
      groupRef.current.rotation.y = time * 0.08 + progress * Math.PI * 1.35;
      groupRef.current.rotation.x = Math.sin(progress * Math.PI) * 0.42;
      groupRef.current.position.x = 1.7 - progress * 2.4;
      groupRef.current.position.y = -0.15 + Math.sin(progress * Math.PI * 2) * 0.36;
      groupRef.current.scale.setScalar(0.74 + attack * 0.26 + capture * 0.18);
    }

    if (lineRef.current) {
      const material = lineRef.current.material as THREE.LineBasicMaterial;
      material.opacity = 0.18 + attack * 0.26 + capture * 0.18;
    }

    if (pulseMatRef.current) {
      pulseMatRef.current.opacity = reducedMotion
        ? 0.18
        : 0.15 + Math.sin(time * 3.4) * 0.09 + capture * 0.18;
    }

    if (packetRef.current) {
      EDGES.forEach(([a, b], i) => {
        const from = NODE_POSITIONS[a];
        const to = NODE_POSITIONS[b];
        const flow = reducedMotion ? 0.5 : (time * (0.18 + i * 0.012) + i * 0.19) % 1;
        const t = capture > 0.15 ? Math.pow(flow, 0.65) : flow;
        packetMatrix.position.set(
          THREE.MathUtils.lerp(from[0], to[0], t),
          THREE.MathUtils.lerp(from[1], to[1], t),
          THREE.MathUtils.lerp(from[2], to[2], t)
        );
        const scale = 0.045 + attack * 0.025 + capture * 0.025;
        packetMatrix.scale.setScalar(scale);
        packetMatrix.updateMatrix();
        packetRef.current?.setMatrixAt(i, packetMatrix.matrix);
      });
      packetRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <group ref={groupRef} position={[1.7, -0.15, 0]} scale={0.74}>
      <lineSegments ref={lineRef} geometry={lineGeometry}>
        <lineBasicMaterial color={COLORS.magenta} transparent opacity={0.28} />
      </lineSegments>

      {NODE_POSITIONS.map((position, index) => (
        <mesh key={index} position={position}>
          <sphereGeometry args={[index === 8 ? 0.16 : 0.105, 24, 24]} />
          <meshStandardMaterial
            color={nodeColors[index % nodeColors.length]}
            emissive={nodeColors[index % nodeColors.length]}
            emissiveIntensity={index === 8 ? 1.5 : 0.85}
            roughness={0.18}
            metalness={0.18}
          />
        </mesh>
      ))}

      <instancedMesh ref={packetRef} args={[undefined, undefined, EDGES.length]}>
        <sphereGeometry args={[1, 12, 12]} />
        <meshBasicMaterial color={COLORS.yellow} transparent opacity={0.92} />
      </instancedMesh>

      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[3.15, 0.012, 8, 160]} />
        <meshBasicMaterial
          ref={pulseMatRef}
          color={COLORS.blue}
          transparent
          opacity={0.18}
        />
      </mesh>
      <mesh rotation={[0.35, 0.65, 0.15]}>
        <torusGeometry args={[2.1, 0.01, 8, 140]} />
        <meshBasicMaterial color={COLORS.orange} transparent opacity={0.18} />
      </mesh>
    </group>
  );
}

function ScanField({
  scroll,
  reducedMotion,
}: {
  scroll: ScrollRef;
  reducedMotion: boolean;
}) {
  const ref = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const count = reducedMotion ? 130 : 320;
    const points = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const angle = i * 2.399963;
      const radius = 2.5 + (i % 47) * 0.13;
      points[i * 3] = Math.cos(angle) * radius;
      points[i * 3 + 1] = Math.sin(angle) * radius * 0.68;
      points[i * 3 + 2] = ((i % 19) - 9) * 0.18;
    }
    return points;
  }, [reducedMotion]);

  const geometry = useMemo(() => {
    const field = new THREE.BufferGeometry();
    field.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    return field;
  }, [positions]);

  useFrame((state) => {
    if (!ref.current) return;
    const time = reducedMotion ? 0 : state.clock.elapsedTime;
    ref.current.rotation.z = time * 0.025 + scroll.current * Math.PI;
    ref.current.rotation.y = scroll.current * 0.85;
  });

  return (
    <points ref={ref} geometry={geometry}>
      <pointsMaterial
        size={0.024}
        color="#ffffff"
        transparent
        opacity={0.42}
        depthWrite={false}
        sizeAttenuation
      />
    </points>
  );
}

function Rig({ reducedMotion }: { reducedMotion: boolean }) {
  useFrame((state) => {
    if (reducedMotion) return;
    state.camera.position.x += (state.pointer.x * 0.45 - state.camera.position.x) * 0.035;
    state.camera.position.y += (state.pointer.y * 0.35 - state.camera.position.y) * 0.035;
    state.camera.lookAt(0, 0, 0);
  });
  return null;
}

export function NetworkCore({ active }: { active: boolean }) {
  const reducedMotion = usePrefersReducedMotion();
  const scroll = usePageScrollProgress(active && !reducedMotion);

  return (
    <div
      className={`fixed inset-0 z-[1] pointer-events-none transition-opacity duration-700 ${
        active ? "opacity-45 md:opacity-55" : "opacity-0"
      }`}
      aria-hidden="true"
    >
      <Canvas
        camera={{ position: [0, 0, 8.8], fov: 48 }}
        gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
        dpr={[1, 1.5]}
      >
        <ambientLight intensity={0.52} />
        <directionalLight position={[5, 6, 5]} intensity={2.1} color={COLORS.orange} />
        <pointLight position={[-4, -2, 3]} intensity={3.6} color={COLORS.blue} />
        <pointLight position={[3, 3, -3]} intensity={2.8} color={COLORS.magenta} />
        <pointLight position={[0, -3.5, 2]} intensity={1.8} color={COLORS.yellow} />

        <Suspense fallback={null}>
          <BridgePortal scroll={scroll} />
        </Suspense>
        <NetworkMap scroll={scroll} reducedMotion={reducedMotion} />
        <ScanField scroll={scroll} reducedMotion={reducedMotion} />
        <Rig reducedMotion={reducedMotion} />
      </Canvas>
    </div>
  );
}
