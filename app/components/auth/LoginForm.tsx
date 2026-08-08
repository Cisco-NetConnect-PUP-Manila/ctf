"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "../../lib/api/auth";
import { ApiError } from "../../lib/api/client";
import AuthNotice from "./AuthNotice";
import PasswordVisibilityButton from "./PasswordVisibilityButton";

export default function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [error, setError] = useState("");
  const [registered, setRegistered] = useState(false);
  const [sessionMessage, setSessionMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const search = new URLSearchParams(window.location.search);
    setRegistered(search.get("registered") === "1");
    const reason = search.get("reason");
    if (reason === "session") {
      setSessionMessage("Your session is missing or expired. Sign in again to continue.");
    } else if (reason === "access") {
      setSessionMessage("A participant team account is required to open that page.");
    } else if (reason === "logged-out") {
      setSessionMessage("Your team session has been closed successfully.");
    }
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const current = await login({ email: email.trim(), password });
      if (current.account.role !== "participant") {
        setError("This login is not a participant account.");
        return;
      }
      router.push("/platform");
      router.refresh();
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Login failed unexpectedly. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit} noValidate>
      {registered && (
        <AuthNotice tone="success">
          Team registration received. Sign in with the team email to continue.
        </AuthNotice>
      )}
      {sessionMessage && <AuthNotice tone="info">{sessionMessage}</AuthNotice>}
      {error && <AuthNotice tone="error">{error}</AuthNotice>}

      <label className="auth-field">
        <span>Team email</span>
        <input
          autoComplete="email"
          inputMode="email"
          name="email"
          onChange={(event) => setEmail(event.target.value)}
          placeholder="team@example.com"
          required
          type="email"
          value={email}
        />
      </label>

      <label className="auth-field">
        <span>Password</span>
        <span className="auth-password-input">
          <input
            autoComplete="current-password"
            minLength={1}
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            required
            type={passwordVisible ? "text" : "password"}
            value={password}
          />
          <PasswordVisibilityButton
            onToggle={() => setPasswordVisible((current) => !current)}
            visible={passwordVisible}
          />
        </span>
      </label>

      <button className="btn btn--primary auth-submit" disabled={submitting} type="submit">
        {submitting ? "Establishing session..." : "Enter team portal"}
      </button>

      <p className="auth-switch">
        No team account yet? <a href="/register">Register your team</a>
      </p>
    </form>
  );
}
