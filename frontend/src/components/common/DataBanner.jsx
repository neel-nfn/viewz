import { useState, useEffect } from "react";

/**
 * DataBanner Component
 * 
 * Shows data source indicator (Live/Demo) based on API response metadata.
 * Reads mock, source, and fallback_reason fields.
 */
export default function DataBanner({ data, page = "page" }) {
  const [bannerInfo, setBannerInfo] = useState(null);

  useEffect(() => {
    if (!data) {
      setBannerInfo(null);
      return;
    }

    // Check if data has mock/source fields
    const isMock = data.mock === true || data.source === 'stub' || data.source === 'demo-fixture';
    const isLive = data.mock === false && data.source === 'youtube';
    const fallbackReason = data.fallback_reason;

    if (isMock || isLive || fallbackReason) {
      setBannerInfo({
        isMock,
        isLive,
        source: data.source || 'unknown',
        fallbackReason,
      });
    } else {
      setBannerInfo(null);
    }
  }, [data]);

  if (!bannerInfo) {
    return null;
  }

  const { isMock, isLive, source, fallbackReason } = bannerInfo;

  return (
    <div className="mb-4">
      {isLive && (
        <div className="alert alert-success py-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">LIVE DATA ✅</span>
            <span className="text-xs opacity-70">Source: {source}</span>
          </div>
        </div>
      )}
      {isMock && (
        <div className="alert alert-warning py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">DEMO DATA</span>
              <span className="text-xs opacity-70">Source: {source}</span>
              {fallbackReason && (
                <span className="text-xs opacity-70">— {fallbackReason}</span>
              )}
            </div>
            {fallbackReason && (
              <a
                href="/app/settings/integrations"
                className="btn btn-xs btn-primary"
              >
                {fallbackReason === 'YOUTUBE_NOT_CONNECTED' ? 'Connect' : 'Fix'}
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

