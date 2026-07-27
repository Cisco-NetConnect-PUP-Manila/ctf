"use client";

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
      { label: "Storyline", href: "/platform#storyline" },
      { label: "Modules", href: "/platform#modules" },
      { label: "Challenges", href: "/platform#challenges" },
      { label: "Status", href: "/platform#portal-status" },
    ],
  },
  admin: {
    brandHref: "/admin#admin-top",
    links: [
      { label: "Overview", href: "/admin#overview" },
      { label: "Modules", href: "/admin#modules" },
      { label: "Authority", href: "/admin#authority" },
      { label: "Status", href: "/admin#admin-status" },
    ],
  },
};

export default function Nav() {
  const pathname = usePathname();
  const mode =
    pathname === "/platform" ? "platform" : pathname === "/admin" ? "admin" : "public";
  const nav = NAVS[mode];

  return (
    <nav className={`nav nav--${mode}`}>
      <div className="nav__inner">
        <a href={nav.brandHref} className="nav__logo">
          PACKET<b>_</b>CAPTURE<span className="nav__blink">_</span>
        </a>
        <div className="nav__links">
          {nav.links.map((link) => (
            <a href={link.href} key={link.href}>
              {link.label}
            </a>
          ))}
        </div>
      </div>
    </nav>
  );
}
