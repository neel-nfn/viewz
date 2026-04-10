import { useState } from "react";
import { switchOrg } from "../../services/orgService";

export default function OrgSwitcher({orgs=[],activeOrgId,onSwitched}){
  const [open,setOpen]=useState(false);

  const current = orgs.find(o=>o.id===activeOrgId) || {name:"Select Org"};

  const choose = async(id)=>{
    await switchOrg(id);
    setOpen(false);
    onSwitched && onSwitched(id);
  };

  return (
    <div className="relative">
      <button className="btn btn-ghost" onClick={()=>setOpen(v=>!v)}>{current.name}</button>
      {open && (
        <div className="absolute mt-2 bg-base-100 shadow rounded-xl p-2 w-56 z-50">
          {orgs.map(o=>(
            <button key={o.id} className="btn btn-ghost justify-start w-full" onClick={()=>choose(o.id)}>{o.name}</button>
          ))}
        </div>
      )}
    </div>
  );
}

