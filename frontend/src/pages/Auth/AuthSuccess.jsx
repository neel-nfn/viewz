import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle, Settings } from "lucide-react";

export default function AuthSuccess(){
  const navigate = useNavigate();
  const params = new URLSearchParams(window.location.search);
  const name = params.get("channel");
  const id = params.get("id");
  const isNew = params.get("new") === "1";

  useEffect(() => {
    if (isNew) {
      // Auto-redirect after 2 seconds
      const timer = setTimeout(() => {
        navigate("/app");
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [isNew, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-teal-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 text-center">
        <div className="mb-6">
          <div className="w-20 h-20 bg-teal-100 dark:bg-teal-900 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-12 h-12 text-teal-600 dark:text-teal-400" />
          </div>
          <h1 className="text-3xl font-bold mb-2 text-gray-900 dark:text-white">YouTube Connected! 🎉</h1>
          {name && (
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">Channel</p>
              <p className="font-semibold text-gray-900 dark:text-white">{name}</p>
              {id && <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{id}</p>}
            </div>
          )}
        </div>
        
        <div className="space-y-3">
          {isNew && (
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Redirecting to your dashboard...
            </p>
          )}
          <a 
            className="btn btn-primary w-full" 
            href="/app"
          >
            Go to Dashboard
          </a>
          <a 
            className="btn btn-ghost w-full flex items-center justify-center gap-2" 
            href="/app/settings/channels"
          >
            <Settings size={16} />
            Manage Connections
          </a>
        </div>
      </div>
    </div>
  );
}

