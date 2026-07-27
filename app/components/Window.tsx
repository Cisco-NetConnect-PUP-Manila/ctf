import type { ReactNode } from "react";

export default function Window({
  title,
  meta,
  icon = "▣",
  tone = "green",
  children,
  className = "",
}: {
  title: string;
  meta?: string;
  icon?: string;
  tone?: "green" | "alert";
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={`win win--${tone} ${className}`.trim()}>
      <div className="win__bar">
        <span className="win__icon">{icon}</span>
        <span className="win__title">{title}</span>
        <span className="win__ctrls" aria-hidden="true">
          <span className="win__ctrl">_</span>
          <span className="win__ctrl">□</span>
          <span className="win__ctrl">×</span>
        </span>
      </div>
      <div className="win__body">{children}</div>
      {meta && <div className="win__status">{meta}</div>}
    </div>
  );
}
