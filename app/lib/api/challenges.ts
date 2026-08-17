import { apiRequest, backendApiUrl } from "./client";
import type {
  AdminAct,
  AdminChallenge,
  AdminChallengeInput,
  AdminHint,
  ChallengeFile,
  ChallengeFlag,
  ChallengeLookup,
  ChallengeStatus,
  FlagSubmissionResult,
  HintInput,
  IntelRequestResult,
  ParticipantChallenge,
  ParticipantChallengeList,
  ParticipantHint,
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

export function listAdminChallengeHints(challengeId: string) {
  return apiRequest<AdminHint[]>(`/admin/challenges/${challengeId}/hints`, {
    method: "GET",
    cache: "no-store",
  });
}

export function createAdminChallengeHint(challengeId: string, payload: HintInput) {
  return apiRequest<AdminHint>(`/admin/challenges/${challengeId}/hints`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAdminChallengeHint(
  challengeId: string,
  hintId: string,
  payload: Partial<HintInput> & { is_active?: boolean }
) {
  return apiRequest<AdminHint>(`/admin/challenges/${challengeId}/hints/${hintId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function listAdminChallengeFiles(challengeId: string) {
  return apiRequest<ChallengeFile[]>(`/admin/challenges/${challengeId}/files`, {
    method: "GET",
    cache: "no-store",
  });
}

export function uploadAdminChallengeFile(
  challengeId: string,
  file: File,
  displayName: string
) {
  const body = new FormData();
  body.append("upload", file);
  if (displayName.trim()) body.append("display_name", displayName.trim());

  return apiRequest<ChallengeFile>(`/admin/challenges/${challengeId}/files`, {
    method: "POST",
    body,
  });
}

export function deactivateAdminChallengeFile(challengeId: string, fileId: string) {
  return apiRequest<ChallengeFile>(
    `/admin/challenges/${challengeId}/files/${fileId}`,
    { method: "DELETE" }
  );
}

export function listParticipantChallengeFiles(challengeId: string) {
  return apiRequest<ChallengeFile[]>(`/challenges/${challengeId}/files`, {
    method: "GET",
    cache: "no-store",
  });
}

export function participantChallengeFileDownloadUrl(challengeId: string, fileId: string) {
  return backendApiUrl(`/challenges/${challengeId}/files/${fileId}/download`);
}

export function submitChallengeFlag(challengeId: string, flag: string) {
  return apiRequest<FlagSubmissionResult>(`/challenges/${challengeId}/submissions`, {
    method: "POST",
    body: JSON.stringify({ flag }),
  });
}

export function reactivateAdminChallengeFile(challengeId: string, fileId: string) {
  return apiRequest<ChallengeFile>(
    `/admin/challenges/${challengeId}/files/${fileId}/reactivate`,
    { method: "PATCH" }
  );
}

export function listParticipantChallengeHints(challengeId: string) {
  return apiRequest<ParticipantHint[]>(`/challenges/${challengeId}/hints`, {
    method: "GET",
    cache: "no-store",
  });
}

export function requestChallengeIntel(challengeId: string, hintId: string) {
  return apiRequest<IntelRequestResult>(`/challenges/${challengeId}/intel-requests`, {
    method: "POST",
    body: JSON.stringify({ hint_id: hintId }),
  });
}
