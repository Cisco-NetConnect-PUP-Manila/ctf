"use client";

import { useRef } from "react";
import { gsap } from "gsap";
import Image from "next/image";
import { useReveal } from "@/lib/useReveal";

export function FinalTransmissionSection() {
  const sectionRef = useRef<HTMLElement>(null);

  useReveal(sectionRef, () => {
    const chars = sectionRef.current?.querySelectorAll(".cta-line");
    if (chars) {
      gsap.from(chars, {
        scrollTrigger: { trigger: sectionRef.current, start: "top 75%" },
        yPercent: 110,
        opacity: 0,
        stagger: 0.12,
        duration: 1.1,
        ease: "expo.out",
      });
    }
  });

  return (
    <section
      id="register"
      ref={sectionRef}
      className="relative container-pad overflow-hidden pb-24 pt-[clamp(80px,10vw,140px)] md:pb-32 lg:pb-40"
    >
      <div className="pointer-events-none absolute bottom-0 left-1/2 h-[70%] w-[120%] -translate-x-1/2 bg-[radial-gradient(ellipse_at_bottom,#ff0a9c44,transparent_65%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[40vw] w-[40vw] bg-[radial-gradient(circle,#5b2eff33,transparent_60%)] blur-[40px]" />

      <div className="relative mx-auto max-w-[1600px]">
        <div className="mx-auto flex flex-col items-center text-center">
          <span className="label mb-6 block text-fg/40">
            Final Transmission
          </span>
          <h2 className="display mb-12 text-5xl leading-[1.06] sm:text-6xl md:text-7xl lg:text-9xl">
            <span className="block overflow-visible">
              <span className="cta-line block leading-[0.95]">Join the</span>
            </span>
            <span className="block overflow-visible py-3">
              <span className="cta-line chaos-type glitch-shadow block leading-[1.12] text-transparent [-webkit-text-stroke:1px_var(--yellow)]">
                Response?
              </span>
            </span>
          </h2>
          <p className="mx-auto max-w-[800px] text-center text-base leading-[1.7] text-fg/50 md:text-lg">
            The network is only the surface. Register your team, preserve every
            artifact, and wait for the final transmission.
          </p>

          <p
            role="status"
            aria-label="Registration opening soon"
            className="terminal mt-7 cursor-default text-center text-xl font-bold uppercase leading-[1.15] tracking-[0.08em] text-fg/80 md:mt-8 md:text-2xl lg:text-3xl"
          >
            Registration Opening Soon
          </p>
        </div>
      </div>
    </section>
  );
}

export function FooterSection() {
  return (
    <footer className="relative mt-auto container-pad pb-0">
      <div className="relative mx-auto max-w-[1600px]">
        <div className="grid grid-cols-2 gap-10 border-t border-fg/10 pb-10 pt-12 text-sm md:grid-cols-4 md:gap-12">
          <div className="col-span-2 flex items-center gap-4 md:col-span-1">
            <Image
              src="/assets/ctf-cross-logo.webp"
              alt=""
              width={388}
              height={837}
              className="h-10 w-auto"
            />
            <span className="pixel text-base text-fg/80">Packet Capture</span>
          </div>

          <div className="flex flex-col gap-3">
            <span className="label mb-1 text-fg/35">Navigate</span>
            <a href="#about" className="terminal link-sweep w-fit text-fg/55 hover:text-fg">About</a>
            <a href="#acts" className="terminal link-sweep w-fit text-fg/55 hover:text-fg">Four Acts</a>
            <a href="#rules" className="terminal link-sweep w-fit text-fg/55 hover:text-fg">Rules</a>
            <a href="#timeline" className="terminal link-sweep w-fit text-fg/55 hover:text-fg">Timeline</a>
          </div>

          <div className="flex flex-col gap-3">
            <span className="label mb-1 text-fg/35">Connect</span>
            <span className="terminal w-fit text-fg/35">Discord / soon</span>
            <span className="terminal w-fit text-fg/35">Twitter / X / soon</span>
            <span className="terminal w-fit text-fg/35">GitHub / soon</span>
          </div>

          <div className="flex flex-col gap-3">
            <span className="label mb-1 text-fg/35">Contact</span>
            <a
              href="mailto:hello@packetcapture.ctf"
              className="terminal link-sweep w-fit text-fg/55 hover:text-fg"
            >
              hello@packetcapture.ctf
            </a>
          </div>
        </div>

        <div className="label flex flex-col items-center justify-between gap-4 border-t border-fg/10 pt-8 text-fg/25 md:flex-row">
          <span>© 2025 Packet Capture CTF</span>
          <span>Beneath the Network</span>
        </div>
      </div>
    </footer>
  );
}
