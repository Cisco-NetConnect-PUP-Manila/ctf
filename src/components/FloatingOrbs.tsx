"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";

export function FloatingOrbs() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const orbs = ref.current.querySelectorAll(".orb");
    orbs.forEach((orb) => {
      gsap.to(orb, {
        x: () => gsap.utils.random(-140, 140),
        y: () => gsap.utils.random(-140, 140),
        duration: gsap.utils.random(12, 20),
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
    });
  }, []);

  return (
    <div ref={ref} className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      <div className="orb w-[600px] h-[600px] bg-[#5b2eff] top-[20%] left-[-200px]" />
      <div className="orb w-[500px] h-[500px] bg-[#ff0a9c] top-[60%] right-[-180px]" />
      <div className="orb w-[400px] h-[400px] bg-[#ff7a18] bottom-[-100px] left-[20%] opacity-30" />
    </div>
  );
}
