import React from "react";

export default function DashboardSidebarCard({ title, children, footer }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-[#1d212e] p-5 shadow-[0_10px_30px_rgba(0,0,0,0.35)]">
      <div className="text-white/90 font-semibold mb-3">{title}</div>
      <div className="text-white/75 text-sm">{children}</div>
      {footer ? <div className="mt-4">{footer}</div> : null}
    </div>
  );
}

