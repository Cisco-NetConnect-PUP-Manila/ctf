import { marqueeItems } from "../data";

export default function Marquee() {
  const items = [...marqueeItems, ...marqueeItems];
  return (
    <div className="marquee" aria-hidden="true">
      <div className="marquee__track">
        {items.map((item, i) => {
          const [tag, ...rest] = item.split(" ");
          return (
            <span className="marquee__item" key={i}>
              <b>{tag}</b> {rest.join(" ")}
              <span className="marquee__sep">{" // "}</span>
            </span>
          );
        })}
      </div>
    </div>
  );
}
