"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { getAdminLeaderboard } from "../../lib/api/adminSubmissions";
import { ApiError } from "../../lib/api/client";
import type { AdminLeaderboardRow } from "../../lib/api/types";

function formatDate(value: string | null) {
  if (!value) return "--";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "2-digit",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function levelLabel(row: AdminLeaderboardRow) {
  return row.current_act > 0 ? `Act ${row.current_act}` : "Pending";
}

function withTestingRows(rows: AdminLeaderboardRow[]) {
  // Temporary visual filler while the event database has fewer test teams.
  // Remove this before final production launch once real registrations exist.
  if (rows.length >= 10) return rows;

  const existing = [...rows];
  for (let index = rows.length; index < 10; index += 1) {
    const rank = index + 1;
    existing.push({
      rank,
      team_id: `testing-team-${rank}`,
      team_name: `Testing Team ${String(rank).padStart(2, "0")}`,
      team_status: rank % 3 === 0 ? "pending" : "approved",
      member_count: rank % 2 === 0 ? 5 : 4,
      score: 0,
      current_act: rank <= 6 ? 1 : 0,
      solves: 0,
      attempts: 0,
      incorrect_attempts: 0,
      last_solve_at: null,
    });
  }

  return existing;
}

export default function AdminLeaderboard() {
  const [rows, setRows] = useState<AdminLeaderboardRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;

    const previousBodyOverflow = document.body.style.overflow;
    const previousHtmlOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousBodyOverflow;
      document.documentElement.style.overflow = previousHtmlOverflow;
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open]);

  useEffect(() => {
    let alive = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const response = await getAdminLeaderboard();
        if (alive) setRows(response.rows);
      } catch (caught) {
        if (alive) {
          setError(
            caught instanceof ApiError
              ? caught.message
              : "Unable to load admin leaderboard."
          );
        }
      } finally {
        if (alive) setLoading(false);
      }
    }
    void load();
    return () => {
      alive = false;
    };
  }, []);

  if (loading) return <p className="challenge-admin__note">Loading leaderboard...</p>;
  if (error) return <p className="challenge-admin__error">{error}</p>;
  if (rows.length === 0) {
    return <p className="challenge-admin__note">No registered teams yet.</p>;
  }

  const displayRows = withTestingRows(rows);
  const leaderboardModal =
    open && typeof document !== "undefined"
      ? createPortal(
          <div
            className="admin-modal"
            onClick={() => setOpen(false)}
            role="dialog"
            aria-modal="true"
            aria-label="Full leaderboard"
          >
            <div className="admin-modal__panel" onClick={(event) => event.stopPropagation()}>
              <header className="admin-modal__head">
                <div>
                  <span className="eyebrow">ADMIN.LEADERBOARD</span>
                  <h3>All Teams</h3>
                </div>
                <button className="btn" onClick={() => setOpen(false)} type="button">
                  Close
                </button>
              </header>
              <div className="admin-leaderboard admin-leaderboard--modal">
                {displayRows.map((row) => (
                  <article className="admin-leaderboard__row" key={row.team_id}>
                    <div className="admin-leaderboard__rank">
                      {String(row.rank).padStart(2, "0")}
                    </div>
                    <div className="admin-leaderboard__team">
                      <b>{row.team_name}</b>
                      <span>
                        {row.team_status} / {levelLabel(row)} / last solve{" "}
                        {formatDate(row.last_solve_at)}
                      </span>
                    </div>
                    <div className="admin-leaderboard__score">
                      <b>{row.score}</b>
                      <span>
                        {row.solves} solves / {row.attempts} attempts /{" "}
                        {row.incorrect_attempts} wrong
                      </span>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </div>,
          document.body
        )
      : null;

  return (
    <div className="admin-leaderboard">
      <div className="admin-leaderboard__head">
        <span>Top 5 teams</span>
        <button className="btn" onClick={() => setOpen(true)} type="button">
          View all
        </button>
      </div>

      {displayRows.slice(0, 5).map((row) => (
        <article className="admin-leaderboard__row" key={row.team_id}>
          <div className="admin-leaderboard__rank">{String(row.rank).padStart(2, "0")}</div>
          <div className="admin-leaderboard__team">
            <b>{row.team_name}</b>
            <span>
              {row.team_status} / {levelLabel(row)} / {row.member_count} members
            </span>
          </div>
          <div className="admin-leaderboard__score">
            <b>{row.score}</b>
            <span>{row.solves} solves / {row.incorrect_attempts} wrong</span>
          </div>
        </article>
      ))}

      {leaderboardModal}
    </div>
  );
}
