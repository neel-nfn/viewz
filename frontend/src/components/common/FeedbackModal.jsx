import { useState } from "react";
import { submitFeedback } from "../../services/feedbackService";
import { useAuth } from "../../context/AuthContext";

export default function FeedbackModal({ onClose }) {
  const { user } = useAuth();
  
  // Get org_id from localStorage or use default
  const orgId = localStorage.getItem('viewz_org_id') || '00000000-0000-0000-0000-000000000000';
  
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("other");
  const [severity, setSeverity] = useState("low");
  const [url, setUrl] = useState(typeof window !== "undefined" ? window.location.href : "");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    if (!title.trim()) return;
    setBusy(true);
    try {
      await submitFeedback({
        org_id: orgId,
        user_id: user?.id || null,
        url,
        category,
        severity,
        title: title.trim(),
        description: description.trim() || null
      });
      // Show success toast
      if (window.dispatchEvent) {
        window.dispatchEvent(new CustomEvent('viewz:feedback-submitted', { detail: { success: true } }));
      }
      onClose();
      // Show alert as fallback
      alert("Feedback submitted successfully! Thank you.");
    } catch (e) {
      alert(`Error: ${e.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="modal modal-open" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <h3 className="font-bold text-lg">Send Feedback</h3>
        <form onSubmit={onSubmit} className="flex flex-col gap-3 mt-3">
          <input
            className="input input-bordered"
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Short title"
            required
          />
          <textarea
            className="textarea textarea-bordered"
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="Describe the issue or idea..."
            rows="4"
          />
          <div className="grid grid-cols-2 gap-3">
            <select
              className="select select-bordered"
              value={category}
              onChange={e => setCategory(e.target.value)}
            >
              <option value="bug">bug</option>
              <option value="idea">idea</option>
              <option value="ui">ui</option>
              <option value="performance">performance</option>
              <option value="other">other</option>
            </select>
            <select
              className="select select-bordered"
              value={severity}
              onChange={e => setSeverity(e.target.value)}
            >
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
              <option value="critical">critical</option>
            </select>
          </div>
          <input
            className="input input-bordered"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="URL (auto-filled)"
          />
          <div className="modal-action">
            <button type="button" className="btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={busy || !title.trim()}>
              {busy ? "Submitting..." : "Submit"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
