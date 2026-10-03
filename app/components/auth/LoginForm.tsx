"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { login } from "../../lib/api/auth";
import { ApiError } from "../../lib/api/client";
import AuthNotice from "./AuthNotice";
import PasswordVisibilityButton from "./PasswordVisibilityButton";

type LoginPortal = "participant" | "admin" | "auto";

type LoginFormProps = {
  portal?: LoginPortal;
};

function copyFor(portal: LoginPortal) {
  if (portal === "admin") {
    return {
      emailLabel: "Admin email",
      placeholder: "you@example.com",
      button: "Enter admin console",
      submitting: "Verifying organizer...",
      access: "An organizer admin account is required to access the admin panel.",
      loggedOut: "Your admin session has been closed successfully.",
    };
  }

  if (portal === "auto") {
    return {
      emailLabel: "Email address",
      placeholder: "you@example.com",
      button: "Sign in",
      submitting: "Signing in...",
      access: "Sign in with an account authorized to open that page.",
      loggedOut: "Your session has been closed successfully.",
    };
  }

  return {
    emailLabel: "Participant email",
    placeholder: "participant@example.com",
    button: "Enter participant portal",
    submitting: "Establishing session...",
    access: "An approved participant account is required to open that page.",
    loggedOut: "Your participant session has been closed successfully.",
  };
}

export default function LoginForm({ portal = "auto" }: LoginFormProps) {
  const router = useRouter();
  const content = copyFor(portal);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [error, setError] = useState("");
  const [sessionMessage, setSessionMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [retryUntil, setRetryUntil] = useState(0);
  const [retrySeconds, setRetrySeconds] = useState(0);
  const [mfaRequired, setMfaRequired] = useState(false);
  const [mfaCode, setMfaCode] = useState("");
  const errorRef = useRef<HTMLDivElement>(null);
  const mfaRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (error) errorRef.current?.focus();
  }, [error]);

  useEffect(() => {
    if (mfaRequired) mfaRef.current?.focus();
  }, [mfaRequired]);

  useEffect(() => {
    if (!retryUntil) return;
    const update = () => {
      const remaining = Math.max(0, Math.ceil((retryUntil - Date.now()) / 1000));
      setRetrySeconds(remaining);
      if (!remaining) setRetryUntil(0);
    };
    update();
    const interval = window.setInterval(update, 1000);
    return () => window.clearInterval(interval);
  }, [retryUntil]);

  useEffect(() => {
    const search = new URLSearchParams(window.location.search);
    const reason = search.get("reason");
    if (reason === "session") {
      setSessionMessage("Your session is missing or expired. Sign in again to continue.");
    } else if (reason === "access") {
      setSessionMessage(content.access);
    } else if (reason === "admin") {
      setSessionMessage("An organizer admin account is required to access the admin panel.");
    } else if (reason === "logged-out") {
      setSessionMessage(content.loggedOut);
    }
  }, [content.access, content.loggedOut, portal]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting || retryUntil > Date.now()) return;
    setError("");
    setSubmitting(true);

    try {
      const current = await login({ email: email.trim(), password, ...(mfaRequired ? { mfa_code: mfaCode } : {}) });
      if (current.account.role === "admin") {
        router.push("/admin");
        router.refresh();
        return;
      }
      if (current.account.role !== "participant") {
        setError("This account role is not recognized.");
        return;
      }
      if (current.team?.status !== "approved") {
        router.push("/participant/pending");
        router.refresh();
        return;
      }
      router.push("/platform");
      router.refresh();
    } catch (caught) {
      if (caught instanceof ApiError && caught.code === "MFA_REQUIRED") {
        setMfaRequired(true);
        return;
      }
      if (caught instanceof ApiError && caught.code === "MFA_INVALID") {
        setMfaCode("");
        setError(caught.message);
        return;
      }
      if (caught instanceof ApiError && caught.status === 429) {
        if (caught.retryAfterSeconds) {
          setRetrySeconds(caught.retryAfterSeconds);
          setRetryUntil(Date.now() + caught.retryAfterSeconds * 1000);
        }
        setError("Too many sign-in attempts. Please wait before trying again.");
        return;
      }
      setError(
        caught instanceof ApiError
          ? caught.status === 401
            ? "Invalid email or password."
            : caught.message
          : "Login failed unexpectedly. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit} aria-busy={submitting}>
      {sessionMessage && <AuthNotice tone="info">{sessionMessage}</AuthNotice>}
      {error && <div id="login-error" ref={errorRef} tabIndex={-1}><AuthNotice tone="error">{error}</AuthNotice></div>}
      {retrySeconds > 0 && (
        <p className="auth-switch" aria-live="off">Try again in {retrySeconds} seconds.</p>
      )}

      <p className="auth-switch">Use the email and password provided for your account.</p>

      <label className="auth-field">
        <span>{content.emailLabel}</span>
        <input
          autoComplete="email"
          inputMode="email"
          name="email"
          aria-describedby={error ? "login-error" : undefined}
          disabled={submitting}
          onChange={(event) => {
            setEmail(event.target.value);
            setMfaRequired(false);
            setMfaCode("");
            setError("");
          }}
          placeholder={content.placeholder}
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
            aria-describedby={error ? "login-error" : undefined}
            disabled={submitting}
            onChange={(event) => {
              setPassword(event.target.value);
              setMfaRequired(false);
              setMfaCode("");
              setError("");
            }}
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

      {mfaRequired && <label className="auth-field">
        <span>Authenticator code</span>
        <input ref={mfaRef} autoComplete="one-time-code" inputMode="numeric" name="mfa_code" pattern="[0-9]{6}" maxLength={6} required value={mfaCode} disabled={submitting} aria-describedby={error ? "login-error" : undefined} onChange={(event) => { setMfaCode(event.target.value.replace(/\D/g, "")); setError(""); }} />
      </label>}

      <button aria-label={submitting ? content.submitting : content.button} className="btn btn--primary auth-submit" disabled={submitting || retrySeconds > 0} type="submit">
        {retrySeconds > 0 ? `Try again in ${retrySeconds}s` : submitting ? content.submitting : content.button}
      </button>
      <p className="auth-switch">
        Need account access? Contact your organizer. <Link href="/">Back to public site</Link>
      </p>
    </form>
  );
}
