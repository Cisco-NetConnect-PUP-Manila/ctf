"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import Image from "next/image";
import { useReveal } from "@/lib/useReveal";

const stats = [
  { value: "4", label: "Narrative Acts", color: "#ff0a9c" },
  { value: "29", label: "Public Cases", color: "#5b2eff" },
  { value: "4,050", label: "Total Points", color: "#ff7a18" },
  { value: "1", label: "Final Layer", color: "#ffc400" },
];

const tags = ["CIRT-BRIEF", "ANOMALY-TRACE", "EVIDENCE-CHAIN", "KEYS-PRESERVED"];

export function AboutSection() {
  const sectionRef = useRef<HTMLElement>(null);

  useReveal(sectionRef, () => {
    const words = sectionRef.current?.querySelectorAll(".reveal-word");
    if (words) {
      gsap.from(words, {
        scrollTrigger: {
          trigger: ".statement",
          start: "top 70%",
          end: "bottom center",
          scrub: 1,
        },
        opacity: 0.1,
        stagger: 0.3,
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
    <section
      id="about"
      ref={sectionRef}
      className="relative isolate section-pad container-pad overflow-hidden"
    >
      <Image
        src="/assets/ctf-gradient.webp"
        alt=""
        width={1655}
        height={1077}
        className="about-gradient pointer-events-none absolute -right-40 top-0 w-[55vw] max-w-[800px] select-none opacity-25 mix-blend-screen"
      />

      <div className="relative mx-auto max-w-[1600px]">
        <div className="mb-4 flex items-center gap-5">
          <span className="label text-magenta">(01)</span>
          <span className="label text-fg/40">Incident Brief</span>
          <span className="h-px flex-1 bg-fg/10" />
        </div>

        <div className="mb-8 flex flex-wrap gap-3">
          {tags.map((tag) => (
            <span
              key={tag}
              className="terminal border border-fg/10 bg-fg/[0.03] px-3 py-2 text-xs text-fg/45"
            >
              {tag}
            </span>
          ))}
        </div>

        <h2 className="statement display mb-16 max-w-6xl text-3xl font-bold leading-[1.08] md:mb-20 md:text-5xl lg:text-7xl">
          {statement.split(" ").map((w, i) => (
            <span key={i} className="reveal-word mr-[0.28em] inline-block">
              {w}
            </span>
          ))}
        </h2>

        <div className="stat-grid grid grid-cols-1 gap-5 sm:grid-cols-2 md:gap-6 lg:grid-cols-4">
          {stats.map((s) => (
            <div
              key={s.label}
              data-cursor
              className="stat scan-panel corner-cut group relative overflow-hidden p-8 md:p-10"
            >
              <div
                className="absolute -bottom-10 -right-10 h-32 w-32 rounded-full opacity-40 blur-[50px] transition-opacity duration-500 group-hover:opacity-70"
                style={{ background: s.color }}
              />
              <div
                className="chaos-type relative mb-3 text-6xl leading-none md:text-8xl"
                style={{ color: s.color }}
              >
                {s.value}
              </div>
              <div className="terminal relative text-xs text-fg/50">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
