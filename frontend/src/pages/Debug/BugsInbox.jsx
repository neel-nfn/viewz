export default function BugsInbox(){
  const items = JSON.parse(localStorage.getItem('viewz_bug_queue')||'[]');

  function clear(){ if(confirm('Clear all?')){ localStorage.removeItem('viewz_bug_queue'); location.reload(); } }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Bug Inbox (demo)</h1>
        <button className="btn btn-ghost btn-sm" onClick={clear}>Clear</button>
      </div>
      {!items.length ? <div className="opacity-60 mt-4">No bugs reported yet.</div> :
        <ul className="mt-4 space-y-3">
          {items.map(b=>(
            <li key={b.id} className="border border-base-300 rounded p-3">
              <div className="font-medium">{b.title||'(no title)'}</div>
              <div className="text-sm mt-1 whitespace-pre-wrap">{b.desc||''}</div>
              <div className="text-xs opacity-60 mt-1">{new Date(b.ts).toLocaleString()}</div>
            </li>
          ))}
        </ul>}
    </div>
  );
}

