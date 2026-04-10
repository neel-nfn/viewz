import React, { useMemo, useState } from "react";
import KanbanColumn from "./KanbanColumn";
import QuickEditModal from "./QuickEditModal";
import { useLocalState } from "../../utils/useLocalState";

function generateId() {
  return 'card_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

const wip = { 
  ideas: 12, 
  research: 8, 
  script: 6, 
  record: 4, 
  edit: 5, 
  thumbnail: 6, 
  upload: 4, 
  publish: 999 
};

const defaultBoard = {
  columns: [
    { id: "ideas", title: "Ideas" },
    { id: "research", title: "Research" },
    { id: "script", title: "Script" },
    { id: "record", title: "Record" },
    { id: "edit", title: "Edit" },
    { id: "thumbnail", title: "Thumbnail" },
    { id: "upload", title: "Upload" },
    { id: "publish", title: "Publish" }
  ],
  cards: [
    { id: "c1", column: "ideas", title: "2026 Driver Market Shakeup", meta: "F1 | 8–12 min", tags: ["news","opinion"] },
    { id: "c2", column: "research", title: "Piastri vs Norris dynamics", meta: "clips needed", tags: ["analysis"] },
    { id: "c3", column: "script", title: "Red Bull internal politics", meta: "draft v1", tags: ["script"] }
  ]
};

export default function KanbanBoard({ onStats }) {
  const [board, setBoard] = useLocalState("viewz_kanban_board_v1", defaultBoard);
  const [filter, setFilter] = useState("");
  const [editing, setEditing] = useState(null);

  const cols = board.columns;
  const grouped = useMemo(() => {
    const g = Object.fromEntries(cols.map((c) => [c.id, []]));
    for (const card of board.cards) {
      if (filter && !card.title.toLowerCase().includes(filter.toLowerCase())) continue;
      if (!g[card.column]) g[card.column] = [];
      g[card.column].push(card);
    }
    return g;
  }, [board, cols, filter]);

  const stats = useMemo(() => {
    const byCol = board.cards.reduce((a, c) => {
      a[c.column] = (a[c.column] || 0) + 1;
      return a;
    }, {});
    return { total: board.cards.length, ...byCol };
  }, [board.cards]);

  React.useEffect(() => {
    if (onStats) onStats(stats);
  }, [stats, onStats]);

  function moveCard(card, toColumn) {
    setBoard((b) => ({
      ...b,
      cards: b.cards.map((c) => (c.id === card.id ? { ...c, column: toColumn } : c))
    }));
  }

  function addCard(columnId) {
    const current = board.cards.filter(c => c.column === columnId).length;
    if (wip[columnId] && current >= wip[columnId]) {
      alert(`WIP limit reached for ${cols.find(c => c.id === columnId)?.title || columnId} (${current}/${wip[columnId]})`);
      return;
    }
    setEditing({ id: generateId(), column: columnId, title: "", meta: "", tags: [], isNew: true });
  }

  function openCard(card) {
    setEditing(card);
  }

  function saveCard(next) {
    setBoard((b) => ({
      ...b,
      cards: next.isNew 
        ? [{ ...next, isNew: false }, ...b.cards]
        : b.cards.map((c) => (c.id === next.id ? next : c))
    }));
    setEditing(null);
  }

  function clearDone() {
    if (!confirm("Archive all cards in Publish?")) return;
    setBoard((b) => ({ ...b, cards: b.cards.filter((c) => c.column !== "publish") }));
  }

  return (
    <>
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="text-white/90 font-semibold text-lg">Workflow</div>
          <div className="flex items-center gap-3">
            <input
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Filter cards..."
              className="rounded-xl bg-[#0f1118] border border-white/10 px-4 py-2 text-white/85 placeholder-white/40 outline-none focus:ring-2 focus:ring-teal-600/40"
            />
            <button 
              onClick={clearDone} 
              className="rounded-xl bg-white/10 border border-white/15 px-4 py-2 text-white/90 hover:bg-white/15 transition"
            >
              Archive Published
            </button>
          </div>
        </div>
        <div className="overflow-x-auto scroll-pb-6">
          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${cols.length}, minmax(220px, 1fr))` }}>
            {cols.map((col) => (
              <KanbanColumn
                key={col.id}
                id={col.id}
                title={col.title}
                cards={grouped[col.id] || []}
                wip={wip}
                onDropCard={moveCard}
                onOpenCard={openCard}
                onAddCard={addCard}
              />
            ))}
          </div>
        </div>
      </div>
      <QuickEditModal 
        open={!!editing} 
        card={editing} 
        onClose={() => setEditing(null)} 
        onSave={saveCard} 
      />
    </>
  );
}

