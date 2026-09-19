"use client";

import { type CSSProperties, useEffect, useState } from "react";
import Image from "next/image";
import { usePathname } from "next/navigation";

type Phase = "loading" | "reveal" | "popup" | "done";
type Transmission = {
  title: string;
  heading: string;
  body: string;
};

const TRANSMISSIONS: Record<string, Transmission> = {
  "/": {
    title: "INCOMING TRANSMISSION",
    heading: "CHANNEL SECURED - WELCOME, RESPONDER.",
    body: "You've slipped past the surface layer. What sits beneath the network is classified, corrupted, and waiting. Trace the evidence, unlock the four acts, and preserve every key you recover.",
  },
};
const PUBLIC_INTRO_SEEN_KEY = "packet-capture-public-intro-seen";

function IntakeLoader({ phase }: { phase: Phase }) {
  return (
    <div className={`fakeland fakeland--${phase}`} role="status" aria-live="polite">
      <div className="fakeland__grid" aria-hidden="true" />
      <div className="fakeland__field" aria-hidden="true" />

      <div className="fakeland__panel">
        <div className="fakeland__seal" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>

        <Image
          alt="Packet Capture"
          className="fakeland__logo"
          height={5464}
          priority
          sizes="min(78vw, 780px)"
          src="/images/packet-capture.png"
          width={9716}
        />

        <div className="fakeland__meter" aria-hidden="true">
          {Array.from({ length: 12 }, (_, index) => (
            <i key={index} style={{ "--tick": index } as CSSProperties} />
          ))}
        </div>

        <div className="fakeland__copy">
          <span>TVA ARCHIVE INTAKE</span>
          <b>Aligning event branch</b>
        </div>
      </div>
    </div>
  );
}

export default function IntroExperience() {
  const pathname = usePathname();
  const [phase, setPhase] = useState<Phase>("done");
  const publicIntroRoute = pathname === "/";
  const transmission = TRANSMISSIONS[pathname] ?? TRANSMISSIONS["/"];

  useEffect(() => {
    if (!publicIntroRoute) {
      window.sessionStorage.setItem(PUBLIC_INTRO_SEEN_KEY, "true");
      setPhase("done");
      return;
    }

    const hasSeenPublicIntro =
      window.sessionStorage.getItem(PUBLIC_INTRO_SEEN_KEY) === "true";

    if (hasSeenPublicIntro) {
      setPhase("done");
      return;
    }

    window.sessionStorage.setItem(PUBLIC_INTRO_SEEN_KEY, "true");
    setPhase("loading");
    const t1 = setTimeout(() => setPhase("reveal"), 1900);
    const t2 = setTimeout(() => setPhase("popup"), 2450);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [pathname, publicIntroRoute]);

  if (!publicIntroRoute || phase === "done") return null;

  return (
    <>
      {(phase === "loading" || phase === "reveal") && <IntakeLoader phase={phase} />}

      {phase === "popup" && (
        <div className="welcome" onClick={() => setPhase("done")}>
          <div className="welcome__box win" role="dialog" aria-label="Welcome">
            <div className="win__bar">
              <span className="win__title">{transmission.title}</span>
            </div>
            <div className="win__body">
              <p className="welcome__hd">{transmission.heading}</p>
              <p className="welcome__p">{transmission.body}</p>
              <p className="welcome__hint">[ CLICK ANYWHERE TO CONTINUE ]</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
