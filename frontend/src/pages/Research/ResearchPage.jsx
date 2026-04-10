import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { scoreIdea } from "../../services/researchService";
import { apiPost } from "../../services/apiClient";
import OutlierBadge from "../../components/OutlierBadge";
import PageHeader from "../../components/primitives/PageHeader";
import Card from "../../components/primitives/Card";
import Button from "../../components/primitives/Button";

export default function ResearchPage({ orgId, channelId }) {
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [adding, setAdding] = useState(false);
  const navigate = useNavigate();
  
  async function onScore() {
    try {
      const data = await scoreIdea({ orgId, channelId, title, url });
      setResult(data);
    } catch (e) {
      console.error("Research score error:", e);
      alert(`Error: ${e.message || "Failed to score idea"}`);
    }
  }

  async function addToPipeline() {
    if (!result || !result.idea_id) {
      alert("Please score an idea first");
      return;
    }

    setAdding(true);
    try {
      const taskData = await apiPost("/api/v1/tasks/from-idea", {
        research_idea_id: result.idea_id,
        channel_id: channelId,
        title: title || "New Task",
        stage: "research"
      });
      navigate(`/app/workflow`);
    } catch (e) {
      console.error("Add to pipeline error:", e);
      alert(`Error: ${e.message || "Failed to add to pipeline"}`);
    } finally {
      setAdding(false);
    }
  }

  return (
    <div className="w-full">
      <PageHeader
        title="Research & Outliers"
        subtitle="Score research ideas and identify high-performing content opportunities"
        actions={
          <Button 
            variant="primary" 
            onClick={onScore}
            disabled={!title.trim()}
          >
            Score Idea
          </Button>
        }
      />
      
      <div className="max-w-[1240px] mx-auto px-6 md:px-8">

      <Card title="Idea Scoring" subtitle="Enter a title and optional URL to score">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-textPrimary mb-2">
              Idea Title *
            </label>
            <input
              className="input input-bordered w-full"
              placeholder="e.g., '10 Productivity Hacks That Changed My Life'"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-textPrimary mb-2">
              Source URL (optional)
            </label>
            <input
              className="input input-bordered w-full"
              placeholder="https://..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>

          <Button 
            variant="primary" 
            onClick={onScore}
            disabled={!title.trim()}
            className="w-full"
          >
            Score Idea
          </Button>
        </div>
      </Card>

      {result && (
        <Card title="Score Results" subtitle="Outlier analysis and pipeline actions" className="mt-6">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <OutlierBadge score={result.score} />
              <Button
                variant="primary"
                onClick={addToPipeline}
                disabled={adding}
              >
                {adding ? "Adding..." : "Add to Pipeline"}
              </Button>
            </div>

            <div className="bg-surface border border-border rounded-lg p-4">
              <h4 className="font-semibold text-textPrimary mb-2">Score Components</h4>
              <pre className="text-xs text-textSecondary overflow-auto">
                {JSON.stringify(result.components, null, 2)}
              </pre>
            </div>
          </div>
        </Card>
      )}
      </div>
    </div>
  );
}
