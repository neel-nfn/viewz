export default function ContentDoctor({ score }) {
  const color = score >= 90 ? "text-green-500" : score >= 70 ? "text-yellow-500" : "text-red-500";
  const icon = score >= 90 ? "✅" : score >= 70 ? "⚠️" : "❌";
  
  let tip = null;
  if (score < 70) {
    tip = "Consider tightening title or adding more keywords to improve SEO.";
  } else if (score < 90) {
    tip = "Good SEO score! Minor optimizations could push it even higher.";
  } else {
    tip = "Excellent SEO optimization! This content is well-optimized for search.";
  }

  return (
    <div className="flex items-center gap-2 p-3 bg-base-200 rounded">
      <span className="text-xl">{icon}</span>
      <div className="flex-1">
        <span className={`font-semibold ${color}`}>SEO Score: {score.toFixed(1)}</span>
        {tip && <p className="text-sm text-opacity-80 mt-1">{tip}</p>}
      </div>
    </div>
  );
}

