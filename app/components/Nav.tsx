"use client";

import { useEffect, useId, useState } from "react";
import { usePathname } from "next/navigation";

const NAVS = {
  public: {
    brandHref: "/#top",
    links: [
      { label: "About", href: "/#about" },
      { label: "Overview", href: "/#overview" },
      { label: "Acts", href: "/#acts" },
      { label: "Rules", href: "/#rules" },
      { label: "FAQ", href: "/#faq" },
      { label: "Timeline", href: "/#timeline" },
      { label: "Sponsors", href: "/#sponsors" },
    ],
  },
  platform: {
    brandHref: "/platform#platform-top",
    links: [
      { label: "Dashboard", href: "/platform#dashboard" },
      { label: "Announcements", href: "/platform#announcements-feed" },
      { label: "Challenges", href: "/platform#challenges" },
    ],
  },
  admin: {
    brandHref: "/admin#admin-top",
    links: [
      { label: "Overview", href: "/admin#overview" },
      { label: "Challenges", href: "/admin#challenges" },
      { label: "Teams", href: "/admin#teams" },
      { label: "Announcements", href: "/admin#announcements" },
      { label: "Submissions", href: "/admin#submissions" },
    ],
  },
};

export default function Nav() {
  const pathname = usePathname();
  const mode =
    pathname === "/platform" ? "platform" : pathname === "/admin" ? "admin" : "public";
  const nav = NAVS[mode];

  const menuId = useId();
  const [open, setOpen] = useState(false);

  // Close the mobile menu whenever the route changes.
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  // Close on Escape for keyboard users.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <nav className={`nav nav--${mode} ${open ? "nav--open" : ""}`}>
      <div className="nav__inner">
        <a href={nav.brandHref} className="nav__logo" onClick={() => setOpen(false)}>
          PACKET<b>_</b>CAPTURE<span className="nav__blink">_</span>
        </a>

        <div className="nav__links" id={menuId}>
          {nav.links.map((link) => (
            <a href={link.href} key={link.href} onClick={() => setOpen(false)}>
              {link.label}
            </a>
          ))}
        </div>

        <button
          type="button"
          className="nav__toggle"
          aria-label={open ? "Close navigation menu" : "Open navigation menu"}
          aria-expanded={open}
          aria-controls={menuId}
          onClick={() => setOpen((v) => !v)}
        >
          <span className="nav__toggle-bars" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
          <span className="nav__toggle-label">{open ? "CLOSE" : "MENU"}</span>
        </button>
      </div>
    </nav>
  );
}
