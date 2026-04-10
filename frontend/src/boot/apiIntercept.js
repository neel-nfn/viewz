const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function isApiPath(p){return typeof p==="string" && p.startsWith("/api/");}

function hardRedirect(p){const q=location.search||"";const h=location.hash||"";location.assign(`${BASE}${p}${q}${h}`);}

// 1) Catch initial load
if(isApiPath(location.pathname)){hardRedirect(location.pathname);}

// 2) Intercept anchor clicks
document.addEventListener("click",(e)=>{
  const a = e.target.closest("a[href]");
  if(!a) return;
  try{
    const url = new URL(a.getAttribute("href"), location.origin);
    if(url.origin===location.origin && isApiPath(url.pathname)){
      e.preventDefault();
      hardRedirect(url.pathname);
    }
  }catch{}
}, true);

// 3) Intercept SPA route changes (pushState/replaceState/popstate)
const _ps = history.pushState; history.pushState = function(s, t, u){
  if(typeof u==="string"){try{const url=new URL(u, location.origin); if(isApiPath(url.pathname)) return hardRedirect(url.pathname);}catch{}}
  return _ps.apply(this, arguments);
};
const _rs = history.replaceState; history.replaceState = function(s, t, u){
  if(typeof u==="string"){try{const url=new URL(u, location.origin); if(isApiPath(url.pathname)) return hardRedirect(url.pathname);}catch{}}
  return _rs.apply(this, arguments);
};
window.addEventListener("popstate",()=>{ if(isApiPath(location.pathname)) hardRedirect(location.pathname); });

