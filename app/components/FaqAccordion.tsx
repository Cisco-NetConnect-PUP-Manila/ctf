"use client";

import { useState } from "react";
import type { FaqItem } from "../data";

export default function FaqAccordion({ items }: { items: FaqItem[] }) {
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <div className="faq-list">
      {items.map((item, i) => (
        <details
          className="faq-item"
          key={item.q}
          open={openIndex === i}
          onToggle={(event) => {
            if (event.currentTarget.open) setOpenIndex(i);
          }}
        >
          <summary className="faq-q">
            {item.q.endsWith("?") ? (
              <>
                {item.q.slice(0, -1)}
                <span className="faq-q__mark">?</span>
              </>
            ) : (
              item.q
            )}
          </summary>
          <p className="faq-a">{item.a}</p>
        </details>
      ))}
    </div>
  );
}
