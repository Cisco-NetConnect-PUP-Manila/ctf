"use client";

import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";

const PUBLIC_MENU = [
  { k: ">", label: "Incident Brief", href: "/#about" },
  { k: "[]", label: "Competition Overview", href: "/#overview" },
  { k: "A", label: "The Four Acts", href: "/#acts" },
  { k: "!", label: "Rules of Engagement", href: "/#rules" },
  { k: "?", label: "FAQ", href: "/#faq" },
  { k: "T", label: "Operation Timeline", href: "/#timeline" },
  { k: "$", label: "Sponsors", href: "/#sponsors" },
];

const PLATFORM_MENU = [
  { k: "D", label: "Dashboard", href: "/platform#dashboard" },
  { k: "S", label: "Storyline", href: "/platform#storyline" },
  { k: "M", label: "Platform Modules", href: "/platform#modules" },
  { k: "C", label: "Challenge Workspace", href: "/platform#challenges" },
  { k: "!", label: "Portal Status", href: "/platform#portal-status" },
];

const ADMIN_MENU = [
  { k: "O", label: "Admin Overview", href: "/admin#overview" },
  { k: "M", label: "Admin Modules", href: "/admin#modules" },
  { k: "A", label: "Backend Authority", href: "/admin#authority" },
  { k: "!", label: "Admin Status", href: "/admin#admin-status" },
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
  const rootRef = useRef<HTMLDivElement | null>(null);

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
    pathname === "/platform" ? "platform" : pathname === "/admin" ? "admin" : "main";
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
              <a
                key={m.label}
                href={m.href}
                className="startmenu__item"
                onClick={() => setOpen(false)}
              >
                <span className="k">{m.k}</span>
                {m.label}
              </a>
            ))}
            <div className="startmenu__sep" />
            {activeRoute === "main" ? (
              <a
                href="/#register"
                className="startmenu__item"
                onClick={() => setOpen(false)}
              >
                <span className="k">&gt;</span>Registration Status
              </a>
            ) : (
              <a
                href="/"
                className="startmenu__item"
                onClick={() => setOpen(false)}
              >
                <span className="k">&gt;</span>Return To Main Site
              </a>
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
          START
        </button>

        <div className="taskbar__tasks">
          <a
            className={`taskbar__task ${
              activeRoute === "main" ? "taskbar__task--active" : ""
            }`}
            href="/"
          >
            MAIN
          </a>
          <a
            className={`taskbar__task ${
              activeRoute === "platform" ? "taskbar__task--active" : ""
            }`}
            href="/platform"
          >
            COMPETITION PLATFORM
          </a>
          <a
            className={`taskbar__task ${
              activeRoute === "admin" ? "taskbar__task--active" : ""
            }`}
            href="/admin"
          >
            ADMIN
          </a>
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
            <span className="tz-caret">v</span>
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
