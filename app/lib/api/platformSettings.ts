import { apiRequest } from "./client";
import type { PlatformSettings } from "./types";

let platformSettingsRequest: Promise<PlatformSettings> | null = null;

export function getPlatformSettings() {
  if (!platformSettingsRequest) {
    platformSettingsRequest = apiRequest<PlatformSettings>("/platform-settings", {
      method: "GET",
      cache: "no-store",
    }).finally(() => {
      platformSettingsRequest = null;
    });
  }

  return platformSettingsRequest;
}

export function platformIsFrozen(settings: PlatformSettings) {
  return !settings.submissions_open || settings.competition_status === "ended";
}
