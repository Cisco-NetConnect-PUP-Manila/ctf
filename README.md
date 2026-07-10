# Packet Capture CTF Website

Official event website for **Packet Capture**, a narrative-driven Capture The Flag experience about incident response, hidden network layers, recovered artifacts, and a final transmission.

The site is built as an interactive landing page with scroll-driven sections, animated typography, a persistent network-core visual layer, and spoiler-safe challenge metadata.

## Features

- Futuristic CTF event landing page
- Narrative sections for the event story and four acts
- Public challenge metadata without flags or solution spoilers
- GSAP and ScrollTrigger-powered scroll animations
- Smooth scrolling with reduced-motion support
- Custom cursor and subtle visual effects
- Responsive layout for desktop, tablet, and mobile
- Local custom fonts and brand assets from `public/fonts` and `public/assets`

## Tech Stack

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- GSAP / ScrollTrigger
- Framer Motion
- Three.js / React Three Fiber / Drei
- Lenis smooth scrolling
- Lucide React icons

## Getting Started

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

Open the site:

```text
http://localhost:3000
```

## Scripts

```bash
npm run dev
```

Starts the local development server.

```bash
npm run build
```

Creates a production build.

```bash
npm run start
```

Runs the production build locally.

```bash
npm run lint
```

Runs ESLint checks.

## Project Structure

```text
ctf-website/
  public/
    assets/          Event imagery and visual assets
    fonts/           Local custom fonts
  src/
    app/             Next.js app entry, layout, and global styles
    components/      Shared UI, effects, navigation, and page sections
    lib/             Animation and preference utilities
  scripts/           Local helper scripts
```

Main page sections live in:

```text
src/components/sections/
```

Shared CTA and section layout primitives live in:

```text
src/components/ui/
```

## Content Guidelines

This website should stay spoiler-safe.

- Do not publish real flags.
- Do not publish final phrases or exact solve paths.
- Challenge names, point values, and public unlock metadata are okay.
- Story hints should tease the mechanic without revealing the final answer.
- Registration status should not look clickable unless a real registration action exists.

## Deployment

The project can be deployed to any platform that supports Next.js, including Vercel.

Before deploying:

```bash
npm run lint
npm run build
```

## Repository Hygiene

Local assistant files, generated logs, build outputs, dependency folders, and environment files are intentionally ignored through `.gitignore`.

Keep private planning notes, local AI workspace files, and machine-specific files out of the public repository.
