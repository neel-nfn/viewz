import { useState, useEffect } from 'react';
import { getTopVideos } from '../../services/analyticsService';
import Card from '../primitives/Card';
import Button from '../primitives/Button';
import { Sparkles, Eye, ThumbsUp, BarChart3, ExternalLink, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function OptimizeLatestVideo() {
  const navigate = useNavigate();
  const [latestVideo, setLatestVideo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLatestVideo();
  }, []);

  async function loadLatestVideo() {
    try {
      setLoading(true);
      const result = await getTopVideos(1);
      const videos = result.data || result;
      
      if (Array.isArray(videos) && videos.length > 0) {
        // Get the most recent video (first one should be latest)
        setLatestVideo(videos[0]);
      } else {
        // Fallback mock data
        setLatestVideo({
          video_id: 'demo_latest',
          title: 'Latest Video Title - Tutorial and Review',
          thumbnail_url: 'https://via.placeholder.com/320x180?text=Latest+Video',
          youtube_url: 'https://youtube.com/watch?v=demo',
          views: 12400,
          likes: 850,
          ctr: 4.8,
          published_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        });
      }
    } catch (err) {
      console.error('Failed to load latest video:', err);
      // Fallback mock data
      setLatestVideo({
        video_id: 'demo_latest',
        title: 'Latest Video Title - Tutorial and Review',
        thumbnail_url: 'https://via.placeholder.com/320x180?text=Latest+Video',
        youtube_url: 'https://youtube.com/watch?v=demo',
        views: 12400,
        likes: 850,
        ctr: 4.8,
        published_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      });
    } finally {
      setLoading(false);
    }
  }

  function formatTimeAgo(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    const days = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    return `${days} days ago`;
  }

  if (loading) {
    return (
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-textPrimary">Optimize Latest Video</h2>
          <div className="w-24 h-8 bg-surface-secondary rounded animate-pulse" />
        </div>
        <div className="flex gap-4">
          <div className="w-48 h-27 bg-surface-secondary rounded animate-pulse" />
          <div className="flex-1 space-y-2">
            <div className="h-6 bg-surface-secondary rounded animate-pulse" />
            <div className="h-4 bg-surface-secondary rounded animate-pulse w-2/3" />
          </div>
        </div>
      </Card>
    );
  }

  if (!latestVideo) {
    return null;
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-textPrimary">Optimize Latest Video</h2>
        <Button 
          variant="primary" 
          size="sm"
          onClick={() => navigate('/app/workflow')}
        >
          <Sparkles size={16} className="mr-2" />
          Optimize
        </Button>
      </div>
      
      <div className="flex gap-4">
        <img
          src={latestVideo.thumbnail_url || latestVideo.thumbnail}
          alt={latestVideo.title || latestVideo.video_title}
          className="w-48 h-27 object-cover rounded flex-shrink-0"
        />
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-textPrimary mb-2 line-clamp-2">
            {latestVideo.title || latestVideo.video_title}
          </h3>
          <div className="flex flex-wrap gap-4 text-sm text-textSecondary mb-3">
            <div className="flex items-center gap-1">
              <Eye size={14} />
              <span>{(latestVideo.views || 0).toLocaleString()} views</span>
            </div>
            {latestVideo.likes !== undefined && (
              <div className="flex items-center gap-1">
                <ThumbsUp size={14} />
                <span>{(latestVideo.likes || 0).toLocaleString()} likes</span>
              </div>
            )}
            {latestVideo.ctr !== undefined && (
              <div className="flex items-center gap-1">
                <BarChart3 size={14} />
                <span>{(latestVideo.ctr || 0).toFixed(1)}% CTR</span>
              </div>
            )}
            <div className="flex items-center gap-1">
              <Clock size={14} />
              <span>{formatTimeAgo(latestVideo.published_at)}</span>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => window.open(latestVideo.youtube_url || latestVideo.url, '_blank')}
          >
            <ExternalLink size={14} className="mr-2" />
            Watch on YouTube
          </Button>
        </div>
      </div>
    </Card>
  );
}

