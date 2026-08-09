import { apiRequest } from "./client";
import type {
  AdminAct,
  AdminChallenge,
  AdminChallengeInput,
  ChallengeFlag,
  ChallengeLookup,
  ChallengeStatus,
  ParticipantChallenge,
  ParticipantChallengeList,
} from "./types";

export function listParticipantChallenges() {
  return apiRequest<ParticipantChallengeList>("/challenges", {
    method: "GET",
    cache: "no-store",
  });
}

export function getParticipantChallenge(id: string) {
  return apiRequest<ParticipantChallenge>(`/challenges/${id}`, {
    method: "GET",
    cache: "no-store",
  });
}

export function listAdminActs() {
  return apiRequest<AdminAct[]>("/admin/acts", { method: "GET", cache: "no-store" });
}

export function listChallengeCategories() {
  return apiRequest<ChallengeLookup[]>("/admin/challenge-categories", {
    method: "GET",
    cache: "no-store",
  });
}

export function listChallengeDifficulties() {
  return apiRequest<ChallengeLookup[]>("/admin/challenge-difficulties", {
    method: "GET",
    cache: "no-store",
  });
}

export function listAdminChallenges() {
  return apiRequest<AdminChallenge[]>("/admin/challenges", {
    method: "GET",
    cache: "no-store",
  });
}

export function createAdminChallenge(payload: AdminChallengeInput) {
  return apiRequest<AdminChallenge>("/admin/challenges", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAdminChallenge(id: string, payload: AdminChallengeInput) {
  return apiRequest<AdminChallenge>(`/admin/challenges/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function setAdminChallengeStatus(id: string, status: ChallengeStatus) {
  return apiRequest<AdminChallenge>(`/admin/challenges/${id}/publish`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function deleteAdminChallenge(id: string) {
  return apiRequest<void>(`/admin/challenges/${id}`, { method: "DELETE" });
}

export function listChallengeFlags(challengeId: string) {
  return apiRequest<ChallengeFlag[]>(`/admin/challenges/${challengeId}/flags`, {
    method: "GET",
    cache: "no-store",
  });
}

export function addChallengeFlag(challengeId: string, value: string, label: string) {
  return apiRequest<ChallengeFlag>(`/admin/challenges/${challengeId}/flags`, {
    method: "POST",
    body: JSON.stringify({ value, label: label.trim() || null }),
  });
}

export function deactivateChallengeFlag(challengeId: string, flagId: string) {
  return apiRequest<ChallengeFlag>(
    `/admin/challenges/${challengeId}/flags/${flagId}`,
    { method: "DELETE" }
  );
}
