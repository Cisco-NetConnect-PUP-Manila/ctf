"use client";

import { useEffect, useMemo, useState } from "react";
import { listParticipantChallenges } from "../../lib/api/challenges";
import { ApiError } from "../../lib/api/client";
import type { ParticipantChallengeList } from "../../lib/api/types";
import { useParticipantSession } from "../auth/ParticipantSessionGuard";

export default function ParticipantDashboardSnapshot() {
  const { team } = useParticipantSession();
  const [manifest, setManifest] = useState<ParticipantChallengeList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;

    async function load() {
      setLoading(true);
      setError("");
      try {
        const data = await listParticipantChallenges();
        if (!alive) return;
        setManifest(data);
      } catch (caught) {
        if (!alive) return;
        setError(
          caught instanceof ApiError
            ? caught.message
            : "Unable to load team snapshot."
        );
      } finally {
        if (alive) setLoading(false);
      }
    }

    void load();
    return () => {
      alive = false;
    };
  }, []);

  const stats = useMemo(() => {
    const groups = manifest?.acts ?? [];
    const challenges = groups.flatMap((group) => group.challenges);
    const solved = challenges.filter((challenge) => challenge.solved).length;
    const accessible = challenges.filter((challenge) => !challenge.locked).length;
    const published = challenges.length;

    return {
      score: manifest?.current_score ?? 0,
      currentAct: manifest?.current_act ? `Act ${manifest.current_act}` : "Locked",
      solved,
      accessible,
      published,
    };
  }, [manifest]);

  if (loading) {
    return <p className="challenge-admin__hint">Loading team snapshot...</p>;
  }

  if (error) {
    return <p className="challenge-admin__error">{error}</p>;
  }

  return (
    <div className="metric-grid">
      <div className="metric">
        <span>Team</span>
        <b>{team?.group_name}</b>
      </div>
      <div className="metric">
        <span>Investigation Score</span>
        <b>{stats.score}</b>
      </div>
      <div className="metric">
        <span>Current Act</span>
        <b>{stats.currentAct}</b>
      </div>
      <div className="metric">
        <span>Solved Challenges</span>
        <b>{stats.solved}</b>
      </div>
      <div className="metric">
        <span>Available Challenges</span>
        <b>{stats.accessible}</b>
      </div>
      <div className="metric">
        <span>Published Challenges</span>
        <b>{stats.published}</b>
      </div>
    </div>
  );
}
