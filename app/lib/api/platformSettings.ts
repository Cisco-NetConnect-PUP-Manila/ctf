import { apiRequest } from "./client";
import type { PlatformSettings } from "./types";

export function getPlatformSettings() {
  return apiRequest<PlatformSettings>("/platform-settings", {
    method: "GET",
    cache: "no-store",
  });
}

export function platformIsFrozen(settings: PlatformSettings) {
  return !settings.submissions_open || settings.competition_status === "ended";
}
