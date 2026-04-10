import { RouterProvider } from "react-router-dom";
import { router } from "./router/AppRouter";
import ToastHost from "./components/ToastHost";

export default function App() {
  if(typeof window!=='undefined' && 'serviceWorker' in navigator){
    window.addEventListener('load',()=>{
      navigator.serviceWorker.register('/sw.js').catch(()=>{});
    });
  }
  
  return (
    <>
      <RouterProvider router={router} />
      <ToastHost />
    </>
  );
}