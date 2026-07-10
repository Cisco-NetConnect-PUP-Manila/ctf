"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import { motion } from "framer-motion";
import Image from "next/image";
import { ArrowRight } from "lucide-react";
import { CtaLink } from "@/components/ui/CtaButton";
import { useReveal } from "@/lib/useReveal";

export function HeroSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const logoRef = useRef<HTMLDivElement>(null);

  useReveal(sectionRef, () => {
    gsap.from(logoRef.current, {
      x: -80,
      opacity: 0,
      duration: 1.4,
      ease: "expo.out",
      delay: 0.5,
    });

    gsap.from(".hero-fade", {
      y: 30,
      opacity: 0,
      duration: 1,
      ease: "expo.out",
      stagger: 0.1,
      delay: 0.9,
    });

    gsap.to(logoRef.current, {
      scrollTrigger: {
        trigger: sectionRef.current,
        start: "top top",
        end: "bottom top",
        scrub: 1,
      },
      y: -56,
      ease: "none",
    });
  });

  return (
    <section
      id="top"
      ref={sectionRef}
      className="relative min-h-screen w-full overflow-hidden"
    >
      <div className="absolute inset-0 z-0">
        <div className="absolute left-[-10%] top-[-20%] h-[80vh] w-[70vw] bg-[radial-gradient(circle,#5b2effaa,transparent_60%)] blur-[60px]" />
        <div className="absolute left-[28%] top-[5%] h-[60vh] w-[45vw] bg-[radial-gradient(circle,#ff7a1855,transparent_60%)] blur-[70px]" />
        <div className="absolute bottom-[-10%] right-[-5%] h-[80vh] w-[55vw] bg-[radial-gradient(circle,#ff0a9c88,transparent_60%)] blur-[60px]" />
        <div className="absolute bottom-[10%] right-[10%] h-[60vh] w-[40vw] bg-[radial-gradient(circle,#8b1fff66,transparent_60%)] blur-[70px]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,#060606_95%)]" />
      </div>
      <div className="arena-grid absolute inset-0 z-[1] opacity-70" />

      <div className="relative z-10 min-h-screen container-pad pointer-events-none">
        <div className="grid min-h-screen items-center gap-10 pb-16 pt-28">
          <div className="max-w-5xl">
            <div ref={logoRef} className="mb-10 flex items-center gap-5">
              <Image
                src="/assets/ctf-complete-logo.webp"
                alt="Packet Capture - Networking x Security Capture The Flag"
                width={1099}
                height={726}
                className="h-auto w-[180px] drop-shadow-[0_0_40px_rgba(255,10,156,0.35)] md:w-[240px]"
                priority
              />
              <div className="hidden h-px flex-1 bg-gradient-to-r from-magenta/70 via-fg/15 to-transparent md:block" />
            </div>

            <div className="hero-fade label mb-5 flex flex-wrap items-center gap-3 text-fg/55">
              <span className="text-magenta">/ Incident channel open</span>
              <span className="h-1.5 w-1.5 bg-yellow" />
              <span>Cyber Incident Response Team</span>
            </div>

            <h1 className="hero-fade display max-w-6xl text-[clamp(3.35rem,10.4vw,10.5rem)] leading-[0.82] text-fg">
              Beneath
              <span className="chaos-type glitch-shadow block text-[clamp(4.6rem,14vw,14rem)] leading-[0.76] text-transparent [-webkit-text-stroke:1.5px_var(--magenta)]">
                The Network
              </span>
            </h1>

            <p className="hero-fade mt-8 max-w-2xl text-base leading-relaxed text-fg/62 md:text-lg">
              A seemingly ordinary infrastructure is broadcasting impossible
              anomalies. Join the response team, trace the evidence, and
              preserve every key you recover.
            </p>

            <div className="hero-fade pointer-events-auto mt-10 flex flex-col items-start gap-5 sm:flex-row sm:items-center">
              <CtaLink
                href="#register"
                data-cursor
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                size="md"
                className="group inline-flex text-sm font-black uppercase tracking-wide"
              >
                Begin Investigation
                <ArrowRight
                  aria-hidden="true"
                  className="h-4 w-4 transition-transform group-hover:translate-x-1"
                  strokeWidth={2}
                />
              </CtaLink>
              <a
                href="#about"
                data-cursor
                className="label link-sweep text-fg/60 transition-colors hover:text-fg"
              >
                Read the brief
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="hero-fade absolute inset-x-0 top-28 z-10 container-pad pointer-events-none">
        <div className="brand-detail flex items-center justify-between gap-6 text-[0.68rem] text-fg/40">
          <span className="whitespace-nowrap leading-relaxed">Networking x Security</span>
          <span className="hidden whitespace-nowrap leading-relaxed md:block">
            Beneath the Network
          </span>
          <span className="whitespace-nowrap text-right leading-relaxed">
            EST. 2026
          </span>
        </div>
      </div>

      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="hero-fade label pointer-events-none absolute bottom-8 left-1/2 z-10 -translate-x-1/2 text-fg/30"
      >
        Scroll to explore
      </motion.div>
    </section>
  );
}
