// src/components/common/RoleBadge.jsx
export default function RoleBadge({ role }) {
  const map = {
    admin: "border-red-500 text-red-500",
    manager: "border-purple-500 text-purple-500",
    writer: "border-blue-500 text-blue-500",
    editor: "border-teal-500 text-teal-500",
  };

  return (
    <span className={`px-2 py-0.5 text-xs rounded-full border ${map[role] || "border-gray-500 text-gray-500"}`}>
      {role}
    </span>
  );
}
