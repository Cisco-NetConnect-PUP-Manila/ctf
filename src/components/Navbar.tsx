"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { Menu, X } from "lucide-react";
import { CtaLink } from "@/components/ui/CtaButton";

const navLinks = [
  { name: "About", href: "#about", index: "01" },
  { name: "Acts", href: "#acts", index: "02" },
  { name: "Rules", href: "#rules", index: "03" },
  { name: "Timeline", href: "#timeline", index: "04" },
  { name: "Sponsors", href: "#sponsors", index: "05" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <motion.header
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 1, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className={`fixed inset-x-0 top-0 z-50 transition-colors duration-500 ${
          scrolled ? "border-b border-fg/8 bg-bg/70 backdrop-blur-xl" : "bg-transparent"
        }`}
      >
        <div className="container-pad flex h-20 items-center justify-between">
          <a href="#top" className="flex items-center gap-3 group" data-cursor>
            <Image
              src="/assets/ctf-text-image.webp"
              alt="Packet Capture"
              width={1508}
              height={362}
              className="h-6 md:h-7 w-auto transition-opacity duration-300 group-hover:opacity-70"
              priority
            />
          </a>

          <nav className="hidden items-center gap-7 md:flex">
            {navLinks.map((l) => (
              <a
                key={l.name}
                href={l.href}
                className="group terminal flex items-baseline gap-1.5 text-xs"
                data-cursor
              >
                <span className="text-[10px] text-magenta">{l.index}</span>
                <span className="link-sweep text-fg/70 transition-colors group-hover:text-fg">
                  {l.name}
                </span>
              </a>
            ))}
          </nav>

          <CtaLink
            href="#register"
            data-cursor
            size="sm"
            className="hidden text-sm font-bold uppercase tracking-wide md:inline-flex"
          >
            Register
          </CtaLink>

          <button
            onClick={() => setOpen((v) => !v)}
            className="md:hidden grid h-10 w-10 place-items-center border border-fg/10 bg-fg/[0.03]"
            aria-label="Menu"
            data-cursor
          >
            {open ? (
              <X aria-hidden="true" className="h-5 w-5 text-white" strokeWidth={1.8} />
            ) : (
              <Menu aria-hidden="true" className="h-5 w-5 text-white" strokeWidth={1.8} />
            )}
          </button>
        </div>
      </motion.header>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ clipPath: "inset(0 0 100% 0)" }}
            animate={{ clipPath: "inset(0 0 0% 0)" }}
            exit={{ clipPath: "inset(0 0 100% 0)" }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="fixed inset-0 z-40 bg-bg flex flex-col items-center justify-center gap-7 md:hidden"
          >
            {navLinks.map((l, i) => (
              <motion.a
                key={l.name}
                href={l.href}
                onClick={() => setOpen(false)}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 + i * 0.08 }}
                className="display text-5xl text-fg/90"
              >
                {l.name}
              </motion.a>
            ))}
            <CtaLink
              href="#register"
              onClick={() => setOpen(false)}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              size="md"
              className="mt-6 inline-flex font-bold uppercase tracking-wide"
            >
              Register
            </CtaLink>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
