"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import {
  getParticipantChallenge,
  listParticipantChallengeFiles,
  participantChallengeFileDownloadUrl,
  submitChallengeFlag,
} from "../../lib/api/challenges";
import { ApiError } from "../../lib/api/client";
import type {
  ChallengeFile,
  FlagSubmissionResult,
  ParticipantChallenge,
} from "../../lib/api/types";

function formatBytes(bytes: number) {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  if (bytes >= 1024) return `${Math.ceil(bytes / 1024)} KB`;
  return `${bytes} B`;
}

function fragmentForDisplay(
  challenge: ParticipantChallenge | null,
  submission: FlagSubmissionResult | null
) {
  return submission?.team_fragment ?? challenge?.team_fragment ?? null;
}

export default function ParticipantChallengeDetail({ challengeId }: { challengeId: string }) {
  const [challenge, setChallenge] = useState<ParticipantChallenge | null>(null);
  const [files, setFiles] = useState<ChallengeFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [flag, setFlag] = useState("");
  const [error, setError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [submission, setSubmission] = useState<FlagSubmissionResult | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [challengeData, fileData] = await Promise.all([
        getParticipantChallenge(challengeId),
        listParticipantChallengeFiles(challengeId),
      ]);
      setChallenge(challengeData);
      setFiles(fileData);
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Unable to load this challenge transmission."
      );
    } finally {
      setLoading(false);
    }
  }, [challengeId]);

  useEffect(() => {
    void load();
  }, [load]);

  const teamFragment = useMemo(
    () => fragmentForDisplay(challenge, submission),
    [challenge, submission]
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!flag.trim() || submitting) return;

    setSubmitting(true);
    setSubmitError("");
    setSubmission(null);

    try {
      const result = await submitChallengeFlag(challengeId, flag);
      setSubmission(result);
      setFlag("");
      setChallenge((current) =>
        current
          ? {
              ...current,
              solved: result.solved || current.solved,
              awarded_points:
                result.awarded_points > 0 ? result.awarded_points : current.awarded_points,
              team_fragment: result.team_fragment ?? current.team_fragment,
            }
          : current
      );
    } catch (caught) {
      setSubmitError(
        caught instanceof ApiError ? caught.message : "Unable to submit the flag."
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="challenge-state" aria-live="polite" aria-busy="true">
        <span className="eyebrow">CHALLENGE.SYNC</span>
        <h3>Opening secured challenge channel</h3>
        <div className="auth-state-page__pulse" aria-hidden="true" />
      </div>
    );
  }

  if (error || !challenge) {
    return (
      <div className="challenge-state" role="alert">
        <span className="eyebrow">CHALLENGE.ACCESS</span>
        <h3>Challenge unavailable</h3>
        <p>{error || "This challenge could not be found."}</p>
        <Link className="btn btn--primary" href="/platform#challenges">
          Back to directory
        </Link>
      </div>
    );
  }

  return (
    <div className="challenge-detail">
      <div className="challenge-detail__nav">
        <Link href="/platform#challenges">Back to directory</Link>
      </div>

      <section className="challenge-detail__hero">
        <div>
          <span className="eyebrow">ACT {String(challenge.act_number).padStart(2, "0")}</span>
          <h1>{challenge.title}</h1>
          <div className="challenge-card__tags">
            <span>{challenge.category ?? "Uncategorized"}</span>
            <span>{challenge.difficulty ?? "Unrated"}</span>
            <span>{challenge.points} pts</span>
          </div>
        </div>
        <span className={`status-pill ${challenge.solved ? "" : "status-pill--locked"}`}>
          {challenge.solved ? "Solved" : "Available"}
        </span>
      </section>

      <section className="challenge-detail__grid">
        <article className="challenge-detail__panel">
          <span className="eyebrow">MISSION.BRIEF</span>
          <p>{challenge.mission_brief}</p>
          {challenge.story_context && (
            <>
              <span className="eyebrow">STORY.CONTEXT</span>
              <p>{challenge.story_context}</p>
            </>
          )}
          {challenge.objectives.length > 0 && (
            <>
              <span className="eyebrow">OBJECTIVES</span>
              <ul>
                {challenge.objectives.map((objective) => (
                  <li key={objective}>{objective}</li>
                ))}
              </ul>
            </>
          )}
        </article>

        <aside className="challenge-detail__panel">
          <span className="eyebrow">EVIDENCE.FILES</span>
          <div className="challenge-card__file-list">
            {files.length === 0 && <small>No attached files for this challenge.</small>}
            {files.map((file) => (
              <a
                href={participantChallengeFileDownloadUrl(challenge.id, file.id)}
                key={file.id}
              >
                <span>{file.display_name}</span>
                <small>{file.extension} - {formatBytes(file.size_bytes)}</small>
              </a>
            ))}
          </div>
        </aside>
      </section>

      <section className="challenge-detail__submit" aria-live="polite">
        <form onSubmit={handleSubmit}>
          <label htmlFor="challenge-flag">Recovered flag</label>
          <div>
            <input
              autoComplete="off"
              id="challenge-flag"
              maxLength={256}
              onChange={(event) => setFlag(event.target.value)}
              placeholder="PacketCapture{...}"
              type="text"
              value={flag}
            />
            <button className="btn btn--primary" disabled={submitting} type="submit">
              {submitting ? "Submitting..." : "Submit flag"}
            </button>
          </div>
        </form>

        {submitError && <p className="challenge-detail__error">{submitError}</p>}
        {submission && (
          <p className={submission.correct ? "challenge-detail__success" : "challenge-detail__error"}>
            {submission.message}
          </p>
        )}
        {teamFragment && (
          <div className="challenge-detail__fragment">
            <span>Team solve fragment</span>
            <b>{teamFragment}</b>
          </div>
        )}
      </section>
    </div>
  );
}
