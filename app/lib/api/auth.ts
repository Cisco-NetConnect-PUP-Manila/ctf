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

export function getCurrentAccount() {
  return apiRequest<CurrentAccount>("/auth/me", {
    method: "GET",
    cache: "no-store",
  });
}

export function logout() {
  return apiRequest<void>("/auth/logout", {
    method: "POST",
  });
}

