"use client";

import { FormEvent, useEffect, useState } from "react";
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
      access: "An organizer admin account is required to access the admin panel.",
      loggedOut: "Your admin session has been closed successfully.",
    };
  }

  if (portal === "auto") {
    return {
      emailLabel: "Account email",
      placeholder: "participant-or-admin@example.com",
      button: "Enter secure portal",
      submitting: "Verifying account...",
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
    setError("");
    setSubmitting(true);

    try {
      const current = await login({ email: email.trim(), password });
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
      {sessionMessage && <AuthNotice tone="info">{sessionMessage}</AuthNotice>}
      {error && <AuthNotice tone="error">{error}</AuthNotice>}

      <AuthNotice tone="info">
        Use the credentials issued through the official registration process. Access
        opens only after organizer confirmation.
      </AuthNotice>

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

    </form>
  );
}
