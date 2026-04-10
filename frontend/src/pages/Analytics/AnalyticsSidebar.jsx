import { useEffect, useState } from 'react';
import { api } from '../../services/apiClient';
import { STAGES } from '../../utils/constants';
import { isOverdue } from '../../utils/date';

export default function AnalyticsSidebar({ channel, open, onClose }) {
  const [stats,setStats]=useState({ perStage:{}, overdue:0, moves24:0, comments24:0, lastActivity:null });

  async function compute() {
    if(!channel) return;

    const tasks = await api.listTasks(channel.id);

    const now = Date.now();

    const perStage = STAGES.reduce((m,s)=> (m[s]=0, m), {});

    let overdue=0, moves24=0, comments24=0, lastActivity=null;

    for(const t of tasks){
      if(perStage[t.status]!=null) perStage[t.status]++;
      if(isOverdue(t.due_date)) overdue++;
    }

    // Best-effort detail fetch for activity sample (bounded)
    const sample = tasks.slice(0, 8);

    for(const t of sample){
      try {
        const d = await api.getTask(t.id);
        for(const a of (d.activity||[])){
          const ts = +new Date(a.timestamp);
          if(!lastActivity || ts>+new Date(lastActivity)) lastActivity = a.timestamp;
          if(now - ts <= 24*3600*1000 && a.action==='status_change') moves24++;
        }
        for(const c of (d.comments||[])){
          const ts = +new Date(c.created_at);
          if(now - ts <= 24*3600*1000) comments24++;
        }
      } catch {}
    }

    setStats({ perStage, overdue, moves24, comments24, lastActivity });
  }

  useEffect(()=>{ if(open) compute(); },[open, channel?.id]);
  useEffect(()=>{
    function refresh(){ if(open) compute(); }
    window.addEventListener('viewz:pipeline-updated', refresh);
    return ()=>window.removeEventListener('viewz:pipeline-updated', refresh);
  },[open]);

  if(!open) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-sm bg-base-100 border-l border-base-300 z-50">
      <div className="p-4 flex items-center justify-between border-b border-base-300">
        <div className="font-semibold">Channel Overview</div>
        <button className="btn btn-sm" onClick={onClose}>Close</button>
      </div>
      <div className="p-4 space-y-6">
        <section>
          <div className="text-sm opacity-70">Tasks per stage</div>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {STAGES.map(s=>(
              <div key={s} className="flex items-center justify-between bg-base-200 rounded px-2 py-1">
                <span className="capitalize">{s}</span>
                <span className="badge">{stats.perStage[s]||0}</span>
              </div>
            ))}
          </div>
        </section>
        <section className="grid grid-cols-3 gap-2">
          <div className="card bg-base-200 p-3">
            <div className="text-xs opacity-60">Overdue</div>
            <div className="text-xl font-semibold">{stats.overdue}</div>
          </div>
          <div className="card bg-base-200 p-3">
            <div className="text-xs opacity-60">Moves (24h)</div>
            <div className="text-xl font-semibold">{stats.moves24}</div>
          </div>
          <div className="card bg-base-200 p-3">
            <div className="text-xs opacity-60">Comments (24h)</div>
            <div className="text-xl font-semibold">{stats.comments24}</div>
          </div>
        </section>
        <section>
          <div className="text-xs opacity-60">Last activity</div>
          <div className="text-sm">{stats.lastActivity ? new Date(stats.lastActivity).toLocaleString() : '—'}</div>
        </section>
      </div>
    </div>
  );
}

