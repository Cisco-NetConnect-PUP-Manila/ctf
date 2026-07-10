"use client";

import { useEffect, useRef } from "react";

export function Cursor() {
  const pointerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const pointer = pointerRef.current!;
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const resize = () => {
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = window.innerWidth + "px";
      canvas.style.height = window.innerHeight + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();

    let mx = window.innerWidth / 2;
    let my = window.innerHeight / 2;
    let sx = mx;
    let sy = my;
    let raf = 0;
    let hover = false;

    type TrailPoint = { x: number; y: number };
    const trail: TrailPoint[] = Array.from({ length: 12 }, () => ({ x: mx, y: my }));

    pointer.style.opacity = "1";
    pointer.style.transform = `translate3d(${mx}px, ${my}px, 0)`;
    canvas.style.opacity = "1";

    const onMove = (e: MouseEvent) => {
      mx = e.clientX;
      my = e.clientY;
    };

    const loop = () => {
      sx += (mx - sx) * 0.32;
      sy += (my - sy) * 0.32;

      trail[0].x += (sx - trail[0].x) * 0.42;
      trail[0].y += (sy - trail[0].y) * 0.42;

      for (let i = 1; i < trail.length; i++) {
        trail[i].x += (trail[i - 1].x - trail[i].x) * 0.34;
        trail[i].y += (trail[i - 1].y - trail[i].y) * 0.34;
      }

      const scale = hover ? 1.14 : 1;
      pointer.style.transform = `translate3d(${sx}px, ${sy}px, 0) scale(${scale})`;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let i = trail.length - 1; i >= 1; i--) {
        const p = trail[i];
        const alpha = (1 - i / trail.length) * 0.11;
        const radius = Math.max(0.8, 2.1 - i * 0.1);

        ctx.globalAlpha = alpha;
        ctx.fillStyle = hover ? "#f5f5f2" : "#ff0a9c";
        ctx.beginPath();
        ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      raf = requestAnimationFrame(loop);
    };
    loop();

    const isCursorTarget = (target: EventTarget | null) =>
      target instanceof Element
        ? target.closest("a, button, [data-cursor]")
        : null;

    const onPointerOver = (event: PointerEvent) => {
      const target = isCursorTarget(event.target);
      if (target && !target.contains(event.relatedTarget as Node | null)) {
        hover = true;
        pointer.classList.add("cursor-pointer-hover");
      }
    };

    const onPointerOut = (event: PointerEvent) => {
      const target = isCursorTarget(event.target);
      if (target && !target.contains(event.relatedTarget as Node | null)) {
        hover = false;
        pointer.classList.remove("cursor-pointer-hover");
      }
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("resize", resize);
    document.addEventListener("pointerover", onPointerOver);
    document.addEventListener("pointerout", onPointerOut);

    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("resize", resize);
      document.removeEventListener("pointerover", onPointerOver);
      document.removeEventListener("pointerout", onPointerOut);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <>
      <canvas
        ref={canvasRef}
        className="fixed inset-0 z-[9998] pointer-events-none opacity-0 will-change-transform"
      />
      <div
        ref={pointerRef}
        className="cursor-pointer-shape fixed left-0 top-0 z-[10000] opacity-0 pointer-events-none will-change-transform"
        style={{ mixBlendMode: "difference" }}
      />
      <style jsx global>{`
        .cursor-pointer-shape {
          width: 15px;
          height: 21px;
          background: var(--fg);
          clip-path: polygon(
            0 0,
            0 17px,
            4.5px 13px,
            7.5px 20px,
            10.2px 18.8px,
            7.2px 12px,
            14.5px 12px
          );
          filter: drop-shadow(0 0 8px rgba(255, 10, 156, 0.32));
          transform-origin: 0 0;
        }

        .cursor-pointer-hover {
          background: var(--magenta) !important;
          filter: drop-shadow(0 0 10px rgba(255, 10, 156, 0.42)) !important;
        }
      `}</style>
    </>
  );
}
