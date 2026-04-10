import { Link } from "react-router-dom";

export default function NotFound(){
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-2">Page not found</h1>
      <p className="mb-4">The page you're looking for doesn't exist.</p>
      <Link className="btn btn-primary" to="/settings/channels">Go to Channels</Link>
    </div>
  );
}

