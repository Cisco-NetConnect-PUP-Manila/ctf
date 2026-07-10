"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReveal } from "@/lib/useReveal";

gsap.registerPlugin(ScrollTrigger);

const events = [
  {
    date: "JUL 15",
    title: "Registration Opens",
    desc: "Assemble your response team and reserve a slot before the operation begins.",
    color: "#ff0a9c",
  },
  {
    date: "AUG 01",
    title: "Briefing Window",
    desc: "Teams receive scope, rules of engagement, and the first incident brief.",
    color: "#5b2eff",
  },
  {
    date: "AUG 15",
    title: "Act I Opens",
    desc: "The Signal goes live and the first public traces enter the case file.",
    color: "#ff7a18",
  },
  {
    date: "SEP 01",
    title: "Live Operation",
    desc: "The Breach, The Echo, and the network restoration phases escalate the investigation.",
    color: "#ffc400",
  },
  {
    date: "SEP 02",
    title: "Final Transmission",
    desc: "Qualifying teams face the last layer after preserving the evidence they recovered.",
    color: "#ff2d4f",
  },
];

export function TimelineSection() {
  const sectionRef = useRef<HTMLElement>(null);

  useReveal(sectionRef, () => {
    const boxes = sectionRef.current?.querySelectorAll<HTMLElement>(".flip-box");
    if (!boxes) return;

    boxes.forEach((box) => {
      // Flip forward on scroll down, flip back on scroll up
      gsap.fromTo(
        box,
        { rotateX: -180 },
        {
          rotateX: 0,
          ease: "power2.out",
          scrollTrigger: {
            trigger: box,
            start: "top 85%",
            end: "top 40%",
            scrub: 1,
          },
        }
      );
    });
  });

  return (
    <section
      id="timeline"
      ref={sectionRef}
      className="relative section-pad container-pad overflow-hidden"
    >
      <div className="mx-auto max-w-[1600px]">
        {/* Section header */}
        <div className="flex items-center gap-5 mb-4">
          <span className="label text-magenta">(04)</span>
          <span className="label text-fg/40">Operation Timeline</span>
          <span className="flex-1 h-px bg-fg/10" />
        </div>

        <h2 className="display text-4xl leading-tight md:text-6xl lg:text-8xl">
          Event <span className="chaos-type glitch-shadow text-blue">Timeline</span>
        </h2>

        {/* Spacer between title and boxes */}
        <div className="h-20 md:h-28" />

        {/* Flip boxes grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8" style={{ perspective: "1200px" }}>
          {events.map((e, i) => (
            <div
              key={e.title}
              className="flip-box group relative"
              style={{
                transformStyle: "preserve-3d",
                willChange: "transform",
              }}
            >
              {/* Front face */}
              <div
                className="scan-panel corner-cut relative overflow-hidden"
                style={{
                  backfaceVisibility: "hidden",
                  transformStyle: "preserve-3d",
                }}
              >
                {/* Background */}
                <div
                  className="absolute inset-0 opacity-[0.07]"
                  style={{ background: e.color }}
                />

                {/* Accent edge */}
                <div
                  className="absolute top-0 left-0 w-full h-[3px]"
                  style={{ background: e.color }}
                />

                {/* Content */}
                <div className="relative flex min-h-[200px] flex-col justify-between p-7 md:min-h-[240px] md:p-9">
                  {/* Top: number + date */}
                  <div className="flex items-start justify-between">
                    <span
                      className="chaos-type text-6xl leading-none opacity-25 md:text-7xl"
                      style={{ color: e.color }}
                    >
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span
                      className="terminal border px-2 py-1 text-[0.6rem]"
                      style={{ borderColor: `${e.color}40`, color: e.color }}
                    >
                      {e.date}
                    </span>
                  </div>

                  {/* Bottom: title + desc */}
                  <div>
                    <h3 className="display mb-2 text-xl leading-tight text-white md:text-2xl">
                      {e.title}
                    </h3>
                    <p className="text-fg/40 text-sm leading-relaxed">
                      {e.desc}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
