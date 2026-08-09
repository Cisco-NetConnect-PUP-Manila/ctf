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

const AdminSessionContext = createContext<CurrentAccount | null>(null);

export function useAdminSession() {
  const session = useContext(AdminSessionContext);
  if (!session) {
    throw new Error("useAdminSession must be used inside AdminSessionGuard.");
  }
  return session;
}

export default function AdminSessionGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [session, setSession] = useState<CurrentAccount | null>(null);
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
      setSession(current);
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

  if (checking || (!session && !error)) {
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

  return (
    <AdminSessionContext.Provider value={session}>
      {children}
    </AdminSessionContext.Provider>
  );
}
