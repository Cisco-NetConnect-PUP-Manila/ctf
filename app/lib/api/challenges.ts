import { apiRequest } from "./client";
import type {
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
