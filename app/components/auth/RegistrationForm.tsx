"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { registerTeam } from "../../lib/api/auth";
import { ApiError } from "../../lib/api/client";
import type { TeamMemberInput } from "../../lib/api/types";
import AuthNotice from "./AuthNotice";
import PasswordVisibilityButton from "./PasswordVisibilityButton";

const EMPTY_MEMBER: TeamMemberInput = { full_name: "", email: "" };

export default function RegistrationForm() {
  const router = useRouter();
  const [groupName, setGroupName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [members, setMembers] = useState<TeamMemberInput[]>([
    { ...EMPTY_MEMBER },
    { ...EMPTY_MEMBER },
    { ...EMPTY_MEMBER },
    { ...EMPTY_MEMBER },
  ]);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  function updateMember(index: number, field: keyof TeamMemberInput, value: string) {
    setMembers((current) =>
      current.map((member, memberIndex) =>
        memberIndex === index ? { ...member, [field]: value } : member
      )
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setFieldErrors({});
    setSubmitting(true);

    const normalizedEmail = email.trim();
    const roster = members.map((member, index) => ({
      full_name: member.full_name.trim(),
      email: index === 0 ? normalizedEmail : member.email.trim(),
    }));

    try {
      await registerTeam({
        group_name: groupName.trim(),
        email: normalizedEmail,
        password,
        members: roster,
      });
      router.push("/login?registered=1");
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught.message);
        setFieldErrors(caught.fieldErrors);
      } else {
        setError("Registration failed unexpectedly. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit} noValidate>
      {error && <AuthNotice tone="error">{error}</AuthNotice>}

      <div className="auth-form__grid">
        <label className="auth-field">
          <span>Group name</span>
          <input
            autoComplete="organization"
            maxLength={120}
            minLength={2}
            name="group_name"
            onChange={(event) => setGroupName(event.target.value)}
            required
            value={groupName}
          />
          {fieldErrors.group_name && <small>{fieldErrors.group_name}</small>}
        </label>

        <label className="auth-field">
          <span>Team login email</span>
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
          {fieldErrors.email && <small>{fieldErrors.email}</small>}
        </label>
      </div>

      <label className="auth-field">
        <span>Password</span>
        <span className="auth-password-input">
          <input
            aria-describedby="password-help"
            autoComplete="new-password"
            maxLength={128}
            minLength={12}
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
        <small id="password-help">Use at least 12 characters.</small>
        {fieldErrors.password && <small>{fieldErrors.password}</small>}
      </label>

      <fieldset className="auth-roster">
        <legend>Team roster ({members.length}/5)</legend>
        <p>
          Register four or five members. Member 1 is the team leader and uses the team login email.
        </p>

        {members.map((member, index) => (
          <div className="auth-member" key={index}>
            <span className="auth-member__number">{String(index + 1).padStart(2, "0")}</span>
            <label className="auth-field">
              <span>{index === 0 ? "Leader name" : "Member name"}</span>
              <input
                autoComplete="name"
                maxLength={160}
                minLength={2}
                onChange={(event) => updateMember(index, "full_name", event.target.value)}
                required
                value={member.full_name}
              />
              {fieldErrors[`members.${index}.full_name`] && (
                <small>{fieldErrors[`members.${index}.full_name`]}</small>
              )}
            </label>
            <label className="auth-field">
              <span>Member email</span>
              <input
                autoComplete="email"
                disabled={index === 0}
                inputMode="email"
                onChange={(event) => updateMember(index, "email", event.target.value)}
                placeholder={index === 0 ? email || "Uses team login email" : "member@example.com"}
                required={index !== 0}
                type="email"
                value={index === 0 ? email : member.email}
              />
              {fieldErrors[`members.${index}.email`] && (
                <small>{fieldErrors[`members.${index}.email`]}</small>
              )}
            </label>
          </div>
        ))}

        <div className="auth-roster__actions">
          {members.length < 5 && (
            <button
              className="btn"
              onClick={() => setMembers((current) => [...current, { ...EMPTY_MEMBER }])}
              type="button"
            >
              Add fifth member
            </button>
          )}
          {members.length === 5 && (
            <button
              className="btn"
              onClick={() => setMembers((current) => current.slice(0, 4))}
              type="button"
            >
              Remove fifth member
            </button>
          )}
        </div>
      </fieldset>

      <button className="btn btn--primary auth-submit" disabled={submitting} type="submit">
        {submitting ? "Transmitting registration..." : "Register team"}
      </button>

      <p className="auth-switch">
        Already registered? <a href="/login">Sign in</a>
      </p>
    </form>
  );
}
