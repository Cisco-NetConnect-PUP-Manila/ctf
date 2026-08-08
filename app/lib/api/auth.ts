import { apiRequest } from "./client";
import type { CurrentAccount, LoginInput, RegisterInput } from "./types";

export function registerTeam(payload: RegisterInput) {
  return apiRequest<CurrentAccount>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function login(payload: LoginInput) {
  return apiRequest<CurrentAccount>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

