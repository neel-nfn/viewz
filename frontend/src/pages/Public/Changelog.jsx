import { useEffect, useState } from 'react';

export default function Changelog() {
  const [content, setContent] = useState(null);

  useEffect(() => {
    fetch('/docs/beta/CHANGELOG.md')
      .then(r => r.ok ? r.text() : null)
      .then(text => {
        if (text) {
          // Simple markdown parsing
          const lines = text.split('\n');
          const parsed = lines.map((line, i) => {
            if (line.startsWith('#')) {
              const level = line.match(/^#+/)[0].length;
              const text = line.replace(/^#+\s*/, '');
              return <h2 key={i} className={`font-bold ${level === 1 ? 'text-2xl' : level === 2 ? 'text-xl' : 'text-lg'} mt-4 mb-2`}>{text}</h2>;
            } else if (line.startsWith('-') || line.startsWith('*')) {
              return <li key={i} className="ml-4">{line.substring(2)}</li>;
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
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">Changelog</h1>
        <div className="space-y-4">
          <section>
            <h2 className="text-xl font-semibold">v1.0.0-beta (Current)</h2>
            <ul className="list-disc ml-6 space-y-1">
              <li>Public release with AppSumo integration</li>
              <li>Onboarding wizard</li>
              <li>Support desk</li>
              <li>AI SEO Assistant</li>
              <li>Workflow & Team Operations</li>
            </ul>
          </section>
          <section>
            <h2 className="text-xl font-semibold">v0.7.0-beta</h2>
            <ul className="list-disc ml-6 space-y-1">
              <li>Topic Research & Outlier Engine</li>
              <li>Analytics v2 fields</li>
              <li>Chrome Extension MVP</li>
            </ul>
          </section>
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

