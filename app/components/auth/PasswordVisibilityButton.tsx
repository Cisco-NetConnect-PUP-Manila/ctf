export default function PasswordVisibilityButton({
  visible,
  onToggle,
}: {
  visible: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      aria-label={visible ? "Hide password" : "Show password"}
      aria-pressed={visible}
      className="auth-password-toggle"
      onClick={onToggle}
      type="button"
    >
      <svg aria-hidden="true" viewBox="0 0 24 24">
        <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" />
        <circle cx="12" cy="12" r="2.75" />
        {visible && <path d="m4 4 16 16" />}
      </svg>
    </button>
  );
}

