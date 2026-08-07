"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "../../lib/api/auth";
import { ApiError } from "../../lib/api/client";
import AuthNotice from "./AuthNotice";

export default function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [registered, setRegistered] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    setRegistered(new URLSearchParams(window.location.search).get("registered") === "1");
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
        <input
          autoComplete="current-password"
          minLength={1}
          name="password"
          onChange={(event) => setPassword(event.target.value)}
          required
          type="password"
          value={password}
        />
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

