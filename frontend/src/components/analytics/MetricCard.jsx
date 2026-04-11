export default function MetricCard({ title, value, previousValue, change, changePct, format = "number", loading = false }) {
  const isPositive = change >= 0;
  const changeAbs = Math.abs(changePct || 0);
  
  const formatValue = (val) => {
    if (format === "duration") {
      // Format seconds to hours/minutes
      const hours = Math.floor(val / 3600);
      const minutes = Math.floor((val % 3600) / 60);
      if (hours > 0) {
        return `${hours}h ${minutes}m`;
      }
      return `${minutes}m`;
    }
    if (format === "percentage") {
      return `${val.toFixed(1)}%`;
    }
    if (format === "number") {
      return val.toLocaleString();
    }
    return val;
  };
  
  if (loading) {
    return (
      <div className="card bg-base-200 p-4 animate-pulse">
        <div className="h-4 bg-base-300 rounded w-1/3 mb-2"></div>
        <div className="h-8 bg-base-300 rounded w-1/2"></div>
      </div>
    );
  }
  
  return (
    <div className="card bg-base-200 p-4">
      <div className="text-sm text-base-content/70 mb-1">{title}</div>
      <div className="text-2xl font-bold mb-2">{formatValue(value)}</div>
      {previousValue !== undefined && (
        <div className="flex items-center gap-2 text-sm">
          <span className={`flex items-center gap-1 ${isPositive ? 'text-success' : 'text-error'}`}>
            {isPositive ? '↑' : '↓'} {changeAbs.toFixed(1)}%
          </span>
          <span className="text-base-content/50">
            vs previous period
          </span>
        </div>
      )}
    </div>
  );
}

