"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { listAllPublishedAnnouncements } from "../../lib/api/announcements";
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
  const [newCount, setNewCount] = useState(0);
  const knownIds = useRef<Set<string>>(new Set());
  const initialized = useRef(false);

  const load = useCallback(async (background = false) => {
    if (!background) {
      setLoading(true);
      setError("");
    }
    try {
      const announcements = await listAllPublishedAnnouncements();
      if (initialized.current) {
        const unseen = announcements.filter((item) => !knownIds.current.has(item.id));
        if (unseen.length > 0) setNewCount((current) => current + unseen.length);
      }
      knownIds.current = new Set(announcements.map((item) => item.id));
      initialized.current = true;
      setItems(announcements);
      setError("");
    } catch (caught) {
      if (!background) {
        setError(
          caught instanceof ApiError
            ? caught.message
            : "Unable to load announcements right now."
        );
      }
    } finally {
      if (!background) setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
    const interval = window.setInterval(() => {
      if (document.visibilityState === "visible") void load(true);
    }, 10000);
    return () => window.clearInterval(interval);
  }, [load]);

  return (
    <Window title="announcements.log" meta="live published event updates">
      <div className="announce-feed" aria-live="polite" aria-busy={loading}>
        {loading && <p className="announce-feed__note">Loading transmissions…</p>}

        {newCount > 0 && (
          <div className="announce-live-alert" role="status">
            <div>
              <span className="eyebrow">NEW.TRANSMISSION</span>
              <b>
                {newCount} new announcement{newCount === 1 ? "" : "s"} received
              </b>
            </div>
            <button className="btn" type="button" onClick={() => setNewCount(0)}>
              Acknowledge
            </button>
          </div>
        )}

        {!loading && error && (
          <div className="announce-feed__error" role="alert">
            <span>{error}</span>
            <button className="btn" type="button" onClick={() => void load(false)}>
              Retry
            </button>
          </div>
        )}

        {!loading && !error && items.length === 0 && (
          <p className="announce-feed__note">
            No announcements have been published yet. New transmissions will appear automatically.
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
