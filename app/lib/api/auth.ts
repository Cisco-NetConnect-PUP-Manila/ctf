import { apiRequest } from "./client";
import type { CurrentAccount, LoginInput, RegisterInput } from "./types";

let currentAccountRequest: Promise<CurrentAccount> | null = null;

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
  if (!currentAccountRequest) {
    currentAccountRequest = apiRequest<CurrentAccount>("/auth/me", {
      method: "GET",
      cache: "no-store",
    }).finally(() => {
      currentAccountRequest = null;
    });
  }

  return currentAccountRequest;
}

export function logout() {
  return apiRequest<void>("/auth/logout", {
    method: "POST",
  });
}

