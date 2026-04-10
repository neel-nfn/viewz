/** @type {import('tailwindcss').Config} */
import daisyui from "daisyui";
export default {
  content: ["./index.html","./src/**/*.{js,jsx,ts,tsx}"],
  theme: { 
    extend: {
      colors: {
        primary: '#0ea5b7',
        accent: '#38bdf8',
        surface: '#ffffff',
        background: '#f8fafc',
        textPrimary: '#0f172a',
        textSecondary: '#64748b',
        border: '#e2e8f0',
      },
      borderRadius: { 
        xl: '1rem', 
        '2xl': '1.5rem' 
      },
      boxShadow: {
        card: '0 2px 8px rgba(0,0,0,0.08)',
        hover: '0 4px 16px rgba(0,0,0,0.12)',
      },
    }
  },
  plugins: [daisyui],
  daisyui: { themes: ["light","dark"] }
}
