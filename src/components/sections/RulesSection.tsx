"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import { EyeOff, KeyRound, Network, ShieldCheck } from "lucide-react";
import { useReveal } from "@/lib/useReveal";

const rules = [
  {
    icon: ShieldCheck,
    title: "Work Inside Scope",
    desc: "Investigate only the systems, files, and infrastructure provided for the operation.",
    color: "#ff0a9c",
  },
  {
    icon: KeyRound,
    title: "Preserve Every Key",
    desc: "Recovered keys and artifacts may matter later. Do not discard evidence just because it looks small.",
    color: "#ffc400",
  },
  {
    icon: Network,
    title: "Unlock in Sequence",
    desc: "Each act opens through its point threshold. The final layer requires Act IV progress and preserved fragments.",
    color: "#5b2eff",
  },
  {
    icon: EyeOff,
    title: "Keep the Case Clean",
    desc: "No flag sharing, team sabotage, or attacks against infrastructure outside the assigned environment.",
    color: "#ff7a18",
  },
];

export function RulesSection() {
  const sectionRef = useRef<HTMLElement>(null);

  useReveal(sectionRef, () => {
    const cards = sectionRef.current?.querySelectorAll(".rule-card");
    if (!cards) return;

    gsap.from(cards, {
      scrollTrigger: { trigger: sectionRef.current, start: "top 72%" },
      y: 42,
      opacity: 0,
      stagger: 0.1,
      duration: 0.9,
      ease: "expo.out",
    });
  });

  return (
    <section
      id="rules"
      ref={sectionRef}
      className="relative section-pad container-pad overflow-hidden"
    >
      <div className="pointer-events-none absolute left-[-20%] top-1/4 h-[55vw] w-[55vw] rounded-full bg-[radial-gradient(circle,#5b2eff33,transparent_62%)] blur-[60px]" />

      <div className="relative mx-auto max-w-[1600px]">
        <div className="mb-4 flex items-center gap-5">
          <span className="label text-magenta">(03)</span>
          <span className="label text-fg/40">Rules of Engagement</span>
          <span className="h-px flex-1 bg-fg/10" />
        </div>

        <div className="mb-14 grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-end">
          <h2 className="display max-w-4xl text-4xl leading-tight md:text-6xl lg:text-8xl">
            Preserve the <span className="chaos-type glitch-shadow text-yellow">Evidence</span>
          </h2>
          <p className="max-w-2xl text-base leading-relaxed text-fg/52 md:text-lg">
            This is an incident response operation, not a free-for-all. Follow
            the trail, respect the scope, and keep every recovered artifact
            until the final transmission tells you otherwise.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
          {rules.map((rule) => {
            const Icon = rule.icon;
            return (
              <article
                key={rule.title}
                className="rule-card scan-panel corner-cut group relative overflow-hidden p-7 md:p-8"
              >
                <div
                  className="absolute -right-12 -top-12 h-36 w-36 rounded-full opacity-25 blur-[50px] transition-opacity duration-500 group-hover:opacity-50"
                  style={{ background: rule.color }}
                />
                <div
                  className="mb-7 grid h-12 w-12 place-items-center border"
                  style={{
                    borderColor: `${rule.color}35`,
                    background: `${rule.color}10`,
                  }}
                >
                  <Icon
                    aria-hidden="true"
                    className="h-5 w-5"
                    style={{ color: rule.color }}
                    strokeWidth={1.6}
                  />
                </div>
                <h3 className="display mb-3 text-2xl leading-tight">
                  {rule.title}
                </h3>
                <p className="text-sm leading-relaxed text-fg/45">
                  {rule.desc}
                </p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
