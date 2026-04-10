export default function AuthFail(){
  const params=new URLSearchParams(window.location.search);
  const err=params.get("error")||"unknown_error";

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-2">Authorization Failed</h1>
      <p className="mb-4">Error: {err}</p>
      <a className="btn" href="/settings/channels">Try Again</a>
    </div>
  );
}

