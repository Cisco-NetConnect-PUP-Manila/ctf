"use client";

import { useCallback, useEffect, useState } from "react";
import {
  addChallengeFlag,
  createAdminChallenge,
  deactivateChallengeFlag,
  deleteAdminChallenge,
  listAdminActs,
  listAdminChallenges,
  listChallengeCategories,
  listChallengeDifficulties,
  listChallengeFlags,
  setAdminChallengeStatus,
  updateAdminChallenge,
} from "../../lib/api/challenges";
import { ApiError } from "../../lib/api/client";
import type {
  AdminAct,
  AdminChallenge,
  AdminChallengeInput,
  ChallengeFlag,
  ChallengeLookup,
  ChallengeStatus,
} from "../../lib/api/types";

type FormState = {
  act_id: string;
  title: string;
  slug: string;
  mission_brief: string;
  story_context: string;
  objectives: string;
  points: string;
  category_id: string;
  difficulty_id: string;
  story_fragment: string;
  sort_order: string;
  is_visible: boolean;
};

const EMPTY_FORM: FormState = {
  act_id: "",
  title: "",
  slug: "",
  mission_brief: "",
  story_context: "",
  objectives: "",
  points: "100",
  category_id: "",
  difficulty_id: "",
  story_fragment: "",
  sort_order: "0",
  is_visible: true,
};

function slugify(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function errorMessage(caught: unknown, fallback: string) {
  return caught instanceof ApiError ? caught.message : fallback;
}

function toPayload(form: FormState): AdminChallengeInput {
  return {
    act_id: form.act_id,
    title: form.title,
    slug: form.slug,
    mission_brief: form.mission_brief,
    story_context: form.story_context.trim() || null,
    objectives: form.objectives.split("\n").map((item) => item.trim()).filter(Boolean),
    points: Number(form.points),
    category_id: form.category_id || null,
    difficulty_id: form.difficulty_id || null,
    story_fragment: form.story_fragment.trim() || null,
    sort_order: Number(form.sort_order),
    is_visible: form.is_visible,
  };
}

function toForm(item: AdminChallenge): FormState {
  return {
    act_id: item.act_id,
    title: item.title,
    slug: item.slug,
    mission_brief: item.mission_brief,
    story_context: item.story_context ?? "",
    objectives: item.objectives.join("\n"),
    points: String(item.points),
    category_id: item.category?.id ?? "",
    difficulty_id: item.difficulty?.id ?? "",
    story_fragment: item.story_fragment ?? "",
    sort_order: String(item.sort_order),
    is_visible: item.is_visible,
  };
}

export default function AdminChallengeManager() {
  const [acts, setActs] = useState<AdminAct[]>([]);
  const [categories, setCategories] = useState<ChallengeLookup[]>([]);
  const [difficulties, setDifficulties] = useState<ChallengeLookup[]>([]);
  const [items, setItems] = useState<AdminChallenge[]>([]);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [flagsByChallenge, setFlagsByChallenge] = useState<Record<string, ChallengeFlag[]>>({});
  const [openFlagsId, setOpenFlagsId] = useState<string | null>(null);
  const [flagValue, setFlagValue] = useState("");
  const [flagLabel, setFlagLabel] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [nextActs, nextCategories, nextDifficulties, nextItems] = await Promise.all([
        listAdminActs(),
        listChallengeCategories(),
        listChallengeDifficulties(),
        listAdminChallenges(),
      ]);
      setActs(nextActs);
      setCategories(nextCategories.filter((item) => item.is_active));
      setDifficulties(nextDifficulties.filter((item) => item.is_active));
      setItems(nextItems);
      setForm((current) => ({ ...current, act_id: current.act_id || nextActs[0]?.id || "" }));
    } catch (caught) {
      setError(errorMessage(caught, "Unable to load challenge management data."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => void load(), [load]);

  function resetForm() {
    setEditingId(null);
    setForm({ ...EMPTY_FORM, act_id: acts[0]?.id ?? "" });
    setError("");
  }

  function beginEdit(item: AdminChallenge) {
    setEditingId(item.id);
    setForm(toForm(item));
    setError("");
    document.getElementById("challenge-editor")?.scrollIntoView({ behavior: "smooth" });
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const wasEditing = editingId !== null;
      const saved = editingId
        ? await updateAdminChallenge(editingId, toPayload(form))
        : await createAdminChallenge(toPayload(form));
      setItems((current) =>
        editingId
          ? current.map((item) => (item.id === saved.id ? saved : item))
          : [...current, saved].sort((a, b) => a.act_number - b.act_number || a.sort_order - b.sort_order)
      );
      resetForm();
      if (!wasEditing) {
        setOpenFlagsId(saved.id);
        setFlagsByChallenge((current) => ({ ...current, [saved.id]: [] }));
        setFlagValue("");
        setFlagLabel("");
        window.setTimeout(
          () => document.getElementById(`challenge-${saved.id}`)?.scrollIntoView({ behavior: "smooth" }),
          0
        );
      }
    } catch (caught) {
      setError(errorMessage(caught, "Could not save this challenge."));
    } finally {
      setSaving(false);
    }
  }

  async function handleStatus(item: AdminChallenge, status: ChallengeStatus) {
    setBusyId(item.id);
    setError("");
    try {
      const updated = await setAdminChallengeStatus(item.id, status);
      setItems((current) => current.map((candidate) => candidate.id === item.id ? updated : candidate));
    } catch (caught) {
      setError(errorMessage(caught, "Could not update challenge status."));
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(item: AdminChallenge) {
    if (!window.confirm(`Permanently delete "${item.title}"? This cannot be undone.`)) return;
    setBusyId(item.id);
    setError("");
    try {
      await deleteAdminChallenge(item.id);
      setItems((current) => current.filter((candidate) => candidate.id !== item.id));
      if (editingId === item.id) resetForm();
    } catch (caught) {
      setError(errorMessage(caught, "Could not delete this challenge."));
    } finally {
      setBusyId(null);
    }
  }

  async function toggleFlags(item: AdminChallenge) {
    if (openFlagsId === item.id) {
      setOpenFlagsId(null);
      return;
    }
    setOpenFlagsId(item.id);
    setFlagValue("");
    setFlagLabel("");
    try {
      const flags = await listChallengeFlags(item.id);
      setFlagsByChallenge((current) => ({ ...current, [item.id]: flags }));
    } catch (caught) {
      setError(errorMessage(caught, "Could not load flag validators."));
    }
  }

  async function handleAddFlag(item: AdminChallenge) {
    setBusyId(item.id);
    setError("");
    try {
      const created = await addChallengeFlag(item.id, flagValue, flagLabel);
      setFlagsByChallenge((current) => ({
        ...current,
        [item.id]: [...(current[item.id] ?? []), created],
      }));
      setItems((current) => current.map((candidate) =>
        candidate.id === item.id
          ? { ...candidate, active_flag_count: candidate.active_flag_count + 1 }
          : candidate
      ));
      setFlagValue("");
      setFlagLabel("");
    } catch (caught) {
      setError(errorMessage(caught, "Could not add the flag validator."));
    } finally {
      setBusyId(null);
    }
  }

  async function handleDeactivateFlag(item: AdminChallenge, flag: ChallengeFlag) {
    setBusyId(item.id);
    setError("");
    try {
      const updated = await deactivateChallengeFlag(item.id, flag.id);
      setFlagsByChallenge((current) => ({
        ...current,
        [item.id]: (current[item.id] ?? []).map((candidate) => candidate.id === flag.id ? updated : candidate),
      }));
      setItems((current) => current.map((candidate) =>
        candidate.id === item.id
          ? { ...candidate, active_flag_count: Math.max(0, candidate.active_flag_count - 1) }
          : candidate
      ));
    } catch (caught) {
      setError(errorMessage(caught, "Could not deactivate the flag validator."));
    } finally {
      setBusyId(null);
    }
  }

  if (loading) return <p className="challenge-admin__note">Loading organizer challenge data…</p>;

  return (
    <div className="challenge-admin">
      {error && <div className="challenge-admin__error" role="alert">{error}</div>}

      <form className="challenge-editor" id="challenge-editor" onSubmit={handleSubmit}>
        <header>
          <div>
            <span className="eyebrow">CHALLENGE.EDITOR</span>
            <h3>{editingId ? "Edit challenge" : "Create challenge"}</h3>
          </div>
          {editingId && <button className="btn" type="button" onClick={resetForm}>Cancel edit</button>}
        </header>

        {acts.length === 0 && (
          <div className="challenge-admin__error" role="alert">
            No Acts are configured. Run the backend reference-data seed before creating challenges.
          </div>
        )}

        <div className="challenge-editor__grid">
          <label>Act<select required value={form.act_id} onChange={(e) => setForm({ ...form, act_id: e.target.value })}>
            <option value="">Select Act</option>
            {acts.map((act) => <option value={act.id} key={act.id}>Act {act.act_number}: {act.title}</option>)}
          </select></label>
          <label>Title<input required maxLength={200} value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value, slug: editingId ? form.slug : slugify(e.target.value) })} /></label>
          <label>Slug<input required maxLength={160} value={form.slug} onChange={(e) => setForm({ ...form, slug: slugify(e.target.value) })} /></label>
          <label>Points<input required min="0" type="number" value={form.points} onChange={(e) => setForm({ ...form, points: e.target.value })} /></label>
          <label>Category<select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
            <option value="">Uncategorized</option>{categories.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}
          </select></label>
          <label>Difficulty<select value={form.difficulty_id} onChange={(e) => setForm({ ...form, difficulty_id: e.target.value })}>
            <option value="">Unrated</option>{difficulties.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}
          </select></label>
          <label>Sort order<input type="number" value={form.sort_order} onChange={(e) => setForm({ ...form, sort_order: e.target.value })} /></label>
          <label>Story fragment<input maxLength={64} value={form.story_fragment} onChange={(e) => setForm({ ...form, story_fragment: e.target.value })} /></label>
          <label className="challenge-editor__wide">Mission brief<textarea required rows={3} value={form.mission_brief} onChange={(e) => setForm({ ...form, mission_brief: e.target.value })} /></label>
          <label className="challenge-editor__wide">Story context<textarea rows={3} value={form.story_context} onChange={(e) => setForm({ ...form, story_context: e.target.value })} /></label>
          <label className="challenge-editor__wide">Objectives <small>one per line</small><textarea rows={4} value={form.objectives} onChange={(e) => setForm({ ...form, objectives: e.target.value })} /></label>
          <label className="challenge-editor__check"><input type="checkbox" checked={form.is_visible} onChange={(e) => setForm({ ...form, is_visible: e.target.checked })} /> Visible to participants when published</label>
        </div>
        <button className="btn btn--primary" disabled={saving || acts.length === 0} type="submit">
          {saving ? "Saving…" : editingId ? "Save changes" : "Create draft"}
        </button>
      </form>

      <div className="challenge-admin__list">
        <header><span className="eyebrow">CHALLENGE.MANIFEST</span><b>{items.length} total</b></header>
        {items.length === 0 && <p className="challenge-admin__note">No challenges yet. Create the first draft above.</p>}
        {items.map((item) => (
          <article className="challenge-admin-row" id={`challenge-${item.id}`} key={item.id}>
            <div className="challenge-admin-row__head">
              <div><span className={`announce-status announce-status--${item.status}`}>{item.status}</span><h4>{item.title}</h4></div>
              <b>{item.points} pts</b>
            </div>
            <p>Act {item.act_number} · {item.category?.name ?? "Uncategorized"} · {item.difficulty?.name ?? "Unrated"}</p>
            <small>{item.slug} · {item.is_visible ? "visible" : "hidden"} · {item.active_flag_count} active flag{item.active_flag_count === 1 ? "" : "s"}</small>
            <div className="challenge-admin-row__actions">
              <button className="btn" type="button" disabled={busyId === item.id} onClick={() => beginEdit(item)}>Edit</button>
              <button className="btn" type="button" disabled={busyId === item.id} onClick={() => void toggleFlags(item)}>Flags</button>
              {item.status !== "published" && <button className="btn btn--primary" type="button" disabled={busyId === item.id} onClick={() => void handleStatus(item, "published")}>Publish</button>}
              {item.status === "published" && <button className="btn" type="button" disabled={busyId === item.id} onClick={() => void handleStatus(item, "draft")}>Unpublish</button>}
              {item.status !== "archived" && <button className="btn" type="button" disabled={busyId === item.id} onClick={() => void handleStatus(item, "archived")}>Archive</button>}
              <button className="btn challenge-admin-row__delete" type="button" disabled={busyId === item.id} onClick={() => void handleDelete(item)}>Delete</button>
            </div>

            {openFlagsId === item.id && (
              <div className="challenge-flags">
                <h5>Flag validators</h5>
                <p>Add at least one active flag here before publishing this draft.</p>
                {(flagsByChallenge[item.id] ?? []).map((flag) => (
                  <div className="challenge-flag" key={flag.id}>
                    <span>{flag.label || "Exact-match flag"} · {flag.is_active ? "active" : "inactive"}</span>
                    {flag.is_active && <button className="btn" type="button" disabled={busyId === item.id} onClick={() => void handleDeactivateFlag(item, flag)}>Deactivate</button>}
                  </div>
                ))}
                <div className="challenge-flag__new">
                  <input aria-label="Flag value" placeholder="FLAG{example}" type="password" value={flagValue} onChange={(e) => setFlagValue(e.target.value)} />
                  <input aria-label="Flag label" placeholder="Label (optional)" value={flagLabel} onChange={(e) => setFlagLabel(e.target.value)} />
                  <button className="btn btn--primary" type="button" disabled={!flagValue || busyId === item.id} onClick={() => void handleAddFlag(item)}>Add validator</button>
                </div>
                <small>Flag values are hashed by the backend and are never returned to this interface.</small>
              </div>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}
