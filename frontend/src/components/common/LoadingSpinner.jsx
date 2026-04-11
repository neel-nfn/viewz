export default function LoadingSpinner({ message = "Loading…" }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="loading loading-spinner loading-lg mb-4"></div>
      <p className="text-sm opacity-70">{message}</p>
    </div>
  );
}

