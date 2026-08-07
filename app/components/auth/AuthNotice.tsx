export default function AuthNotice({
  tone,
  children,
}: {
  tone: "error" | "success" | "info";
  children: React.ReactNode;
}) {
  return (
    <div className={`auth-notice auth-notice--${tone}`} role={tone === "error" ? "alert" : "status"}>
      <span aria-hidden="true">{tone === "error" ? "!" : ">"}</span>
      <p>{children}</p>
    </div>
  );
}

