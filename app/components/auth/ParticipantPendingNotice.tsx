"use client";

import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Reveal from "../Reveal";
import Window from "../Window";
import ParticipantAccountControls, { ParticipantTeamName } from "./ParticipantAccountControls";
import { useParticipantSession } from "./ParticipantSessionGuard";

export default function ParticipantPendingNotice() {
  const router = useRouter();
  const { team } = useParticipantSession();
  const approved = team?.status === "approved";

  useEffect(() => {
    if (approved) {
      router.replace("/platform");
    }
  }, [approved, router]);

  if (approved) {
    return (
      <main className="auth-state-page" aria-live="polite">
        <span className="eyebrow">ACCESS.APPROVED</span>
        <h1>Opening team platform</h1>
        <div className="auth-state-page__pulse" aria-hidden="true" />
      </main>
    );
  }

  return (
    <main className="auth-page">
      <div className="shell auth-page__shell">
        <Reveal className="auth-page__intro">
          <span className="eyebrow">REGISTRATION.PENDING</span>
          <h1 className="auth-title">
            Awaiting
            <br />
            Organizer
            <br />
            <span className="glitch" data-text="Approval">
              Approval
            </span>
          </h1>
          <p>
            <ParticipantTeamName /> is registered. Challenge access opens after an
            organizer approves the team.
          </p>
        </Reveal>

        <Reveal>
          <Window title="TEAM.STATUS" meta="approval required">
            <div className="portal-lock portal-lock--pending">
              <b>Team registration received.</b>
              <span>
                The admin approval queue controls participant access. Once approved,
                Act 1 challenges become available through the platform.
              </span>
              <div className="portal-actions">
                <ParticipantAccountControls />
                <Link className="btn btn--primary portal-lock__main-link" href="/">
                  Back to public site
                </Link>
              </div>
            </div>
          </Window>
        </Reveal>
      </div>
    </main>
  );
}
