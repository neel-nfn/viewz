import { useState } from "react";
import { startABTest } from "../../services/abtestService";

export default function ABTestModal({open,onClose,channelId,videoId}){
  const [a,setA]=useState({title:"",thumbnail:""});
  const [b,setB]=useState({title:"",thumbnail:""});
  const [busy,setBusy]=useState(false);

  if(!open) return null;

  const run = async ()=>{
    setBusy(true);
    await startABTest({channel_id:channelId, video_id:videoId, variant_a:a, variant_b:b});
    setBusy(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div className="bg-base-100 p-6 rounded-2xl w-full max-w-xl">
        <h2 className="text-xl font-semibold mb-4">Start A/B Test</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="font-medium mb-2">Variant A</div>
            <input className="input input-bordered w-full mb-2" placeholder="Title" value={a.title} onChange={e=>setA({...a,title:e.target.value})}/>
            <input className="input input-bordered w-full" placeholder="Thumbnail URL" value={a.thumbnail} onChange={e=>setA({...a,thumbnail:e.target.value})}/>
          </div>
          <div>
            <div className="font-medium mb-2">Variant B</div>
            <input className="input input-bordered w-full mb-2" placeholder="Title" value={b.title} onChange={e=>setB({...b,title:e.target.value})}/>
            <input className="input input-bordered w-full" placeholder="Thumbnail URL" value={b.thumbnail} onChange={e=>setB({...b,thumbnail:e.target.value})}/>
          </div>
        </div>
        <div className="mt-6 flex gap-2 justify-end">
          <button className="btn" onClick={onClose} disabled={busy}>Cancel</button>
          <button className="btn btn-primary" onClick={run} disabled={busy}>Start</button>
        </div>
      </div>
    </div>
  );
}

