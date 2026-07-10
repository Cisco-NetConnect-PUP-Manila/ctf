"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import { useReveal } from "@/lib/useReveal";

interface PageDividerProps {
  /** Label shown in the center of the divider, e.g. "/ about" */
  label?: string;
}

export function PageDivider({ label }: PageDividerProps) {
  const ref = useRef<HTMLDivElement>(null);

  useReveal(ref, () => {
    const line = ref.current?.querySelector(".divider-line");
    const text = ref.current?.querySelector(".divider-label");

    if (line) {
      gsap.fromTo(
        line,
        { scaleX: 0 },
        {
          scaleX: 1,
          duration: 1.2,
          ease: "expo.out",
          scrollTrigger: { trigger: ref.current, start: "top 85%" },
        }
      );
    }
    if (text) {
      gsap.fromTo(
        text,
        { opacity: 0, y: 10 },
        {
          opacity: 1,
          y: 0,
          duration: 0.8,
          delay: 0.3,
          ease: "expo.out",
          scrollTrigger: { trigger: ref.current, start: "top 85%" },
        }
      );
    }
  });

  return (
    <div ref={ref} className="relative py-8 md:py-12 container-pad">
      <div className="mx-auto max-w-[1600px] flex items-center gap-6">
        <div
          className="divider-line flex-1 h-px origin-left"
          style={{
            background:
              "linear-gradient(90deg, transparent, rgba(245,245,242,0.12) 20%, rgba(245,245,242,0.12) 80%, transparent)",
          }}
        />
        {label && (
          <span className="divider-label label text-fg/20 shrink-0">
            {label}
          </span>
        )}
        <div
          className="divider-line flex-1 h-px origin-right"
          style={{
            background:
              "linear-gradient(90deg, transparent, rgba(245,245,242,0.12) 20%, rgba(245,245,242,0.12) 80%, transparent)",
          }}
        />
      </div>
    </div>
  );
}
