"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getCurrentAccount } from "../../lib/api/auth";
import { getPlatformSettings } from "../../lib/api/platformSettings";
import type { CurrentAccount, PlatformSettings } from "../../lib/api/types";

export default function HomeAuthActions({ terminal = false }: { terminal?: boolean }) {
  const [session, setSession] = useState<CurrentAccount | null>(null);
  const [settings, setSettings] = useState<PlatformSettings | null>(null);
  const [settingsUnavailable, setSettingsUnavailable] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadAccessState() {
      const [currentResult, settingsResult] = await Promise.allSettled([
        getCurrentAccount(),
        getPlatformSettings(),
      ]);

      if (!active) return;

      setSession(currentResult.status === "fulfilled" ? currentResult.value : null);
      if (settingsResult.status === "fulfilled") {
        setSettings(settingsResult.value);
        setSettingsUnavailable(false);
      } else {
        setSettings(null);
        setSettingsUnavailable(true);
      }
      setChecking(false);
    }

    void loadAccessState();

    return () => {
      active = false;
    };
  }, []);

  const terminalClass = terminal ? " btn--terminal" : "";
  const containerClass = terminal ? "hero__auth-actions" : "btn-row";

  if (checking) {
    return (
      <div className={`${containerClass} home-auth-closed`} aria-live="polite">
        <p>
          <span>Registration is currently closed.</span>
          <b>Please check back for the official opening.</b>
        </p>
      </div>
    );
  }

  const registrationUnavailable =
    settingsUnavailable || !settings || !settings.registration_open;

  if (session?.account.role === "participant" && session.team) {
    return (
      <div className={containerClass}>
        <Link className={`btn btn--primary${terminalClass}`} href="/platform">
          Competition Platform
        </Link>
      </div>
    );
  }

  if (session?.account.role === "admin") {
    return (
      <div className={containerClass}>
        <Link className={`btn btn--primary${terminalClass}`} href="/admin">
          Admin Dashboard
        </Link>
      </div>
    );
  }

  if (registrationUnavailable) {
    return (
      <div className={`${containerClass} home-auth-closed`} aria-live="polite">
        <p>
          <span>Registration is currently closed.</span>
          <b>Please check back for the official opening.</b>
        </p>
      </div>
    );
  }

  return (
    <div className={containerClass}>
      <Link className={`btn btn--primary${terminalClass}`} href="/register">
        Register team
      </Link>
      <Link
        className={`btn${terminal ? " btn--ghost btn--terminal hero__sign-in" : ""}`}
        href="/login"
      >
        {terminal ? "Sign in" : "Team login"}
      </Link>
    </div>
  );
}
