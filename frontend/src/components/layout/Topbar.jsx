import { DEMO_MODE, DEMO_ROLE, DENSITY, setDensity } from '../../utils/constants';
import { getSourceLabel } from '../../services/providers/providerFactory';
import NotificationPanel from '../NotificationPanel';
import FeedbackButton from '../common/FeedbackButton';

export default function Topbar(){
  return (
    <>
    <div className="w-full px-3 py-2 flex justify-between items-center border-b border-base-300">
      <div className="flex items-center gap-2">
        <img src="/logo.svg" alt="Viewz" className="w-5 h-5"/>
        <span className="font-semibold">Viewz</span>
      </div>
      <div className="flex gap-2 items-center">
        <button className="btn btn-xs" onClick={()=>{ localStorage.setItem('viewz_demo', DEMO_MODE ? '0' : '1'); location.reload(); }}>
          {DEMO_MODE ? 'Exit Demo' : 'Enter Demo'} Mode
        </button>
        <button className="btn btn-xs" onClick={()=>window.dispatchEvent(new Event('viewz:toggle-analytics'))}>Analytics</button>
        <button className="btn btn-xs" onClick={()=>window.dispatchEvent(new Event('viewz:toggle-ai'))}>AI Assist</button>
        <NotificationPanel />
        <a className="btn btn-ghost btn-xs" href="/roadmap">Roadmap</a>
        <FeedbackButton />
        <select id="theme_switch" className="select select-xs" defaultValue={localStorage.getItem('viewz_theme')||'system'} onChange={async (e)=>{
          localStorage.setItem('viewz_theme', e.target.value);
          const {applyTheme} = await import('../../utils/theme');
          applyTheme();
        }}>
          <option value="system">system</option>
          <option value="light">light</option>
          <option value="dark">dark</option>
        </select>
        <span className="badge badge-outline text-xs">Data: {getSourceLabel()}</span>
        <select id="user_switch" className="select select-xs" defaultValue={localStorage.getItem('viewz_user_id')||'u_mgr'} onChange={(e)=>{
          const map={u_admin:'admin',u_mgr:'manager',u_wrt:'writer',u_edt:'editor'};
          localStorage.setItem('viewz_user_id', e.target.value);
          localStorage.setItem('viewz_user_role', map[e.target.value]||'manager');
          window.dispatchEvent(new Event('viewz:user-changed'));
          location.reload();
        }}>
          <option value="u_admin">Admin Alex</option>
          <option value="u_mgr">Manager Mia</option>
          <option value="u_wrt">Writer Will</option>
          <option value="u_edt">Editor Eva</option>
        </select>
        <span className="badge">Role: {(localStorage.getItem('viewz_user_role')||DEMO_ROLE)}</span>
        <button className="btn btn-outline btn-xs" onClick={()=>document.getElementById('invite_modal')?.showModal()}>Invite</button>
        <select className="select select-xs" value={DENSITY} onChange={(e)=>{ setDensity(e.target.value); location.reload(); }}>
          <option value="comfortable">Comfortable</option>
          <option value="compact">Compact</option>
        </select>
      </div>
    </div>
    </>
  );
}

