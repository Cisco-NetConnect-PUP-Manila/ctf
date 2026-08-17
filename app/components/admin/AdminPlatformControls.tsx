"use client";

import { useEffect, useState } from "react";
import {
  getAdminPlatformSettings,
  updateAdminPlatformSettings,
} from "../../lib/api/adminSettings";
import { listAdminTeams } from "../../lib/api/adminTeams";
import { ApiError } from "../../lib/api/client";
import type { CompetitionStatus, PlatformSettings } from "../../lib/api/types";

const STATUS_OPTIONS: Array<{ value: CompetitionStatus; label: string }> = [
  { value: "upcoming", label: "Upcoming" },
  { value: "live", label: "Live" },
  { value: "paused", label: "Paused" },
  { value: "ended", label: "Ended" },
];

function errorMessage(caught: unknown) {
  return caught instanceof ApiError
    ? caught.message
    : "Unable to update platform controls.";
}

export default function AdminPlatformControls() {
  const [settings, setSettings] = useState<PlatformSettings | null>(null);
  const [pendingTeams, setPendingTeams] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let alive = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const [next, teams] = await Promise.all([
          getAdminPlatformSettings(),
          listAdminTeams(),
        ]);
        if (!alive) return;
        setSettings(next);
        setPendingTeams(teams.filter((team) => team.status === "pending").length);
      } catch (caught) {
        if (alive) setError(errorMessage(caught));
      } finally {
        if (alive) setLoading(false);
      }
    }
    void load();
    return () => {
      alive = false;
    };
  }, []);

  async function patch(label: string, payload: Partial<PlatformSettings>) {
    setSaving(label);
    setError("");
    setNotice("");
    try {
      const next = await updateAdminPlatformSettings(payload);
      setSettings(next);
      setNotice("Platform controls updated.");
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setSaving("");
    }
  }

  if (loading) return <p className="challenge-admin__note">Loading platform controls...</p>;
  if (!settings) return <p className="challenge-admin__error">{error}</p>;

  const submissionsClosed =
    !settings.submissions_open || settings.competition_status === "ended";

  return (
    <div className="admin-control-panel">
      {error && <div className="challenge-admin__error" role="alert">{error}</div>}
      {notice && <div className="challenge-admin__success" role="status">{notice}</div>}

      <div className="admin-control-panel__status">
        <span className={`announce-status announce-status--${submissionsClosed ? "archived" : "published"}`}>
          {submissionsClosed ? "Submissions closed" : "Submissions open"}
        </span>
        <strong>{settings.competition_status}</strong>
      </div>

      <div className="admin-control-grid">
        <button
          className={`admin-toggle ${settings.registration_open ? "is-on" : ""}`}
          disabled={Boolean(saving)}
          onClick={() =>
            void patch("registration", {
              registration_open: !settings.registration_open,
            })
          }
          type="button"
        >
          <span>Registration</span>
          <b>{settings.registration_open ? "Open" : "Closed"}</b>
        </button>

        <button
          className={`admin-toggle ${settings.submissions_open ? "is-on" : ""}`}
          disabled={Boolean(saving)}
          onClick={() =>
            void patch("submissions", {
              submissions_open: !settings.submissions_open,
            })
          }
          type="button"
        >
          <span>Submissions</span>
          <b>{settings.submissions_open ? "Open" : "Closed"}</b>
        </button>

        <button
          className={`admin-toggle ${pendingTeams > 0 ? "is-attention" : ""}`}
          disabled
          type="button"
        >
          <span>Pending teams</span>
          <b>{pendingTeams}</b>
        </button>

        <button
          className={`admin-toggle ${settings.leaderboard_visible ? "is-on" : ""}`}
          disabled={Boolean(saving)}
          onClick={() =>
            void patch("leaderboard", {
              leaderboard_visible: !settings.leaderboard_visible,
            })
          }
          type="button"
        >
          <span>Leaderboard</span>
          <b>{settings.leaderboard_visible ? "Visible" : "Hidden"}</b>
        </button>
      </div>

      <label className="admin-control-panel__select">
        Event status
        <select
          disabled={Boolean(saving)}
          onChange={(event) =>
            void patch("status", {
              competition_status: event.target.value as CompetitionStatus,
            })
          }
          value={settings.competition_status}
        >
          {STATUS_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <button
        className="btn btn--primary admin-freeze-button"
        disabled={Boolean(saving)}
        onClick={() =>
          void patch("freeze", {
            competition_status: submissionsClosed ? "live" : "ended",
            submissions_open: submissionsClosed,
            leaderboard_visible: true,
          })
        }
        type="button"
      >
        {submissionsClosed ? "Resume submissions" : "Close submissions"}
      </button>

      <p className="admin-control-panel__note">
        Closing submissions stops new score changes. Existing solves remain recorded
        for the admin leaderboard.
      </p>
    </div>
  );
}
