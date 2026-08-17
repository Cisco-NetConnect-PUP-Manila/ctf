import { apiRequest } from "./client";
import type { AdminLeaderboardResponse, AdminSubmissionMonitorResponse } from "./types";

export function getAdminSubmissionMonitor() {
  return apiRequest<AdminSubmissionMonitorResponse>("/admin/submission-monitor", {
    method: "GET",
    cache: "no-store",
  });
}

export function getAdminLeaderboard() {
  return apiRequest<AdminLeaderboardResponse>("/admin/leaderboard", {
    method: "GET",
    cache: "no-store",
  });
}
