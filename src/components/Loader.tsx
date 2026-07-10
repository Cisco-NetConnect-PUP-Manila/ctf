"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import Image from "next/image";

interface LoaderProps {
  onComplete: () => void;
}

export function Loader({ onComplete }: LoaderProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const logoRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tl = gsap.timeline();

    // Logo fades in and sits for a beat
    tl.fromTo(
      logoRef.current,
      { opacity: 0, scale: 0.8 },
      { opacity: 1, scale: 1, duration: 0.8, ease: "power3.out" }
    );

    // Hold for a moment
    tl.to(logoRef.current, { duration: 0.6 });

    // Zoom INTO the logo — scale way up, slight blur as it fills screen
    tl.to(logoRef.current, {
      scale: 12,
      opacity: 0,
      filter: "blur(6px)",
      duration: 1.0,
      ease: "power3.in",
    });

    // Fade out the entire overlay
    tl.to(
      rootRef.current,
      {
        opacity: 0,
        duration: 0.4,
        ease: "power2.out",
        onComplete,
      },
      "-=0.3"
    );

    return () => {
      tl.kill();
    };
  }, [onComplete]);

  return (
    <div
      ref={rootRef}
      className="fixed inset-0 z-[9999] bg-[#060606] flex items-center justify-center"
    >
      <div
        ref={logoRef}
        className="will-change-transform"
      >
        <Image
          src="/assets/ctf-colored-logo.webp"
          alt="Packet Capture"
          width={973}
          height={593}
          className="w-36 md:w-48 h-auto"
          priority
        />
      </div>
    </div>
  );
}
