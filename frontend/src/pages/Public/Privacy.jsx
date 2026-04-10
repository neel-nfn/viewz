import { useEffect, useState } from 'react';

export default function Privacy() {
  const [content, setContent] = useState(null);

  useEffect(() => {
    fetch('/docs/beta/PRIVACY_DRAFT.md')
      .then(r => r.ok ? r.text() : null)
      .then(text => {
        if (text) {
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
        <h1 className="text-3xl font-bold">Privacy Policy</h1>
        <p className="text-sm opacity-70">Last updated: {new Date().toLocaleDateString()}</p>
        <div className="space-y-3">
          <section>
            <h2 className="text-xl font-semibold">1. Data Collection</h2>
            <p>Viewz collects data necessary to provide the service, including YouTube channel information and usage analytics.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold">2. Data Storage</h2>
            <p>Data is stored securely using Supabase. We do not sell your data to third parties.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold">3. Beta Mode</h2>
            <p>In demo mode, data is stored locally in your browser. No personal data is transmitted.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold">4. Cookies</h2>
            <p>We use essential cookies for authentication and session management.</p>
          </section>
          <section>
            <h2 className="text-xl font-semibold">5. Your Rights</h2>
            <p>You can request access, correction, or deletion of your data by contacting support.</p>
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
