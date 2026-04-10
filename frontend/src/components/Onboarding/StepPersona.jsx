export default function StepPersona({ selected, onSelect, onNext, onSkip }) {
  const personas = [
    { id: 'Max', name: 'Max', desc: 'Analytical and data-driven' },
    { id: 'Lolo', name: 'Lolo', desc: 'Creative and engaging' },
    { id: 'Loki', name: 'Loki', desc: 'Bold and attention-grabbing' }
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Choose Your AI Persona</h2>
      <p className="opacity-70">Select a persona for AI-generated content that matches your style.</p>
      
      <div className="grid grid-cols-1 gap-3 mt-6">
        {personas.map((p) => (
          <button
            key={p.id}
            className={`card bg-base-100 p-4 text-left border-2 ${
              selected === p.id ? 'border-primary' : 'border-base-300'
            }`}
            onClick={() => onSelect(p.id)}
          >
            <div className="font-semibold">{p.name}</div>
            <div className="text-sm opacity-60">{p.desc}</div>
          </button>
        ))}
      </div>
      
      <div className="flex gap-2 mt-6">
        <button
          className="btn btn-primary flex-1"
          onClick={onNext}
          disabled={!selected}
        >
          Continue
        </button>
        <button className="btn btn-ghost" onClick={onSkip}>
          Skip
        </button>
      </div>
    </div>
  );
}

