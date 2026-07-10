"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import { ArrowRight } from "lucide-react";
import { CtaLink } from "@/components/ui/CtaButton";
import { useReveal } from "@/lib/useReveal";

export function HeroSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const introRef = useRef<HTMLDivElement>(null);

  useReveal(sectionRef, () => {
    gsap.from(introRef.current, {
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

    gsap.to(introRef.current, {
      scrollTrigger: {
        trigger: sectionRef.current,
        start: "top top",
        end: "bottom top",
        scrub: 1,
      },
      y: -24,
      ease: "none",
    });
  });

  return (
    <section
      id="top"
      ref={sectionRef}
      className="relative min-h-[calc(100svh-84px)] w-full overflow-hidden"
    >
      <div className="absolute inset-0 z-0">
        <div className="absolute left-[-10%] top-[-20%] h-[72vh] w-[62vw] bg-[radial-gradient(circle,#5b2eff66,transparent_62%)] blur-[70px]" />
        <div className="absolute bottom-[-14%] right-[-8%] h-[72vh] w-[52vw] bg-[radial-gradient(circle,#ff0a9c55,transparent_64%)] blur-[72px]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,#060606_95%)]" />
      </div>
      <div className="arena-grid absolute inset-0 z-[1] opacity-40" />

      <div className="relative z-10 min-h-[calc(100svh-84px)] container-pad pointer-events-none">
        <div className="grid min-h-[calc(100svh-84px)] items-center pb-8 pt-24 md:pt-28">
          <div className="max-w-4xl">
            <div ref={introRef} className="label mb-3 flex flex-wrap items-center gap-3 text-fg/55">
              <span className="text-magenta">/ Incident channel open</span>
              <span className="hidden h-px w-8 bg-fg/18 sm:block" />
              <span>Cyber Incident Response Team</span>
            </div>

            <h1 className="hero-fade display max-w-5xl text-[clamp(2.35rem,6.2vw,6.5rem)] leading-[0.94] text-fg">
              Beneath
              <span className="chaos-type glitch-shadow block text-[clamp(2.95rem,7.8vw,7.5rem)] leading-[0.9] text-transparent [-webkit-text-stroke:1.15px_var(--magenta)]">
                The Network
              </span>
            </h1>

            <p className="hero-fade mt-5 max-w-xl text-sm leading-relaxed text-fg/62 md:text-base">
              A seemingly ordinary infrastructure is broadcasting impossible
              anomalies. Join the response team, trace the evidence, and
              preserve every key you recover.
            </p>

            <div className="hero-fade pointer-events-auto mt-7 flex flex-col items-start gap-4 sm:flex-row sm:items-center">
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
    </section>
  );
}
