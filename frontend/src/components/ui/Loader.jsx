import React from "react";

export default function Loader({ label="Loading..." }) {
  return (
    <div className="flex items-center gap-2 text-sm opacity-70">
      <span className="loading loading-spinner loading-sm" />
      <span>{label}</span>
    </div>
  );
}

