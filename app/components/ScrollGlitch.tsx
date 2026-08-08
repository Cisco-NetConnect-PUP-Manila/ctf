"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

/**
 * Fake "the signal is breaking up" horror effect: brief glitch pulses
 * fired while scrolling. Purely visual (transform/opacity), so scrolling
 * itself stays smooth and the site never actually lags.
 */
export default function ScrollGlitch() {
  const pathname = usePathname();

  useEffect(() => {
    if (pathname.startsWith("/platform") || pathname.startsWith("/admin")) {
      document.documentElement.removeAttribute("data-glitch");
      return;
    }

    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;

    const screen = document.getElementById("screen");
    if (!screen) return;

    const root = document.documentElement;
    let last = 0;
    let off: ReturnType<typeof setTimeout>;

    const rand = (min: number, max: number) =>
      min + Math.random() * (max - min);
    const pick = <T,>(items: T[]) =>
      items[Math.floor(Math.random() * items.length)];
    const px = (value: number) => `${value.toFixed(1)}px`;
    const pct = (value: number) => `${value.toFixed(1)}%`;
    const deg = (value: number) => `${value.toFixed(2)}deg`;
    const ms = (value: number) => `${Math.round(value)}ms`;
    const signed = (range: number) => rand(-range, range);

    const setGlitchVars = (hard: boolean) => {
      const duration = hard ? rand(190, 330) : rand(120, 240);
      const offset = hard ? 7 : 4;
      const tearHeight = hard ? [7, 22] : [4, 14];

      root.style.setProperty("--scr-dur", ms(duration));
      root.style.setProperty("--scr-x1", px(signed(offset)));
      root.style.setProperty("--scr-y1", px(signed(offset * 0.55)));
      root.style.setProperty("--scr-x2", px(signed(offset)));
      root.style.setProperty("--scr-y2", px(signed(offset * 0.55)));
      root.style.setProperty("--scr-x3", px(signed(offset)));
      root.style.setProperty("--scr-y3", px(signed(offset * 0.55)));
      root.style.setProperty("--scr-x4", px(signed(offset)));
      root.style.setProperty("--scr-y4", px(signed(offset * 0.55)));
      root.style.setProperty("--scr-skew1", deg(signed(hard ? 1.4 : 0.7)));
      root.style.setProperty("--scr-skew2", deg(signed(hard ? 1.4 : 0.7)));
      root.style.setProperty("--scr-skew3", deg(signed(hard ? 1.2 : 0.6)));

      root.style.setProperty("--glitch-flash-dur", ms(duration + rand(-45, 70)));
      root.style.setProperty("--glitch-line-alpha", hard ? "0.10" : "0.05");
      root.style.setProperty("--glitch-line-on", px(rand(1, hard ? 4 : 3)));
      root.style.setProperty("--glitch-line-off", px(rand(4, hard ? 10 : 7)));

      root.style.setProperty("--tear-a-top", pct(rand(8, 78)));
      root.style.setProperty("--tear-a-height", pct(rand(tearHeight[0], tearHeight[1])));
      root.style.setProperty("--tear-a-x1", px(signed(hard ? 64 : 36)));
      root.style.setProperty("--tear-a-x2", px(signed(hard ? 48 : 28)));
      root.style.setProperty("--tear-a-dur", ms(duration + rand(-70, 40)));
      root.style.setProperty("--tear-a-bg", pick([
        "rgba(255, 150, 40, 0.12)",
        "rgba(255, 40, 70, 0.14)",
        "rgba(255, 206, 74, 0.10)",
      ]));

      root.style.setProperty("--tear-b-top", pct(rand(14, 86)));
      root.style.setProperty("--tear-b-height", pct(rand(tearHeight[0] * 0.7, tearHeight[1] * 0.75)));
      root.style.setProperty("--tear-b-x1", px(signed(hard ? 58 : 32)));
      root.style.setProperty("--tear-b-x2", px(signed(hard ? 44 : 26)));
      root.style.setProperty("--tear-b-dur", ms(duration + rand(-80, 50)));
      root.style.setProperty("--tear-b-bg", pick([
        "rgba(40, 210, 255, 0.10)",
        "rgba(255, 255, 255, 0.08)",
        "rgba(255, 120, 20, 0.11)",
      ]));

      root.style.setProperty("--bar-dur", ms(duration + rand(-30, 40)));
      root.style.setProperty("--bar-x1", px(signed(hard ? 7 : 3)));
      root.style.setProperty("--bar-x2", px(signed(hard ? 7 : 3)));
      root.style.setProperty("--rgb-x", px(hard ? rand(2, 4.5) : rand(1, 2.4)));
      root.style.setProperty("--nav-rgb-alpha", hard ? "0.82" : "0.52");
    };

    const fire = () => {
      const now = Date.now();
      if (now - last < 380) return; // throttle so it doesn't run every frame
      if (Math.random() < 0.28) return; // skip some -> feels erratic / broken
      last = now;

      // pick a random intensity level for organic corruption
      const lvl = Math.random() < 0.18 ? "hard" : "soft";
      setGlitchVars(lvl === "hard");
      root.setAttribute("data-glitch", lvl);
      clearTimeout(off);
      off = setTimeout(
        () => root.removeAttribute("data-glitch"),
        lvl === "hard" ? 260 : 150 + Math.random() * 120
      );
    };

    screen.addEventListener("scroll", fire, { passive: true });
    return () => {
      screen.removeEventListener("scroll", fire);
      clearTimeout(off);
      root.removeAttribute("data-glitch");
    };
  }, [pathname]);

  return <div className="glitch-fx" aria-hidden="true" />;
}
