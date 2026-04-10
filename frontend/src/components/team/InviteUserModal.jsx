// src/components/team/InviteUserModal.jsx
import { useState } from "react";

export default function InviteUserModal({ open, onClose, onSubmit }) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("writer");

  if (!open) return null;

  return (
    <div className="modal modal-open">
      <div className="modal-box">
        <h3 className="font-semibold mb-3">Invite a teammate</h3>
        <div className="space-y-3">
          <input 
            className="input input-bordered w-full" 
            placeholder="email@team.com" 
            value={email} 
            onChange={(e)=>setEmail(e.target.value)} 
          />
          <select 
            className="select select-bordered w-full" 
            value={role} 
            onChange={(e)=>setRole(e.target.value)}
          >
            <option value="writer">Writer</option>
            <option value="editor">Editor</option>
            <option value="manager">Manager</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <div className="modal-action">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={()=>onSubmit({email, role})}>Send Invite</button>
        </div>
      </div>
    </div>
  );
}
