import React, { useEffect, useRef } from "react";

export default function QuickEditModal({ open, card, onClose, onSave }) {
  const titleRef = useRef(null);
  const metaRef = useRef(null);

  useEffect(() => {
    if (open && titleRef.current) {
      titleRef.current.focus();
      titleRef.current.select();
    }
  }, [open]);

  if (!open) return null;

  function handleSave() {
    const title = titleRef.current?.value || card?.title || "";
    const meta = metaRef.current?.value || card?.meta || "";
    onSave({ ...card, title, meta });
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      handleSave();
    } else if (e.key === "Escape") {
      onClose();
    }
  }

  return (
    <div 
      className="fixed inset-0 z-50 grid place-items-center bg-black/50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div 
        className="w-full max-w-md rounded-2xl bg-[#1d212e] border border-white/10 p-5 shadow-[0_10px_30px_rgba(0,0,0,0.5)]"
        onKeyDown={handleKeyDown}
      >
        <div className="text-white/90 font-semibold mb-4">Edit card</div>
        <label className="block text-xs text-white/60 mb-1">Title</label>
        <input 
          ref={titleRef}
          defaultValue={card?.title || ""} 
          className="w-full rounded-xl bg-[#0f1118] border border-white/10 px-3 py-2 text-white/85 mb-3 outline-none focus:ring-2 focus:ring-teal-600/40" 
        />
        <label className="block text-xs text-white/60 mb-1">Meta</label>
        <input 
          ref={metaRef}
          defaultValue={card?.meta || ""} 
          className="w-full rounded-xl bg-[#0f1118] border border-white/10 px-3 py-2 text-white/85 mb-4 outline-none focus:ring-2 focus:ring-teal-600/40" 
        />
        <div className="flex justify-end gap-2">
          <button 
            onClick={onClose} 
            className="rounded-xl bg-white/10 px-4 py-2 text-white/90 hover:bg-white/15 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="rounded-xl bg-teal-600 hover:bg-teal-700 px-4 py-2 text-white transition"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

