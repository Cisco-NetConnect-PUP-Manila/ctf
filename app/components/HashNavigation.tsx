"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

function scrollToHash(hash: string, behavior: ScrollBehavior = "auto") {
  const id = decodeURIComponent(hash.replace(/^#/, ""));
  if (!id) return false;

  const screen = document.getElementById("screen");
  const target = document.getElementById(id);
  if (!screen || !target) return false;

  const targetTop =
    target.getBoundingClientRect().top -
    screen.getBoundingClientRect().top +
    screen.scrollTop;
  const scrollMarginTop = Number.parseFloat(
    window.getComputedStyle(target).scrollMarginTop
  );

  screen.scrollTo({
    top: Math.max(0, targetTop - (Number.isFinite(scrollMarginTop) ? scrollMarginTop : 0)),
    behavior,
  });
  return true;
}

export default function HashNavigation() {
  const pathname = usePathname();

  useEffect(() => {
    const settleHash = () => {
      if (!window.location.hash) return;
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          scrollToHash(window.location.hash);
        });
      });
    };

    const onHashChange = () => scrollToHash(window.location.hash, "smooth");
    const onPopState = () => scrollToHash(window.location.hash, "auto");

    settleHash();
    window.addEventListener("hashchange", onHashChange);
    window.addEventListener("popstate", onPopState);

    const onClick = (event: MouseEvent) => {
      if (event.defaultPrevented || event.button !== 0) return;
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

      const link = (event.target as HTMLElement).closest<HTMLAnchorElement>("a[href]");
      if (!link) return;

      const url = new URL(link.href, window.location.href);
      if (url.origin !== window.location.origin || !url.hash) return;
      if (url.pathname !== window.location.pathname || url.search !== window.location.search) {
        return;
      }

      if (!document.getElementById(decodeURIComponent(url.hash.slice(1)))) return;

      event.preventDefault();
      window.history.pushState({}, "", `${url.pathname}${url.search}${url.hash}`);
      scrollToHash(url.hash, "smooth");
    };

    document.addEventListener("click", onClick);
    return () => {
      window.removeEventListener("hashchange", onHashChange);
      window.removeEventListener("popstate", onPopState);
      document.removeEventListener("click", onClick);
    };
  }, [pathname]);

  return null;
}
