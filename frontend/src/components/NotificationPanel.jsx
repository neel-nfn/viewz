import { useState, useEffect } from "react";
import { apiGet, apiPost } from "../services/apiClient";

export default function NotificationPanel() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadNotifications();
    // Poll for new notifications every 30 seconds
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  async function loadNotifications() {
    try {
      const data = await apiGet("/api/v1/notifications/list?unread_only=true");
      setNotifications(data.notifications || []);
      setUnreadCount(data.unread_count || 0);
    } catch (e) {
      console.error("Failed to load notifications:", e);
    }
  }

  async function markRead(notificationId) {
    try {
      await apiPost("/api/v1/notifications/read", { notification_id: notificationId });
      await loadNotifications();
    } catch (e) {
      console.error("Failed to mark as read:", e);
    }
  }

  function getNotificationText(notif) {
    if (notif.event === "mention") {
      const payload = notif.payload || {};
      return `${payload.mentioned_by || "Someone"} mentioned you in a comment`;
    }
    return notif.event;
  }

  return (
    <div className="relative">
      <button
        className="btn btn-ghost btn-sm relative"
        onClick={() => setOpen(!open)}
      >
        🔔
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 badge badge-error badge-sm">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>
      {open && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 bg-base-100 border border-base-300 rounded shadow-lg z-50 max-h-96 overflow-y-auto">
            <div className="p-4 border-b border-base-300">
              <div className="font-semibold">Notifications</div>
              {unreadCount > 0 && (
                <div className="text-xs opacity-60">{unreadCount} unread</div>
              )}
            </div>
            <div className="divide-y divide-base-300">
              {notifications.length === 0 ? (
                <div className="p-4 text-sm opacity-60 text-center">
                  No notifications
                </div>
              ) : (
                notifications.map((n) => (
                  <div
                    key={n.id}
                    className={`p-3 cursor-pointer hover:bg-base-200 ${
                      !n.is_read ? "bg-base-200" : ""
                    }`}
                    onClick={() => markRead(n.id)}
                  >
                    <div className="text-sm">{getNotificationText(n)}</div>
                    <div className="text-xs opacity-60 mt-1">
                      {new Date(n.created_at).toLocaleString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

