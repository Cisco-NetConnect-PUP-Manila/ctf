"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { listParticipantChallenges } from "../../lib/api/challenges";
import type { ParticipantChallengeList as ChallengeListData } from "../../lib/api/types";
import { ApiError } from "../../lib/api/client";

function challengeStatus(locked: boolean, solved: boolean) {
  if (solved) return "Solved";
  return locked ? "Locked" : "Available";
}

export default function ParticipantChallengeList() {
  const [data, setData] = useState<ChallengeListData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setData(await listParticipantChallenges());
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Unable to load the challenge directory."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const challengeCount = useMemo(
    () => data?.acts.reduce((total, group) => total + group.challenges.length, 0) ?? 0,
    [data]
  );

  if (loading) {
    return (
      <div className="challenge-state" aria-live="polite" aria-busy="true">
        <span className="eyebrow">DIRECTORY.SYNC</span>
        <h3>Decrypting challenge manifest</h3>
        <div className="auth-state-page__pulse" aria-hidden="true" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="challenge-state" role="alert">
        <span className="eyebrow">DIRECTORY.ERROR</span>
        <h3>Challenge manifest unavailable</h3>
        <p>{error}</p>
        <button className="btn btn--primary" type="button" onClick={() => void load()}>
          Retry sync
        </button>
      </div>
    );
  }

  if (!data || challengeCount === 0) {
    return (
      <div className="challenge-state" aria-live="polite">
        <span className="eyebrow">DIRECTORY.EMPTY</span>
        <h3>No published challenges yet</h3>
        <p>Organizer transmissions will appear here when challenges are released.</p>
      </div>
    );
  }

  return (
    <div className="challenge-directory">
      <div className="challenge-summary" aria-label="Team challenge progress">
        <div>
          <span>Investigation score</span>
          <b>{data.current_score}</b>
        </div>
        <div>
          <span>Current Act</span>
          <b>{data.current_act || "Locked"}</b>
        </div>
        <div>
          <span>Published challenges</span>
          <b>{challengeCount}</b>
        </div>
      </div>

      {data.acts.map(({ act, challenges }) => (
        <section
          className={`challenge-act ${act.unlocked ? "" : "challenge-act--locked"}`.trim()}
          key={act.id}
          aria-labelledby={`act-${act.id}`}
        >
          <header className="challenge-act__header">
            <div>
              <span className="eyebrow">ACT {String(act.act_number).padStart(2, "0")}</span>
              <h3 id={`act-${act.id}`}>{act.title}</h3>
              {act.description && <p>{act.description}</p>}
            </div>
            <div className="challenge-act__progress">
              <span className={`status-pill ${act.unlocked ? "" : "status-pill--locked"}`}>
                {act.unlocked ? "Unlocked" : "Locked"}
              </span>
              <small>
                {act.earned_points} / {act.required_points} progression points
              </small>
            </div>
          </header>

          {challenges.length === 0 ? (
            <p className="challenge-act__empty">No published challenges in this Act.</p>
          ) : (
            <div className="challenge-grid">
              {challenges.map((challenge) => (
                <article
                  className={`challenge-card ${challenge.locked ? "challenge-card--locked" : ""} ${
                    challenge.solved ? "challenge-card--solved" : ""
                  }`.trim()}
                  key={challenge.id}
                >
                  <div className="challenge-card__top">
                    <span className="status-pill">
                      {challengeStatus(challenge.locked, challenge.solved)}
                    </span>
                    <b>{challenge.points} pts</b>
                  </div>
                  <h4>{challenge.title}</h4>
                  <div className="challenge-card__tags">
                    <span>{challenge.category ?? "Uncategorized"}</span>
                    <span>{challenge.difficulty ?? "Unrated"}</span>
                  </div>
                  <p>{challenge.mission_brief}</p>
                  {challenge.story_context && (
                    <p className="challenge-card__context">{challenge.story_context}</p>
                  )}
                  {challenge.objectives.length > 0 && (
                    <ul>
                      {challenge.objectives.map((objective) => (
                        <li key={objective}>{objective}</li>
                      ))}
                    </ul>
                  )}
                  {challenge.locked && (
                    <small className="challenge-card__notice">
                      Complete the current Act requirements to unlock this challenge.
                    </small>
                  )}
                </article>
              ))}
            </div>
          )}
        </section>
      ))}
    </div>
  );
}
