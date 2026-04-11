import { useEffect, useState } from "react";

export default function ConsoleErrors() {
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    // Get errors from window.__APP_ERRORS__
    const appErrors = window.__APP_ERRORS__ || [];
    setErrors(appErrors);
    
    // Update every 2 seconds
    const interval = setInterval(() => {
      const newErrors = window.__APP_ERRORS__ || [];
      setErrors([...newErrors]);
    }, 2000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-semibold">Console Errors</h2>
      <div className="text-sm opacity-70 mb-4">
        Last {errors.length} errors collected from frontend API calls
      </div>
      
      {errors.length === 0 ? (
        <div className="alert alert-success">
          <span>No errors collected yet. Errors will appear here as they occur.</span>
        </div>
      ) : (
        <div className="space-y-2">
          {errors.slice().reverse().map((error, idx) => (
            <div key={idx} className="card bg-base-100 border border-base-300">
              <div className="card-body">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-mono text-xs opacity-70">
                      {new Date(error.ts).toLocaleString()}
                    </div>
                    <div className="font-semibold mt-1">
                      {error.method} {error.url}
                    </div>
                    {error.status > 0 && (
                      <div className="badge badge-error badge-sm mt-1">
                        Status: {error.status}
                      </div>
                    )}
                    <div className="text-sm mt-2 opacity-80">
                      {error.message}
                    </div>
                    {error.data && (
                      <details className="mt-2">
                        <summary className="text-xs cursor-pointer opacity-70">
                          Response Data
                        </summary>
                        <pre className="text-xs mt-2 p-2 bg-base-200 rounded overflow-auto">
                          {JSON.stringify(error.data, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

