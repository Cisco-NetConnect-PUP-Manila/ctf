"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { usePathname } from "next/navigation";

type Phase = "landing" | "glitch" | "popup" | "done";
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

function Frame({ cls }: { cls?: string }) {
  return (
    <div className={`fakeland__frame ${cls ?? ""}`.trim()}>
      <Image
        alt=""
        className="fakeland__logo"
        height={5464}
        priority
        sizes="74vw"
        src="/images/packet-capture.png"
        width={9716}
      />
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
    setPhase("landing");
    const t1 = setTimeout(() => setPhase("glitch"), 1600);
    const t2 = setTimeout(() => setPhase("popup"), 3300);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [pathname, publicIntroRoute]);

  if (!publicIntroRoute || phase === "done") return null;

  return (
    <>
      {(phase === "landing" || phase === "glitch") && (
        <div
          className={`fakeland ${phase === "glitch" ? "is-glitch" : ""}`}
          aria-hidden="true"
        >
          {/* Three full-screen copies create a slow, low-contrast signal drift. */}
          <Frame />
          <Frame cls="fakeland__frame--r" />
          <Frame cls="fakeland__frame--b" />
          <div className="fakeland__scan" />
          <div className="fakeland__tear" />
          <div className="fakeland__dropout" />
        </div>
      )}

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
