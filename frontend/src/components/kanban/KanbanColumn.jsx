import React, { useMemo, useState } from "react";
import KanbanCard from "./KanbanCard";

export default function KanbanColumn({ id, title, cards, wip, onDropCard, onOpenCard, onAddCard }) {
  const [isOver, setIsOver] = useState(false);
  const count = useMemo(() => cards.length, [cards]);
  const over = wip?.[id] ? count > wip[id] : false;
  
  return (
    <div
      className={`rounded-2xl bg-[#1d212e] border ${isOver ? "border-teal-400/70 ring-2 ring-teal-500/20" : "border-white/5"} p-4 flex flex-col gap-3 min-h-[280px] transition`}
      onDragOver={(e) => { e.preventDefault(); setIsOver(true); }}
      onDragLeave={() => setIsOver(false)}
      onDrop={(e) => {
        setIsOver(false);
        const data = e.dataTransfer.getData("text/plain");
        if (!data) return;
        try { 
          const card = JSON.parse(data); 
          onDropCard?.(card, id); 
        } catch {}
      }}
    >
      <div className="flex items-center justify-between">
        <div className="text-white/90 font-semibold">{title}</div>
        <div className={`text-xs ${over ? "text-amber-300" : "text-white/50"}`}>
          {count}{wip?.[id] ? `/${wip[id]}` : ""}
        </div>
      </div>
      <button
        onClick={() => onAddCard?.(id)}
        className="rounded-xl border border-white/10 bg-[#0f1118] text-white/80 text-xs px-3 py-2 hover:bg-white/15 transition"
      >
        Add card
      </button>
      {isOver ? (
        <div className="rounded-xl border-2 border-dashed border-teal-400/60 bg-teal-500/5 h-16 grid place-content-center text-teal-300 text-xs">
          Drop here
        </div>
      ) : null}
      <div className="flex flex-col gap-3">
        {cards.map((c) => (
          <KanbanCard key={c.id} card={c} onOpen={onOpenCard} />
        ))}
      </div>
    </div>
  );
}

