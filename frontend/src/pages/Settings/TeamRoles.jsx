// src/pages/Settings/TeamRoles.jsx
import { useEffect, useState } from "react";
import { fetchTeam, inviteUser } from "../../services/teamService";
import UserCard from "../../components/team/UserCard";
import InviteUserModal from "../../components/team/InviteUserModal";
import { useAuth } from "../../context/AuthContext";
import toast from "react-hot-toast";

export default function TeamRoles() {
  const [team, setTeam] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const { user } = useAuth();

  async function load() {
    setLoading(true);
    try {
      const data = await fetchTeam();
      setTeam(data);
    } catch (e) {
      toast.error("Failed to load team");
      setTeam([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleInvite({ email, role }) {
    try {
      const res = await inviteUser({ email, role, assigned_channel_ids: [] });
      setOpen(false);
      await load();
      if (res?.token && navigator.clipboard) {
        navigator.clipboard.writeText(`${window.location.origin}/invite/accept/${res.token}`);
        toast.success("Invite sent! Link copied to clipboard.");
      } else {
        toast.success("Invite sent!");
      }
    } catch (e) {
      toast.error("Failed to send invite");
    }
  }

  const normalizedEmail = (user?.email || "").toLowerCase();
  const meInTeam = team.find(m => (m.email || "").toLowerCase() === normalizedEmail);
  const effectiveRole = user?.role || meInTeam?.role || "";
  const canInvite = ["admin","manager"].includes(effectiveRole);

  if (loading) {
    return <div className="p-6">Loading…</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Team & Roles
          </h2>
          <p className="text-sm text-gray-400 mt-1">Manage your team members and their permissions</p>
        </div>
        {canInvite ? (
          <button 
            className="btn btn-primary bg-gradient-to-r from-blue-500 to-purple-600 border-0 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 flex items-center gap-2"
            onClick={() => setOpen(true)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <line x1="19" y1="8" x2="19" y2="14"></line>
              <line x1="22" y1="11" x2="16" y2="11"></line>
            </svg>
            Invite Team Member
          </button>
        ) : (
          <div className="px-4 py-2 bg-gray-700/50 rounded-lg border border-gray-600">
            <p className="text-sm text-gray-400">Only admins and managers can invite team members</p>
          </div>
        )}
      </div>
      
      {team.length === 0 ? (
        <div className="text-center p-12 bg-gray-800/30 rounded-xl border border-gray-700">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto mb-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <p className="text-lg text-gray-400 mb-2">No team members yet</p>
          {canInvite && (
            <button 
              className="btn btn-primary btn-sm mt-4 bg-gradient-to-r from-blue-500 to-purple-600 border-0"
              onClick={() => setOpen(true)}
            >
              Invite Your First Team Member
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {team.map(member => (
            <UserCard key={member.user_id} email={member.email} role={member.role} status={member.status}/>
          ))}
        </div>
      )}
      
      <InviteUserModal open={open} onClose={()=>setOpen(false)} onSubmit={handleInvite}/>
    </div>
  );
}
