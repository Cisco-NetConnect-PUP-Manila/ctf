"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import type { LucideIcon } from "lucide-react";
import { EyeOff, GlobeLock, HardDrive, Network } from "lucide-react";
import { useReveal } from "@/lib/useReveal";

gsap.registerPlugin(ScrollTrigger);

const acts = [
  {
    icon: EyeOff,
    act: "Act I",
    name: "The Signal",
    category: "OSINT",
    challenges: 8,
    points: "800",
    unlock: "500 pts unlocks Act II",
    color: "#ff0a9c",
    desc: "Anonymous profiles, forgotten repositories, archived domains, and leaked traces point toward an organization operating in the shadows.",
    names: [
      "Hidden Profile",
      "Forgotten Repository",
      "Metadata Never Lies",
      "Ghost Domain",
      "Digital Footprints",
      "Mirror Identity",
      "Silent Observer",
      "The Last Breadcrumb",
    ],
  },
  {
    icon: GlobeLock,
    act: "Act II",
    name: "The Breach",
    category: "Web Penetration",
    challenges: 8,
    points: "1,125",
    unlock: "700 pts unlocks Act III",
    color: "#5b2eff",
    desc: "The trail leads to abandoned web applications, hidden portals, confidential documents, source code, and tokens that should not still exist.",
    names: [
      "Login Failure",
      "Employee Records",
      "Hidden Admin",
      "Poisoned Search",
      "Echo Chamber",
      "Backdoor Upload",
      "Session Drift",
      "Final Console",
    ],
  },
  {
    icon: HardDrive,
    act: "Act III",
    name: "The Echo",
    category: "Digital Forensics",
    challenges: 8,
    points: "1,125",
    unlock: "700 pts unlocks Act IV",
    color: "#ff7a18",
    desc: "Hard drives, memory dumps, packet captures, deleted files, and system logs begin contradicting the timeline of the incident.",
    names: [
      "Deleted Doesn't Mean Gone",
      "Hidden Within",
      "USB Secrets",
      "Memory Echoes",
      "Timeline Reconstruction",
      "Registry Secrets",
      "Last Packet",
      "Buried Evidence",
    ],
  },
  {
    icon: Network,
    act: "Act IV",
    name: "Beneath the Network",
    category: "Cisco Packet Tracer",
    challenges: 5,
    points: "1,000",
    unlock: "700 pts + preserved fragments unlock the final layer",
    color: "#ffc400",
    desc: "Connectivity must be restored, routing paths rebuilt, vulnerable devices secured, and hidden infrastructure recovered from the network itself.",
    names: [
      "Broken Topology",
      "VLAN Maze",
      "Routing Blackout",
      "Compromised Edge",
      "Final Backbone",
    ],
  },
] satisfies Array<{
  icon: LucideIcon;
  act: string;
  name: string;
  category: string;
  challenges: number;
  points: string;
  unlock: string;
  color: string;
  desc: string;
  names: string[];
}>;

export function FourActsSection() {
  const sectionRef = useRef<HTMLElement>(null);

  useReveal(sectionRef, () => {
    const scenes = sectionRef.current?.querySelectorAll<HTMLElement>(".act-scene");
    if (!scenes || scenes.length === 0) return;

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: sectionRef.current,
        start: "top top",
        end: () => `+=${scenes.length * window.innerHeight * 0.82}`,
        scrub: 0.6,
        pin: true,
        pinSpacing: "margin",
        anticipatePin: 1,
        invalidateOnRefresh: true,
      },
    });

    scenes.forEach((scene, i) => {
      const enterTargets = scene.querySelectorAll(".act-enter");

      if (i === 0) {
        tl.fromTo(
          enterTargets,
          { y: 42, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.35, stagger: 0.04, ease: "power3.out" },
          0
        );
      }

      if (i < scenes.length - 1) {
        tl.to(enterTargets, {
          y: -34,
          opacity: 0,
          duration: 0.24,
          stagger: 0.02,
          ease: "power2.in",
        });
        tl.set(scene, { visibility: "hidden" });

        const next = scenes[i + 1];
        const nextTargets = next.querySelectorAll(".act-enter");
        tl.set(next, { visibility: "visible" });
        tl.fromTo(
          nextTargets,
          { y: 42, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.35, stagger: 0.04, ease: "power3.out" }
        );
        tl.to({}, { duration: 0.16 });
      }
    });
  });

  return (
    <section
      id="acts"
      ref={sectionRef}
      className="relative isolate h-screen min-h-[720px] overflow-hidden"
    >
      <div className="absolute left-0 right-0 top-6 z-10 container-pad md:top-9">
        <div className="mx-auto max-w-[1600px]">
          <div className="mb-3 flex items-center gap-5">
            <span className="label text-magenta">(02)</span>
            <span className="label text-fg/40">Four Acts</span>
            <span className="h-px flex-1 bg-fg/10" />
          </div>
          <h2 className="display text-3xl leading-[1.05] md:text-5xl">
            The <span className="chaos-type glitch-shadow text-magenta">Investigation</span>
          </h2>
          <p className="terminal mt-3 max-w-2xl text-xs text-fg/35">
            Challenge names, point totals, and unlock thresholds are public.
            Flags and solution fragments stay classified.
          </p>
        </div>
      </div>

      <div className="absolute bottom-6 left-0 right-0 z-10 container-pad md:bottom-9">
        <div className="mx-auto flex max-w-[1600px] items-center justify-center gap-3">
          {acts.map((act) => (
            <div
              key={act.name}
              className="h-1.5 w-12 opacity-45"
              style={{ background: act.color }}
            />
          ))}
        </div>
      </div>

      {acts.map((act, i) => {
        const Icon = act.icon;
        return (
          <div
            key={act.name}
            className="act-scene absolute inset-0 flex items-center justify-center container-pad pb-20 pt-36 md:pb-24 md:pt-40"
            style={{
              visibility: i === 0 ? "visible" : "hidden",
              perspective: "800px",
            }}
          >
            <div
              className="absolute h-[42vw] max-h-[520px] w-[42vw] max-w-[520px] rounded-full opacity-22 blur-[110px]"
              style={{ background: act.color }}
            />

            <div
              className="absolute left-[8%] right-[8%] top-1/2 h-px origin-left"
              style={{ background: `${act.color}18` }}
            />
            <div
              className="absolute bottom-[12%] left-1/2 top-[12%] w-px origin-top"
              style={{ background: `${act.color}12` }}
            />

            <article className="relative z-10 grid w-full max-w-5xl gap-8 md:grid-cols-[0.82fr_1.18fr]">
              <div
                className="pointer-events-none absolute -left-4 top-6 h-24 w-px"
                style={{
                  background: `linear-gradient(${act.color}, transparent)`,
                  boxShadow: `0 0 28px ${act.color}55`,
                }}
              />
              <div
                className="pointer-events-none absolute -right-4 bottom-8 h-px w-36"
                style={{
                  background: `linear-gradient(90deg, transparent, ${act.color})`,
                }}
              />
              <div className="act-enter">
                <div
                  className="meta-chip mb-6 inline-flex border-b px-0 pb-1 text-[0.62rem]"
                  style={{ borderColor: `${act.color}80`, color: act.color }}
                >
                  {act.act} / {act.category}
                </div>

                <div
                  className="mb-5 grid h-14 w-14 place-items-center md:h-16 md:w-16"
                  style={{
                    background: `${act.color}10`,
                    border: `1px solid ${act.color}25`,
                    boxShadow: `0 0 50px ${act.color}30`,
                  }}
                >
                  <Icon
                    aria-hidden="true"
                    className="h-6 w-6 md:h-7 md:w-7"
                    style={{ color: act.color }}
                    strokeWidth={1.5}
                  />
                </div>

                <h3
                  className="display mb-4 text-3xl leading-[1.05] drop-shadow-[0_0_28px_rgba(255,10,156,0.13)] md:text-5xl"
                  style={{ textShadow: `0 0 34px ${act.color}24` }}
                >
                  {act.name}
                </h3>
                <p className="max-w-md text-sm leading-[1.65] text-fg/50">
                  {act.desc}
                </p>
              </div>

              <div className="act-enter flex flex-col justify-between gap-6">
                <div className="grid grid-cols-3 gap-3">
                  <div className="border-t border-fg/12 py-3">
                    <span className="meta-chip block text-[0.56rem] text-fg/35">Cases</span>
                    <strong className="pixel text-lg leading-relaxed text-fg md:text-xl">{act.challenges}</strong>
                  </div>
                  <div className="border-t border-fg/12 py-3">
                    <span className="meta-chip block text-[0.56rem] text-fg/35">Points</span>
                    <strong className="pixel text-lg leading-relaxed text-fg md:text-xl">{act.points}</strong>
                  </div>
                  <div className="border-t border-fg/12 py-3">
                    <span className="meta-chip block text-[0.56rem] text-fg/35">Status</span>
                    <strong className="pixel text-lg leading-relaxed text-fg md:text-xl">Live</strong>
                  </div>
                </div>

                <div>
                  <div className="meta-chip mb-3 text-[0.65rem] text-fg/35">
                    Public case names
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {act.names.map((name) => (
                      <span
                        key={name}
                        className="meta-chip border-b border-fg/12 px-0 py-1 text-[0.6rem] text-fg/52"
                      >
                        {name}
                      </span>
                    ))}
                  </div>
                </div>

                <div
                  className="meta-chip border-l-2 py-2 pl-4 text-xs text-fg/52"
                  style={{ borderColor: act.color }}
                >
                  {act.unlock}
                </div>
              </div>
            </article>
          </div>
        );
      })}
    </section>
  );
}
