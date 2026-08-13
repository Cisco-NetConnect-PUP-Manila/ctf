"use client";

import { useEffect, useMemo, useState } from "react";
import { getAdminSubmissionMonitor } from "../../lib/api/adminSubmissions";
import { ApiError } from "../../lib/api/client";
import type { AdminSubmissionMonitorRow } from "../../lib/api/types";

function formatDate(value: string | null) {
  if (!value) return "--";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatSeconds(value: number | null) {
  if (value === null) return "--";
  if (value < 60) return `${value}s`;
  const minutes = Math.floor(value / 60);
  const seconds = value % 60;
  return `${minutes}m ${seconds}s`;
}

export default function AdminSubmissionMonitor() {
  const [rows, setRows] = useState<AdminSubmissionMonitorRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await getAdminSubmissionMonitor();
      setRows(data.rows);
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Unable to load submission monitor."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const summary = useMemo(() => {
    const suspicious = rows.filter((row) => row.suspicious_notes.length > 0).length;
    const solves = rows.filter((row) => row.solved_at).length;
    const attempts = rows.reduce(
      (total, row) => total + row.correct_attempts + row.incorrect_attempts,
      0
    );
    return { suspicious, solves, attempts };
  }, [rows]);

  if (loading) {
    return <p className="challenge-admin__hint">Loading submission monitor...</p>;
  }

  if (error) {
    return (
      <div className="challenge-state" role="alert">
        <h3>Submission monitor unavailable</h3>
        <p>{error}</p>
        <button className="btn btn--primary" onClick={() => void load()} type="button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="submission-monitor">
      <div className="metric-grid">
        <div className="metric">
          <span>Recorded Attempts</span>
          <b>{summary.attempts}</b>
        </div>
        <div className="metric">
          <span>Recorded Solves</span>
          <b>{summary.solves}</b>
        </div>
        <div className="metric">
          <span>Flagged Signals</span>
          <b>{summary.suspicious}</b>
        </div>
      </div>

      {rows.length === 0 ? (
        <p className="challenge-admin__hint">
          No submissions yet. Attempts will appear here after teams submit flags.
        </p>
      ) : (
        <div className="submission-monitor__list">
          {rows.map((row) => (
            <article
              className={`submission-monitor__row ${
                row.suspicious_notes.length > 0 ? "submission-monitor__row--flagged" : ""
              }`}
              key={`${row.team_id}-${row.challenge_id}`}
            >
              <div className="submission-monitor__main">
                <span className="eyebrow">{row.challenge_title}</span>
                <h4>{row.team_name}</h4>
                <small>
                  First attempt {formatDate(row.first_attempt_at)} / solved{" "}
                  {formatDate(row.solved_at)}
                </small>
              </div>
              <div className="submission-monitor__stats">
                <span>{row.correct_attempts} correct</span>
                <span>{row.incorrect_attempts} wrong</span>
                <span>{formatSeconds(row.seconds_to_solve)} to solve</span>
                <span>IP x{row.shared_ip_hash_team_count || 1}</span>
              </div>
              {row.suspicious_notes.length > 0 && (
                <ul className="submission-monitor__notes">
                  {row.suspicious_notes.map((note) => (
                    <li key={note}>{note}</li>
                  ))}
                </ul>
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
