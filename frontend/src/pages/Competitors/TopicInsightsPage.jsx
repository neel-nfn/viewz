import { useState, useEffect } from 'react';
import { listTopicIdeas, updateTopicIdeaStatus, deleteTopicIdea } from '../../services/competitorService';
import PageHeader from '../../components/primitives/PageHeader';
import Card from '../../components/primitives/Card';
import Button from '../../components/primitives/Button';
import ChannelOverviewBar from '../../components/layout/ChannelOverviewBar';
import OutlierBadge from '../../components/OutlierBadge';
import { ExternalLink, Trash2, TrendingUp, Eye } from 'lucide-react';

export default function TopicInsightsPage() {
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);

  useEffect(() => {
    loadTopicIdeas();
  }, [statusFilter]);

  async function loadTopicIdeas() {
    try {
      setLoading(true);
      const data = await listTopicIdeas(statusFilter);
      setIdeas(data.ideas || []);
    } catch (err) {
      console.error('Error loading topic ideas:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleStatusChange(ideaId, newStatus) {
    try {
      setUpdatingId(ideaId);
      await updateTopicIdeaStatus(ideaId, newStatus);
      loadTopicIdeas();
    } catch (err) {
      console.error('Error updating status:', err);
      alert('Failed to update status');
    } finally {
      setUpdatingId(null);
    }
  }

  async function handleDelete(ideaId) {
    if (!confirm('Are you sure you want to delete this topic idea?')) return;

    try {
      await deleteTopicIdea(ideaId);
      loadTopicIdeas();
    } catch (err) {
      console.error('Error deleting idea:', err);
      alert('Failed to delete topic idea');
    }
  }

  function getStatusColor(status) {
    switch (status) {
      case 'to_script':
        return 'bg-primary text-white';
      case 'in_progress':
        return 'bg-warning text-white';
      case 'ignore':
        return 'bg-surface text-textSecondary';
      default:
        return 'bg-accent text-primary';
    }
  }

  function getStatusLabel(status) {
    switch (status) {
      case 'to_script':
        return 'To Script';
      case 'in_progress':
        return 'In Progress';
      case 'ignore':
        return 'Ignore';
      default:
        return 'Saved';
    }
  }

  if (loading) {
    return (
      <div className="w-full">
        <PageHeader
          title="Topic Insights"
          subtitle="Competitor inspirations and saved content ideas"
        />
        <div className="max-w-[1240px] mx-auto px-6 md:px-8">
          <div className="text-center py-12 text-textSecondary">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Channel Overview Bar */}
      <ChannelOverviewBar />

      <PageHeader
        title="Topic Insights"
        subtitle="Competitor inspirations and saved content ideas"
        actions={
          <div className="flex gap-2 bg-surface border border-border rounded-lg p-1">
            <button
              onClick={() => setStatusFilter(null)}
              className={`px-3 py-1 rounded text-sm transition ${
                statusFilter === null
                  ? 'bg-primary text-white'
                  : 'text-textSecondary hover:text-textPrimary'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setStatusFilter('saved')}
              className={`px-3 py-1 rounded text-sm transition ${
                statusFilter === 'saved'
                  ? 'bg-primary text-white'
                  : 'text-textSecondary hover:text-textPrimary'
              }`}
            >
              Saved
            </button>
            <button
              onClick={() => setStatusFilter('to_script')}
              className={`px-3 py-1 rounded text-sm transition ${
                statusFilter === 'to_script'
                  ? 'bg-primary text-white'
                  : 'text-textSecondary hover:text-textPrimary'
              }`}
            >
              To Script
            </button>
            <button
              onClick={() => setStatusFilter('in_progress')}
              className={`px-3 py-1 rounded text-sm transition ${
                statusFilter === 'in_progress'
                  ? 'bg-primary text-white'
                  : 'text-textSecondary hover:text-textPrimary'
              }`}
            >
              In Progress
            </button>
          </div>
        }
      />

      <div className="max-w-[1240px] mx-auto px-6 md:px-8 py-6">
        {ideas.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <TrendingUp size={48} className="mx-auto mb-4 text-textSecondary" />
              <h3 className="text-lg font-semibold text-textPrimary mb-2">
                No Topic Ideas Yet
              </h3>
              <p className="text-textSecondary mb-6">
                Start saving high-performing videos from competitors as topic ideas.
              </p>
              <Button variant="primary" onClick={() => window.location.href = '/app/competitors'}>
                Go to Competitors
              </Button>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            {/* Section: Competitor Inspirations */}
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-textPrimary mb-4">
                Competitor Inspirations
              </h2>
              <div className="space-y-4">
                {ideas.map((idea) => (
                  <Card key={idea.id} className="hover:shadow-md transition-shadow">
                    <div className="flex gap-4">
                      {/* Thumbnail */}
                      <div className="flex-shrink-0">
                        <img
                          src={idea.thumbnail_url || 'https://via.placeholder.com/200x113?text=Video'}
                          alt={idea.video_title}
                          className="w-32 h-18 object-cover rounded"
                        />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-2">
                          <div className="flex-1">
                            <h3 className="font-semibold text-textPrimary line-clamp-2 mb-1">
                              {idea.video_title}
                            </h3>
                            <p className="text-sm text-textSecondary">
                              From: <span className="font-medium">{idea.competitor_name || 'Unknown'}</span>
                            </p>
                          </div>
                          {idea.outlier_score && (
                            <OutlierBadge score={idea.outlier_score} />
                          )}
                        </div>

                        {/* Stats */}
                        <div className="flex items-center gap-4 text-sm text-textSecondary mb-3">
                          <div className="flex items-center gap-1">
                            <Eye size={14} />
                            <span className="font-semibold text-textPrimary">
                              {idea.views.toLocaleString()}
                            </span>{' '}
                            views
                          </div>
                          <div>
                            Added: {new Date(idea.created_at).toLocaleDateString()}
                          </div>
                        </div>

                        {/* Notes */}
                        {idea.notes && (
                          <p className="text-sm text-textSecondary mb-3 italic">
                            Note: {idea.notes}
                          </p>
                        )}

                        {/* Actions */}
                        <div className="flex items-center gap-2 flex-wrap">
                          {/* Status Dropdown */}
                          <select
                            value={idea.status}
                            onChange={(e) => handleStatusChange(idea.id, e.target.value)}
                            disabled={updatingId === idea.id}
                            className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(idea.status)}`}
                          >
                            <option value="saved">Saved</option>
                            <option value="to_script">To Script</option>
                            <option value="in_progress">In Progress</option>
                            <option value="ignore">Ignore</option>
                          </select>

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(idea.video_url, '_blank')}
                          >
                            <ExternalLink size={14} className="mr-1" />
                            Watch
                          </Button>

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(idea.id)}
                            className="text-error hover:bg-error/10"
                          >
                            <Trash2 size={14} />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

