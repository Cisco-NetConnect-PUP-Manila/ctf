"use client";

import { useState, useEffect } from "react";
import { Loader } from "@/components/Loader";
import { Cursor } from "@/components/Cursor";
import { RevealWrapper } from "@/components/RevealWrapper";
import { SmoothScroll } from "@/components/SmoothScroll";
import { FloatingOrbs } from "@/components/FloatingOrbs";
import { NetworkCore } from "@/components/NetworkCore";
import { Navbar } from "@/components/Navbar";
import { PageDivider } from "@/components/PageDivider";
import { HeroSection } from "@/components/sections/HeroSection";
import { Marquee } from "@/components/sections/Marquee";
import { AboutSection } from "@/components/sections/AboutSection";
import { FourActsSection } from "@/components/sections/FourActsSection";
import { RulesSection } from "@/components/sections/RulesSection";
import { TimelineSection } from "@/components/sections/TimelineSection";
import { SponsorsSection } from "@/components/sections/SponsorsSection";
import {
  FinalTransmissionSection,
  FooterSection,
} from "@/components/sections/FooterSection";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

export default function Home() {
  const [loaded, setLoaded] = useState(false);
  const reducedMotion = usePrefersReducedMotion();

  useEffect(() => {
    document.body.style.overflow = loaded ? "" : "hidden";
  }, [loaded]);

  return (
    <>
      <Cursor />
      {!loaded && <Loader onComplete={() => setLoaded(true)} />}

      <SmoothScroll enabled={loaded && !reducedMotion}>
        <RevealWrapper start={loaded}>
          <div className="relative flex min-h-screen flex-col">
            <FloatingOrbs />
            <NetworkCore active={loaded} />
            <div
              className="muted-backdrop pointer-events-none fixed inset-0 z-[2]"
              aria-hidden="true"
            />
            <Navbar />
            <main className="relative z-10 flex flex-1 flex-col">
              <HeroSection />
              <Marquee />

              <PageDivider label="/ story" />
              <AboutSection />

              <PageDivider label="/ four acts" />
              <FourActsSection />

              <PageDivider label="/ rules of engagement" />
              <RulesSection />

              <PageDivider label="/ timeline" />
              <TimelineSection />

              <PageDivider label="/ sponsors" />
              <SponsorsSection />

              <PageDivider label="/ register" />
              <FinalTransmissionSection />
              <FooterSection />
            </main>
          </div>
        </RevealWrapper>
      </SmoothScroll>
    </>
  );
}
