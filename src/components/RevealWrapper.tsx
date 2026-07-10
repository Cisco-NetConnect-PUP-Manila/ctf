"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";

export function RevealWrapper({
  children,
  start,
}: {
  children: React.ReactNode;
  start: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!start || !ref.current) return;

    // Simple fade-in, no scale (scale was breaking layout)
    gsap.fromTo(
      ref.current,
      {
        opacity: 0,
      },
      {
        opacity: 1,
        duration: 0.8,
        ease: "power2.out",
      }
    );
  }, [start]);

  return (
    <div ref={ref} className="min-h-screen">
      {children}
    </div>
  );
}
