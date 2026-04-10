export default function FAQ() {
  const faqs = [
    {
      q: "What is Viewz?",
      a: "Viewz is a YouTube Production OS that helps creators and teams manage their content pipeline from research to publication, with AI-powered SEO optimization and team collaboration tools."
    },
    {
      q: "How do I get started?",
      a: "Click 'Get Started' on the landing page, connect your YouTube channel via OAuth, or try the demo mode to explore features without an account."
    },
    {
      q: "Is there a free trial?",
      a: "Yes! Demo mode is available for unlimited exploration. For production use, we offer tiered plans via AppSumo."
    },
    {
      q: "What are the channel limits?",
      a: "Tier 1: 1 channel, Tier 2: 5 channels, Tier 3: 20 channels. Limits are enforced per organization."
    },
    {
      q: "Can I use Viewz with a team?",
      a: "Yes! Viewz supports multi-user collaboration with role-based access (Admin, Manager, Writer, Editor)."
    },
    {
      q: "How does the AI SEO Assistant work?",
      a: "The AI SEO Assistant analyzes your content topic and generates optimized titles, descriptions, and tags using Google's Gemini API."
    },
    {
      q: "What browsers are supported?",
      a: "Viewz works in modern browsers (Chrome, Firefox, Safari, Edge) with JavaScript enabled."
    },
    {
      q: "How do I contact support?",
      a: "Visit /public/support or email support@viewz.getarainc.com. We typically respond within 24 hours."
    }
  ];

  return (
    <div className="min-h-screen bg-base-100">
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">Frequently Asked Questions</h1>
        <div className="space-y-4">
          {faqs.map((faq, i) => (
            <div key={i} className="card bg-base-200 p-4">
              <h2 className="font-semibold text-lg mb-2">{faq.q}</h2>
              <p className="opacity-80">{faq.a}</p>
            </div>
          ))}
        </div>
        <div className="mt-8 pt-8 border-t border-base-300">
          <a href="/" className="btn btn-sm">← Back to Home</a>
        </div>
      </div>
    </div>
  );
}

