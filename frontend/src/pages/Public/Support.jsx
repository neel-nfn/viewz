import { useState } from 'react';
import { apiPost } from '../../services/apiClient';

export default function Support() {
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [ticketId, setTicketId] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email.trim() || !subject.trim() || !body.trim()) {
      alert('Please fill in all fields');
      return;
    }

    setSubmitting(true);
    try {
      const result = await apiPost('/api/v1/support/ticket', {
        email: email.trim(),
        subject: subject.trim(),
        body: body.trim()
      });
      setTicketId(result.ticket_id);
      setSubmitted(true);
      setEmail('');
      setSubject('');
      setBody('');
    } catch (e) {
      alert(`Error submitting ticket: ${e.message}`);
    } finally {
      setSubmitting(false);
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-base-100">
        <div className="max-w-2xl mx-auto p-6">
          <div className="card bg-base-200 p-8 text-center">
            <div className="text-6xl mb-4">✓</div>
            <h1 className="text-2xl font-bold mb-2">Ticket Submitted</h1>
            <p className="opacity-70 mb-4">We'll get back to you within 24 hours.</p>
            {ticketId && (
              <p className="text-sm opacity-60 mb-4">Ticket ID: {ticketId}</p>
            )}
            <a href="/" className="btn btn-primary">Back to Home</a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-100">
      <div className="max-w-2xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-4">Support</h1>
        <p className="opacity-70 mb-6">Have a question or need help? Submit a ticket and we'll respond within 24 hours.</p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">
              <span className="label-text">Email</span>
            </label>
            <input
              type="email"
              className="input input-bordered w-full"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
            />
          </div>
          
          <div>
            <label className="label">
              <span className="label-text">Subject</span>
            </label>
            <input
              type="text"
              className="input input-bordered w-full"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Brief description of your issue"
              required
            />
          </div>
          
          <div>
            <label className="label">
              <span className="label-text">Message</span>
            </label>
            <textarea
              className="textarea textarea-bordered w-full h-32"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Describe your issue or question in detail..."
              required
            />
          </div>
          
          <button
            type="submit"
            className="btn btn-primary w-full"
            disabled={submitting}
          >
            {submitting ? 'Submitting...' : 'Submit Ticket'}
          </button>
        </form>
        
        <div className="mt-8 pt-8 border-t border-base-300">
          <p className="text-sm opacity-60 mb-2">Or check out our:</p>
          <div className="flex gap-2">
            <a href="/public/faq" className="btn btn-ghost btn-sm">FAQ</a>
            <a href="/public/roadmap" className="btn btn-ghost btn-sm">Roadmap</a>
            <a href="/" className="btn btn-ghost btn-sm">← Back to Home</a>
          </div>
        </div>
      </div>
    </div>
  );
}

