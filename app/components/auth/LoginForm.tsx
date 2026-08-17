"use client";

import { FormEvent, useEffect, useState } from "react";
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
      placeholder: "admin@example.com",
      button: "Enter admin console",
      submitting: "Verifying organizer...",
      registered: "Team registration received. Wait for admin approval before entering the platform.",
      access: "An organizer admin account is required to access the admin panel.",
      loggedOut: "Your admin session has been closed successfully.",
    };
  }

  return {
    emailLabel: "Team email",
    placeholder: "team@example.com",
    button: "Enter team portal",
    submitting: "Establishing session...",
    registered: "Team registration received. Sign in with the team email to continue.",
    access: "A participant team account is required to open that page.",
    loggedOut: "Your team session has been closed successfully.",
  };
}

export default function LoginForm({ portal = "participant" }: LoginFormProps) {
  const router = useRouter();
  const content = copyFor(portal);
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
      setSessionMessage(content.access);
    } else if (reason === "admin") {
      setSessionMessage("An organizer admin account is required to access the admin panel.");
    } else if (reason === "logged-out") {
      setSessionMessage(content.loggedOut);
    }
  }, [content.access, content.loggedOut, portal]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const current = await login({ email: email.trim(), password });
      if (current.account.role === "admin") {
        if (portal === "participant") {
          setError("Use the admin login page for organizer accounts.");
          return;
        }
        router.push("/admin");
        router.refresh();
        return;
      }
      if (current.account.role !== "participant") {
        setError("This account role is not recognized.");
        return;
      }
      if (portal === "admin") {
        setError("Use a team account on the participant login page.");
        return;
      }
      if (portal !== "auto" && current.team?.status !== "approved") {
        router.push("/participant/pending");
        router.refresh();
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
          {content.registered}
        </AuthNotice>
      )}
      {sessionMessage && <AuthNotice tone="info">{sessionMessage}</AuthNotice>}
      {error && <AuthNotice tone="error">{error}</AuthNotice>}

      <label className="auth-field">
        <span>{content.emailLabel}</span>
        <input
          autoComplete="email"
          inputMode="email"
          name="email"
          onChange={(event) => {
            setEmail(event.target.value);
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
            onChange={(event) => {
              setPassword(event.target.value);
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

      <button className="btn btn--primary auth-submit" disabled={submitting} type="submit">
        {submitting ? content.submitting : content.button}
      </button>

      {portal !== "admin" && (
        <p className="auth-switch">
          No team account yet? <Link href="/register">Register your team</Link>
        </p>
      )}
    </form>
  );
}
