export default function Privacy(){
  return (
    <div className="max-w-3xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Privacy Policy</h1>
      <p>This draft policy is for demo purposes only. Replace with your actual Privacy Policy before public beta.</p>
      <ul className="list-disc pl-6 space-y-1">
        <li>Demo mode stores data locally in your browser.</li>
        <li>No personal data is transmitted in demo mode.</li>
        <li>When connected to Basix, data is processed under your org's policies.</li>
      </ul>
    </div>
  );
}

