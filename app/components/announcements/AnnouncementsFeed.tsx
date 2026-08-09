"use client";

import { useCallback, useEffect, useState } from "react";
import { listPublishedAnnouncements } from "../../lib/api/announcements";
import { ApiError } from "../../lib/api/client";
import type { Announcement } from "../../lib/api/types";
import Window from "../Window";

function formatPublished(value: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function AnnouncementsFeed() {
  const [items, setItems] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const page = await listPublishedAnnouncements();
      setItems(page.items);
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Unable to load announcements right now."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <Window title="announcements.log" meta="published event updates">
      <div className="announce-feed" aria-live="polite" aria-busy={loading}>
        {loading && <p className="announce-feed__note">Loading transmissions…</p>}

        {!loading && error && (
          <div className="announce-feed__error" role="alert">
            <span>{error}</span>
            <button className="btn" type="button" onClick={() => void load()}>
              Retry
            </button>
          </div>
        )}

        {!loading && !error && items.length === 0 && (
          <p className="announce-feed__note">
            No announcements have been published yet. Check back for event updates.
          </p>
        )}

        {!loading && !error && items.length > 0 && (
          <ul className="announce-list">
            {items.map((item) => (
              <li className="announce-item" key={item.id}>
                <div className="announce-item__head">
                  <h4>{item.title}</h4>
                  <time dateTime={item.published_at ?? undefined}>
                    {formatPublished(item.published_at)}
                  </time>
                </div>
                <p className="announce-item__body">{item.body}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Window>
  );
}
