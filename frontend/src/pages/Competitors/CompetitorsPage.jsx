import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { listCompetitors, addCompetitor, deleteCompetitor } from '../../services/competitorService';
import Card from '../../components/primitives/Card';
import Button from '../../components/primitives/Button';
import ChannelOverviewBar from '../../components/layout/ChannelOverviewBar';
import { Plus, Trash2, Eye, Users, Lightbulb, TrendingUp, X, Youtube } from 'lucide-react';

export default function CompetitorsPage() {
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newChannelUrl, setNewChannelUrl] = useState('');
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadCompetitors();
  }, []);

  async function loadCompetitors() {
    try {
      setLoading(true);
      setError(null);
      const data = await listCompetitors();
      setCompetitors(data.competitors || []);
    } catch (err) {
      console.error('Error loading competitors:', err);
      const errorDetail = err.response?.data?.detail || err.response?.data?.error || err.message;
      const errorMsg = typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail);
      setError(errorMsg || 'Failed to load competitors. Please check your database connection.');
      // Don't block the UI - just show empty state
      setCompetitors([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleAddCompetitor() {
    if (!newChannelUrl.trim()) return;

    try {
      setAdding(true);
      setError(null);
      await addCompetitor(newChannelUrl);
      setNewChannelUrl('');
      setShowAddModal(false);
      await loadCompetitors();
    } catch (err) {
      console.error('Error adding competitor:', err);
      const errorDetail = err.response?.data?.detail || err.response?.data?.error || err.message;
      const errorMsg = typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail);
      const finalError = errorMsg || 'Failed to add competitor. Please check your database connection.';
      setError(finalError);
      alert(finalError);
    } finally {
      setAdding(false);
    }
  }

  async function handleDelete(competitorId) {
    if (!confirm('Are you sure you want to remove this competitor?')) return;

    try {
      await deleteCompetitor(competitorId);
      loadCompetitors();
    } catch (err) {
      console.error('Error deleting competitor:', err);
      alert(err.response?.data?.detail || 'Failed to delete competitor');
    }
  }

  function handleViewVideos(competitorId) {
    navigate(`/app/competitors/${competitorId}/videos`);
  }

  function openAddModal() {
    setNewChannelUrl('');
    setError(null);
    setShowAddModal(true);
  }

  if (loading) {
    return (
      <div className="w-full min-h-screen bg-background">
        {/* Header */}
        <div className="bg-surface border-b border-border">
          <div className="max-w-[1400px] mx-auto px-6 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-textPrimary mb-2">Competitors</h1>
                <p className="text-textSecondary">Track competitor channels and discover winning content ideas</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Loading State */}
        <div className="max-w-[1400px] mx-auto px-6 py-12">
          <div className="flex items-center justify-center gap-3 text-textSecondary">
            <div className="loading loading-spinner loading-md"></div>
            <span>Loading competitors...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-background">
      {/* Channel Overview Bar */}
      <ChannelOverviewBar />

      {/* Header */}
      <div className="bg-surface border-b border-border">
        <div className="max-w-[1400px] mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-textPrimary mb-2">Competitors</h1>
              <p className="text-textSecondary">Track competitor channels and discover winning content ideas</p>
            </div>
            <div className="flex gap-3">
              <Button variant="secondary" onClick={() => navigate('/app/topic-insights')}>
                <Lightbulb size={18} className="mr-2" />
                Saved Ideas
              </Button>
              <Button variant="primary" onClick={openAddModal}>
                <Plus size={18} className="mr-2" />
                Add Competitor
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="max-w-[1400px] mx-auto px-6 pt-6">
          <div className="alert alert-warning bg-warning/10 border-warning/30 rounded-lg">
            <div className="flex items-center justify-between w-full">
              <span className="text-textPrimary">{error}</span>
              <button onClick={() => setError(null)} className="btn btn-ghost btn-sm">
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="max-w-[1400px] mx-auto px-6 py-8">
        {competitors.length === 0 ? (
          /* Empty State */
          <div className="flex items-center justify-center min-h-[500px]">
            <div className="text-center max-w-md">
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-primary/10 mb-6">
                <Users size={48} className="text-primary" />
              </div>
              <h2 className="text-2xl font-bold text-textPrimary mb-3">
                Start Tracking Competitors
              </h2>
              <p className="text-textSecondary mb-8 text-lg">
                Add competitor YouTube channels to discover their top-performing videos and generate winning content ideas for your own channel.
              </p>
              <div className="flex flex-col gap-4">
                <Button variant="primary" size="lg" onClick={openAddModal} className="w-full">
                  <Plus size={20} className="mr-2" />
                  Add Your First Competitor
                </Button>
                <div className="flex items-center gap-6 text-sm text-textSecondary justify-center">
                  <div className="flex items-center gap-2">
                    <TrendingUp size={16} className="text-success" />
                    <span>Track Performance</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Lightbulb size={16} className="text-warning" />
                    <span>Discover Ideas</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Eye size={16} className="text-info" />
                    <span>Analyze Outliers</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Grid of Competitors */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {competitors.map((competitor) => (
              <div 
                key={competitor.id} 
                className="group bg-surface border border-border rounded-xl p-6 hover:shadow-lg hover:border-primary/50 transition-all duration-200"
              >
                {/* Channel Avatar & Info */}
                <div className="flex items-start gap-4 mb-4">
                  {competitor.channel_avatar_url ? (
                    <img
                      src={competitor.channel_avatar_url}
                      alt={competitor.channel_name}
                      className="w-16 h-16 rounded-full border-2 border-border"
                    />
                  ) : (
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center border-2 border-border">
                      <Youtube size={28} className="text-primary" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-textPrimary text-lg truncate group-hover:text-primary transition-colors">
                      {competitor.channel_name || 'Unknown Channel'}
                    </h3>
                    <p className="text-xs text-textSecondary truncate mt-1">
                      {competitor.youtube_channel_id}
                    </p>
                  </div>
                </div>

                {/* Stats */}
                {(competitor.subscriber_count > 0 || competitor.video_count > 0) && (
                  <div className="grid grid-cols-2 gap-3 mb-4 p-3 bg-background rounded-lg">
                    {competitor.subscriber_count > 0 && (
                      <div>
                        <div className="text-xs text-textSecondary mb-1">Subscribers</div>
                        <div className="text-lg font-bold text-textPrimary">
                          {(competitor.subscriber_count / 1000).toFixed(1)}K
                        </div>
                      </div>
                    )}
                    {competitor.video_count > 0 && (
                      <div>
                        <div className="text-xs text-textSecondary mb-1">Videos</div>
                        <div className="text-lg font-bold text-textPrimary">
                          {competitor.video_count}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Last Refreshed */}
                {competitor.last_refreshed_at && (
                  <p className="text-xs text-textSecondary mb-4 flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-success"></span>
                    Updated {new Date(competitor.last_refreshed_at).toLocaleDateString()}
                  </p>
                )}

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleViewVideos(competitor.id)}
                    className="flex-1"
                  >
                    <Eye size={16} className="mr-2" />
                    View Videos
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(competitor.id)}
                    className="text-error hover:bg-error/10 hover:text-error"
                  >
                    <Trash2 size={16} />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Competitor Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-2xl shadow-2xl max-w-md w-full border border-border">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-border">
              <div>
                <h3 className="text-xl font-bold text-textPrimary">Add Competitor</h3>
                <p className="text-sm text-textSecondary mt-1">
                  Track a YouTube channel's performance
                </p>
              </div>
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setNewChannelUrl('');
                  setError(null);
                }}
                className="btn btn-ghost btn-sm btn-circle"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6">
              <label className="block text-sm font-medium text-textPrimary mb-2">
                YouTube Channel URL or ID
              </label>
              <div className="relative">
                <input
                  type="text"
                  className="input input-bordered w-full pr-10 bg-background text-textPrimary placeholder-textSecondary"
                  placeholder="@MrBeast or UCX6OQ3DkcsbYNE6H8uQQuVA"
                  value={newChannelUrl}
                  onChange={(e) => {
                    setNewChannelUrl(e.target.value);
                    setError(null);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && newChannelUrl.trim() && !adding) {
                      handleAddCompetitor();
                    }
                  }}
                  autoFocus
                />
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  <Youtube size={20} className="text-textSecondary" />
                </div>
              </div>
              <p className="text-xs text-textSecondary mt-2">
                Paste a channel URL (youtube.com/@username) or channel ID (starts with UC)
              </p>
            </div>

            {/* Modal Footer */}
            <div className="flex gap-3 p-6 border-t border-border">
              <Button
                variant="ghost"
                onClick={() => {
                  setShowAddModal(false);
                  setNewChannelUrl('');
                  setError(null);
                }}
                className="flex-1"
                disabled={adding}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleAddCompetitor}
                className="flex-1"
                disabled={!newChannelUrl.trim() || adding}
              >
                {adding ? (
                  <>
                    <span className="loading loading-spinner loading-sm mr-2"></span>
                    Adding...
                  </>
                ) : (
                  <>
                    <Plus size={16} className="mr-2" />
                    Add Competitor
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
