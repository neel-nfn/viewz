import React from "react";

export default function DashboardStatCard({ label, value, trend }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-[#1d212e] p-5 shadow-[0_10px_30px_rgba(0,0,0,0.35)]">
      <div className="text-white/60 text-sm">{label}</div>
      <div className="mt-1 text-2xl font-semibold text-white">{value}</div>
      {trend ? <div className="mt-1 text-xs text-white/60">{trend}</div> : null}
    </div>
  );
}

