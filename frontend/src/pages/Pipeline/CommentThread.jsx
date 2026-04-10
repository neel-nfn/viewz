import { useState, useEffect } from "react";
import { apiPost, apiGet } from "../../services/apiClient";

export default function CommentThread({ taskId }) {
  const [text, setText] = useState("");
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (taskId) {
      loadComments();
    }
  }, [taskId]);

  async function loadComments() {
    try {
      const data = await apiGet(`/comments/list?task_id=${taskId}`);
      setComments(data.comments || []);
    } catch (e) {
      console.error("Failed to load comments:", e);
    }
  }

  async function post() {
    if (!text.trim()) return;
    
    setLoading(true);
    try {
      await apiPost("/comments/add", {
        task_id: taskId,
        comment: text.trim(),
        mentions: extractMentions(text)
      });
      setText("");
      await loadComments();
    } catch (e) {
      alert(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }

  function extractMentions(text) {
    const matches = text.match(/@\w+/g) || [];
    return matches.map(m => m.substring(1)); // Remove @
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input
          className="input input-bordered flex-1"
          placeholder="Add a comment... (use @username to mention)"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && post()}
        />
        <button className="btn btn-primary" onClick={post} disabled={loading || !text.trim()}>
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
      <div className="space-y-2 mt-4">
        {comments.map((c) => (
          <div key={c.id} className="border border-base-300 rounded p-3">
            <div className="text-sm whitespace-pre-wrap">{c.comment}</div>
            {c.mentions && c.mentions.length > 0 && (
              <div className="text-xs opacity-60 mt-1">
                Mentions: {c.mentions.join(", ")}
              </div>
            )}
            <div className="text-xs opacity-60 mt-1">
              {new Date(c.created_at).toLocaleString()}
            </div>
          </div>
        ))}
        {comments.length === 0 && (
          <div className="text-sm opacity-60 text-center py-4">No comments yet</div>
        )}
      </div>
    </div>
  );
}

