import { apiRequest } from "./client";
import type {
  AdminAnnouncement,
  Announcement,
  AnnouncementInput,
  AnnouncementStatus,
  Page,
} from "./types";

// ---- Participant ----------------------------------------------------------

export function listPublishedAnnouncements(page = 1, pageSize = 20) {
  const query = `?page=${page}&page_size=${pageSize}`;
  return apiRequest<Page<Announcement>>(`/announcements${query}`, {
    method: "GET",
    cache: "no-store",
  });
}

export async function listAllPublishedAnnouncements() {
  const items: Announcement[] = [];
  let pageNumber = 1;

  while (true) {
    const page = await listPublishedAnnouncements(pageNumber, 100);
    items.push(...page.items);
    if (!page.has_more) return items;
    pageNumber += 1;
  }
}

// ---- Admin ----------------------------------------------------------------

export function listAllAnnouncements() {
  return apiRequest<AdminAnnouncement[]>("/admin/announcements", {
    method: "GET",
    cache: "no-store",
  });
}

export function createAnnouncement(payload: AnnouncementInput) {
  return apiRequest<AdminAnnouncement>("/admin/announcements", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAnnouncement(id: string, payload: AnnouncementInput) {
  return apiRequest<AdminAnnouncement>(`/admin/announcements/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function setAnnouncementStatus(id: string, status: AnnouncementStatus) {
  return apiRequest<AdminAnnouncement>(`/admin/announcements/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function deleteAnnouncement(id: string) {
  return apiRequest<void>(`/admin/announcements/${id}`, {
    method: "DELETE",
  });
}
