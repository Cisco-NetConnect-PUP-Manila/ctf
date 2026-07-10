"use client";

import { motion, type HTMLMotionProps } from "framer-motion";
import type { ReactNode } from "react";

type CtaSize = "sm" | "md" | "lg";
type CtaVariant = "primary" | "neutral";

const sizeClasses: Record<CtaSize, string> = {
  sm: "cta-button--sm",
  md: "cta-button--md",
  lg: "cta-button--lg",
};

const variantClasses: Record<CtaVariant, string> = {
  primary: "cta-button--primary",
  neutral: "cta-button--neutral",
};

function classes(size: CtaSize, variant: CtaVariant, className = "") {
  return [
    "cta-button corner-cut items-center justify-center whitespace-nowrap",
    sizeClasses[size],
    variantClasses[variant],
    className,
  ]
    .filter(Boolean)
    .join(" ");
}

type CtaLinkProps = Omit<HTMLMotionProps<"a">, "children"> & {
  size?: CtaSize;
  variant?: CtaVariant;
  children: ReactNode;
};

type CtaButtonProps = Omit<HTMLMotionProps<"button">, "children"> & {
  size?: CtaSize;
  variant?: CtaVariant;
  children: ReactNode;
};

export function CtaLink({
  size = "md",
  variant = "primary",
  className,
  children,
  ...props
}: CtaLinkProps) {
  return (
    <motion.a {...props} className={classes(size, variant, className)}>
      <span className="cta-button__label">{children}</span>
    </motion.a>
  );
}

export function CtaButton({
  size = "md",
  variant = "primary",
  className,
  children,
  ...props
}: CtaButtonProps) {
  return (
    <motion.button {...props} className={classes(size, variant, className)}>
      <span className="cta-button__label">{children}</span>
    </motion.button>
  );
}
