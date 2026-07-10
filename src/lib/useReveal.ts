"use client";

import { useEffect, RefObject } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * Center-triggered reveal. Animations fire when the target reaches
 * the MIDDLE of the viewport (start: "top center"), not the top.
 */
export function useReveal(
  scopeRef: RefObject<HTMLElement | null>,
  build: (ctx: gsap.Context) => void,
  deps: unknown[] = []
) {
  useEffect(() => {
    if (!scopeRef.current) return;
    const ctx = gsap.context(build, scopeRef);
    // Recalculate once after mount so pinned/positioned elements are correct
    const id = requestAnimationFrame(() => ScrollTrigger.refresh());
    return () => {
      cancelAnimationFrame(id);
      ctx.revert();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}

/** Shared default: fire when element's top hits viewport center. */
export const CENTER_START = "top center";
export const CENTER_SCRUB_END = "center center";
