import type { ComponentPropsWithoutRef, ReactNode, Ref } from "react";

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

type SectionShellProps = ComponentPropsWithoutRef<"section"> & {
  children: ReactNode;
  pad?: "none" | "compact" | "normal" | "large";
  sectionRef?: Ref<HTMLElement>;
};

const padClasses = {
  none: "",
  compact: "py-20 md:py-28 lg:py-32",
  normal: "py-24 md:py-32 lg:py-40",
  large: "py-28 md:py-40 lg:py-48",
};

export function SectionShell({
  children,
  className,
  pad = "normal",
  sectionRef,
  ...props
}: SectionShellProps) {
  return (
    <section
      {...props}
      ref={sectionRef}
      className={cx(
        "relative isolate container-pad overflow-hidden",
        padClasses[pad],
        className
      )}
    >
      {children}
    </section>
  );
}

type SectionContainerProps = ComponentPropsWithoutRef<"div"> & {
  children: ReactNode;
};

export function SectionContainer({
  children,
  className,
  ...props
}: SectionContainerProps) {
  return (
    <div {...props} className={cx("relative mx-auto max-w-[1600px]", className)}>
      {children}
    </div>
  );
}

type SectionHeaderProps = {
  index: string;
  label: string;
  className?: string;
};

export function SectionHeader({ index, label, className }: SectionHeaderProps) {
  return (
    <div className={cx("mb-4 flex items-center gap-5", className)}>
      <span className="label text-magenta">{index}</span>
      <span className="label text-fg/40">{label}</span>
      <span className="h-px flex-1 bg-fg/10" />
    </div>
  );
}
