import { useEffect, useState } from "react";
import { getChannelSnapshot, getKeywords, getRecommendations } from "../../services/analyticsService";

export default function AnalyticsPage(){
  const [snapshot,setSnapshot] = useState(null);
  const [recs,setRecs] = useState([]);
  const [kw,setKw] = useState({ q:"", data:null });
  const [loading,setLoading] = useState(true);
  const [error,setError] = useState("");

  useEffect(()=>{
    async function load(){
      try{
        setLoading(true);
        const [s, r] = await Promise.all([
          getChannelSnapshot({ window:"7d" }),
          getRecommendations({ window:"7d" })
        ]);
        setSnapshot(s);
        setRecs(r || []);
      }catch(e){
        setError("Failed to load analytics");
      }finally{
        setLoading(false);
      }
    }
    load();
  },[]);

  async function onSearch(term){
    setKw(prev=>({ ...prev, q: term, data: null }));
    try{
      const data = await getKeywords(term);
      setKw({ q: term, data });
    }catch(e){
      setError("Keyword fetch failed");
    }
  }

  if (loading) return <div className="p-4">Loading…</div>;
  if (error) return <div className="p-4 text-error">{error}</div>;

  return (
    <div className="p-4 space-y-4">
      <section className="card bg-base-200 p-4">
        <h2 className="font-bold">Channel Snapshot (7d)</h2>
        {snapshot && (
          <div className="mt-2">
            <div>Views: {snapshot.views_7d}</div>
            <div>Avg CTR: {snapshot.avg_ctr}%</div>
            <div className="text-xs opacity-60">Last sync: {new Date(snapshot.last_sync_at).toLocaleString()}</div>
          </div>
        )}
      </section>

      <section className="card bg-base-200 p-4">
        <h2 className="font-bold">Topic Explorer</h2>
        <div className="flex gap-2 mt-2">
          <input 
            className="input input-bordered" 
            placeholder="Search keyword…" 
            onKeyDown={e => e.key==='Enter' && onSearch(e.target.value)} 
          />
          <button className="btn" onClick={()=>onSearch(kw.q)}>Search</button>
        </div>
        {kw.data && (
          <div className="mt-3">
            <div>Reach: {kw.data.reach_score}/100</div>
            <div>Competition: {kw.data.competition_level}</div>
            <div>Suggested length: {kw.data.suggested_length}</div>
          </div>
        )}
      </section>

      <section className="card bg-base-200 p-4">
        <h2 className="font-bold">AI Recommendations</h2>
        <ul className="mt-2 list-disc ml-6">
          {recs.map(x => <li key={x.id}>{x.text}</li>)}
        </ul>
      </section>
    </div>
  );
}
