"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { getCurrentAccount } from "../lib/api/auth";

const PUBLIC_MENU = [
  { label: "Incident Brief", href: "/#about" },
  { label: "Competition Overview", href: "/#overview" },
  { label: "The Four Acts", href: "/#acts" },
  { label: "Rules of Engagement", href: "/#rules" },
  { label: "FAQ", href: "/#faq" },
  { label: "Operation Timeline", href: "/#timeline" },
  { label: "Sponsors", href: "/#sponsors" },
];

const PLATFORM_MENU = [
  { label: "Dashboard", href: "/platform#dashboard" },
  { label: "Announcements", href: "/platform#announcements-feed" },
  { label: "Challenge Workspace", href: "/platform#challenges" },
];

const ADMIN_MENU = [
  { label: "Admin Overview", href: "/admin#overview" },
  { label: "Challenge Console", href: "/admin#challenges" },
  { label: "Team Approval", href: "/admin#teams" },
  { label: "Announcements", href: "/admin#announcements" },
  { label: "Submission Monitor", href: "/admin#submissions" },
];

const ZONES = [
  { tz: "Asia/Manila", label: "MNL" },
  { tz: "Australia/Sydney", label: "SYD" },
];

function fmtTime(tz: string, d: Date) {
  try {
    return new Intl.DateTimeFormat("en-US", {
      timeZone: tz,
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    }).format(d);
  } catch {
    return "--:--";
  }
}

function fmtDate(tz: string, d: Date) {
  try {
    return new Intl.DateTimeFormat("en-US", {
      timeZone: tz,
      month: "short",
      day: "2-digit",
    })
      .format(d)
      .toUpperCase();
  } catch {
    return "--- --";
  }
}

export default function Taskbar() {
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);
  const [now, setNow] = useState<Date | null>(null);
  const [selected, setSelected] = useState(0);
  const [gli, setGli] = useState(false);
  const [open, setOpen] = useState(false);
  const [tzOpen, setTzOpen] = useState(false);
  const [accountRole, setAccountRole] = useState<string | null>(null);
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let active = true;
    getCurrentAccount()
      .then((current) => {
        if (active) setAccountRole(current.account.role);
      })
      .catch(() => {
        if (active) setAccountRole(null);
      });
    return () => {
      active = false;
    };
  }, [pathname]);

  useEffect(() => {
    setMounted(true);
    setNow(new Date());
    try {
      const s = localStorage.getItem("pc_tz");
      if (s === "0" || s === "1") setSelected(Number(s));
    } catch {}
    const id = setInterval(() => setNow(new Date()), 10000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const screen = document.getElementById("screen");
    if (!screen) return;
    let idle: ReturnType<typeof setTimeout>;
    const onScroll = () => {
      setGli(true);
      clearTimeout(idle);
      idle = setTimeout(() => setGli(false), 480);
    };
    screen.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      screen.removeEventListener("scroll", onScroll);
      clearTimeout(idle);
    };
  }, []);

  const chooseZone = (n: number) => {
    setSelected(n);
    try {
      localStorage.setItem("pc_tz", String(n));
    } catch {}
    setTzOpen(false);
  };

  useEffect(() => {
    const onDown = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
        setTzOpen(false);
      }
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, []);

  const displayZone = gli ? (selected === 0 ? 1 : 0) : selected;
  const z = ZONES[displayZone];
  const time = mounted && now ? fmtTime(z.tz, now) : "--:--";
  const date = mounted && now ? fmtDate(z.tz, now) : "--- --";
  const activeRoute =
    pathname === "/platform"
      ? "platform"
      : pathname === "/admin"
        ? "admin"
        : pathname.includes("/login")
          ? "login"
          : "main";
  const menu =
    activeRoute === "platform"
      ? PLATFORM_MENU
      : activeRoute === "admin"
        ? ADMIN_MENU
        : PUBLIC_MENU;
  const startSide =
    activeRoute === "platform"
      ? "COMPETITION_PLATFORM"
      : activeRoute === "admin"
        ? "ADMIN_PANEL"
        : "PACKET_CAPTURE";

  return (
    <div ref={rootRef}>
      <div className={`startmenu ${open ? "open" : ""}`}>
        <div className="startmenu__rail">
          <div className="startmenu__side">{startSide}</div>
          <div className="startmenu__items">
            {menu.map((m) => (
              <Link
                key={m.label}
                href={m.href}
                className="startmenu__item"
                onClick={() => setOpen(false)}
              >
                {m.label}
              </Link>
            ))}
            <div className="startmenu__sep" />
            {activeRoute === "main" ? (
              <Link
                href="/#register"
                className="startmenu__item"
                onClick={() => setOpen(false)}
              >
                Registration Status
              </Link>
            ) : (
              <Link
                href="/"
                className="startmenu__item"
                onClick={() => setOpen(false)}
              >
                Return To Main Site
              </Link>
            )}
          </div>
        </div>
      </div>

      <div className="taskbar">
        <button
          className="taskbar__start"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
        >
          <span className="flag">&gt;</span>
          Start
        </button>

        <div className="taskbar__tasks">
          <Link
            className={`taskbar__task ${
              activeRoute === "main" ? "taskbar__task--active" : ""
            }`}
            href="/"
          >
            Main
          </Link>
          {!accountRole && (
            <Link
              className={`taskbar__task ${
                activeRoute === "login" ? "taskbar__task--active" : ""
              }`}
              href="/login"
            >
              Login
            </Link>
          )}
          {accountRole === "participant" && (
            <Link
              className={`taskbar__task ${
                activeRoute === "platform" ? "taskbar__task--active" : ""
              }`}
              href="/platform"
            >
              Competition Platform
            </Link>
          )}
          {accountRole === "admin" && (
            <Link
              className={`taskbar__task ${
                activeRoute === "admin" ? "taskbar__task--active" : ""
              }`}
              href="/admin"
            >
              Admin
            </Link>
          )}
        </div>

        <div className="taskbar__tray tzdd">
          <button
            className={`tz-pick ${gli ? "is-glitch" : ""}`}
            onClick={() => setTzOpen((v) => !v)}
            aria-haspopup="listbox"
            aria-expanded={tzOpen}
            title="Change timezone - Philippines / Australia"
          >
            <span className="taskbar__date">{date}</span>
            <span className="taskbar__clock">{time}</span>
            <span className="tz-zone">{z.label}</span>
            <span
              className={`tz-caret ${tzOpen ? "is-open" : ""}`}
              aria-hidden="true"
            />
          </button>

          {tzOpen && (
            <div className="tz-menu" role="listbox">
              <button
                role="option"
                aria-selected={selected === 0}
                className={selected === 0 ? "sel" : ""}
                onClick={() => chooseZone(0)}
              >
                Philippines - MNL
              </button>
              <button
                role="option"
                aria-selected={selected === 1}
                className={selected === 1 ? "sel" : ""}
                onClick={() => chooseZone(1)}
              >
                Australia - SYD
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
