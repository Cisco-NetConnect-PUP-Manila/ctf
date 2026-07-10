"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Image from "next/image";
import { SectionContainer, SectionHeader, SectionShell } from "@/components/ui/SectionLayout";
import { useReveal } from "@/lib/useReveal";

gsap.registerPlugin(ScrollTrigger);

const stats = [
  { value: "4", label: "Narrative Acts", color: "#ff0a9c" },
  { value: "29", label: "Public Cases", color: "#5b2eff" },
  { value: "4,050", label: "Total Points", color: "#ff7a18" },
  { value: "1", label: "Final Layer", color: "#ffc400" },
];

export function AboutSection() {
  const sectionRef = useRef<HTMLElement>(null);

  useReveal(sectionRef, () => {
    const statementEl = sectionRef.current?.querySelector(".statement");
    const words = sectionRef.current?.querySelectorAll(".reveal-word");
    if (statementEl && words) {
      const wordList = Array.from(words) as HTMLElement[];
      const clamp = gsap.utils.clamp(0, 1);

      gsap.set(wordList, { color: "rgba(245, 245, 242, 0.2)" });

      ScrollTrigger.create({
        trigger: statementEl,
        start: "top 78%",
        end: "bottom 28%",
        scrub: true,
        onUpdate: ({ progress }) => {
          wordList.forEach((word, i) => {
            const activationPoint = i / Math.max(wordList.length - 1, 1);
            const localProgress = clamp((progress - activationPoint * 0.78) / 0.22);
            const alpha = 0.2 + localProgress * 0.8;
            word.style.color = `rgba(245, 245, 242, ${alpha})`;
          });
        },
      });
    }

    const statEls = sectionRef.current?.querySelectorAll(".stat");
    if (statEls) {
      gsap.from(statEls, {
        scrollTrigger: { trigger: ".stat-grid", start: "top 75%" },
        y: 60,
        opacity: 0,
        stagger: 0.12,
        duration: 1,
        ease: "expo.out",
      });
    }

    gsap.to(".about-gradient", {
      scrollTrigger: {
        trigger: sectionRef.current,
        start: "top bottom",
        end: "bottom top",
        scrub: 1.5,
      },
      yPercent: -25,
      rotate: 15,
    });
  });

  const statement =
    "Every network has two realities: the trusted surface everyone sees, and the hidden layer where abandoned systems, corrupted logs, and impossible traffic tell the real story.";

  return (
    <SectionShell
      id="about"
      sectionRef={sectionRef}
      pad="compact"
    >
      <Image
        src="/assets/ctf-gradient.webp"
        alt=""
        width={1655}
        height={1077}
        className="about-gradient pointer-events-none absolute -right-40 top-0 w-[55vw] max-w-[800px] select-none opacity-25 mix-blend-screen"
      />

      <SectionContainer>
        <SectionHeader index="(01)" label="Incident Brief" />

        <h2
          aria-label={statement}
          className="statement display mb-12 flex max-w-5xl flex-wrap gap-x-[0.32em] gap-y-[0.16em] text-3xl font-bold leading-[1.16] md:mb-16 md:text-5xl md:leading-[1.12] lg:text-6xl"
        >
          {statement.split(" ").map((w, i) => (
            <span
              key={i}
              aria-hidden="true"
              className="reveal-word inline-block will-change-[color]"
              style={{ color: "rgba(245, 245, 242, 0.22)" }}
            >
              {w}
            </span>
          ))}
        </h2>

        <div className="stat-grid grid grid-cols-1 gap-4 sm:grid-cols-2 md:gap-5 lg:grid-cols-4">
          {stats.map((s) => (
            <div
              key={s.label}
              data-cursor
              className="stat scan-panel corner-cut group relative overflow-hidden p-6 md:p-8"
            >
              <div
                className="absolute -bottom-10 -right-10 h-32 w-32 rounded-full opacity-40 blur-[50px] transition-opacity duration-500 group-hover:opacity-70"
                style={{ background: s.color }}
              />
              <div
                className="chaos-type relative mb-3 text-5xl leading-[1.05] md:text-7xl"
                style={{ color: s.color }}
              >
                {s.value}
              </div>
              <div className="terminal relative text-xs text-fg/50">{s.label}</div>
            </div>
          ))}
        </div>
      </SectionContainer>
    </SectionShell>
  );
}
