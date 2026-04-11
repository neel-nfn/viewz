export default function TopVideosBlock({ videos, loading = false, dateRange = 7 }) {
  // Ensure videos is always an array
  const videosArray = Array.isArray(videos) ? videos : [];
  
  if (loading) {
    return (
      <div className="card bg-base-200 p-4">
        <h3 className="font-bold mb-4">Top Videos</h3>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex gap-3 animate-pulse">
              <div className="w-24 h-16 bg-base-300 rounded"></div>
              <div className="flex-1">
                <div className="h-4 bg-base-300 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-base-300 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }
  
  if (!videosArray || videosArray.length === 0) {
    return (
      <div className="card bg-base-200 p-4">
        <h3 className="font-bold mb-4">Top Videos</h3>
        <div className="text-center py-8 text-base-content/70">
          <p className="mb-2">No videos available for this period.</p>
          <p className="text-sm">Try selecting a different date range (30d or 90d) to see more videos.</p>
        </div>
      </div>
    );
  }
  
  return (
      <div className="card bg-base-200 p-4">
        <h3 className="font-bold mb-4">Top Videos</h3>
        <div className="space-y-3">
          {videosArray.map((video, i) => (
          <a
            key={video.video_id || i}
            href={video.youtube_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex gap-3 hover:bg-base-300/50 p-2 rounded transition-colors"
          >
            <img
              src={video.thumbnail_url}
              alt={video.title}
              className="w-24 h-16 object-cover rounded"
              onError={(e) => {
                e.target.src = "https://via.placeholder.com/160x90?text=No+Thumbnail";
              }}
            />
            <div className="flex-1 min-w-0">
              <div className="font-medium text-sm line-clamp-2 mb-1">
                {video.title}
              </div>
              <div className="flex items-center gap-3 text-xs text-base-content/70">
                <span>{video.views?.toLocaleString()} views</span>
                <span>•</span>
                <span>CTR: {video.ctr?.toFixed(1)}%</span>
                {video.outlier_score !== undefined && (
                  <>
                    <span>•</span>
                    <span className="font-semibold">
                      Outlier: {video.outlier_score.toFixed(1)}
                    </span>
                  </>
                )}
                <span
                  className={`badge badge-xs ${
                    video.performance_indicator === "above_average"
                      ? "badge-success"
                      : "badge-warning"
                  }`}
                >
                  {video.performance_indicator === "above_average" ? "↑ Above Average" : "↓ Needs Work"}
                </span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
