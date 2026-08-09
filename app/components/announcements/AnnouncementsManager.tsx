"use client";

import { useCallback, useEffect, useState } from "react";
import {
  createAnnouncement,
  deleteAnnouncement,
  listAllAnnouncements,
  setAnnouncementStatus,
  updateAnnouncement,
} from "../../lib/api/announcements";
import { ApiError } from "../../lib/api/client";
import type {
  AdminAnnouncement,
  AnnouncementStatus,
  FieldErrors,
} from "../../lib/api/types";

const STATUS_ACTIONS: { status: AnnouncementStatus; label: string }[] = [
  { status: "published", label: "Publish" },
  { status: "archived", label: "Archive" },
  { status: "draft", label: "Unpublish" },
];

function formatDate(value: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "—"
    : date.toLocaleString(undefined, {
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
}

export default function AnnouncementsManager() {
  const [items, setItems] = useState<AdminAnnouncement[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  // Create form state.
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [creating, setCreating] = useState(false);
  const [createErrors, setCreateErrors] = useState<FieldErrors>({});
  const [createError, setCreateError] = useState("");

  // Per-row busy + edit state.
  const [busyId, setBusyId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editBody, setEditBody] = useState("");
  const [rowError, setRowError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError("");
    try {
      setItems(await listAllAnnouncements());
    } catch (caught) {
      setLoadError(
        caught instanceof ApiError ? caught.message : "Unable to load announcements."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    setCreating(true);
    setCreateError("");
    setCreateErrors({});
    try {
      const created = await createAnnouncement({ title, body });
      setItems((prev) => [created, ...prev]);
      setTitle("");
      setBody("");
    } catch (caught) {
      if (caught instanceof ApiError) {
        setCreateError(caught.message);
        setCreateErrors(caught.fieldErrors);
      } else {
        setCreateError("Could not create the announcement.");
      }
    } finally {
      setCreating(false);
    }
  }

  function beginEdit(item: AdminAnnouncement) {
    setEditingId(item.id);
    setEditTitle(item.title);
    setEditBody(item.body);
    setRowError("");
  }

  async function handleSaveEdit(id: string) {
    setBusyId(id);
    setRowError("");
    try {
      const updated = await updateAnnouncement(id, { title: editTitle, body: editBody });
      setItems((prev) => prev.map((it) => (it.id === id ? updated : it)));
      setEditingId(null);
    } catch (caught) {
      setRowError(caught instanceof ApiError ? caught.message : "Could not save changes.");
    } finally {
      setBusyId(null);
    }
  }

  async function handleStatus(id: string, status: AnnouncementStatus) {
    setBusyId(id);
    setRowError("");
    try {
      const updated = await setAnnouncementStatus(id, status);
      setItems((prev) => prev.map((it) => (it.id === id ? updated : it)));
    } catch (caught) {
      setRowError(caught instanceof ApiError ? caught.message : "Could not update status.");
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(item: AdminAnnouncement) {
    const confirmed = window.confirm(
      `Permanently delete "${item.title}"? This cannot be undone.`
    );
    if (!confirmed) return;

    setBusyId(item.id);
    setRowError("");
    try {
      await deleteAnnouncement(item.id);
      setItems((prev) => prev.filter((candidate) => candidate.id !== item.id));
      if (editingId === item.id) setEditingId(null);
    } catch (caught) {
      setRowError(
        caught instanceof ApiError ? caught.message : "Could not delete the announcement."
      );
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="announce-admin">
      <form className="announce-admin__form" onSubmit={handleCreate}>
        <div className="announce-field">
          <label htmlFor="announce-title">Title</label>
          <input
            id="announce-title"
            value={title}
            maxLength={200}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Act I is live"
            required
          />
          {createErrors.title && (
            <small className="announce-field__error">{createErrors.title}</small>
          )}
        </div>
        <div className="announce-field">
          <label htmlFor="announce-body">Body</label>
          <textarea
            id="announce-body"
            value={body}
            rows={3}
            onChange={(e) => setBody(e.target.value)}
            placeholder="The Signal has begun. Trace the first anomaly."
            required
          />
          {createErrors.body && (
            <small className="announce-field__error">{createErrors.body}</small>
          )}
        </div>
        {createError && (
          <small className="announce-field__error" role="alert">
            {createError}
          </small>
        )}
        <button className="btn btn--primary" type="submit" disabled={creating}>
          {creating ? "Saving draft…" : "Create draft"}
        </button>
      </form>

      <div className="announce-admin__list" aria-busy={loading}>
        {loading && <p className="announce-feed__note">Loading announcements…</p>}

        {!loading && loadError && (
          <div className="announce-feed__error" role="alert">
            <span>{loadError}</span>
            <button className="btn" type="button" onClick={() => void load()}>
              Retry
            </button>
          </div>
        )}

        {!loading && !loadError && items.length === 0 && (
          <p className="announce-feed__note">No announcements yet. Create the first draft above.</p>
        )}

        {rowError && (
          <small className="announce-field__error" role="alert">
            {rowError}
          </small>
        )}

        {!loading &&
          !loadError &&
          items.map((item) => (
            <article className="announce-row" key={item.id}>
              <div className="announce-row__head">
                <span className={`announce-status announce-status--${item.status}`}>
                  {item.status}
                </span>
                <span className="announce-row__meta">
                  {item.status === "published"
                    ? `published ${formatDate(item.published_at)}`
                    : `updated ${formatDate(item.updated_at)}`}
                </span>
              </div>

              {editingId === item.id ? (
                <div className="announce-row__edit">
                  <input
                    aria-label="Edit title"
                    value={editTitle}
                    maxLength={200}
                    onChange={(e) => setEditTitle(e.target.value)}
                  />
                  <textarea
                    aria-label="Edit body"
                    value={editBody}
                    rows={3}
                    onChange={(e) => setEditBody(e.target.value)}
                  />
                  <div className="announce-row__actions">
                    <button
                      className="btn btn--primary"
                      type="button"
                      disabled={busyId === item.id}
                      onClick={() => void handleSaveEdit(item.id)}
                    >
                      Save
                    </button>
                    <button
                      className="btn"
                      type="button"
                      disabled={busyId === item.id}
                      onClick={() => setEditingId(null)}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <h4 className="announce-row__title">{item.title}</h4>
                  <p className="announce-row__body">{item.body}</p>
                  <div className="announce-row__actions">
                    <button
                      className="btn"
                      type="button"
                      disabled={busyId === item.id}
                      onClick={() => beginEdit(item)}
                    >
                      Edit
                    </button>
                    {STATUS_ACTIONS.filter((action) => action.status !== item.status).map(
                      (action) => (
                        <button
                          className="btn"
                          key={action.status}
                          type="button"
                          disabled={busyId === item.id}
                          onClick={() => void handleStatus(item.id, action.status)}
                        >
                          {action.label}
                        </button>
                      )
                    )}
                    <button
                      className="btn announce-row__delete"
                      type="button"
                      disabled={busyId === item.id}
                      onClick={() => void handleDelete(item)}
                    >
                      {busyId === item.id ? "Workingâ€¦" : "Delete"}
                    </button>
                  </div>
                </>
              )}
            </article>
          ))}
      </div>
    </div>
  );
}
