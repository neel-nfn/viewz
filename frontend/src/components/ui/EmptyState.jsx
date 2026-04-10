import React from "react";

export default function EmptyState({ title="Nothing here yet", subtitle="Come back after you generate or connect data.", action=null }) {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 border rounded-lg bg-base-100">
      <div className="text-xl font-semibold">{title}</div>
      <div className="opacity-70 mt-1">{subtitle}</div>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}

