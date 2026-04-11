import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCompetitorVideos, saveTopicIdea } from '../../services/competitorService';
import PageHeader from '../../components/primitives/PageHeader';
import Card from '../../components/primitives/Card';
import Button from '../../components/primitives/Button';
import OutlierBadge from '../../components/OutlierBadge';
import { ArrowLeft, Bookmark, ExternalLink, TrendingUp, Eye, ThumbsUp, MessageCircle } from 'lucide-react';

export default function CompetitorVideosPage() {
  const { competitorId } = useParams();
  const navigate = useNavigate();
  const [videos, setVideos] = useState([]);
  const [channelName, setChannelName] = useState('');
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [savingVideoId, setSavingVideoId] = useState(null);
  const [savedVideoIds, setSavedVideoIds] = useState(new Set());

  useEffect(() => {
    loadVideos();
  }, [competitorId, days]);

  async function loadVideos() {
    try {
      setLoading(true);
      const data = await getCompetitorVideos(competitorId, days);
      setVideos(data.videos || []);
      setChannelName(data.channel_name || 'Competitor Channel');
    } catch (err) {
      console.error('Error loading videos:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveTopicIdea(video) {
    if (savedVideoIds.has(video.video_id)) {
      return; // Already saved
    }

    try {
      setSavingVideoId(video.video_id);
      await saveTopicIdea({
        competitor_id: competitorId,
        video_id: video.video_id,
        video_title: video.video_title,
        video_url: video.video_url,
        thumbnail_url: video.thumbnail_url,
        views: video.views,
        likes: video.likes,
        comments: video.comments,
        published_at: video.published_at,
        outlier_score: video.outlier_score,
        performance_indicator: video.performance_indicator,
      });
      setSavedVideoIds(new Set([...savedVideoIds, video.video_id]));
    } catch (err) {
      console.error('Error saving topic idea:', err);
      if (err.response?.status === 400) {
        // Already saved
        setSavedVideoIds(new Set([...savedVideoIds, video.video_id]));
      } else {
        alert(err.response?.data?.detail || 'Failed to save topic idea');
      }
    } finally {
      setSavingVideoId(null);
    }
  }

  function getPerformanceBadge(indicator) {
    switch (indicator) {
      case 'outlier':
        return <span className="text-error flex items-center gap-1"><TrendingUp size={16} /> Outlier</span>;
      case 'above_average':
        return <span className="text-warning flex items-center gap-1">📈 Above Average</span>;
      default:
        return <span className="text-textSecondary flex items-center gap-1">⚪ Normal</span>;
    }
  }

  if (loading) {
    return (
      <div className="w-full">
        <PageHeader
          title="Loading..."
          subtitle="Fetching top videos"
        />
        <div className="max-w-[1240px] mx-auto px-6 md:px-8">
          <div className="text-center py-12 text-textSecondary">Loading videos...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <PageHeader
        title={channelName}
        subtitle="Top-performing videos"
        actions={
          <div className="flex items-center gap-3">
            {/* Time range selector */}
            <div className="flex gap-2 bg-surface border border-border rounded-lg p-1">
              {[7, 30, 90].map((d) => (
                <button
                  key={d}
                  onClick={() => setDays(d)}
                  className={`px-3 py-1 rounded text-sm transition ${
                    days === d
                      ? 'bg-primary text-white'
                      : 'text-textSecondary hover:text-textPrimary'
                  }`}
                >
                  {d}d
                </button>
              ))}
            </div>
            <Button variant="ghost" onClick={() => navigate('/app/competitors')}>
              <ArrowLeft size={16} className="mr-2" />
              Back
            </Button>
          </div>
        }
      />

      <div className="max-w-[1240px] mx-auto px-6 md:px-8">
        {videos.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <p className="text-textSecondary">No videos found for this time range.</p>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            {videos.map((video) => (
              <Card key={video.video_id} className="hover:shadow-md transition-shadow">
                <div className="flex gap-4">
                  {/* Thumbnail */}
                  <div className="flex-shrink-0">
                    <img
                      src={video.thumbnail_url || 'https://via.placeholder.com/320x180?text=Video'}
                      alt={video.video_title}
                      className="w-48 h-27 object-cover rounded"
                    />
                  </div>

                  {/* Video Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <h3 className="font-semibold text-textPrimary text-lg line-clamp-2">
                        {video.video_title}
                      </h3>
                      {video.outlier_score && (
                        <OutlierBadge score={video.outlier_score} />
                      )}
                    </div>

                    {/* Performance Badge */}
                    <div className="mb-3">
                      {getPerformanceBadge(video.performance_indicator)}
                    </div>

                    {/* Stats */}
                    <div className="flex flex-wrap gap-4 text-sm text-textSecondary mb-4">
                      <div className="flex items-center gap-1">
                        <Eye size={16} />
                        <span className="font-semibold text-textPrimary">
                          {video.views.toLocaleString()}
                        </span>{' '}
                        views
                      </div>
                      {video.likes && (
                        <div className="flex items-center gap-1">
                          <ThumbsUp size={16} />
                          <span className="font-semibold text-textPrimary">
                            {video.likes.toLocaleString()}
                          </span>{' '}
                          likes
                        </div>
                      )}
                      {video.comments && (
                        <div className="flex items-center gap-1">
                          <MessageCircle size={16} />
                          <span className="font-semibold text-textPrimary">
                            {video.comments.toLocaleString()}
                          </span>{' '}
                          comments
                        </div>
                      )}
                      {video.published_at && (
                        <div>
                          Published: {new Date(video.published_at).toLocaleDateString()}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleSaveTopicIdea(video)}
                        disabled={savingVideoId === video.video_id || savedVideoIds.has(video.video_id)}
                      >
                        <Bookmark size={16} className="mr-2" />
                        {savedVideoIds.has(video.video_id)
                          ? 'Saved'
                          : savingVideoId === video.video_id
                          ? 'Saving...'
                          : 'Save as Topic Idea'}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(video.video_url, '_blank')}
                      >
                        <ExternalLink size={16} className="mr-2" />
                        Watch on YouTube
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

