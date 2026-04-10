import { useEffect, useState, Suspense, lazy } from 'react';
import { api } from '../services/apiClient';
import PipelineBoard from './Pipeline/PipelineBoard';
import Loader from '../components/common/Loader';
const AnalyticsSidebar = lazy(()=>import('./Analytics/AnalyticsSidebar'));
const AIDrawer = lazy(()=>import('./AI/AIDrawer'));

export default function DemoPipeline(){
  const [channels,setChannels]=useState(null);
  const [active,setActive]=useState(null);
  const storedId=localStorage.getItem('viewz_user_id')||'u_mgr';
  const storedRole=localStorage.getItem('viewz_user_role')||'manager';
  const [me,setMe]=useState({ 
    id:storedId, 
    name: storedId==='u_mgr'?'Manager Mia': storedId==='u_admin'?'Admin Alex': storedId==='u_wrt'?'Writer Will':'Editor Eva', 
    role: storedRole 
  });
  const [filter,setFilter]=useState('all');
  const [showAnalytics,setShowAnalytics]=useState(false);
  const [showAI,setShowAI]=useState(false);
  
  useEffect(()=>{
    function onToggle(){ setShowAnalytics(v=>!v);}
    window.addEventListener('viewz:toggle-analytics', onToggle);
    return ()=>window.removeEventListener('viewz:toggle-analytics', onToggle);
  },[]);

  useEffect(()=>{
    function t(){setShowAI(v=>!v);}
    window.addEventListener('viewz:toggle-ai', t);
    const k=(e)=>{
      if(e.key==='G'||e.key==='g'){
        t();
      }
    };
    window.addEventListener('keydown', k);
    return ()=>{
      window.removeEventListener('viewz:toggle-ai', t);
      window.removeEventListener('keydown', k);
    };
  },[]);

  useEffect(()=>{
    function onU(){
      const id=localStorage.getItem('viewz_user_id')||'u_mgr';
      const role=localStorage.getItem('viewz_user_role')||'manager';
      setMe({ 
        id, 
        name: id==='u_mgr'?'Manager Mia': id==='u_admin'?'Admin Alex': id==='u_wrt'?'Writer Will':'Editor Eva', 
        role 
      });
    }
    window.addEventListener('viewz:user-changed', onU);
    window.addEventListener('keydown', (e)=>{
      if(e.key==='U'||e.key==='u'){
        const order=['u_admin','u_mgr','u_wrt','u_edt'];
        const cur=localStorage.getItem('viewz_user_id')||'u_mgr';
        const i=(order.indexOf(cur)+1)%order.length;
        const next=order[i];
        const map={u_admin:'admin',u_mgr:'manager',u_wrt:'writer',u_edt:'editor'};
        localStorage.setItem('viewz_user_id', next);
        localStorage.setItem('viewz_user_role', map[next]);
        window.dispatchEvent(new Event('viewz:user-changed'));
        location.reload();
      }
    });
    return ()=>{
      window.removeEventListener('viewz:user-changed', onU);
    };
  },[]);

  useEffect(()=>{ let m=true; api.listChannels().then(c=>{ if(m){ setChannels(c); setActive(c[0]); }}); return ()=>{m=false}; },[]);

  if(!channels) return <Loader label="Loading channels..." />;

  return (
    <>
      <div className="mb-4 flex gap-2">
        {channels.map(c=>(
          <button key={c.id} className={`btn btn-sm ${active?.id===c.id?'btn-primary':''}`} onClick={()=>setActive(c)}>{c.title}</button>
        ))}
        <div className="ml-auto join">
          <button className={`btn btn-xs join-item ${filter==='all'?'btn-active':''}`} onClick={()=>setFilter('all')}>All</button>
          <button className={`btn btn-xs join-item ${filter==='overdue'?'btn-active':''}`} onClick={()=>setFilter('overdue')}>Overdue</button>
          <button className={`btn btn-xs join-item ${filter==='mine'?'btn-active':''}`} onClick={()=>setFilter('mine')}>Assigned to Me</button>
        </div>
        <button className="btn btn-ghost btn-xs ml-2" onClick={()=>import('../services/mock/pipelineMock.js').then(m=>m.__reset&&m.__reset()).then(()=>location.reload())}>Reset Demo Data</button>
      </div>
      <PipelineBoard activeChannel={active} currentUser={me} filter={filter} />
      <Suspense fallback={<div className="fixed right-0 top-0 p-3">Loading…</div>}>
        <AnalyticsSidebar channel={active} open={showAnalytics} onClose={()=>setShowAnalytics(false)} />
        <AIDrawer open={showAI} onClose={()=>setShowAI(false)} />
      </Suspense>
    </>
  );
}
