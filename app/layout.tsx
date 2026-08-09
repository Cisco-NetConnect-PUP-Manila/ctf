import type { Metadata, Viewport } from "next";
import "./globals.css";
import Taskbar from "./components/Taskbar";
import ScrollGlitch from "./components/ScrollGlitch";
import Nav from "./components/Nav";
import IntroExperience from "./components/IntroExperience";

export const metadata: Metadata = {
  title: "Packet Capture | Beneath the Network",
  description:
    "A team-based, story-driven Capture-the-Flag competition bridging networking fundamentals and cybersecurity.",
  keywords: ["CTF", "cybersecurity", "capture the flag", "packet capture", "incident response"],
  icons: {
    icon: "/images/ctf-icon.ico",
  },
  openGraph: {
    title: "PACKET CAPTURE // Beneath The Network",
    description:
      "Trace the evidence across four sequential Acts and reconstruct the investigation beneath the network.",
    type: "website",
  },
};

/* Explicit viewport control for mobile / tablet / iPad. Zoom is left
   enabled (no maximum-scale / user-scalable=no) for accessibility.
   viewportFit=cover lets the CRT frame reach into iPhone safe areas. */
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#050302",
};

/* Displacement map for the CRT barrel: R = horizontal offset, G = vertical.
   Center neutral (128,128); ease-in-out ramps toward edges = real bulge. */
const BARREL_MAP =
  "data:image/svg+xml," +
  encodeURIComponent(
    `<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'>
      <defs>
        <linearGradient id='rx' x1='0%' y1='0%' x2='100%' y2='0%'>
          <stop offset='0%' stop-color='rgb(0,0,0)'/>
          <stop offset='34%' stop-color='rgb(104,0,0)'/>
          <stop offset='50%' stop-color='rgb(128,0,0)'/>
          <stop offset='66%' stop-color='rgb(152,0,0)'/>
          <stop offset='100%' stop-color='rgb(255,0,0)'/>
        </linearGradient>
        <linearGradient id='gy' x1='0%' y1='0%' x2='0%' y2='100%'>
          <stop offset='0%' stop-color='rgb(0,0,0)'/>
          <stop offset='34%' stop-color='rgb(0,104,0)'/>
          <stop offset='50%' stop-color='rgb(0,128,0)'/>
          <stop offset='66%' stop-color='rgb(0,152,0)'/>
          <stop offset='100%' stop-color='rgb(0,255,0)'/>
        </linearGradient>
      </defs>
      <rect width='120' height='120' fill='rgb(0,0,0)'/>
      <rect width='120' height='120' fill='url(#rx)'/>
      <rect width='120' height='120' fill='url(#gy)' style='mix-blend-mode:screen'/>
    </svg>`
  );

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // suppressHydrationWarning: some browser extensions inject attributes
    // (e.g. data-*-nonce) onto <html> before React hydrates, which would
    // otherwise trip a hydration-mismatch warning. This only suppresses
    // attribute noise on <html> itself, not real mismatches in the tree.
    <html lang="en" suppressHydrationWarning>
      <body>
        <div className="tube">
          {/* dark CRT desktop + faint tech grid + phosphor glow */}
          <div className="crt-bg" aria-hidden="true" />

          {/* fixed nav overlay (outside the scroller so it never shifts) */}
          <Nav />

          {/* the scrolling screen contents */}
          <div className="screen" id="screen">
            {children}
          </div>

          <Taskbar />
          <ScrollGlitch />

          {/* CRT glass: curvature, scanlines, sweep, flicker, bezel */}
          <div className="crt" aria-hidden="true">
            <div className="crt__scanlines" />
            <div className="crt__sweep" />
            <div className="crt__glass" />
            <div className="crt__flicker" />
            <div className="crt__bezel" />
          </div>
        </div>

        {/* barrel-distortion filter definition (referenced by .tube) */}
        <svg className="crt-filter-def" aria-hidden="true" focusable="false">
          <filter
            id="barrel"
            x="-6%"
            y="-6%"
            width="112%"
            height="112%"
            colorInterpolationFilters="sRGB"
          >
            <feImage
              href={BARREL_MAP}
              xlinkHref={BARREL_MAP}
              x="0"
              y="0"
              width="100%"
              height="100%"
              preserveAspectRatio="none"
              result="map"
            />
            <feDisplacementMap
              in="SourceGraphic"
              in2="map"
              scale="6"
              xChannelSelector="R"
              yChannelSelector="G"
            />
          </filter>
        </svg>

        {/* fake landing -> glitch -> reveal TVA site -> welcome pop-up */}
        <IntroExperience />
      </body>
    </html>
  );
}
