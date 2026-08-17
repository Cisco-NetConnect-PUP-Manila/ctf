"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getCurrentAccount } from "../../lib/api/auth";
import type { CurrentAccount } from "../../lib/api/types";

export default function HomeAuthActions({ terminal = false }: { terminal?: boolean }) {
  const [session, setSession] = useState<CurrentAccount | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let active = true;

    getCurrentAccount()
      .then((current) => {
        if (active) setSession(current);
      })
      .catch(() => {
        if (active) setSession(null);
      })
      .finally(() => {
        if (active) setChecking(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const terminalClass = terminal ? " btn--terminal" : "";
  const containerClass = terminal ? "hero__auth-actions" : "btn-row";

  if (checking) {
    return (
      <div className={containerClass} aria-live="polite">
        <span className={`btn btn--ghost${terminalClass}`} aria-disabled="true">
          Checking team channel...
        </span>
      </div>
    );
  }

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
