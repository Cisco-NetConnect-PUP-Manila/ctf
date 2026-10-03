"use client";

import { useEffect, useMemo, useState } from "react";
import { listAdminTeams } from "../../lib/api/adminTeams";
import { listAdminChallenges } from "../../lib/api/challenges";
import { ApiError } from "../../lib/api/client";
import type { AdminChallenge, AdminTeam } from "../../lib/api/types";

export default function AdminOverviewSnapshot() {
  const [teams, setTeams] = useState<AdminTeam[]>([]);
  const [challenges, setChallenges] = useState<AdminChallenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;

    async function load() {
      setLoading(true);
      setError("");
      try {
        const [teamList, challengeList] = await Promise.all([
          listAdminTeams(),
          listAdminChallenges(),
        ]);
        if (!alive) return;
        setTeams(teamList);
        setChallenges(challengeList);
      } catch (caught) {
        if (!alive) return;
        setError(
          caught instanceof ApiError
            ? caught.message
            : "Unable to load admin overview."
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
    const approvedParticipants = teams.filter((team) => team.status === "approved").length;
    const pendingParticipants = teams.filter((team) => team.status === "pending").length;
    const activeParticipants = teams.reduce((total, team) => total + team.member_count, 0);
    const publishedChallenges = challenges.filter(
      (challenge) => challenge.status === "published"
    ).length;
    const draftChallenges = challenges.filter(
      (challenge) => challenge.status !== "published"
    ).length;

    return {
      approvedParticipants,
      activeParticipants,
      pendingParticipants,
      publishedChallenges,
      draftChallenges,
    };
  }, [teams, challenges]);

  if (loading) {
    return <p className="challenge-admin__hint">Loading backend overview...</p>;
  }

  if (error) {
    return <p className="challenge-admin__error">{error}</p>;
  }

  return (
    <div className="metric-grid">
      <div className="metric">
        <span>Approved Records</span>
        <b>{stats.approvedParticipants}</b>
      </div>
      <div className="metric">
        <span>Registered Members</span>
        <b>{stats.activeParticipants}</b>
      </div>
      <div className="metric">
        <span>Pending Confirmation</span>
        <b>{stats.pendingParticipants}</b>
      </div>
      <div className="metric">
        <span>Published Challenges</span>
        <b>{stats.publishedChallenges}</b>
      </div>
      <div className="metric">
        <span>Draft / Hidden</span>
        <b>{stats.draftChallenges}</b>
      </div>
      <div className="metric">
        <span>Backend Status</span>
        <b>Connected</b>
      </div>
    </div>
  );
}
