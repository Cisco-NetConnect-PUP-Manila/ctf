"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { getCurrentAccount } from "../../lib/api/auth";
import { ApiError } from "../../lib/api/client";
import type { CurrentAccount } from "../../lib/api/types";

const ParticipantSessionContext = createContext<CurrentAccount | null>(null);

export function useParticipantSession() {
  const session = useContext(ParticipantSessionContext);
  if (!session) {
    throw new Error("useParticipantSession must be used inside ParticipantSessionGuard.");
  }
  return session;
}

export default function ParticipantSessionGuard({
  allowPending = false,
  children,
}: {
  allowPending?: boolean;
  children: ReactNode;
}) {
  const router = useRouter();
  const [session, setSession] = useState<CurrentAccount | null>(null);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState("");

  const checkSession = useCallback(async () => {
    setChecking(true);
    setError("");

    try {
      const current = await getCurrentAccount();
      if (current.account.role !== "participant" || !current.team) {
        router.replace("/participant/login?reason=access");
        return;
      }
      if (!allowPending && current.team.status !== "approved") {
        router.replace("/participant/pending");
        return;
      }
      setSession(current);
    } catch (caught) {
      if (caught instanceof ApiError && (caught.status === 401 || caught.status === 403)) {
        router.replace("/participant/login?reason=session");
        return;
      }
      setError(
        caught instanceof ApiError
          ? caught.message
          : "The session check failed unexpectedly."
      );
    } finally {
      setChecking(false);
    }
  }, [allowPending, router]);

  useEffect(() => {
    void checkSession();
  }, [checkSession]);

  if (checking || (!session && !error)) {
    return (
      <main className="auth-state-page" aria-live="polite">
        <span className="eyebrow">SESSION.CHECK</span>
        <h1>Authenticating team channel</h1>
        <div className="auth-state-page__pulse" aria-hidden="true" />
      </main>
    );
  }

  if (error) {
    return (
      <main className="auth-state-page" role="alert">
        <span className="eyebrow">CONNECTION.ERROR</span>
        <h1>Unable to verify session</h1>
        <p>{error}</p>
        <button className="btn btn--primary" onClick={() => void checkSession()} type="button">
          Retry connection
        </button>
      </main>
    );
  }

  return (
    <ParticipantSessionContext.Provider value={session}>
      {children}
    </ParticipantSessionContext.Provider>
  );
}

