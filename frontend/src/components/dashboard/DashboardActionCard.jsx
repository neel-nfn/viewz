import React from "react";
import { cn } from "../../utils/cn";

export default function DashboardActionCard({ title, subtitle, icon: Icon, href = "#", color = "teal" }) {
  const tone = color === "teal" ? "from-teal-500 to-sky-500" : "from-sky-500 to-indigo-500";
  
  return (
    <a href={href} className="group rounded-2xl border border-white/5 bg-[#1d212e] p-4 shadow-[0_10px_30px_rgba(0,0,0,0.35)] hover:shadow-[0_16px_40px_rgba(0,0,0,0.45)] transition block">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`h-10 w-10 rounded-xl bg-gradient-to-br ${tone} text-white grid place-content-center shadow-[0_6px_24px_rgba(14,165,183,0.35)]`}>
            {Icon ? <Icon className="h-5 w-5" /> : null}
          </div>
          <div>
            <div className="text-white font-semibold tracking-tight">{title}</div>
            {subtitle ? <div className="text-white/60 text-sm">{subtitle}</div> : null}
          </div>
        </div>
        <div className={cn("h-2 w-2 rounded-full bg-teal-400/60 group-hover:bg-teal-300", color !== "teal" && "bg-sky-400/60 group-hover:bg-sky-300")} />
      </div>
      <div className={cn("mt-4 h-1.5 w-full rounded-full bg-gradient-to-r", tone)} />
    </a>
  );
}

