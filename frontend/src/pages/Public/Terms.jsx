import { useEffect, useState } from 'react';

export default function Terms() {
  const [content, setContent] = useState(null);

  useEffect(() => {
    // Try to load from docs/beta/TERMS_DRAFT.md
    fetch('/docs/beta/TERMS_DRAFT.md')
      .then(r => r.ok ? r.text() : null)
      .then(text => {
        if (text) {
          // Simple markdown to HTML conversion (basic)
          setContent(<div className="prose max-w-none" dangerouslySetInnerHTML={{__html: text.replace(/\n/g, '<br/>')}} />);
        } else {
          setContent(<DefaultContent />);
        }
      })
      .catch(() => setContent(<DefaultContent />));
  }, []);

  function DefaultContent() {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">Terms of Service</h1>
        <p className="text-sm opacity-70">Last updated: {new Date().toLocaleDateString()}</p>
        <div className="space-y-3">
          <section>
            <h2 className="text-xl font-semibold">1. Acceptance of Terms</h2>
            <p>By accessing and using Viewz, you accept and agree to be bound by these Terms of Service.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold">2. Use License</h2>
            <p>During beta, Viewz is provided "as-is" for evaluation. Features may change without notice.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold">3. User Responsibilities</h2>
            <p>You are responsible for maintaining the confidentiality of your account and for all activities under your account.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold">4. Beta Disclaimer</h2>
            <p>This is beta software. Do not upload sensitive data. Features may change or be discontinued.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold">5. Intellectual Property</h2>
            <p>All trademarks and content belong to their respective owners.</p>
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

