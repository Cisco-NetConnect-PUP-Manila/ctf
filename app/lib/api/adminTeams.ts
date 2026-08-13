import { apiRequest } from "./client";
import type { AdminTeam } from "./types";

export function listAdminTeams() {
  return apiRequest<AdminTeam[]>("/admin/teams", {
    method: "GET",
    cache: "no-store",
  });
}

export function approveAdminTeam(teamId: string) {
  return apiRequest<AdminTeam>(`/admin/teams/${teamId}/approve`, {
    method: "PATCH",
  });
}

export function rejectAdminTeam(teamId: string, reason: string) {
  return apiRequest<AdminTeam>(`/admin/teams/${teamId}/reject`, {
    method: "PATCH",
    body: JSON.stringify({ reason }),
  });
}

export function disableAdminTeam(teamId: string) {
  return apiRequest<AdminTeam>(`/admin/teams/${teamId}/disable`, {
    method: "PATCH",
  });
}

export function reactivateAdminTeam(teamId: string) {
  return apiRequest<AdminTeam>(`/admin/teams/${teamId}/reactivate`, {
    method: "PATCH",
  });
}
