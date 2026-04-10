import React, { useState, useEffect } from "react";
import { FileText, Image, Calendar, BarChart3, Sparkles, PlayCircle, TrendingUp } from "lucide-react";
import DashboardActionCard from "../components/dashboard/DashboardActionCard";
import DashboardSidebarCard from "../components/dashboard/DashboardSidebarCard";
import DashboardTextArea from "../components/dashboard/DashboardTextArea";
import DashboardStatCard from "../components/dashboard/DashboardStatCard";
import { getChannelSnapshot, getKeywords, getTasksToday, getRecommendations } from "../services/analyticsService";

export default function DashboardToday() {
  const [channelSnapshot, setChannelSnapshot] = useState(null);
  const [keywordData, setKeywordData] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [keywordQuery, setKeywordQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [dataSource, setDataSource] = useState({ source: 'demo', error: null });

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function loadDashboardData() {
    setLoading(true);
    try {
      const [snapshot, tasksData, recs] = await Promise.all([
        getChannelSnapshot(),
        getTasksToday(),
        getRecommendations()
      ]);
      
      setChannelSnapshot(snapshot);
      setTasks(Array.isArray(tasksData) ? tasksData : []);
      setRecommendations(Array.isArray(recs) ? recs : []);
      setDataSource({ source: 'live', error: null });
    } catch (e) {
      console.error("Failed to load dashboard data:", e);
      setDataSource({ source: 'error', error: e.message });
      // Fallback to demo data
      setChannelSnapshot({ views_7d: 12400, avg_ctr: 4.8, channel_name: "Demo Channel", last_sync_at: null });
      setTasks([
        { id: "t1", title: "Review AI draft for 'F1 Off-Season Drama'", status: "pending" },
        { id: "t2", title: "Generate thumbnail concepts", status: "in_progress" }
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleKeywordSearch() {
    if (!keywordQuery.trim()) return;
    try {
      const data = await getKeywords(keywordQuery);
      setKeywordData(data);
    } catch (e) {
      console.error("Failed to fetch keywords:", e);
      // Fallback to mock data
      setKeywordData({
        term: keywordQuery,
        reach_score: 75,
        competition_level: "medium",
        suggested_length: 90
      });
    }
  }

  const displaySnapshot = channelSnapshot || { views_7d: 0, avg_ctr: 0, channel_name: "Loading...", last_sync_at: null };
  const displayKeyword = keywordData || { reach_score: 87, competition_level: "Low", suggested_length: "8–12 min" };
  const isDemo = dataSource.source === 'demo' || dataSource.source === 'error';

  return (
    <div className="min-h-screen bg-[#0f1118] text-white">
      <div className="mx-auto max-w-[1240px] px-6 md:px-8 py-8">
        <div className="flex items-center justify-between mb-5">
          <h1 className="text-2xl font-semibold tracking-tight">Today</h1>
          {isDemo && (
            <span className="badge badge-warning">Demo Mode</span>
          )}
          {dataSource.source === 'live' && (
            <span className="badge badge-success">Live Data</span>
          )}
        </div>
        <div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-6 items-start">
          <div className="flex flex-col gap-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <DashboardActionCard title="Create Script" subtitle="AI draft" icon={FileText} href="/ai/script" color="teal" />
              <DashboardActionCard title="Generate Thumbnail" subtitle="Text → Image" icon={Image} href="/ai/thumbnail" color="teal" />
              <DashboardActionCard title="Plan Posts" subtitle="Calendar" icon={Calendar} href="/workflow/calendar" color="teal" />
              <DashboardActionCard title="Analyze Channel" subtitle="Overview" icon={BarChart3} href="/app/analytics" color="teal" />
            </div>

            <DashboardTextArea
              title="Start from your idea"
              placeholder="Describe your video idea in a natural way..."
              action={<a href="/ai/script" className="rounded-xl bg-teal-600 hover:bg-teal-700 px-4 py-2 text-sm font-medium">Draft with AI</a>}
            />

            <div className="rounded-2xl border border-white/5 bg-[#1d212e] p-5 shadow-[0_10px_30px_rgba(0,0,0,0.35)]">
              <div className="flex items-center justify-between mb-3">
                <div className="text-white/90 font-semibold">Topic Explorer</div>
                <a href="/analytics/topics" className="text-sm text-teal-400 hover:text-teal-300">Manage</a>
              </div>
              <div className="flex gap-2">
                <input
                  placeholder="Search a keyword"
                  value={keywordQuery}
                  onChange={e => setKeywordQuery(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && handleKeywordSearch()}
                  className="flex-1 rounded-xl bg-[#0f1118] border border-white/10 px-4 py-3 text-white/85 placeholder-white/40 outline-none focus:ring-2 focus:ring-teal-600/40"
                />
                <button
                  onClick={handleKeywordSearch}
                  className="rounded-xl bg-teal-600 hover:bg-teal-700 px-4 py-2"
                >
                  Search
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
                <DashboardStatCard 
                  label="Potential Reach" 
                  value={typeof displayKeyword.reach_score === 'number' ? `${displayKeyword.reach_score}/100` : displayKeyword.reach_score || "87/100"} 
                  trend="Very High" 
                />
                <DashboardStatCard 
                  label="Competition" 
                  value={displayKeyword.competition_level || "Low"} 
                  trend="Good to target" 
                />
                <DashboardStatCard 
                  label="Suggested Length" 
                  value={typeof displayKeyword.suggested_length === 'number' ? `${displayKeyword.suggested_length} min` : displayKeyword.suggested_length || "8–12 min"} 
                  trend="Based on top results" 
                />
              </div>
            </div>

            <div className="rounded-2xl border border-white/5 bg-[#1d212e] p-5 shadow-[0_10px_30px_rgba(0,0,0,0.35)]">
              <div className="flex items-center justify-between mb-3">
                <div className="text-white/90 font-semibold">Daily Tasks</div>
                <div className="text-white/50 text-sm">
                  {tasks.filter(t => t.status === 'completed').length}/{tasks.length}
                </div>
              </div>
              {loading ? (
                <div className="text-white/50 text-sm">Loading tasks...</div>
              ) : tasks.length === 0 ? (
                <div className="text-white/50 text-sm">No tasks for today</div>
              ) : (
                <div className="space-y-3">
                  {tasks.map(task => (
                    <div key={task.id} className="flex items-center justify-between rounded-xl bg-[#0f1118] border border-white/10 px-4 py-3">
                      <div className="flex items-center gap-3">
                        <Sparkles className="h-4 w-4 text-teal-400" />
                        <div className="text-white/85">{task.title}</div>
                      </div>
                      <span className={`badge badge-xs ${task.status === 'completed' ? 'badge-success' : task.status === 'in_progress' ? 'badge-warning' : 'badge-info'}`}>
                        {task.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-col gap-4">
            <DashboardSidebarCard title="Get Started">
              <div className="space-y-3">
                <a href="/guide/intro" className="flex items-center gap-3 rounded-xl bg-[#0f1118] border border-white/10 px-4 py-3 hover:border-white/20 transition">
                  <PlayCircle className="h-4 w-4 text-white/70" />
                  <div className="text-white/85 text-sm">Watch quick intro</div>
                </a>
                <a href="/app/settings/channels" className="flex items-center gap-3 rounded-xl bg-[#0f1118] border border-white/10 px-4 py-3 hover:border-white/20 transition">
                  <TrendingUp className="h-4 w-4 text-white/70" />
                  <div className="text-white/85 text-sm">Connect your channel</div>
                </a>
              </div>
            </DashboardSidebarCard>

            <DashboardSidebarCard 
              title="Channel Snapshot" 
              footer={
                <a href="/app/analytics" className="inline-flex items-center rounded-xl bg-white/10 px-4 py-2 text-sm hover:bg-white/15 transition">View More</a>
              }
            >
              {loading ? (
                <div className="text-white/50 text-sm">Loading...</div>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <DashboardStatCard label="7-day Views" value={`${(displaySnapshot.views_7d / 1000).toFixed(1)}k`} />
                    <DashboardStatCard label="Avg. CTR" value={`${displaySnapshot.avg_ctr}%`} />
                  </div>
                  {displaySnapshot.last_sync_at && (
                    <div className="mt-3 text-xs text-white/50">
                      Last sync: {new Date(displaySnapshot.last_sync_at).toLocaleString()}
                    </div>
                  )}
                </>
              )}
            </DashboardSidebarCard>

            <DashboardSidebarCard title="AI Recommendations">
              {loading ? (
                <div className="text-white/50 text-sm">Loading...</div>
              ) : recommendations.length === 0 ? (
                <div className="text-white/50 text-sm">No recommendations</div>
              ) : (
                <div className="space-y-3">
                  {recommendations.map(rec => (
                    <div key={rec.id} className="rounded-xl bg-[#0f1118] border border-white/10 px-4 py-3 text-sm text-white/80">
                      {rec.text}
                      {rec.action_uri && (
                        <a href={rec.action_uri} className="block mt-2 text-teal-400 hover:text-teal-300 text-xs">
                          View →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </DashboardSidebarCard>
          </div>
        </div>
      </div>
    </div>
  );
}
