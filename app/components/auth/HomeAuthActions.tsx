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

    async function loadAccessState() {
      const [currentResult] = await Promise.allSettled([getCurrentAccount()]);

      if (!active) return;

      setSession(currentResult.status === "fulfilled" ? currentResult.value : null);
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
    return terminal ? <div className={containerClass} aria-hidden="true" /> : null;
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
      <Link
        className={`btn btn--primary${terminalClass}`}
        href="/login"
      >
        {terminal ? "Participant sign in" : "Participant access"}
      </Link>
    </div>
  );
}
