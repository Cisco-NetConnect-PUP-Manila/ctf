"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import type { LucideIcon } from "lucide-react";
import {
  ArrowRight,
  Award,
  Building2,
  Cpu,
  Handshake,
  Network,
  ShieldCheck,
  Trophy,
  Users,
  Zap,
} from "lucide-react";
import { CtaLink } from "@/components/ui/CtaButton";
import { useReveal } from "@/lib/useReveal";

const sponsors = [
  { label: "CyberGuard", icon: ShieldCheck, color: "#ff2d4f" },
  { label: "NetCore", icon: Network, color: "#5b2eff" },
  { label: "CloudSec", icon: Cpu, color: "#ff7a18" },
  { label: "CorpShield", icon: Building2, color: "#ffc400" },
  { label: "HackCom", icon: Users, color: "#ff0a9c" },
  { label: "FlagPrize", icon: Trophy, color: "#ff7a18" },
  { label: "AllyNet", icon: Handshake, color: "#5b2eff" },
  { label: "TopAward", icon: Award, color: "#ff2d4f" },
  { label: "ZeroDay", icon: Zap, color: "#ffc400" },
  { label: "RootKit", icon: ShieldCheck, color: "#ff0a9c" },
  { label: "ByteForce", icon: Cpu, color: "#5b2eff" },
  { label: "VaultNet", icon: Network, color: "#ff7a18" },
] satisfies Array<{ label: string; icon: LucideIcon; color: string }>;

export function SponsorsSection() {
  const sectionRef = useRef<HTMLElement>(null);

  useReveal(sectionRef, () => {
    const cells = sectionRef.current?.querySelectorAll<HTMLElement>(".sponsor-cell");
    if (cells) {
      cells.forEach((cell, i) => {
        // Wave flip â€” each card flips, staggered by column+row position for a wave
        const col = i % 4;
        const row = Math.floor(i / 4);
        const wave = (col + row) * 0.06;

        gsap.fromTo(
          cell,
          { rotateY: -100, opacity: 0 },
          {
            rotateY: 0,
            opacity: 1,
            ease: "power2.out",
            scrollTrigger: {
              trigger: ".sponsor-grid",
              start: `top ${80 - wave * 100}%`,
              end: `top ${40 - wave * 100}%`,
              scrub: 1,
            },
          }
        );
      });
    }

    const cta = sectionRef.current?.querySelector(".sponsor-cta");
    if (cta) {
      gsap.from(cta, {
        scrollTrigger: { trigger: cta, start: "top 88%" },
        y: 50,
        opacity: 0,
        duration: 0.9,
        ease: "expo.out",
      });
    }
  });

  return (
    <section
      id="sponsors"
      ref={sectionRef}
      className="relative section-pad container-pad overflow-hidden"
    >
      <div className="relative mx-auto max-w-[1600px]">
        {/* Section label */}
        <div className="flex items-center gap-5 mb-4">
          <span className="label text-magenta">(05)</span>
          <span className="label text-fg/40">Backed By</span>
          <span className="flex-1 h-px bg-fg/10" />
        </div>

        {/* Section heading */}
        <h2 className="display mb-16 max-w-5xl text-4xl leading-tight md:mb-20 md:text-6xl lg:text-8xl">
          Partners <span className="chaos-type glitch-shadow text-orange">&amp;</span> Sponsors
        </h2>

        {/* Sponsor grid â€” uniform square tiles */}
        <div
          className="sponsor-grid grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5 md:gap-6"
          style={{ perspective: "1000px" }}
        >
          {sponsors.map((s) => {
            const Icon = s.icon;
            return (
              <div
                key={s.label}
                data-cursor
                className="sponsor-cell scan-panel corner-cut group relative flex aspect-square flex-col items-center justify-center gap-5 overflow-hidden"
                style={{ transformStyle: "preserve-3d", willChange: "transform" }}
              >
                {/* Hover color glow */}
                <div
                  className="absolute -bottom-10 -right-10 w-32 h-32 rounded-full blur-[50px] opacity-0 group-hover:opacity-50 transition-opacity duration-500"
                  style={{ background: s.color }}
                />

                {/* Icon */}
                <div
                  className="relative grid h-14 w-14 md:h-16 md:w-16 place-items-center rounded-xl transition-transform duration-500 group-hover:scale-110"
                  style={{
                    background: `${s.color}12`,
                    border: `1px solid ${s.color}30`,
                  }}
                >
                  <Icon
                    aria-hidden="true"
                    className="h-6 w-6 md:h-7 md:w-7"
                    style={{ color: s.color }}
                    strokeWidth={1.6}
                  />
                </div>

                {/* Name */}
                <span className="terminal relative text-xs text-fg/40 transition-colors duration-300 group-hover:text-fg/80">
                  {s.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Spacer */}
        <div className="h-16 md:h-20" />

        {/* CTA */}
        <div className="sponsor-cta scan-panel corner-cut flex flex-col items-start justify-between gap-8 p-8 md:flex-row md:items-center md:p-12">
          <div>
            <h3 className="display mb-3 text-2xl leading-tight md:text-3xl">
              Become a Partner
            </h3>
            <p className="text-fg/45 text-sm md:text-base leading-relaxed max-w-lg">
              Put your brand in front of the region&apos;s sharpest security
              talent. Let&apos;s build something together.
            </p>
          </div>
          <CtaLink
            href="mailto:sponsors@packetcapture.ctf"
            data-cursor
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            size="md"
            className="inline-flex shrink-0 text-sm font-bold uppercase tracking-wide"
          >
            Get in Touch
            <ArrowRight aria-hidden="true" className="h-4 w-4" strokeWidth={2} />
          </CtaLink>
        </div>
      </div>
    </section>
  );
}
