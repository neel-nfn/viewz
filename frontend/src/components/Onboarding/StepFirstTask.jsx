import { useState } from 'react';
import { apiPost } from '../../services/apiClient';

export default function StepFirstTask({ persona, onComplete, onSkip }) {
  const [creating, setCreating] = useState(false);
  const [template, setTemplate] = useState(null);

  const templates = [
    { id: 'tutorial', title: 'How-to Tutorial', desc: 'Create a step-by-step guide' },
    { id: 'review', title: 'Product Review', desc: 'Review and analyze a product' },
    { id: 'vlog', title: 'Vlog Entry', desc: 'Share your daily experiences' }
  ];

  async function createFromTemplate(templateId) {
    setTemplate(templateId);
    setCreating(true);
    try {
      // Create a task from template
      await apiPost('/tasks/from-idea', {
        research_idea_id: null,
        channel_id: 'mock-channel',
        title: templates.find(t => t.id === templateId)?.title || 'New Task',
        stage: 'research'
      });
      setTimeout(() => {
        onComplete();
      }, 1000);
    } catch (e) {
      alert(`Error creating task: ${e.message}`);
      setCreating(false);
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Create Your First Task</h2>
      <p className="opacity-70">Choose a template to get started, or skip to explore on your own.</p>
      
      <div className="grid gap-3 mt-6">
        {templates.map((t) => (
          <button
            key={t.id}
            className={`card bg-base-100 p-4 text-left border-2 ${
              template === t.id ? 'border-primary' : 'border-base-300'
            }`}
            onClick={() => createFromTemplate(t.id)}
            disabled={creating}
          >
            <div className="font-semibold">{t.title}</div>
            <div className="text-sm opacity-60">{t.desc}</div>
          </button>
        ))}
      </div>
      
      {creating && (
        <div className="alert alert-info">
          <span>Creating your first task...</span>
        </div>
      )}
      
      <div className="flex gap-2 mt-6">
        <button
          className="btn btn-primary flex-1"
          onClick={onComplete}
          disabled={!template && !creating}
        >
          {creating ? 'Creating...' : 'Complete Setup'}
        </button>
        <button className="btn btn-ghost" onClick={onSkip} disabled={creating}>
          Skip
        </button>
      </div>
    </div>
  );
}

