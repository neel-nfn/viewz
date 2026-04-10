// src/components/team/UserCard.jsx
import RoleBadge from "../common/RoleBadge";

export default function UserCard({ email, role, status }) {
  return (
    <div className="flex items-center justify-between rounded-xl border p-3">
      <div className="flex items-center gap-3">
        <div className="avatar placeholder">
          <div className="bg-neutral text-neutral-content rounded-full w-10">
            <span>{email ? email[0]?.toUpperCase() : "U"}</span>
          </div>
        </div>
        <div>
          <div className="font-medium">{email || "Invited user"}</div>
          <div className="text-xs opacity-70">{status}</div>
        </div>
      </div>
      <RoleBadge role={role} />
    </div>
  );
}
