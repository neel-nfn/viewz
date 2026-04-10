import { useEffect, useState } from 'react';

export default function Roadmap(){
  const [content, setContent] = useState(null);

  useEffect(() => {
    fetch('/docs/beta/ROADMAP_PUBLIC.md')
      .then(r => r.ok ? r.text() : null)
      .then(text => {
        if (text) {
          const lines = text.split('\n');
          const parsed = lines.map((line, i) => {
            if (line.startsWith('#')) {
              const level = line.match(/^#+/)[0].length;
              const text = line.replace(/^#+\s*/, '');
              return <h2 key={i} className={`font-bold ${level === 1 ? 'text-2xl' : 'text-xl'} mt-6 mb-3`}>{text}</h2>;
            } else if (line.startsWith('-') || line.startsWith('*')) {
              return <li key={i} className="ml-4 mb-1">{line.substring(2)}</li>;
            } else if (line.trim()) {
              return <p key={i} className="mb-2">{line}</p>;
            }
            return null;
          }).filter(Boolean);
          setContent(<div className="space-y-2">{parsed}</div>);
        } else {
          setContent(<DefaultContent />);
        }
      })
      .catch(() => setContent(<DefaultContent />));
  }, []);

  function DefaultContent() {
    const DATA = {
      now: [
        "Kanban + Drawer + Analytics (done)",
        "Multi-user simulation + invites (done)",
        "AI Assist placeholder (done)"
      ],
      next: [
        "Basix REST provider hookup",
        "Channel templates (Checklists, brief prompts)",
        "Quick publish checklist"
      ],
      later: [
        "MCP provider (Basix as MCP server)",
        "AB testing for titles/thumbnails",
        "Team workload heatmap"
      ]
    };
    
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold">Public Roadmap</h1>
        {["now","next","later"].map(k=>(
          <section key={k}>
            <h2 className="text-lg font-semibold capitalize">{k}</h2>
            <ul className="list-disc pl-6 space-y-1">{DATA[k].map(i=><li key={i}>{i}</li>)}</ul>
          </section>
        ))}
        <div className="mt-6">
          <a href="/feedback" className="btn btn-sm">Suggest a feature</a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-100">
      <div className="max-w-4xl mx-auto p-6">
        {content || <DefaultContent />}
        <div className="mt-8 pt-8 border-t border-base-300">
          <a href="/" className="btn btn-sm">← Back to Home</a>
        </div>
      </div>
    </div>
  );
}

