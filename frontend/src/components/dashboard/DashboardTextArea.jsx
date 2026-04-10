import React from "react";

export default function DashboardTextArea({ title, placeholder, action }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-[#1d212e] p-5 shadow-[0_10px_30px_rgba(0,0,0,0.35)]">
      <div className="flex items-center justify-between mb-3">
        <div className="text-white/90 font-semibold">{title}</div>
        {action}
      </div>
      <textarea
        rows={3}
        placeholder={placeholder}
        className="w-full resize-y rounded-xl bg-[#0f1118] border border-white/10 px-4 py-3 text-white/85 placeholder-white/40 outline-none focus:ring-2 focus:ring-teal-600/40"
      />
    </div>
  );
}

