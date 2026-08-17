"use client";

import Link from "next/link";
import { ReactNode, useEffect, useState } from "react";
import { ApiError } from "../../lib/api/client";
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

  useEffect(() => {
    let alive = true;

    async function load() {
      setLoading(true);
      setError("");
      try {
        const next = await getPlatformSettings();
        if (alive) setSettings(next);
      } catch (caught) {
        if (!alive) return;
        setError(
          caught instanceof ApiError
            ? caught.message
            : "Unable to check registration status."
        );
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
    if (!registrationClosed) return;
    document.body.classList.add("registration-closed-active");
    return () => {
      document.body.classList.remove("registration-closed-active");
    };
  }, [registrationClosed]);

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
        <div className="registration-state" role="alert">
          <span className="eyebrow">REGISTRATION.STATUS</span>
          <h2>Unable to verify registration</h2>
          <AuthNotice tone="error">{error}</AuthNotice>
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
          <span className="eyebrow">REGISTRATION.CLOSED</span>
          <h2>Registration is currently closed</h2>
          <p>
            Team registration is paused by the organizers. Existing approved teams can
            still sign in through the participant channel when the platform is open.
          </p>
          <div className="registration-state__actions">
            <Link className="btn btn--primary" href="/">
              Back to main
            </Link>
            <Link className="btn" href="/participant/login">
              Team login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
