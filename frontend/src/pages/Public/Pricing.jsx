export default function Pricing() {
  const tiers = [
    {
      name: "Tier 1",
      channels: 1,
      price: "$49",
      features: [
        "1 YouTube channel",
        "AI SEO Assistant",
        "Research & Outlier Engine",
        "Team collaboration (up to 3 users)",
        "Pipeline management",
        "Basic analytics"
      ]
    },
    {
      name: "Tier 2",
      channels: 5,
      price: "$99",
      features: [
        "5 YouTube channels",
        "All Tier 1 features",
        "Advanced analytics",
        "Team collaboration (up to 10 users)",
        "Priority support",
        "Custom integrations"
      ]
    },
    {
      name: "Tier 3",
      channels: 20,
      price: "$199",
      features: [
        "20 YouTube channels",
        "All Tier 2 features",
        "Unlimited team members",
        "Dedicated support",
        "API access",
        "Custom workflows"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-base-100">
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-4xl font-bold text-center mb-4">Pricing</h1>
        <p className="text-center opacity-70 mb-8">Choose the plan that fits your team size</p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {tiers.map((tier, i) => (
            <div key={i} className="card bg-base-200 p-6">
              <h2 className="text-2xl font-bold mb-2">{tier.name}</h2>
              <div className="text-3xl font-bold mb-1">{tier.price}</div>
              <div className="text-sm opacity-60 mb-4">{tier.channels} channel{tier.channels > 1 ? 's' : ''}</div>
              
              <ul className="space-y-2 mb-6">
                {tier.features.map((feature, j) => (
                  <li key={j} className="flex items-start gap-2">
                    <span className="text-green-500">✓</span>
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
              
              <a href="/app" className="btn btn-primary w-full">Get Started</a>
            </div>
          ))}
        </div>
        
        <div className="mt-8 text-center">
          <p className="opacity-70 mb-4">All plans include 30-day money-back guarantee</p>
          <a href="/public/faq" className="btn btn-ghost btn-sm">View FAQ</a>
        </div>
        
        <div className="mt-8 pt-8 border-t border-base-300">
          <a href="/" className="btn btn-sm">← Back to Home</a>
        </div>
      </div>
    </div>
  );
}

