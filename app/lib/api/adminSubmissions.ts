import { apiRequest } from "./client";
import type { AdminSubmissionMonitorResponse } from "./types";

export function getAdminSubmissionMonitor() {
  return apiRequest<AdminSubmissionMonitorResponse>("/admin/submission-monitor", {
    method: "GET",
    cache: "no-store",
  });
}
