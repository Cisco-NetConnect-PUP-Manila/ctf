"use client";

import { useEffect, useMemo, useState } from "react";
import { getAdminPlatformSettings } from "../../lib/api/adminSettings";
import { getAdminSubmissionMonitor } from "../../lib/api/adminSubmissions";
import { listAdminTeams } from "../../lib/api/adminTeams";
import { ApiError } from "../../lib/api/client";
import type {
  AdminSubmissionMonitorRow,
  AdminTeam,
  PlatformSettings,
} from "../../lib/api/types";

function message(caught: unknown) {
  return caught instanceof ApiError ? caught.message : "Unable to load action center.";
}

export default function AdminActionCenter() {
  const [teams, setTeams] = useState<AdminTeam[]>([]);
  const [signals, setSignals] = useState<AdminSubmissionMonitorRow[]>([]);
  const [settings, setSettings] = useState<PlatformSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const [teamRows, monitor, platformSettings] = await Promise.all([
          listAdminTeams(),
          getAdminSubmissionMonitor(),
          getAdminPlatformSettings(),
        ]);
        if (!alive) return;
        setTeams(teamRows);
        setSignals(monitor.rows);
        setSettings(platformSettings);
      } catch (caught) {
        if (alive) setError(message(caught));
      } finally {
        if (alive) setLoading(false);
      }
    }
    void load();
    return () => {
      alive = false;
    };
  }, []);

  const items = useMemo(() => {
    const pendingTeams = teams.filter((team) => team.status === "pending");
    const suspicious = signals.filter((row) => row.suspicious_notes.length > 0);
    const disabled = teams.filter((team) => team.status === "disabled");
    const entries = [];

    if (pendingTeams.length > 0) {
      entries.push({
        tone: "warn",
        label: "Participant approval",
        value: pendingTeams.length,
        body: `${pendingTeams.length} participant record${pendingTeams.length === 1 ? "" : "s"} waiting for confirmation.`,
        href: "#teams",
      });
    }
    if (suspicious.length > 0) {
      entries.push({
        tone: "danger",
        label: "Suspicious signals",
        value: suspicious.length,
        body: "Review rapid solves or shared client fingerprints.",
        href: "#submissions",
      });
    }
    if (settings && !settings.submissions_open) {
      entries.push({
        tone: "quiet",
        label: "Submissions closed",
        value: "OFF",
        body: "Participant scoring is currently frozen.",
        href: "#control",
      });
    }
    if (settings && !settings.registration_open) {
      entries.push({
        tone: "quiet",
        label: "External intake closed",
        value: "OFF",
        body: "The external registration portal is not accepting new records.",
        href: "#control",
      });
    }
    if (disabled.length > 0) {
      entries.push({
        tone: "quiet",
        label: "Disabled participants",
        value: disabled.length,
        body: "Participant records currently blocked from platform access.",
        href: "#teams",
      });
    }
    return entries;
  }, [signals, settings, teams]);

  if (loading) return <p className="challenge-admin__note">Scanning admin concerns...</p>;
  if (error) return <p className="challenge-admin__error">{error}</p>;

  return (
    <div className="admin-action-center">
      {items.length === 0 ? (
        <div className="admin-action-empty">
          <b>No urgent concerns</b>
          <span>Participant approvals, suspicious signals, and platform controls are clear.</span>
        </div>
      ) : (
        items.map((item) => (
          <a className={`admin-action-item admin-action-item--${item.tone}`} href={item.href} key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.body}</small>
          </a>
        ))
      )}
    </div>
  );
}
