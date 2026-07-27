"use client";

import { useEffect, useRef, useState } from "react";

const MENU = [
  { k: "◈", label: "Incident Brief", href: "#about" },
  { k: "▤", label: "The Four Acts", href: "#acts" },
  { k: "!", label: "Rules of Engagement", href: "#rules" },
  { k: "◷", label: "Operation Timeline", href: "#timeline" },
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
  const [mounted, setMounted] = useState(false);
  const [now, setNow] = useState<Date | null>(null);
  const [selected, setSelected] = useState(0); // 0 = PH, 1 = AU (user's choice)
  const [gli, setGli] = useState(false);
  const [open, setOpen] = useState(false);
  const [tzOpen, setTzOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  // clock tick + restore saved timezone choice
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

  // scroll → time briefly swaps to the OTHER zone (minimal glitch, stays visible)
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

  // close start menu on outside click
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

  // while glitching, show the OTHER zone than the one the user picked
  const displayZone = gli ? (selected === 0 ? 1 : 0) : selected;
  const z = ZONES[displayZone];
  const time = mounted && now ? fmtTime(z.tz, now) : "--:--";
  const date = mounted && now ? fmtDate(z.tz, now) : "--- --";

  return (
    <div ref={rootRef}>
      <div className={`startmenu ${open ? "open" : ""}`}>
        <div className="startmenu__rail">
          <div className="startmenu__side">PACKET·CAPTURE</div>
          <div className="startmenu__items">
            {MENU.map((m) => (
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
            <a
              href="#register"
              className="startmenu__item"
              onClick={() => setOpen(false)}
            >
              <span className="k">&raquo;</span>Begin Investigation
            </a>
          </div>
        </div>
      </div>

      <div className="taskbar">
        <button
          className="taskbar__start"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
        >
          <span className="flag">◈</span>
          START
        </button>

        <div className="taskbar__tasks">
          <span className="taskbar__task taskbar__task--active">
            <i>▣</i> STATUS.LCD
          </span>
          <span className="taskbar__task">
            <i>▤</i> ACTS.DAT
          </span>
          <span className="taskbar__task">
            <i>!</i> INTRUSION.LOG
          </span>
        </div>

        <div className="taskbar__tray tzdd">
          <button
            className={`tz-pick ${gli ? "is-glitch" : ""}`}
            onClick={() => setTzOpen((v) => !v)}
            aria-haspopup="listbox"
            aria-expanded={tzOpen}
            title="Change timezone — Philippines / Australia"
          >
            <span className="taskbar__date">{date}</span>
            <span className="taskbar__clock">{time}</span>
            <span className="tz-zone">{z.label}</span>
            <span className="tz-caret">▾</span>
          </button>

          {tzOpen && (
            <div className="tz-menu" role="listbox">
              <button
                role="option"
                aria-selected={selected === 0}
                className={selected === 0 ? "sel" : ""}
                onClick={() => chooseZone(0)}
              >
                Philippines &middot; MNL
              </button>
              <button
                role="option"
                aria-selected={selected === 1}
                className={selected === 1 ? "sel" : ""}
                onClick={() => chooseZone(1)}
              >
                Australia &middot; SYD
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
