import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Get saved theme from localStorage or default to 'dark'
    const savedTheme = localStorage.getItem('app-theme');
    return savedTheme || 'dark';
  });

  useEffect(() => {
    // Save theme to localStorage
    localStorage.setItem('app-theme', theme);
    
    // Update document root class for global styling
    document.documentElement.setAttribute('data-theme', theme);
    
    // Also add class to body for easier styling
    document.body.className = `theme-${theme}`;
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

