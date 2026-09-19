"use client";

import Link from "next/link";
import { ReactNode, useEffect, useState } from "react";
import { getPlatformSettings } from "../../lib/api/platformSettings";
import type { PlatformSettings } from "../../lib/api/types";
import AuthNotice from "./AuthNotice";

export default function RegistrationAvailabilityGate({
  children,
}: {
  children: ReactNode;
}) {
  const [settings, setSettings] = useState<PlatformSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const registrationClosed = Boolean(settings && !settings.registration_open);
  const registrationPaused = Boolean(error || registrationClosed);

  useEffect(() => {
    let alive = true;

    async function load() {
      setLoading(true);
      setError("");
      try {
        const next = await getPlatformSettings();
        if (alive) setSettings(next);
      } catch {
        if (!alive) return;
        setError("Registration is temporarily paused while the competition server is unavailable.");
      } finally {
        if (alive) setLoading(false);
      }
    }

    void load();
    return () => {
      alive = false;
    };
  }, []);

  useEffect(() => {
    if (!registrationPaused) return;
    document.body.classList.add("registration-closed-active");
    return () => {
      document.body.classList.remove("registration-closed-active");
    };
  }, [registrationPaused]);

  if (loading) {
    return (
      <div className="shell auth-page__shell auth-page__shell--single">
        <div className="registration-state" aria-live="polite" aria-busy="true">
          <span className="eyebrow">REGISTRATION.CHECK</span>
          <h2>Checking registration channel</h2>
          <div className="auth-state-page__pulse" aria-hidden="true" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="shell auth-page__shell auth-page__shell--single">
        <div className="registration-state registration-state--closed" role="status">
          <span className="eyebrow">REGISTRATION.PAUSED</span>
          <h2>Registration is temporarily closed</h2>
          <p>
            New team registration is paused while organizers restore the production
            backend. Please wait for the official registration window to reopen.
          </p>
          <AuthNotice tone="info">{error}</AuthNotice>
          <div className="registration-state__actions">
            <Link className="btn" href="/">
              Back to main
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (registrationClosed) {
    return (
      <div className="shell auth-page__shell auth-page__shell--single">
        <div className="registration-state registration-state--closed">
          <span className="eyebrow">REGISTRATION.NOT_OPEN</span>
          <h2>Registration has not opened</h2>
          <p>
            Team registration is not open yet. Please check back when the official
            registration window is announced.
          </p>
          <div className="registration-state__actions">
            <Link className="btn btn--primary" href="/">
              Back to main
            </Link>
            <Link className="btn" href="/login">
              Team login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
