"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export default function BootSequence() {
  const [progress, setProgress] = useState(0);
  const [gone, setGone] = useState(false);
  const [skip, setSkip] = useState(false);
  const doneRef = useRef(false);

  const finish = useCallback(() => {
    if (doneRef.current) return;
    doneRef.current = true;
    try {
      sessionStorage.setItem("pc_booted", "1");
    } catch {}
    setGone(true);
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined" && sessionStorage.getItem("pc_booted")) {
      setGone(true);
      doneRef.current = true;
      setSkip(true);
      return;
    }

    let p = 0;
    let raf: ReturnType<typeof setTimeout>;
    const tick = () => {
      if (doneRef.current) return;
      p = Math.min(100, p + 2 + Math.random() * 4);
      setProgress(p);
      if (p >= 100) {
        raf = setTimeout(() => finish(), 400);
      } else {
        raf = setTimeout(tick, 55);
      }
    };
    raf = setTimeout(tick, 200);
    return () => clearTimeout(raf);
  }, [finish]);

  if (skip) return null;

  const pct = Math.floor(progress);

  return (
    <div
      className={`boot ${gone ? "boot--gone" : ""}`}
      onClick={finish}
      onTransitionEnd={() => gone && setSkip(true)}
      role="button"
      tabIndex={0}
      aria-label="Skip loading"
    >
      <div className="boot__mini">
        <div className="boot__title">
          PACKET CAPTURE<span className="cursor" />
        </div>
        <div className="boot__track" aria-hidden="true">
          <i style={{ width: `${pct}%` }} />
        </div>
        <div className="boot__label">
          SYSTEM LOADING <b>{String(pct).padStart(3, "0")}%</b>
        </div>
      </div>
    </div>
  );
}
