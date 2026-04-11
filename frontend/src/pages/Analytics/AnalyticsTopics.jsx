import { Link } from "react-router-dom";

export default function AnalyticsTopics() {
  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Analytics Topics</h2>
        <Link to="/app" className="btn btn-sm btn-ghost">
          ← Back to Dashboard
        </Link>
      </div>
      <div className="card bg-base-100 border border-base-300">
        <div className="card-body">
          <p className="text-sm opacity-70">
            Analytics Topics — coming soon. API ready at /api/v1/analytics/topics
          </p>
        </div>
      </div>
    </div>
  );
}

