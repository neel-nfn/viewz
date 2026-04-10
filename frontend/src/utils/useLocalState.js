import { useEffect, useRef, useState } from "react";

export function useLocalState(key, initial) {
  const [state, setState] = useState(() => {
    try { 
      const v = localStorage.getItem(key); 
      return v ? JSON.parse(v) : initial; 
    } catch { 
      return initial; 
    }
  });

  const t = useRef();

  useEffect(() => { 
    clearTimeout(t.current);
    t.current = setTimeout(() => { 
      try { 
        localStorage.setItem(key, JSON.stringify(state)); 
      } catch {} 
    }, 200);
    return () => clearTimeout(t.current);
  }, [key, state]);

  return [state, setState];
}

