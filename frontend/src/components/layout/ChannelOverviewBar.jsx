import { useState, useEffect } from 'react';
import { getChannelSnapshot } from '../../services/analyticsService';
import { TrendingUp, TrendingDown, Eye, Users, Clock, MousePointerClick } from 'lucide-react';

export default function ChannelOverviewBar({ dateRange: initialDateRange = 7, onDateRangeChange }) {
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState(initialDateRange);

  useEffect(() => {
    loadSnapshot();
  }, [dateRange]);

  async function loadSnapshot() {
    try {
      setLoading(true);
      const data = await getChannelSnapshot({ days: dateRange });
      setSnapshot(data);
    } catch (err) {
      console.error('Failed to load channel snapshot:', err);
      // Use fallback data
      setSnapshot({
        views_7d: 0,
        subscribers_net: 0,
        watch_time_7d: 0,
        avg_ctr: 0,
        views_change_pct: 0,
        subscribers_change_pct: 0,
        watch_time_change_pct: 0,
        ctr_change: 0,
      });
    } finally {
      setLoading(false);
    }
  }

  function handleDateRangeChange(days) {
    setDateRange(days);
    if (onDateRangeChange) {
      onDateRangeChange(days);
    }
  }

  function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }

  function formatWatchTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    if (hours >= 1000) return (hours / 1000).toFixed(1) + 'K hrs';
    return `${hours} hrs`;
  }

  const displaySnapshot = snapshot || {
    views_7d: 0,
    subscribers_net: 0,
    watch_time_7d: 0,
    avg_ctr: 0,
    views_change_pct: 0,
    subscribers_change_pct: 0,
    watch_time_change_pct: 0,
    ctr_change: 0,
  };

  return (
    <div className="bg-surface border-b border-border">
      <div className="max-w-[1240px] mx-auto px-4 sm:px-6 py-4">
        {/* Header with Date Range Selector */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-textPrimary">Channel Overview</h2>
          <div className="flex gap-2 bg-background border border-border rounded-lg p-1">
            {[
              { days: 7, label: '7d' },
              { days: 30, label: '30d' },
              { days: 90, label: '90d' }
            ].map(({ days, label }) => (
              <button
                key={days}
                onClick={() => handleDateRangeChange(days)}
                className={`px-3 py-1 rounded text-sm font-medium transition ${
                  dateRange === days
                    ? 'bg-primary text-white'
                    : 'text-textSecondary hover:text-textPrimary'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Metrics Grid */}
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-20 bg-surface-secondary rounded-lg animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Views */}
            <div className="bg-background rounded-lg p-4 border border-border">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-textSecondary">
                  <Eye size={16} />
                  <span className="text-sm font-medium">Views</span>
                </div>
                {displaySnapshot.views_change_pct !== undefined && (
                  <div className={`flex items-center gap-1 text-xs ${
                    displaySnapshot.views_change_pct >= 0 ? 'text-success' : 'text-error'
                  }`}>
                    {displaySnapshot.views_change_pct >= 0 ? (
                      <TrendingUp size={14} />
                    ) : (
                      <TrendingDown size={14} />
                    )}
                    <span>{Math.abs(displaySnapshot.views_change_pct || 0).toFixed(1)}%</span>
                  </div>
                )}
              </div>
              <div className="text-2xl font-bold text-textPrimary">
                {formatNumber(displaySnapshot.views_7d || 0)}
              </div>
            </div>

            {/* Subscribers */}
            <div className="bg-background rounded-lg p-4 border border-border">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-textSecondary">
                  <Users size={16} />
                  <span className="text-sm font-medium">Subscribers</span>
                </div>
                {displaySnapshot.subscribers_change_pct !== undefined && (
                  <div className={`flex items-center gap-1 text-xs ${
                    displaySnapshot.subscribers_change_pct >= 0 ? 'text-success' : 'text-error'
                  }`}>
                    {displaySnapshot.subscribers_change_pct >= 0 ? (
                      <TrendingUp size={14} />
                    ) : (
                      <TrendingDown size={14} />
                    )}
                    <span>{Math.abs(displaySnapshot.subscribers_change_pct || 0).toFixed(1)}%</span>
                  </div>
                )}
              </div>
              <div className="text-2xl font-bold text-textPrimary">
                {formatNumber(displaySnapshot.subscribers_net || 0)}
              </div>
            </div>

            {/* Watch Time */}
            <div className="bg-background rounded-lg p-4 border border-border">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-textSecondary">
                  <Clock size={16} />
                  <span className="text-sm font-medium">Watch Time</span>
                </div>
                {displaySnapshot.watch_time_change_pct !== undefined && (
                  <div className={`flex items-center gap-1 text-xs ${
                    displaySnapshot.watch_time_change_pct >= 0 ? 'text-success' : 'text-error'
                  }`}>
                    {displaySnapshot.watch_time_change_pct >= 0 ? (
                      <TrendingUp size={14} />
                    ) : (
                      <TrendingDown size={14} />
                    )}
                    <span>{Math.abs(displaySnapshot.watch_time_change_pct || 0).toFixed(1)}%</span>
                  </div>
                )}
              </div>
              <div className="text-2xl font-bold text-textPrimary">
                {formatWatchTime(displaySnapshot.watch_time_7d || 0)}
              </div>
            </div>

            {/* CTR */}
            <div className="bg-background rounded-lg p-4 border border-border">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-textSecondary">
                  <MousePointerClick size={16} />
                  <span className="text-sm font-medium">Avg CTR</span>
                </div>
                {displaySnapshot.ctr_change !== undefined && (
                  <div className={`flex items-center gap-1 text-xs ${
                    displaySnapshot.ctr_change >= 0 ? 'text-success' : 'text-error'
                  }`}>
                    {displaySnapshot.ctr_change >= 0 ? (
                      <TrendingUp size={14} />
                    ) : (
                      <TrendingDown size={14} />
                    )}
                    <span>{Math.abs(displaySnapshot.ctr_change || 0).toFixed(1)}%</span>
                  </div>
                )}
              </div>
              <div className="text-2xl font-bold text-textPrimary">
                {(displaySnapshot.avg_ctr || 0).toFixed(1)}%
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

