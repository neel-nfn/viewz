import { DENSITY, setDensity } from '../../utils/constants';
import { getSourceLabel } from '../../services/providers/providerFactory';
import NotificationPanel from '../NotificationPanel';
import FeedbackButton from '../common/FeedbackButton';
import { useAuth } from '../../context/AuthContext';

export default function Topbar(){
  const { user } = useAuth();
  const userRole = (user?.role || 'manager').toLowerCase();

  return (
    <>
    <div className="w-full px-3 py-2 flex justify-between items-center border-b border-base-300">
      <div className="flex items-center gap-2">
        <img src="/logo.svg" alt="Viewz" className="w-5 h-5"/>
        <span className="font-semibold">Viewz</span>
      </div>
      <div className="flex gap-2 items-center">
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
        <span className="badge">Role: {userRole}</span>
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

