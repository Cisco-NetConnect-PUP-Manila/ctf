"use client";

import { useEffect, useState } from "react";

type Phase = "landing" | "glitch" | "popup" | "done";

function Frame({ cls }: { cls?: string }) {
  return (
    <div className={`fakeland__frame ${cls ?? ""}`.trim()}>
      <img className="fakeland__logo" src="/images/packet-capture.png" alt="" />
    </div>
  );
}

export default function IntroExperience() {
  const [phase, setPhase] = useState<Phase>("landing");

  useEffect(() => {
    const t1 = setTimeout(() => setPhase("glitch"), 1500); // clean landing, then corrupt
    const t2 = setTimeout(() => setPhase("popup"), 2950); // full-screen glitch -> reveal + welcome
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, []);

  if (phase === "done") return null;

  return (
    <>
      {(phase === "landing" || phase === "glitch") && (
        <div
          className={`fakeland ${phase === "glitch" ? "is-glitch" : ""}`}
          aria-hidden="true"
        >
          {/* three full-screen copies -> RGB channel split across the whole screen */}
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
              <span className="win__title">INCOMING TRANSMISSION</span>
            </div>
            <div className="win__body">
              <p className="welcome__hd">CHANNEL SECURED — WELCOME, RESPONDER.</p>
              <p className="welcome__p">
                You&apos;ve slipped past the surface layer. What sits beneath the
                network is classified, corrupted, and waiting. Trace the evidence,
                unlock the four acts, and preserve every key you recover.
              </p>
              <p className="welcome__hint">[ CLICK ANYWHERE TO CONTINUE ]</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
