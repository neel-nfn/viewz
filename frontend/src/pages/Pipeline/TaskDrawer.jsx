import { useState, useEffect } from 'react';
import { api } from '../../services/apiClient';
import CommentThread from './CommentThread';
import FileUploader from './FileUploader';

export default function TaskDrawer({ taskId, open, onClose }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (open && taskId) {
      api.getTask(taskId).then(setData);
    }
  }, [open, taskId]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose}></div>
      <div className="fixed right-0 top-0 w-96 bg-base-100 h-full shadow-xl overflow-y-auto">
        <div className="p-4">
          <div className="flex justify-between mb-4">
            <h2 className="text-lg font-semibold">Task Details</h2>
            <button className="btn btn-sm" onClick={onClose}>Close</button>
          </div>
          {data && (
            <>
              {data.title && (
                <div className="mb-4">
                  <div className="text-lg font-semibold">{data.title}</div>
                  {data.research_idea_id && (
                    <div className="text-xs opacity-60 mt-1">
                      Linked to research idea
                    </div>
                  )}
                </div>
              )}
              
              <section className="mb-6">
                <div className="font-semibold mb-2">Comments</div>
                <CommentThread taskId={taskId} />
              </section>

              <section className="mb-6">
                <div className="font-semibold mb-2">Attachments</div>
                <FileUploader taskId={taskId} type="script" />
              </section>

              <section>
                <div className="font-semibold mb-2">Activity</div>
                <ul className="timeline timeline-vertical timeline-compact">
                  {(data.activity||[]).map(a=>(
                    <li key={a.id}>
                      <div className="timeline-start text-xs opacity-70">{new Date(a.timestamp).toLocaleString()}</div>
                      <div className="timeline-middle"><div className="badge badge-ghost">↔</div></div>
                      <div className="timeline-end card bg-base-200 text-xs p-2">
                        {a.action==='status_change'
                          ? <>Moved <b>{a.old_status}</b> → <b>{a.new_status}</b></>
                          : <>{a.action}</>}
                      </div>
                    </li>
                  ))}
                  {(!data.activity || data.activity.length === 0) && (
                    <li className="text-xs opacity-60 py-2">No activity yet</li>
                  )}
                </ul>
              </section>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

