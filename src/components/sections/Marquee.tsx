"use client";

const items = [
  "ACT I / THE SIGNAL",
  "ACT II / THE BREACH",
  "ACT III / THE ECHO",
  "ACT IV / BENEATH",
  "PRESERVE / EVERY KEY",
  "RECOVER / EVIDENCE",
  "FINAL / TRANSMISSION",
];

export function Marquee() {
  const row = [...items, ...items];
  return (
    <section className="relative z-10 overflow-hidden border-y border-fg/10 bg-bg-soft/70 py-4">
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(90deg,#060606,transparent_18%,transparent_82%,#060606)]" />
      <div className="marquee-track">
        {row.map((item, i) => (
          <div key={i} className="flex items-center gap-8 px-8">
            <span className="terminal whitespace-nowrap text-xs text-magenta/80">
              [{String((i % items.length) + 1).padStart(2, "0")}]
            </span>
            <span className="pixel whitespace-nowrap text-2xl text-fg/85 md:text-4xl">
              {item}
            </span>
            <span className="h-px w-10 bg-gradient-to-r from-transparent via-fg/18 to-transparent" />
          </div>
        ))}
      </div>
    </section>
  );
}
