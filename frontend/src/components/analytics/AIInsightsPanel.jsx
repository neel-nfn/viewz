import { useState, useEffect } from "react";

export default function AIInsightsPanel({ initialInsights, loading: initialLoading = false, onGenerate }) {
  const [insights, setInsights] = useState(initialInsights);
  const [generating, setGenerating] = useState(false);
  
  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await onGenerate();
      // Insights will be updated via parent component
    } catch (error) {
      console.error("Error generating insights:", error);
    } finally {
      setGenerating(false);
    }
  };
  
  // Update insights when parent updates them
  useEffect(() => {
    if (initialInsights) {
      setInsights(initialInsights);
    }
  }, [initialInsights]);
  
  const insightsList = insights?.insights || [];
  const isMock = insights?.mock === true;
  const generatedAt = insights?.generated_at;
  
  return (
    <div className="card bg-base-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold">AI Insights</h3>
        <button
          className="btn btn-sm btn-primary"
          onClick={handleGenerate}
          disabled={generating}
        >
          {generating ? (
            <>
              <span className="loading loading-spinner loading-xs"></span>
              Generating...
            </>
          ) : (
            <>
              <span>✨</span>
              Generate Insights
            </>
          )}
        </button>
      </div>
      
      <div className="alert alert-info alert-sm mb-3">
        <span className="text-xs">✨ This will use AI credit</span>
      </div>
      
      {isMock && insightsList.length === 0 && (
        <div className="alert alert-warning alert-sm mb-3">
          <span className="text-xs">Connect YouTube for AI-powered insights</span>
        </div>
      )}
      
      {insightsList.length > 0 ? (
        <>
          <ul className="space-y-2 mb-3">
            {insightsList.map((insight, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="text-primary mt-1">•</span>
                <span>{insight}</span>
              </li>
            ))}
          </ul>
          
          {generatedAt && (
            <div className="text-xs text-base-content/50">
              Generated {new Date(generatedAt).toLocaleString()}
            </div>
          )}
        </>
      ) : (
        <p className="text-sm text-base-content/70">
          Click "Generate Insights" to get AI-powered analysis of your channel performance.
        </p>
      )}
    </div>
  );
}
