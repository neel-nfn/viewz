export default function OutlierBadge({ score }) {
  let label = "Neutral";
  if (score >= 80) label = "🔥 Outlier";
  else if (score >= 60) label = "High";
  else if (score >= 40) label = "Medium";
  else label = "Low";

  return (
    <span className="inline-flex items-center px-2 py-1 rounded-2xl text-xs font-medium bg-base-200">
      {label} · {score}
    </span>
  );
}

