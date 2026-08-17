"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  approveAdminTeam,
  deleteAdminTeamRegistration,
  disableAdminTeam,
  listAdminTeams,
  reactivateAdminTeam,
  rejectAdminTeam,
} from "../../lib/api/adminTeams";
import { ApiError } from "../../lib/api/client";
import type { AdminTeam } from "../../lib/api/types";

function errorMessage(caught: unknown, fallback: string) {
  return caught instanceof ApiError ? caught.message : fallback;
}

function statusLabel(status: string) {
  return status.replace(/_/g, " ");
}

function formatDate(value: string | null) {
  if (!value) return "--";
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function AdminTeamManager() {
  const [teams, setTeams] = useState<AdminTeam[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [openTeamId, setOpenTeamId] = useState<string | null>(null);
  const [rejectReasons, setRejectReasons] = useState<Record<string, string>>({});

  const counts = useMemo(
    () =>
      teams.reduce(
        (summary, team) => {
          summary.total += 1;
          summary[team.status as keyof typeof summary] =
            Number(summary[team.status as keyof typeof summary] ?? 0) + 1;
          return summary;
        },
        { total: 0, pending: 0, approved: 0, rejected: 0, disabled: 0 }
      ),
    [teams]
  );

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setTeams(await listAdminTeams());
    } catch (caught) {
      setError(errorMessage(caught, "Unable to load team registrations."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => void load(), [load]);

  function updateTeam(updated: AdminTeam) {
    setTeams((current) =>
      current.map((team) => (team.id === updated.id ? updated : team))
    );
  }

  async function runAction(team: AdminTeam, action: () => Promise<AdminTeam>, fallback: string) {
    setBusyId(team.id);
    setError("");
    try {
      updateTeam(await action());
      return true;
    } catch (caught) {
      setError(errorMessage(caught, fallback));
      return false;
    } finally {
      setBusyId(null);
    }
  }

  async function handleReject(team: AdminTeam) {
    const reason = (rejectReasons[team.id] ?? "").trim();
    if (reason.length < 2) {
      setError("Add a rejection reason with at least 2 characters before rejecting this team.");
      return;
    }
    if (!window.confirm(`Reject "${team.group_name}"?\n\nReason: ${reason}`)) return;

    const rejected = await runAction(
      team,
      () => rejectAdminTeam(team.id, reason),
      "Could not reject team."
    );
    if (rejected) {
      setRejectReasons((current) => {
        const next = { ...current };
        delete next[team.id];
        return next;
      });
    }
  }

  async function handleDeleteRegistration(team: AdminTeam) {
    const confirmed = window.confirm(
      `Permanently delete the registration for "${team.group_name}"?\n\nThis removes the team account and cannot be undone.`
    );
    if (!confirmed) return;

    setBusyId(team.id);
    setError("");
    try {
      await deleteAdminTeamRegistration(team.id);
      setTeams((current) => current.filter((candidate) => candidate.id !== team.id));
      setRejectReasons((current) => {
        const next = { ...current };
        delete next[team.id];
        return next;
      });
      if (openTeamId === team.id) setOpenTeamId(null);
    } catch (caught) {
      setError(errorMessage(caught, "Could not delete team registration."));
    } finally {
      setBusyId(null);
    }
  }

  if (loading) {
    return <p className="challenge-admin__note">Loading team registration queue...</p>;
  }

  return (
    <div className="team-admin">
      {error && <div className="challenge-admin__error" role="alert">{error}</div>}

      <div className="challenge-summary team-admin__summary" aria-label="Team registration summary">
        <div>
          <span>Total teams</span>
          <b>{counts.total}</b>
        </div>
        <div>
          <span>Pending approval</span>
          <b>{counts.pending}</b>
        </div>
        <div>
          <span>Approved</span>
          <b>{counts.approved}</b>
        </div>
      </div>

      <div className="team-admin__list">
        {teams.length === 0 && (
          <p className="challenge-admin__note">No team registrations yet.</p>
        )}

        {teams.map((team) => (
          <article className="team-admin-row" key={team.id}>
            <header className="team-admin-row__head">
              <div>
                <span className={`announce-status announce-status--${team.status}`}>
                  {statusLabel(team.status)}
                </span>
                <h4>{team.group_name}</h4>
                <small>{team.email}</small>
              </div>
              <div>
                <b>{team.member_count}</b>
                <small>members</small>
              </div>
            </header>

            <div className="team-admin-row__meta">
              <span>Registered {formatDate(team.created_at)}</span>
              <span>Approved {formatDate(team.approved_at)}</span>
              {team.rejection_reason && <span>Reason: {team.rejection_reason}</span>}
            </div>

            <div className="challenge-admin-row__actions">
              <button
                className="btn"
                onClick={() => setOpenTeamId(openTeamId === team.id ? null : team.id)}
                type="button"
              >
                Members
              </button>
              {team.status !== "approved" && (
                <button
                  className="btn btn--primary"
                  disabled={busyId === team.id}
                  onClick={() =>
                    void runAction(
                      team,
                      () => approveAdminTeam(team.id),
                      "Could not approve team."
                    )
                  }
                  type="button"
                >
                  Approve
                </button>
              )}
              {team.status === "pending" && (
                <button
                  className="btn"
                  disabled={busyId === team.id}
                  onClick={() => void handleReject(team)}
                  type="button"
                >
                  Reject
                </button>
              )}
              {team.status === "approved" && (
                <button
                  className="btn challenge-admin-row__delete"
                  disabled={busyId === team.id}
                  onClick={() =>
                    void runAction(
                      team,
                      () => disableAdminTeam(team.id),
                      "Could not disable team."
                    )
                  }
                  type="button"
                >
                  Disable
                </button>
              )}
              {(team.status === "rejected" || team.status === "disabled") && (
                <button
                  className="btn"
                  disabled={busyId === team.id}
                  onClick={() =>
                    void runAction(
                      team,
                      () => reactivateAdminTeam(team.id),
                      "Could not reactivate team."
                    )
                  }
                  type="button"
                >
                  Reactivate
                </button>
              )}
              {(team.status === "pending" || team.status === "rejected") && (
                <button
                  className="btn challenge-admin-row__delete"
                  disabled={busyId === team.id}
                  onClick={() => void handleDeleteRegistration(team)}
                  type="button"
                >
                  Delete registration
                </button>
              )}
            </div>

            {team.status === "pending" && (
              <label className="team-admin-row__reject">
                Rejection reason
                <input
                  maxLength={500}
                  minLength={2}
                  onChange={(event) =>
                    setRejectReasons((current) => ({
                      ...current,
                      [team.id]: event.target.value,
                    }))
                  }
                  placeholder="Only needed if rejecting this team"
                  value={rejectReasons[team.id] ?? ""}
                />
              </label>
            )}

            {openTeamId === team.id && (
              <div className="team-admin-members">
                {team.members.map((member) => (
                  <div className="challenge-flag" key={member.id}>
                    <span>
                      {member.full_name} - {member.email}
                      {member.is_leader ? " - leader" : ""}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}
