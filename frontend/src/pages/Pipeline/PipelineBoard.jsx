import { useEffect, useState, useCallback } from 'react';
import { api } from '../../services/apiClient';
import Loader from '../../components/common/Loader';
import EmptyState from '../../components/common/EmptyState';
import TaskDrawer from './TaskDrawer';
import { STAGES, STAGE_COLORS, DENSITY } from '../../utils/constants';
import { isOverdue } from '../../utils/date';

export default function PipelineBoard({ activeChannel, currentUser, filter = 'all' }) {
  const [tasks,setTasks]=useState(null);
  const [loading,setLoading]=useState(true);
  const [err,setErr]=useState(null);
  const [openId, setOpenId] = useState(null);

  useEffect(()=>{ let m=true; setLoading(true);
    api.listTasks(activeChannel?.id).then(d=>{ if(m){ setTasks(d); setLoading(false);} }).catch(e=>{ setErr(e.message); setLoading(false);});
    return ()=>{m=false};
  },[activeChannel?.id]);

  useEffect(()=>{
    function onKey(e){
      if(!tasks||!tasks.length)return;
      const focus=document.querySelector('[data-task-focus="1"]');
      const first=tasks[0];
      const pick=(el)=>{
        const id=el?.getAttribute?.('data-task-id');
        return tasks.find(t=>t.id===id)||first;
      };
      if(e.key==='C' || e.key==='c'){
        const el=document.querySelector('[data-task-focus="1"]')||document.querySelector('[data-task-id]');
        if(el){
          const id=el.getAttribute('data-task-id');
          setOpenId(id);
        }
      }
      if(e.key==='['){
        const el=document.querySelector('[data-task-focus="1"]')||document.querySelector('[data-task-id]');
        const t=pick(el);
        const i=STAGES.indexOf(t.status);
        if(i>0) moveTaskSafely(t, STAGES[i-1]);
      }
      if(e.key===']'){
        const el=document.querySelector('[data-task-focus="1"]')||document.querySelector('[data-task-id]');
        const t=pick(el);
        const i=STAGES.indexOf(t.status);
        if(i<STAGES.length-1) moveTaskSafely(t, STAGES[i+1]);
      }
      if(e.key==='Escape'){
        setOpenId(null);
      }
    }
    function onAnalyticsKey(e){
      if(e.key==='A'||e.key==='a'){
        window.dispatchEvent(new Event('viewz:toggle-analytics'));
      }
    }
    window.addEventListener('keydown', onKey);
    window.addEventListener('keydown', onAnalyticsKey);
    return ()=>{
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('keydown', onAnalyticsKey);
    };
  }, [tasks]);

  useEffect(()=>{
    function onTitle(e){
      const {taskId,title}=e.detail||{};
      setTasks(v=>v?.map(x=>x.id===taskId?{...x,title}:x));
    }
    window.addEventListener('viewz:title-updated', onTitle);
    return ()=>window.removeEventListener('viewz:title-updated', onTitle);
  },[]);

  if(loading) return <Loader label="Loading pipeline" />;
  if(err) return <EmptyState title="Couldn't load pipeline" subtitle={err} />;
  if(!tasks?.length) return <EmptyState title="No tasks yet" subtitle="Start by adding an Idea." />;

  const filtered = (tasks||[]).filter(t=>{
    if(filter==='overdue') return !!isOverdue(t.due_date);
    if(filter==='mine') return t.assigned_to===currentUser.id;
    return true;
  });
  const byStage = STAGES.reduce((m,s)=> (m[s]=filtered.filter(t=>t.status===s), m), {});

  function moveTaskSafely(task,toStage){ 
    const prev = tasks ? tasks.slice() : []; 
    setTasks(t=>t.map(x=>x.id===task.id? {...x,status:toStage}:x)); 
    api.moveTask(task.id,toStage,currentUser.id).then(()=>{
      window.dispatchEvent(new Event('viewz:pipeline-updated'));
    }).catch(e=>{ 
      setTasks(prev); 
      alert(e.message==='forbidden_backward'?'Only Manager/Admin can move backward.':e.message); 
    }); 
  }

  return (
    <>
    <div className="grid grid-cols-7 gap-3 overflow-x-auto">
      {STAGES.map(stage=>(
        <div key={stage} className={`rounded-xl bg-base-200 min-w-64 ${DENSITY==="compact"?"p-2":"p-3"}`}>
          <div className="mb-2 font-semibold capitalize">{stage} <span className="badge">{byStage[stage]?.length||0}</span></div>
          <ul className={`space-y-2 ${DENSITY==="compact"?"p-2":"p-3"}`}>
            {byStage[stage]?.length === 0 && (
              <li className="text-xs opacity-50 text-center py-2">Drop tasks here</li>
            )}
            {byStage[stage]?.map(t=>(
              <li 
                key={t.id} 
                data-task-id={t.id}
                className={`card bg-base-100 shadow cursor-pointer border-l-4 ${DENSITY==="compact"?"p-2":"p-3"} ${STAGE_COLORS[t.status] ? STAGE_COLORS[t.status].replace("badge-","border-") : "border-base-300"}`}
                onClick={()=>{
                  window._viewz_focus=t.id;
                  localStorage.setItem('viewz_focus', t.id);
                  setOpenId(t.id);
                }}
                onFocus={(e)=>{
                  document.querySelectorAll("[data-task-focus]").forEach(n=>n.removeAttribute("data-task-focus"));
                  e.currentTarget.setAttribute("data-task-focus","1");
                }}
                tabIndex={0}
              >
                <div className="flex items-center justify-between">
                  <div className="font-medium">{t.title}</div>
                  <div className="text-xs opacity-60">{t.priority}</div>
                </div>
                <div className="mt-2 flex items-center gap-2">
                  {isOverdue(t.due_date) && <span className="badge badge-error badge-xs">Overdue</span>}
                  {t.assigned_to && <span className="badge badge-ghost badge-xs">{t.assigned_to.replace("u_","@")}</span>}
                  <span className={`badge badge-xs ${STAGE_COLORS[t.status]||""}`}>{t.status}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
    <TaskDrawer taskId={openId} open={!!openId} onClose={()=>setOpenId(null)} />
    </>
  );
}
