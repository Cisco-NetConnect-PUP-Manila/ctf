import { apiRequest } from "./client";
import type { ParticipantLeaderboardResponse } from "./types";

export function getParticipantLeaderboard() {
  return apiRequest<ParticipantLeaderboardResponse>("/leaderboard", {
    method: "GET",
    cache: "no-store",
  });
}
