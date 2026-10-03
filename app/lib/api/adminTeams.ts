import { apiRequest } from "./client";
import type {
  AdminParticipantImportResponse,
  AdminTeam,
  RegisterInput,
} from "./types";

export function listAdminTeams() {
  return apiRequest<AdminTeam[]>("/admin/teams", {
    method: "GET",
    cache: "no-store",
  });
}

export function createAdminParticipant(payload: RegisterInput) {
  return apiRequest<AdminTeam>("/admin/teams", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function importAdminParticipants(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest<AdminParticipantImportResponse>("/admin/teams/import", {
    method: "POST",
    body: formData,
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

export function deleteAdminTeamRegistration(teamId: string) {
  return apiRequest<void>(`/admin/teams/${teamId}`, {
    method: "DELETE",
  });
}
