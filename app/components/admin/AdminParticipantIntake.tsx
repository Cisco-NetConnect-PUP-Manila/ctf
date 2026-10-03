"use client";

import { useState } from "react";
import { createAdminParticipant, importAdminParticipants } from "../../lib/api/adminTeams";
import { ApiError } from "../../lib/api/client";
import type { AdminTeam, RegisterInput, TeamMemberInput } from "../../lib/api/types";

type ParticipantType = "solo" | "team";

type AdminParticipantIntakeProps = {
  onCreated: (participant: AdminTeam) => void;
  onImported: (participants: AdminTeam[]) => void;
};

const CSV_HEADERS = [
  "participant_type",
  "group_name",
  "email",
  "password",
  "member_1_name",
  "member_1_email",
  "member_2_name",
  "member_2_email",
  "member_3_name",
  "member_3_email",
  "member_4_name",
  "member_4_email",
  "member_5_name",
  "member_5_email",
];

const CSV_EXAMPLE = [
  CSV_HEADERS.join(","),
  "team,Team Alpha,team@example.com,temporary-password,Leader One,team@example.com,Member Two,two@example.com,Member Three,three@example.com,Member Four,four@example.com,,",
  "solo,Jane Doe,jane@example.com,temporary-password,Jane Doe,jane@example.com,,,,,,,,",
].join("\n");

function newMembers(type: ParticipantType): TeamMemberInput[] {
  return Array.from({ length: type === "solo" ? 1 : 4 }, () => ({
    full_name: "",
    email: "",
  }));
}

function errorMessage(caught: unknown, fallback: string) {
  if (!(caught instanceof ApiError)) return fallback;
  const details = Object.entries(caught.fieldErrors)
    .map(([field, message]) => `${field.replace("row_", "Row ")}: ${message}`)
    .join(" ");
  return details ? `${caught.message} ${details}` : caught.message;
}

export default function AdminParticipantIntake({
  onCreated,
  onImported,
}: AdminParticipantIntakeProps) {
  const [mode, setMode] = useState<"manual" | "csv">("manual");
  const [participantType, setParticipantType] = useState<ParticipantType>("team");
  const [groupName, setGroupName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [members, setMembers] = useState<TeamMemberInput[]>(newMembers("team"));
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function selectType(nextType: ParticipantType) {
    setParticipantType(nextType);
    setMembers(newMembers(nextType));
  }

  function updateMember(index: number, field: keyof TeamMemberInput, value: string) {
    setMembers((current) =>
      current.map((member, memberIndex) =>
        memberIndex === index ? { ...member, [field]: value } : member
      )
    );
  }

  function resetManualForm() {
    setGroupName("");
    setEmail("");
    setPassword("");
    setMembers(newMembers(participantType));
  }

  async function handleManualSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");

    const payload: RegisterInput = {
      participant_type: participantType,
      group_name: groupName,
      email,
      password,
      members,
    };

    try {
      const participant = await createAdminParticipant(payload);
      onCreated(participant);
      setMessage(`${participant.group_name} was added to the pending queue.`);
      resetManualForm();
    } catch (caught) {
      setError(errorMessage(caught, "Could not create the participant record."));
    } finally {
      setBusy(false);
    }
  }

  async function handleCsvSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Choose a CSV file before importing.");
      return;
    }

    setBusy(true);
    setError("");
    setMessage("");
    try {
      const result = await importAdminParticipants(file);
      onImported(result.participants);
      setMessage(`${result.created_count} participant record(s) added to the pending queue.`);
      setFile(null);
      event.currentTarget.reset();
    } catch (caught) {
      setError(errorMessage(caught, "CSV import failed. No records were added."));
    } finally {
      setBusy(false);
    }
  }

  function downloadTemplate() {
    const blob = new Blob([CSV_EXAMPLE], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "packet-capture-participants-template.csv";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="participant-intake" aria-label="Add participants">
      <div className="participant-intake__header">
        <div>
          <span className="eyebrow">ADMIN INTAKE</span>
          <h3>Add participant records</h3>
          <p>Create a pending record manually or import a prepared participant list.</p>
        </div>
        <div className="participant-intake__mode" role="tablist" aria-label="Participant intake method">
          <button
            aria-selected={mode === "manual"}
            className={mode === "manual" ? "is-active" : ""}
            onClick={() => { setMode("manual"); setError(""); setMessage(""); }}
            role="tab"
            type="button"
          >
            Add manually
          </button>
          <button
            aria-selected={mode === "csv"}
            className={mode === "csv" ? "is-active" : ""}
            onClick={() => { setMode("csv"); setError(""); setMessage(""); }}
            role="tab"
            type="button"
          >
            Import CSV
          </button>
        </div>
      </div>

      {message && <div className="challenge-admin__success" role="status">{message}</div>}
      {error && <div className="challenge-admin__error" role="alert">{error}</div>}

      {mode === "manual" ? (
        <form className="participant-intake__form" onSubmit={handleManualSubmit}>
          <div className="participant-intake__type" role="group" aria-label="Participant type">
            <button
              className={participantType === "team" ? "is-active" : ""}
              onClick={() => selectType("team")}
              type="button"
            >
              Team
            </button>
            <button
              className={participantType === "solo" ? "is-active" : ""}
              onClick={() => selectType("solo")}
              type="button"
            >
              Solo
            </button>
          </div>

          <div className="participant-intake__fields">
            <label>
              <span>{participantType === "team" ? "Team name" : "Participant name"}</span>
              <input required value={groupName} onChange={(event) => setGroupName(event.target.value)} />
            </label>
            <label>
              <span>Login email</span>
              <input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
            </label>
            <label>
              <span>Temporary password</span>
              <input
                required
                minLength={12}
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
          </div>

          <div className="participant-intake__roster">
            <div className="participant-intake__roster-head">
              <div>
                <span className="eyebrow">ROSTER</span>
                <h4>{participantType === "team" ? "Team members" : "Participant details"}</h4>
              </div>
              <small>{participantType === "team" ? "4-5 members" : "1 participant"}</small>
            </div>
            {members.map((member, index) => (
              <div className="participant-intake__member" key={index}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <input
                  aria-label={`Member ${index + 1} name`}
                  placeholder="Full name"
                  required
                  value={member.full_name}
                  onChange={(event) => updateMember(index, "full_name", event.target.value)}
                />
                <input
                  aria-label={`Member ${index + 1} email`}
                  placeholder="Email address"
                  required
                  type="email"
                  value={member.email}
                  onChange={(event) => updateMember(index, "email", event.target.value)}
                />
              </div>
            ))}
            {participantType === "team" && members.length < 5 && (
              <button
                className="btn participant-intake__add-member"
                onClick={() => setMembers((current) => [...current, { full_name: "", email: "" }])}
                type="button"
              >
                + Add fifth member
              </button>
            )}
          </div>

          <div className="participant-intake__actions">
            <small>New records stay pending until an organizer approves them.</small>
            <button className="btn btn--primary" disabled={busy} type="submit">
              {busy ? "Creating..." : "Create pending record"}
            </button>
          </div>
        </form>
      ) : (
        <form className="participant-intake__csv" onSubmit={handleCsvSubmit}>
          <div className="participant-intake__csv-copy">
            <h4>Import a participant list</h4>
            <p>
              Use the template so each row represents one solo participant or team. Team rows
              need four or five member pairs; solo rows need one.
            </p>
            <button className="btn" onClick={downloadTemplate} type="button">
              Download CSV template
            </button>
          </div>
          <label className="participant-intake__file">
            <span>CSV file</span>
            <input
              accept=".csv,text/csv"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              required
              type="file"
            />
            <small>{file ? file.name : "UTF-8 CSV, up to 2 MB and 500 records"}</small>
          </label>
          <div className="participant-intake__actions">
            <small>Import is atomic: if one row fails validation, no rows are added.</small>
            <button className="btn btn--primary" disabled={busy} type="submit">
              {busy ? "Importing..." : "Import pending records"}
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
