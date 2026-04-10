export function applyTheme(initial){
  const key='viewz_theme';
  const saved=localStorage.getItem(key);
  const prefer=initial||saved||'system';
  const root=document.documentElement;
  const sys=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
  const map={light:'light',dark:'dark',system:sys};
  root.setAttribute('data-theme',map[prefer]||'light');
  localStorage.setItem(key,prefer);
}

export function setTheme(v){
  applyTheme(v);
}

