"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { logout } from "../../lib/api/auth";
import { ApiError } from "../../lib/api/client";
import { useParticipantSession } from "./ParticipantSessionGuard";

export default function ParticipantAccountControls() {
  const router = useRouter();
  const { account, team } = useParticipantSession();
  const [signingOut, setSigningOut] = useState(false);
  const [error, setError] = useState("");

  async function handleLogout() {
    setSigningOut(true);
    setError("");
    try {
      await logout();
      router.replace("/login?reason=logged-out");
      router.refresh();
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Logout failed unexpectedly. Please try again."
      );
      setSigningOut(false);
    }
  }

  return (
    <div className="portal-account">
      <div className="portal-account__identity">
        <span>Authenticated team</span>
        <strong>{team?.group_name}</strong>
        <small>{account.email} // {team?.status}</small>
      </div>
      <button className="btn" disabled={signingOut} onClick={handleLogout} type="button">
        {signingOut ? "Closing session..." : "Logout"}
      </button>
      {error && <small className="portal-account__error" role="alert">{error}</small>}
    </div>
  );
}

export function ParticipantTeamName() {
  const { team } = useParticipantSession();
  return <b>{team?.group_name}</b>;
}

