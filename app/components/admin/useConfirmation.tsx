"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";

type ConfirmationRequest = { message: string; resolve: (approved: boolean) => void };

/** Native modal dialog traps focus; cancel is initially focused and Escape cancels. */
export default function useConfirmation() {
  const [request, setRequest] = useState<ConfirmationRequest | null>(null);
  const pending = useRef<ConfirmationRequest | null>(null);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);
  const titleId = useId();
  const bodyId = useId();

  const confirm = useCallback((message: string) => new Promise<boolean>((resolve) => {
    if (pending.current) { resolve(false); return; }
    const next = { message, resolve };
    pending.current = next;
    setRequest(next);
  }), []);

  const finish = useCallback((approved: boolean) => {
    const current = pending.current;
    pending.current = null;
    dialogRef.current?.close();
    setRequest(null);
    current?.resolve(approved);
  }, []);

  useEffect(() => {
    if (!request) return;
    const previous = document.activeElement as HTMLElement | null;
    dialogRef.current?.showModal();
    cancelRef.current?.focus();
    return () => previous?.focus();
  }, [request]);

  useEffect(() => () => {
    pending.current?.resolve(false);
    pending.current = null;
  }, []);

  const confirmationDialog = request && (
    <dialog ref={dialogRef} className="admin-confirm" aria-labelledby={titleId} aria-describedby={bodyId} onCancel={(event) => { event.preventDefault(); finish(false); }}>
      <h3 id={titleId}>Confirm organizer action</h3>
      <p id={bodyId}>{request.message}</p>
      <div className="admin-confirm__actions">
        <button ref={cancelRef} className="btn" type="button" onClick={() => finish(false)}>Cancel</button>
        <button className="btn btn--primary" type="button" onClick={() => finish(true)}>Confirm action</button>
      </div>
    </dialog>
  );
  return { confirm, confirmationDialog };
}
