import { useEffect, useState } from "react";
import { getRecommendations } from "../../services/optimizeService";

export default function OptimizationFeed(){
  const [items,setItems]=useState([]);
  const [loading,setLoading]=useState(true);

  useEffect(()=>{
    (async()=>{
      const r=await getRecommendations();
      setItems(r||[]);
      setLoading(false);
    })();
  },[]);

  if(loading) return <div className="p-6">Loading…</div>;
  if(!items.length) return <div className="p-6">No recommendations yet.</div>;

  return (
    <div className="p-6 grid gap-3">
      {items.map(x=>(
        <div key={x.id} className="rounded-2xl p-4 shadow bg-base-200">
          <div className="text-sm opacity-70">{x.type.toUpperCase()} • {x.priority}</div>
          <div className="text-lg font-semibold">{x.message}</div>
        </div>
      ))}
    </div>
  );
}

