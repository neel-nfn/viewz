import { useEffect, useState } from "react";
import { getUsage } from "../../services/billingService";

export default function Billing(){
  const [u,setU]=useState(null);

  useEffect(()=>{(async()=>setU(await getUsage()))();},[]);

  if(!u) return <div className="p-6">Loading…</div>;

  const pct=Math.round((u.credits_used/u.credits_total)*100);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Billing & Usage</h1>
      <div className="mb-2">Total: {u.credits_total}</div>
      <div className="mb-2">Used: {u.credits_used}</div>
      <div className="mb-4">Remaining: {u.credits_remaining}</div>
      <progress className="progress w-full" value={pct} max="100" />
    </div>
  );
}

