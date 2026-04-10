import PageHeader from '../components/primitives/PageHeader';
import Card from '../components/primitives/Card';
import EmptyState from '../components/primitives/EmptyState';
import Button from '../components/primitives/Button';
import { Link } from 'react-router-dom';
import { BarChart3, Zap, Users, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  // Mock data - replace with actual API calls
  const stats = [
    { label: 'Active Channels', value: '3', icon: BarChart3, color: 'text-primary' },
    { label: 'Tasks This Week', value: '24', icon: Zap, color: 'text-accent' },
    { label: 'Team Members', value: '8', icon: Users, color: 'text-success' },
    { label: 'Overdue Tasks', value: '2', icon: AlertCircle, color: 'text-error' },
  ];

  const hasChannels = false; // Replace with actual check

  return (
    <div className="w-full">
      <PageHeader
        title="Dashboard"
        subtitle="Overview of your YouTube production pipeline"
        actions={
          <>
            <Button variant="ghost" onClick={() => console.log('Analytics')}>
              View Analytics
            </Button>
            <Button variant="ghost" onClick={() => window.dispatchEvent(new Event('viewz:toggle-ai'))}>
              AI Assist
            </Button>
            <Button variant="primary" onClick={() => console.log('New task')}>
              New Task
            </Button>
          </>
        }
      />

      <div className="max-w-[1240px] mx-auto px-6 md:px-8">
        {hasChannels ? (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            {stats.map((stat, i) => {
              const Icon = stat.icon;
              return (
                <Card key={i} className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-textSecondary mb-1">{stat.label}</p>
                      <p className="text-2xl font-bold text-textPrimary">{stat.value}</p>
                    </div>
                    <Icon className={`${stat.color} shrink-0`} size={24} />
                  </div>
                </Card>
              );
            })}
          </div>

          {/* Channel Grid */}
          <Card title="Your Channels" subtitle="Connected YouTube channels">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Channel cards would go here */}
              <div className="text-sm text-textSecondary">Channel grid appears after connection</div>
            </div>
          </Card>

          {/* Recent Activity */}
          <Card title="Recent Activity" subtitle="Latest updates across your channels" className="mt-6">
            <EmptyState
              icon={AlertCircle}
              title="No recent activity"
              description="Activity will appear here as you work on your content pipeline"
            />
          </Card>
        </>
      ) : (
        <Card>
          <EmptyState
            icon={BarChart3}
            title="No channels connected"
            description="Connect your first YouTube channel to get started with your production pipeline"
            action={{
              label: 'Connect Channel',
              variant: 'primary',
              onClick: () => window.location.href = '/app/settings/channels',
            }}
          />
        </Card>
          )}
      </div>
    </div>
  );
}
