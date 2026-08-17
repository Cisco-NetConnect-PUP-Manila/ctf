"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../../lib/api/client";
import { getParticipantLeaderboard } from "../../lib/api/leaderboard";
import type { ParticipantLeaderboardResponse } from "../../lib/api/types";
import { useParticipantSession } from "../auth/ParticipantSessionGuard";
import Window from "../Window";

function formatLastSolve(value: string | null) {
  if (!value) return "No solve recorded";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "No solve recorded";
  return date.toLocaleString(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ParticipantLeaderboard() {
  const { team } = useParticipantSession();
  const [data, setData] = useState<ParticipantLeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [hidden, setHidden] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    setHidden(false);
    try {
      setData(await getParticipantLeaderboard());
    } catch (caught) {
      if (caught instanceof ApiError && caught.code === "LEADERBOARD_HIDDEN") {
        setHidden(true);
        setData(null);
      } else {
        setError(
          caught instanceof ApiError
            ? caught.message
            : "Unable to load leaderboard standings."
        );
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <Window title="leaderboard.live" meta="backend-calculated standings">
      <div className="participant-leaderboard" aria-live="polite" aria-busy={loading}>
        {loading && <p className="participant-leaderboard__note">Calculating team standings...</p>}

        {!loading && hidden && (
          <div className="participant-leaderboard__state">
            <span className="eyebrow">RANKING.CHANNEL // SEALED</span>
            <h3>Standings are currently hidden</h3>
            <p>Organizers will publish the leaderboard when rankings are ready.</p>
          </div>
        )}

        {!loading && error && (
          <div className="participant-leaderboard__state" role="alert">
            <span className="eyebrow">RANKING.CHANNEL // ERROR</span>
            <p>{error}</p>
            <button className="btn" type="button" onClick={() => void load()}>
              Retry
            </button>
          </div>
        )}

        {!loading && !hidden && !error && data && (
          <>
            <div className="participant-leaderboard__summary">
              <div>
                <span>Your current rank</span>
                <b>#{data.current_team_rank}</b>
              </div>
              <button className="btn" type="button" onClick={() => void load()}>
                Refresh standings
              </button>
            </div>

            {data.rows.length === 0 ? (
              <p className="participant-leaderboard__note">No approved teams are ranked yet.</p>
            ) : (
              <div className="participant-leaderboard__table">
                <div className="participant-leaderboard__labels" aria-hidden="true">
                  <span>Rank / Team</span>
                  <span>Progress</span>
                  <span>Investigation Score</span>
                </div>
                {data.rows.map((row) => {
                  const current = row.team_id === team?.id;
                  return (
                    <article
                      className={`participant-leaderboard__row${current ? " participant-leaderboard__row--current" : ""}`}
                      key={row.team_id}
                    >
                      <div className="participant-leaderboard__identity">
                        <strong>#{row.rank}</strong>
                        <div>
                          <b>{row.team_name}</b>
                          {current && <span>YOUR TEAM</span>}
                        </div>
                      </div>
                      <div className="participant-leaderboard__progress">
                        <span>{row.solved_count} solved</span>
                        <span>Act {row.current_act}</span>
                        <span>{row.intel_penalty} pt Intel penalty</span>
                        <small>{formatLastSolve(row.last_solve_at)}</small>
                      </div>
                      <div className="participant-leaderboard__score">
                        <b>{row.investigation_score}</b>
                        <span>points</span>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
          </>
        )}
      </div>
    </Window>
  );
}
