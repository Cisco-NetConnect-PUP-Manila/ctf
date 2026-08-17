import { apiRequest } from "./client";
import type { PlatformSettings, PlatformSettingsUpdate } from "./types";

export function getAdminPlatformSettings() {
  return apiRequest<PlatformSettings>("/admin/platform-settings", {
    method: "GET",
    cache: "no-store",
  });
}

export function updateAdminPlatformSettings(payload: PlatformSettingsUpdate) {
  return apiRequest<PlatformSettings>("/admin/platform-settings", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
