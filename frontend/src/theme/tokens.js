/**
 * Design Tokens - Single source of truth for visual design
 * DO NOT use custom colors/shadows/radii in components - use these tokens only
 */

export const tokens = {
  // Colors
  colors: {
    primary: '#0ea5b7',      // Teal-500
    accent: '#38bdf8',       // Sky-400
    textPrimary: '#0f172a',  // Slate-900
    textSecondary: '#64748b', // Slate-500
    surface: '#ffffff',      // White
    background: '#f8fafc',   // Slate-50
    border: '#e2e8f0',       // Slate-200
    success: '#10b981',     // Green-500
    error: '#ef4444',        // Red-500
    warning: '#f59e0b',      // Amber-500
    info: '#3b82f6',         // Blue-500
  },

  // Border Radius
  radius: {
    sm: '0.375rem',   // 6px
    md: '0.5rem',     // 8px
    lg: '0.75rem',    // 12px
    xl: '1rem',       // 16px
    '2xl': '1.5rem',  // 24px
    full: '9999px',
  },

  // Shadows
  shadows: {
    sm: '0 1px 2px rgba(0,0,0,0.05)',
    md: '0 2px 8px rgba(0,0,0,0.08)',
    lg: '0 4px 16px rgba(0,0,0,0.12)',
    xl: '0 8px 24px rgba(0,0,0,0.16)',
    card: '0 2px 8px rgba(0,0,0,0.08)',
    hover: '0 4px 16px rgba(0,0,0,0.12)',
  },

  // Typography
  typography: {
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
    scale: {
      h1: { fontSize: '3rem', lineHeight: '1.2', fontWeight: '700' },      // 48px
      h2: { fontSize: '2rem', lineHeight: '1.3', fontWeight: '600' },      // 32px
      h3: { fontSize: '1.5rem', lineHeight: '1.4', fontWeight: '600' },   // 24px
      h4: { fontSize: '1.25rem', lineHeight: '1.5', fontWeight: '600' },   // 20px
      body: { fontSize: '1rem', lineHeight: '1.5', fontWeight: '400' },    // 16px
      small: { fontSize: '0.875rem', lineHeight: '1.5', fontWeight: '400' }, // 14px
      xs: { fontSize: '0.75rem', lineHeight: '1.5', fontWeight: '400' },    // 12px
    },
  },

  // Spacing
  spacing: {
    pageMaxWidth: '1240px',
    pagePadding: { base: '1.5rem', md: '2rem' },
    sectionGap: '2rem',
  },

  // Transitions
  transitions: {
    default: 'all 0.2s ease',
    hover: 'all 0.2s ease',
  },
};

