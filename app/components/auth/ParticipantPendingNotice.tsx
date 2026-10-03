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
  const rejected = team?.status === "rejected";
  const disabled = team?.status === "disabled";

  useEffect(() => {
    if (approved) {
      router.replace("/platform");
    }
  }, [approved, router]);

  if (approved) {
    return (
      <main className="auth-state-page" aria-live="polite">
        <span className="eyebrow">ACCESS.APPROVED</span>
        <h1>Opening participant platform</h1>
        <div className="auth-state-page__pulse" aria-hidden="true" />
      </main>
    );
  }

  if (rejected || disabled) {
    return (
      <main className="auth-page">
        <div className="shell auth-page__shell">
          <Reveal className="auth-page__intro">
              <span className="eyebrow">{disabled ? "ACCESS.DISABLED" : "ACCESS.REJECTED"}</span>
            <h1 className="auth-title">
              Access
              <br />
              <span className="glitch" data-text={disabled ? "Disabled" : "Rejected"}>
                {disabled ? "Disabled" : "Rejected"}
              </span>
            </h1>
            <p>
              <ParticipantTeamName /> {disabled ? "has been disabled by an organizer." : "was reviewed but could not be approved by the organizers."}
            </p>
          </Reveal>

          <Reveal>
            <Window title="TEAM.STATUS" meta="organizer review complete">
              <div className="portal-lock portal-lock--pending">
                <b>{disabled ? "Participant access is disabled." : "Participant access was not approved."}</b>
                {!disabled && <span>
                  <strong>Organizer reason:</strong>{" "}
                  {team?.rejection_reason || "No rejection reason was provided."}
                </span>}
                <span>
                  Contact the organizers if you need clarification or need your
                  participant record corrected.
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

  return (
    <main className="auth-page">
      <div className="shell auth-page__shell">
        <Reveal className="auth-page__intro">
          <span className="eyebrow">ACCESS.PENDING</span>
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
            <ParticipantTeamName /> is on the participant list. Challenge access
            opens after an organizer confirms the record.
          </p>
        </Reveal>

        <Reveal>
          <Window title="TEAM.STATUS" meta="approval required">
            <div className="portal-lock portal-lock--pending">
            <b>Participant record awaiting confirmation.</b>
              <span>
                The organizer approval queue controls participant access. Once
                confirmed, Act 1 challenges become available through the platform.
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
