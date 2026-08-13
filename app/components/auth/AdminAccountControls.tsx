"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { logout } from "../../lib/api/auth";
import { ApiError } from "../../lib/api/client";
import { useAdminSession } from "./AdminSessionGuard";

export default function AdminAccountControls() {
  const router = useRouter();
  const { account } = useAdminSession();
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
    <div className="portal-account portal-account--admin">
      <div className="portal-account__identity">
        <span>Organizer account</span>
        <strong>Administrator</strong>
        <small>{account.email} / {account.status}</small>
      </div>
      <button className="btn" disabled={signingOut} onClick={handleLogout} type="button">
        {signingOut ? "Closing console..." : "Logout"}
      </button>
      {error && <small className="portal-account__error" role="alert">{error}</small>}
    </div>
  );
}
