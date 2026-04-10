import React from "react";

export default function PageHeader({ title, subtitle, actions, breadcrumbs }) {
  return (
    <div className="w-full bg-background">
      <div className="max-w-[1240px] mx-auto px-6 md:px-8 py-6">
        {breadcrumbs ? (
          <div className="mb-2 text-sm text-textSecondary">{breadcrumbs}</div>
        ) : null}

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <h1 className="text-3xl md:text-4xl font-semibold text-textPrimary tracking-tight">
              {title}
            </h1>
            {subtitle ? (
              <p className="mt-1 text-textSecondary">{subtitle}</p>
            ) : null}
          </div>

          <div className="flex items-center gap-2">{actions}</div>
        </div>
      </div>
    </div>
  );
}
