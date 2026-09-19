import type { ReactNode } from "react";

export default function Reveal({
  children,
  as: Tag = "div",
  className = "",
}: {
  children: ReactNode;
  as?: keyof React.JSX.IntrinsicElements;
  className?: string;
  delay?: number;
}) {
  const Component = Tag as React.ElementType;
  return (
    <Component className={className}>{children}</Component>
  );
}
