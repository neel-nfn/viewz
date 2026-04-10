export default function StepConnect({ onNext, onSkip }) {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Connect Your YouTube Channel</h2>
      <p className="opacity-70">Link your YouTube channel to start managing your content pipeline.</p>
      
      <div className="space-y-4 mt-6">
        <button className="btn btn-primary w-full" onClick={onNext}>
          Connect via Google OAuth
        </button>
        <button className="btn btn-outline w-full" onClick={onSkip}>
          Skip for Now (Demo Mode)
        </button>
      </div>
      
      <div className="mt-6 p-4 bg-base-300 rounded text-sm">
        <p className="font-semibold mb-2">What happens next:</p>
        <ul className="list-disc ml-5 space-y-1">
          <li>Authorize Viewz to access your YouTube channel</li>
          <li>We'll sync your channel data</li>
          <li>Start creating tasks and managing your content</li>
        </ul>
      </div>
    </div>
  );
}

