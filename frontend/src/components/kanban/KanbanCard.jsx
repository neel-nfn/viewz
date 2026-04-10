import React from "react";

export default function KanbanCard({ card, onOpen }) {
  return (
    <div
      className="rounded-xl bg-[#0f1118] border border-white/10 p-4 text-white/90 shadow-[0_10px_30px_rgba(0,0,0,0.35)] cursor-grab active:cursor-grabbing select-none hover:border-white/20 transition"
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData("text/plain", JSON.stringify(card));
        e.currentTarget.setAttribute("aria-grabbed", "true");
      }}
      onDragEnd={(e) => e.currentTarget.removeAttribute("aria-grabbed")}
      onDoubleClick={() => onOpen?.(card)}
    >
      <div className="text-sm font-medium">{card.title}</div>
      {card.meta ? <div className="mt-1 text-xs text-white/60">{card.meta}</div> : null}
      {card.tags?.length ? (
        <div className="mt-2 flex flex-wrap gap-1">
          {card.tags.map((t) => (
            <span key={t} className="text-[10px] rounded-md bg-white/5 px-2 py-1 text-white/70 border border-white/10">{t}</span>
          ))}
        </div>
      ) : null}
    </div>
  );
}

