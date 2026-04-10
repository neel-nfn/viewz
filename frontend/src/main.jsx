import "./boot/apiIntercept.js";
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import ErrorBoundary from './components/system/ErrorBoundary.jsx';
import "./styles/index.css";
import { AuthProvider } from "./context/AuthContext.jsx";
import { applyTheme } from "./utils/theme";
import debugAuth from "./utils/debugAuth";

// Initialize theme
applyTheme();

// Expose debug function globally for browser console
window.debugAuth = debugAuth;
console.log("🧠 Supabase debugAuth() ready globally");

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ErrorBoundary>
      <AuthProvider><App /></AuthProvider>
    </ErrorBoundary>
  </React.StrictMode>
);