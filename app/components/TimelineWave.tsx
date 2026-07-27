"use client";

import { useEffect, useRef, useState } from "react";

type TItem = { date: string; title: string; body: string };

const VW = 1000;
const VH = 200;
const CY = 100;
const AMP = 40; /* wave depth */

export default function TimelineWave({ items }: { items: TItem[] }) {
  const n = items.length;
  const dx = VW / n;
  const x0 = dx / 2; // first node x (sine extremum)
  const yAt = (x: number) => CY + AMP * Math.cos((Math.PI * (x - x0)) / dx);

  // dense samples for a very smooth polyline; spans node 1 -> node n
  const xLast = x0 + (n - 1) * dx;
  const STEP = 3;
  const samples: { x: number; y: number }[] = [];
  for (let x = x0; x <= xLast; x += STEP) samples.push({ x, y: yAt(x) });
  if (samples[samples.length - 1].x !== xLast) samples.push({ x: xLast, y: yAt(xLast) });

  // cumulative arc length + fraction at each node
  const cum: number[] = [0];
  for (let i = 1; i < samples.length; i++) {
    cum[i] = cum[i - 1] + Math.hypot(samples[i].x - samples[i - 1].x, samples[i].y - samples[i - 1].y);
  }
  const totalLen = cum[cum.length - 1] || 1;

  const pts = items.map((_, i) => {
    const x = x0 + i * dx;
    return { x, y: yAt(x) };
  });
  const fracNode = pts.map((p) => {
    const idx = Math.min(samples.length - 1, Math.round((p.x - x0) / STEP));
    return cum[idx] / totalLen;
  });

  const pathFrom = (arr: { x: number; y: number }[]) =>
    arr.length < 2 ? "" : "M " + arr.map((p, i) => (i ? "L " : "") + p.x.toFixed(2) + " " + p.y.toFixed(2)).join(" ");

  const fullPath = pathFrom(samples);

  const [active, setActive] = useState(-1);
  const [prog, setProg] = useState(0); // animated fraction (0..1) of the line drawn

  const progRef = useRef(0);
  const targetRef = useRef(0);
  const rafRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    targetRef.current = active < 0 ? 0 : fracNode[active];
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    const tick = () => {
      const cur = progRef.current;
      const tgt = targetRef.current;
      const next = cur + (tgt - cur) * 0.16; // eased flow
      if (Math.abs(tgt - next) < 0.0006) {
        progRef.current = tgt;
        setProg(tgt);
        return;
      }
      progRef.current = next;
      setProg(next);
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active]);

  // build the glowing fill up to the current animated fraction (with a
  // partial last segment so the tip flows smoothly between orbs)
  const buildFill = (f: number) => {
    if (f <= 0.001) return "";
    const L = f * totalLen;
    let i = 0;
    while (i < cum.length - 1 && cum[i + 1] < L) i++;
    const b = samples[i + 1] || samples[i];
    const seg = (cum[i + 1] ?? cum[i]) - cum[i] || 1;
    const t = Math.min(1, Math.max(0, (L - cum[i]) / seg));
    const tip = { x: samples[i].x + (b.x - samples[i].x) * t, y: samples[i].y + (b.y - samples[i].y) * t };
    return pathFrom(samples.slice(0, i + 1).concat(tip));
  };
  const fillPath = buildFill(prog);

  return (
    <div className="wave" onMouseLeave={() => setActive(-1)}>
      <svg className="wave__svg" viewBox={`0 0 ${VW} ${VH}`} preserveAspectRatio="none">
        <defs>
          <linearGradient id="wavegrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#ffcf94" />
            <stop offset="0.5" stopColor="#ff8a2e" />
            <stop offset="1" stopColor="#ff6412" />
          </linearGradient>
        </defs>
        <path className="wave__base" d={fullPath} vectorEffect="non-scaling-stroke" />
        {fillPath && <path className="wave__fill" d={fillPath} vectorEffect="non-scaling-stroke" />}
      </svg>

      {items.map((t, i) => {
        const leftPct = (pts[i].x / VW) * 100;
        const topPct = (pts[i].y / VH) * 100;
        const above = pts[i].y < CY;
        const cardStyle: React.CSSProperties = above
          ? { left: `${leftPct}%`, bottom: `calc(${100 - topPct}% + 44px)` }
          : { left: `${leftPct}%`, top: `calc(${topPct}% + 44px)` };
        return (
          <div key={i}>
            <button
              className={`wave__node ${i <= active ? "on" : ""} ${i === active ? "cur" : ""}`}
              style={{ left: `${leftPct}%`, top: `${topPct}%` }}
              onMouseEnter={() => setActive(i)}
              onFocus={() => setActive(i)}
              aria-label={t.title}
            >
              <span className="wave__num">{String(i + 1).padStart(2, "0")}</span>
            </button>
            <div className={`wave__card ${above ? "above" : "below"} ${i <= active ? "on" : ""}`} style={cardStyle}>
              <div className="wave__step">STEP {String(i + 1).padStart(2, "0")} / {t.date}</div>
              <h3>{t.title}</h3>
              <p>{t.body}</p>
            </div>
          </div>
        );
      })}

      {/* vertical fallback for small screens */}
      <div className="wave__mobile">
        {items.map((t, i) => (
          <div className="wm-item" key={i}>
            <span className="wm-node">{String(i + 1).padStart(2, "0")}</span>
            <div>
              <div className="wave__step">STEP {String(i + 1).padStart(2, "0")} / {t.date}</div>
              <h3>{t.title}</h3>
              <p>{t.body}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
