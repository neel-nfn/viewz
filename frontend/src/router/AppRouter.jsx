import { createBrowserRouter, Navigate } from "react-router-dom";
import ErrorBoundary from "../components/system/ErrorBoundary";
import AppShell from "../components/layout/AppShell";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import DashboardToday from "../pages/DashboardToday";
import WorkflowKanban from "../pages/WorkflowKanban";
import Settings from "../pages/Settings";
import TeamRoles from "../pages/Settings/TeamRoles";
import Channels from "../pages/Settings/Channels";
import Billing from "../pages/Settings/Billing";
import Integrations from "../pages/Settings/Integrations";
import FeedbackAdmin from "../pages/Settings/FeedbackAdmin";
import AnalyticsPage from "../pages/Analytics/AnalyticsPage";
import AnalyticsTopics from "../pages/Analytics/AnalyticsTopics";
import OptimizationFeed from "../pages/Dashboard/OptimizationFeed";
import { useAuth } from "../context/AuthContext";
import AcceptInvite from "../pages/Auth/AcceptInvite";
import AuthCallback from "../pages/Auth/Callback";
import AuthSuccess from "../pages/Auth/AuthSuccess";
import AuthFail from "../pages/Auth/AuthFail";
import NotFound from "../pages/Misc/NotFound";
import ScriptBreakdownPage from "../pages/Phase1/ScriptBreakdownPage";
import ApprovalQueuePage from "../pages/Phase1/ApprovalQueuePage";
import AssetValidationPanelPage from "../pages/Phase1/AssetValidationPanelPage";
import EditorInstructionsPage from "../pages/Phase1/EditorInstructionsPage";
import OperatorQueuePage from "../pages/Phase4/OperatorQueuePage";
import OperatorJobDetailPage from "../pages/Phase4/OperatorJobDetailPage";
import WorkerDashboardPage from "../pages/Phase4/WorkerDashboardPage";
import StorageObjectsPage from "../pages/Phase4/StorageObjectsPage";
import FilenameRulesPage from "../pages/Phase4/FilenameRulesPage";
import CompetitorsPage from "../pages/Competitors/CompetitorsPage";
import CompetitorVideosPage from "../pages/Competitors/CompetitorVideosPage";
import TopicInsightsPage from "../pages/Competitors/TopicInsightsPage";
import Landing from "../pages/Public/Landing";
import Roadmap from "../pages/Public/Roadmap";
import Terms from "../pages/Public/Terms";
import Privacy from "../pages/Public/Privacy";
import Changelog from "../pages/Public/Changelog";
import FAQ from "../pages/Public/FAQ";
import Support from "../pages/Public/Support";
import Pricing from "../pages/Public/Pricing";
import Wizard from "../pages/Onboarding/Wizard";

function Protected({ children }) {
  const { user, ready } = useAuth();
  // #region agent log
  fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AppRouter.jsx:38',message:'Protected component render',data:{ready,hasUser:!!user},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  // #endregion
  if (!ready) {
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AppRouter.jsx:41',message:'Protected: showing loading (ready=false)',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion
    return <div className="p-6">Loading…</div>;
  }
  if (!user) {
    // #region agent log
    fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AppRouter.jsx:45',message:'Protected: redirecting to login (no user)',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion
    return <Navigate to="/login" replace />;
  }
  // #region agent log
  fetch('http://127.0.0.1:7243/ingest/967e0ff5-1071-4c6c-958d-ca0e3611333c',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AppRouter.jsx:48',message:'Protected: rendering children (user exists)',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  // #endregion
  return children;
}

export const router = createBrowserRouter([
  { 
    path: "/",
    element: <ErrorBoundary><Landing /></ErrorBoundary>,
    errorElement: <ErrorBoundary><Landing /></ErrorBoundary>
  },
  { path: "/onboarding", element: <ErrorBoundary><Wizard /></ErrorBoundary> },
  { path: "/public/terms", element: <ErrorBoundary><Terms /></ErrorBoundary> },
  { path: "/terms", element: <ErrorBoundary><Terms /></ErrorBoundary> },
  { path: "/public/privacy", element: <ErrorBoundary><Privacy /></ErrorBoundary> },
  { path: "/privacy", element: <ErrorBoundary><Privacy /></ErrorBoundary> },
  { path: "/public/roadmap", element: <ErrorBoundary><Roadmap /></ErrorBoundary> },
  { path: "/roadmap", element: <ErrorBoundary><Roadmap /></ErrorBoundary> },
  { path: "/public/changelog", element: <ErrorBoundary><Changelog /></ErrorBoundary> },
  { path: "/public/faq", element: <ErrorBoundary><FAQ /></ErrorBoundary> },
  { path: "/public/support", element: <ErrorBoundary><Support /></ErrorBoundary> },
  { path: "/public/pricing", element: <ErrorBoundary><Pricing /></ErrorBoundary> },
  { path: "/login", element: <ErrorBoundary><Login /></ErrorBoundary> },
  { path: "/auth/callback", element: <ErrorBoundary><AuthCallback /></ErrorBoundary> },
  { path: "/auth/success", element: <ErrorBoundary><AuthSuccess /></ErrorBoundary> },
  { path: "/auth/fail", element: <ErrorBoundary><AuthFail /></ErrorBoundary> },
  { path: "/invite/accept/:token", element: <ErrorBoundary><AcceptInvite /></ErrorBoundary> },
  // Redirect routes without /app prefix to /app versions
  { path: "/analytics/topics", element: <ErrorBoundary><Navigate to="/app/analytics/topics" replace /></ErrorBoundary> },
  { path: "/settings/integrations", element: <ErrorBoundary><Navigate to="/app/settings/integrations" replace /></ErrorBoundary> },
  { path: "/tasks", element: <ErrorBoundary><Navigate to="/app/scripts" replace /></ErrorBoundary> },
  {
    path: "/app",
    element: <ErrorBoundary><Protected><AppShell /></Protected></ErrorBoundary>,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "dashboard-alt", element: <DashboardToday /> },
      { path: "workflow", element: <WorkflowKanban /> },
      { path: "analytics", element: <AnalyticsPage /> },
      { path: "analytics/topics", element: <AnalyticsTopics /> },
      { path: "tasks", element: <Navigate to="/app/scripts" replace /> },
      { path: "scripts", element: <ScriptBreakdownPage /> },
      { path: "research", element: <ApprovalQueuePage /> },
      { path: "assets", element: <Navigate to="/app/assets/validation" replace /> },
      { path: "assets/validation", element: <AssetValidationPanelPage /> },
      { path: "editor", element: <EditorInstructionsPage /> },
      { path: "operator", element: <OperatorQueuePage /> },
      { path: "operator/jobs/:jobId", element: <OperatorJobDetailPage /> },
      { path: "worker", element: <WorkerDashboardPage /> },
      { path: "storage", element: <StorageObjectsPage /> },
      { path: "filename-rules", element: <FilenameRulesPage /> },
      { path: "competitors", element: <CompetitorsPage /> },
      { path: "competitors/:competitorId/videos", element: <CompetitorVideosPage /> },
      { path: "topic-insights", element: <TopicInsightsPage /> },
      { path: "optimization", element: <OptimizationFeed /> },
      { 
        path: "settings", 
        element: <Settings />,
        children: [
          { index: true, element: <div></div> },
          { path: "channels", element: <Channels /> },
          { path: "billing", element: <Billing /> },
          { path: "team-roles", element: <TeamRoles /> },
          { path: "integrations", element: <Integrations /> },
          { path: "feedback", element: <FeedbackAdmin /> },
        ],
      },
      { path: "404", element: <NotFound /> },
      { path: "*", element: <NotFound /> }, // App-level 404 - show NotFound instead of redirecting
    ],
  },
  // Final global catch-all - show NotFound for truly unknown routes
  { path: "*", element: <ErrorBoundary><NotFound /></ErrorBoundary> },
]);
