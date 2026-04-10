import { useEffect, useState } from 'react';
import { api } from '../../services/apiClient';
import { generateSEO } from '../../services/aiService';
import ContentDoctor from '../../components/ContentDoctor';

function suggestTitle(task, comments){
  const base = (task?.title||'').toLowerCase().replace(/\b(thumbnail|explainer|video)\b/g,'').trim();
  const stage = task?.status ? ` (${task.status})` : '';
  const spice = comments?.length ? ' — with insider angle' : '';
  let t = base || 'New video concept';
  t = t.replace(/\s+/g,' ').trim();
  return t.charAt(0).toUpperCase()+t.slice(1) + spice + stage;
}

function summarize(task, comments){
  const c = (comments||[]).slice(-2).map(x=>`• ${x.body}`).join('\n');
  return `Task: ${task?.title}\nStage: ${task?.status}\nDue: ${task?.due_date||'—'}\n\nRecent notes:\n${c||'• (no recent notes)'}`;
}

export default function AIDrawer({ open, onClose }){
  const [loading,setLoading]=useState(false);
  const [task,setTask]=useState(null);
  const [data,setData]=useState(null);
  const [output,setOutput]=useState('');
  const [seoData, setSeoData] = useState(null);
  const [seoLoading, setSeoLoading] = useState(false);
  const focusedId = window._viewz_focus || localStorage.getItem('viewz_focus') || null;

  useEffect(()=>{ if(!open) return;
    setLoading(true); setTask(null); setData(null); setOutput('');
    setSeoData(null);
    if(!focusedId){ setLoading(false); return; }
    api.getTask(focusedId).then(d=>{ setData(d); setTask(d.task); }).finally(()=>setLoading(false));
  },[open, focusedId]);

  function runSuggest(){ if(!task) return; setOutput(suggestTitle(task, data?.comments)); }
  function runSummarize(){ if(!task) return; setOutput(summarize(task, data?.comments)); }
  
  async function runGenerateSEO(){
    if(!task) return;
    setSeoLoading(true);
    try {
      const topic = task.title || 'Video content';
      const result = await generateSEO({
        orgId: 'mock-org',
        taskId: task.id,
        topic,
        persona: 'Max'
      });
      setSeoData(result);
    } catch(e) {
      alert(`Error generating SEO: ${e.message}`);
    } finally {
      setSeoLoading(false);
    }
  }
  
  async function applyTitle(){
    if(!task || !output) return;
    await api.updateTaskTitle(task.id, output);
    window.dispatchEvent(new CustomEvent('viewz:title-updated', { detail:{ taskId: task.id, title: output } }));
    onClose?.();
  }

  if(!open) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-md bg-base-100 border-l border-base-300 z-50 overflow-y-auto">
      <div className="p-4 flex items-center justify-between border-b border-base-300">
        <div className="font-semibold">AI Assist</div>
        <button className="btn btn-sm" onClick={onClose}>Close</button>
      </div>
      <div className="p-4 space-y-4">
        {!focusedId ? (
          <div className="opacity-70">Click a task card first, then press <kbd className="kbd kbd-sm">G</kbd> to open AI.</div>
        ) : loading ? (
          <div>Loading…</div>
        ) : (
          <>
            <div className="text-sm opacity-70">Selected task</div>
            <div className="card bg-base-200 p-3">
              <div className="font-medium">{task?.title}</div>
              <div className="text-xs opacity-60">Stage: {task?.status} · Due: {task?.due_date||'—'}</div>
            </div>
            
            {/* SEO Generation Section */}
            <div className="space-y-2">
              <div className="font-semibold text-sm">SEO Assistant</div>
              <button 
                className="btn btn-sm btn-primary w-full" 
                onClick={runGenerateSEO}
                disabled={seoLoading}
              >
                {seoLoading ? "Generating..." : "Generate SEO"}
              </button>
              {seoData && (
                <div className="space-y-3 mt-3">
                  <ContentDoctor score={seoData.score} />
                  <div className="space-y-2">
                    <div>
                      <div className="text-xs opacity-60 mb-1">Title</div>
                      <div className="input input-bordered input-sm w-full">{seoData.title}</div>
                    </div>
                    <div>
                      <div className="text-xs opacity-60 mb-1">Description</div>
                      <textarea className="textarea textarea-bordered textarea-sm w-full h-20" readOnly>{seoData.description}</textarea>
                    </div>
                    <div>
                      <div className="text-xs opacity-60 mb-1">Tags</div>
                      <div className="flex flex-wrap gap-1">
                        {seoData.tags?.map((tag, i) => (
                          <span key={i} className="badge badge-sm">{tag}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div className="divider">OR</div>
            
            {/* Original AI Functions */}
            <div className="flex gap-2">
              <button className="btn btn-sm btn-primary" onClick={runSuggest}>Suggest title</button>
              <button className="btn btn-sm" onClick={runSummarize}>Summarize</button>
            </div>
            <textarea className="textarea textarea-bordered w-full h-36" value={output} onChange={e=>setOutput(e.target.value)} placeholder="AI output here…"/>
            <div className="flex justify-between">
              <button className="btn btn-ghost btn-sm" onClick={()=>navigator.clipboard?.writeText(output||'')}>Copy</button>
              <button className="btn btn-accent btn-sm" disabled={!output} onClick={applyTitle}>Apply title</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

