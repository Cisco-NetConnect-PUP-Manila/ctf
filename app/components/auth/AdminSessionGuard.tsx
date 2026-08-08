"use client";

import {
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { getCurrentAccount } from "../../lib/api/auth";
import { ApiError } from "../../lib/api/client";

export default function AdminSessionGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState("");

  const checkAdmin = useCallback(async () => {
    setChecking(true);
    setError("");

    try {
      const current = await getCurrentAccount();
      if (current.account.role !== "admin") {
        router.replace("/login?reason=admin");
        return;
      }
      setAuthorized(true);
    } catch (caught) {
      if (caught instanceof ApiError && (caught.status === 401 || caught.status === 403)) {
        router.replace("/login?reason=session");
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
  }, [router]);

  useEffect(() => {
    void checkAdmin();
  }, [checkAdmin]);

  if (checking || (!authorized && !error)) {
    return (
      <main className="auth-state-page" aria-live="polite">
        <span className="eyebrow">ADMIN.AUTH</span>
        <h1>Verifying organizer credentials</h1>
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
        <button className="btn btn--primary" onClick={() => void checkAdmin()} type="button">
          Retry connection
        </button>
      </main>
    );
  }

  return <>{children}</>;
}
