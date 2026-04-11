import { useState, useEffect } from "react";
import { getTrends } from "../../services/analyticsService";

export default function TrendlineChart({ initialData, loading: initialLoading = false, dateRange = 7 }) {
  const [metric, setMetric] = useState("views"); // "views" or "ctr"
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(initialLoading);
  
  useEffect(() => {
    async function loadTrends() {
      setLoading(true);
      try {
        const result = await getTrends(dateRange);
        setData(result);
      } catch (error) {
        console.error("Error loading trends:", error);
      } finally {
        setLoading(false);
      }
    }
    
    if (dateRange !== 7 || !initialData) {
      loadTrends();
    } else {
      setData(initialData);
    }
  }, [dateRange, initialData]);
  
  if (loading || !data || !data.data || data.data.length === 0) {
    if (loading) {
      return (
        <div className="card bg-base-200 p-4">
          <div className="h-64 bg-base-300 rounded animate-pulse"></div>
        </div>
      );
    }
    
    // Empty state
    return (
      <div className="card bg-base-200 p-4">
        <h3 className="font-bold mb-4">Trends</h3>
        <div className="text-center py-8 text-base-content/70">
          <p className="mb-2">No trend data available for this period.</p>
          <p className="text-sm">Try selecting a different date range or connect your YouTube channel.</p>
        </div>
      </div>
    );
  }
  
  const chartData = data.data;
  const maxValue = Math.max(...chartData.map(d => d[metric]));
  const minValue = Math.min(...chartData.map(d => d[metric]));
  const range = maxValue - minValue || 1;
  
  // Simple SVG line chart
  const width = 600;
  const height = 200;
  const padding = 40;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;
  
  const points = chartData.map((d, i) => {
    const x = padding + (i / (chartData.length - 1)) * chartWidth;
    const y = padding + chartHeight - ((d[metric] - minValue) / range) * chartHeight;
    return { x, y, value: d[metric], date: d.date };
  });
  
  const pathData = points.map((p, i) => 
    `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
  ).join(' ');
  
  return (
    <div className="card bg-base-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold">Trends</h3>
        <div className="flex gap-2">
          <button
            className={`btn btn-xs ${metric === "views" ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setMetric("views")}
          >
            Views
          </button>
          <button
            className={`btn btn-xs ${metric === "ctr" ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setMetric("ctr")}
          >
            CTR
          </button>
        </div>
      </div>
      
      <div className="relative">
        <svg width={width} height={height} className="w-full">
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
            <line
              key={ratio}
              x1={padding}
              y1={padding + ratio * chartHeight}
              x2={width - padding}
              y2={padding + ratio * chartHeight}
              stroke="currentColor"
              strokeWidth="1"
              opacity="0.1"
            />
          ))}
          
          {/* Line */}
          <path
            d={pathData}
            fill="none"
            stroke="hsl(var(--p))"
            strokeWidth="2"
            className="transition-all"
          />
          
          {/* Points */}
          {points.map((p, i) => (
            <g key={i}>
              <circle
                cx={p.x}
                cy={p.y}
                r="4"
                fill="hsl(var(--p))"
                className="hover:r-6 transition-all cursor-pointer"
              />
              <title>{`${p.date}: ${metric === "views" ? p.value.toLocaleString() : p.value.toFixed(1) + "%"}`}</title>
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}

