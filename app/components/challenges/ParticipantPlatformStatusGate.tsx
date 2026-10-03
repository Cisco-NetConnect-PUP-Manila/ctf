"use client";

import Link from "next/link";
import { ReactNode, useEffect, useMemo, useState } from "react";
import { listParticipantChallenges } from "../../lib/api/challenges";
import { ApiError } from "../../lib/api/client";
import {
  getPlatformSettings,
  platformIsFrozen,
} from "../../lib/api/platformSettings";
import type {
  ParticipantChallenge,
  ParticipantChallengeList,
  PlatformSettings,
} from "../../lib/api/types";

type LoadState = {
  settings: PlatformSettings | null;
  manifest: ParticipantChallengeList | null;
};

function firstInProgress(manifest: ParticipantChallengeList | null) {
  const challenges = manifest?.acts.flatMap((group) => group.challenges) ?? [];
  return challenges.find((challenge) => !challenge.locked && !challenge.solved) ?? null;
}

function recapStats(manifest: ParticipantChallengeList | null) {
  const challenges = manifest?.acts.flatMap((group) => group.challenges) ?? [];
  const solved = challenges.filter((challenge) => challenge.solved);
  const available = challenges.filter((challenge) => !challenge.locked);
  const inProgress = firstInProgress(manifest);

  return {
    score: manifest?.current_score ?? 0,
    currentAct: manifest?.current_act ? `Act ${manifest.current_act}` : "Pending",
    solvedCount: solved.length,
    availableCount: available.length,
    publishedCount: challenges.length,
    inProgress,
  };
}

function InProgressLine({
  challenge,
}: {
  challenge: ParticipantChallenge | null;
}) {
  if (!challenge) {
    return (
      <p>
        No active unsolved challenge was left in the unlocked Act when scoring was
        frozen.
      </p>
    );
  }

  return (
    <p>
      Current active problem: <strong>{challenge.title}</strong> in Act{" "}
      {challenge.act_number}, worth {challenge.points} points.
    </p>
  );
}

export default function ParticipantPlatformStatusGate({
  children,
}: {
  children: ReactNode;
}) {
  const [state, setState] = useState<LoadState>({
    settings: null,
    manifest: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;

    async function load(background = false) {
      if (!background) { setLoading(true); setError(""); }
      try {
        const [settings, manifest] = await Promise.all([
          getPlatformSettings(),
          listParticipantChallenges(),
        ]);
        if (alive) setState({ settings, manifest });
      } catch (caught) {
        if (!alive || background) return;
        setError(
          caught instanceof ApiError
            ? caught.message
            : "Unable to verify competition status."
        );
      } finally {
        if (alive && !background) setLoading(false);
      }
    }

    void load();
    const refresh = () => { if (document.visibilityState === "visible") void load(true); };
    const timer = window.setInterval(refresh, 30000);
    window.addEventListener("focus", refresh);
    return () => {
      alive = false;
      window.clearInterval(timer);
      window.removeEventListener("focus", refresh);
    };
  }, []);

  const stats = useMemo(() => recapStats(state.manifest), [state.manifest]);

  if (loading) {
    return (
      <section className="sec">
        <div className="shell">
          <div className="challenge-state" aria-live="polite" aria-busy="true">
            <span className="eyebrow">COMPETITION.STATUS</span>
            <h3>Checking platform controls</h3>
            <div className="auth-state-page__pulse" aria-hidden="true" />
          </div>
        </div>
      </section>
    );
  }

  if (error || !state.settings) {
    return (
      <>
        <section className="sec">
          <div className="shell">
            <div className="challenge-state" role="alert">
              <span className="eyebrow">COMPETITION.STATUS</span>
              <h3>Status check unavailable</h3>
              <p>{error || "Unable to load platform controls."}</p>
              <p>Challenge access remains controlled by the backend.</p>
            </div>
          </div>
        </section>
        {children}
      </>
    );
  }

  const status = state.settings.competition_status;
  const ended = status === "ended";
  const unavailable = platformIsFrozen(state.settings) || status === "paused" || status === "upcoming";
  if (!unavailable) {
    return <>{children}</>;
  }

  return (
    <section className="sec" id="time-up">
      <div className="shell">
        <div className="time-up-panel">
          <div className="time-up-panel__head">
            <span className="eyebrow">COMPETITION.{status.toUpperCase()}</span>
            <h2>{ended ? "Time is up" : status === "upcoming" ? "Competition has not started" : "Scoring is paused"}</h2>
            <p>
              {ended ? "The organizers have closed scoring. Your recorded solves and points remain saved on the leaderboard." : status === "upcoming" ? "Wait for the organizers to open the competition. Your participant account remains registered." : "The organizers have temporarily paused scoring. Your recorded progress remains saved. Check announcements for updates."}
            </p>
          </div>

          <div className="time-up-grid" aria-label="Team final recap">
            <div>
              <span>{ended ? "Final score" : "Recorded score"}</span>
              <b>{stats.score}</b>
            </div>
            <div>
              <span>Stopped at</span>
              <b>{stats.currentAct}</b>
            </div>
            <div>
              <span>Solved</span>
              <b>{stats.solvedCount}</b>
            </div>
            <div>
              <span>Unlocked</span>
              <b>
                {stats.availableCount}/{stats.publishedCount}
              </b>
            </div>
          </div>

          <div className="time-up-panel__progress">
            <span className="eyebrow">CURRENTLY.IN.PROGRESS</span>
            <InProgressLine challenge={stats.inProgress} />
          </div>

          <div className="time-up-panel__actions">
            <Link className="btn btn--primary" href="/">
              Back to main
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
