import React, { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { 
  BarChart3, LayoutGrid, Sparkles, ArrowRight, Check, 
  Zap, Users, Calendar, FileText, Video, Target,
  TrendingUp, Clock, Shield, Star, ChevronDown,
  Play, X, Menu
} from "lucide-react";

function LogoMark() {
  return (
    <div className="flex items-center gap-2">
      <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-teal-500 to-sky-500 shadow-lg" />
      <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-teal-600 to-sky-600 bg-clip-text text-transparent">
        Viewz
      </span>
    </div>
  );
}

function PrimaryButton({ href = "#", children, className = "" }) {
  return (
    <a
      href={href}
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3.5 bg-gradient-to-r from-teal-600 to-sky-600 text-white font-semibold hover:shadow-lg hover:scale-105 transition-all duration-200 ${className}`}
    >
      {children}
    </a>
  );
}

function SecondaryButton({ href = "#", children, className = "" }) {
  return (
    <a
      href={href}
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3.5 border-2 border-slate-300 text-slate-700 font-semibold hover:bg-slate-50 hover:border-slate-400 transition-all duration-200 ${className}`}
    >
      {children}
    </a>
  );
}

function AppSumoBadge() {
  return (
    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-orange-100 border border-orange-200">
      <span className="text-orange-600 font-bold text-sm">🔥 APPSUMO EXCLUSIVE</span>
    </div>
  );
}

function HeroIllustration() {
  return (
    <div className="relative">
      <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-teal-600/20 via-sky-500/20 to-purple-600/20 blur-3xl animate-pulse" />
      <div className="relative rounded-2xl border-2 border-slate-200 bg-white shadow-2xl overflow-hidden">
        {/* Mock Dashboard Screenshot */}
        <div className="bg-gradient-to-br from-slate-50 to-slate-100 p-4">
          <div className="grid grid-cols-4 gap-2 mb-3">
            <div className="col-span-3 h-24 rounded-lg bg-gradient-to-br from-teal-500 to-sky-500 p-3 text-white">
              <div className="text-xs opacity-75">Monthly Views</div>
              <div className="text-2xl font-bold mt-1">1.2M</div>
            </div>
            <div className="h-24 rounded-lg bg-white border border-slate-200 p-3">
              <div className="text-xs text-slate-600">Videos</div>
              <div className="text-xl font-bold mt-1">42</div>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <div className="h-20 rounded-lg bg-white border border-slate-200" />
            <div className="h-20 rounded-lg bg-white border border-slate-200" />
            <div className="h-20 rounded-lg bg-white border border-slate-200" />
          </div>
        </div>
        <div className="absolute -bottom-4 -right-4 rounded-xl border-2 border-slate-200 bg-white p-3 shadow-xl">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
              <TrendingUp className="h-4 w-4 text-green-600" />
            </div>
            <div>
              <div className="text-xs text-slate-600">Growth</div>
              <div className="text-sm font-bold text-green-600">+24%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon: Icon, title, description }) {
  return (
    <div className="group rounded-2xl border-2 border-slate-200 bg-white p-6 hover:border-teal-300 hover:shadow-xl transition-all duration-300">
      <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-teal-500 to-sky-500 text-white grid place-content-center mb-4 group-hover:scale-110 transition-transform">
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="text-xl font-bold tracking-tight mb-2">{title}</h3>
      <p className="text-slate-600 leading-relaxed">{description}</p>
    </div>
  );
}

function PricingCard({ tier, price, features, isPopular = false }) {
  return (
    <div className={`relative rounded-2xl border-2 bg-white p-8 ${isPopular ? 'border-teal-500 shadow-2xl scale-105' : 'border-slate-200'}`}>
      {isPopular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <span className="inline-flex items-center gap-1 px-4 py-1 rounded-full bg-gradient-to-r from-teal-600 to-sky-600 text-white text-sm font-semibold">
            <Star className="h-4 w-4" /> MOST POPULAR
          </span>
        </div>
      )}
      <div className="text-center mb-6">
        <h3 className="text-2xl font-bold mb-2">{tier}</h3>
        <div className="text-4xl font-bold text-teal-600">${price}</div>
        <div className="text-sm text-slate-600 mt-1">Lifetime Access</div>
      </div>
      <ul className="space-y-3 mb-8">
        {features.map((feature, idx) => (
          <li key={idx} className="flex items-start gap-2">
            <Check className="h-5 w-5 text-teal-600 flex-shrink-0 mt-0.5" />
            <span className="text-slate-700">{feature}</span>
          </li>
        ))}
      </ul>
      <PrimaryButton href="/onboarding" className="w-full">
        Get This Deal
      </PrimaryButton>
    </div>
  );
}

function FAQ({ question, answer }) {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className="border-b border-slate-200 pb-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left py-4 hover:text-teal-600 transition"
      >
        <span className="text-lg font-semibold">{question}</span>
        <ChevronDown className={`h-5 w-5 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <p className="text-slate-600 leading-relaxed pb-2">{answer}</p>
      )}
    </div>
  );
}

export default function Landing() {
  const { user, ready } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  return (
    <div className="min-h-screen bg-white text-slate-900">
      {/* Top nav */}
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <LogoMark />
            
            {/* Desktop Nav */}
            <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
              <a href="#features" className="text-slate-700 hover:text-teal-600 transition">Features</a>
              <a href="#pricing" className="text-slate-700 hover:text-teal-600 transition">Pricing</a>
              <a href="#faq" className="text-slate-700 hover:text-teal-600 transition">FAQ</a>
            </nav>
            
            <div className="hidden md:flex items-center gap-4">
              <a href="/login" className="text-sm font-medium text-slate-700 hover:text-teal-600 transition">
                Sign in
              </a>
              <PrimaryButton href="/onboarding">
                Get Lifetime Deal <ArrowRight className="h-4 w-4" />
              </PrimaryButton>
            </div>

            {/* Mobile menu button */}
            <button 
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>

          {/* Mobile Nav */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 space-y-4 border-t border-slate-200">
              <a href="#features" className="block text-slate-700 hover:text-teal-600">Features</a>
              <a href="#pricing" className="block text-slate-700 hover:text-teal-600">Pricing</a>
              <a href="#faq" className="block text-slate-700 hover:text-teal-600">FAQ</a>
              <hr className="border-slate-200" />
              <a href="/login" className="block text-slate-700 hover:text-teal-600">Sign in</a>
              <PrimaryButton href="/onboarding" className="w-full">Get Lifetime Deal</PrimaryButton>
            </div>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-teal-50 via-sky-50 to-purple-50 -z-10" />
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-20 md:py-28">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <AppSumoBadge />
              <h1 className="mt-6 text-5xl md:text-6xl font-bold tracking-tight leading-tight">
                Manage YouTube Like a{" "}
                <span className="bg-gradient-to-r from-teal-600 to-sky-600 bg-clip-text text-transparent">
                  Production Studio
                </span>
              </h1>
              <p className="mt-6 text-xl text-slate-600 leading-relaxed">
                End-to-end content workflow: From idea to publish with AI-powered optimization, 
                team collaboration, and data-driven insights. Perfect for solo creators and production teams.
              </p>
              
              <div className="mt-10 flex flex-wrap items-center gap-4">
                <PrimaryButton href="/onboarding" className="text-lg">
                  Claim Lifetime Deal <Zap className="h-5 w-5" />
                </PrimaryButton>
              </div>

              {/* Social Proof */}
              <div className="mt-10 flex items-center gap-8">
                <div>
                  <div className="flex items-center gap-1">
                    {[1,2,3,4,5].map(i => <Star key={i} className="h-5 w-5 fill-amber-400 text-amber-400" />)}
                  </div>
                  <p className="mt-1 text-sm text-slate-600">
                    <span className="font-bold text-slate-900">4.9/5</span> from 127+ users
                  </p>
                </div>
                <div className="h-12 w-px bg-slate-300" />
                <div>
                  <p className="text-2xl font-bold text-slate-900">2,000+</p>
                  <p className="text-sm text-slate-600">Videos Managed</p>
                </div>
              </div>
            </div>

            <HeroIllustration />
          </div>
        </div>
      </section>

      {/* Trust Bar */}
      <section className="border-y border-slate-200 bg-slate-50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <p className="text-sm font-medium text-slate-600">TRUSTED BY CREATORS & TEAMS</p>
            <div className="flex items-center gap-8 flex-wrap justify-center">
              <div className="h-8 w-24 rounded bg-slate-200" />
              <div className="h-8 w-24 rounded bg-slate-200" />
              <div className="h-8 w-24 rounded bg-slate-200" />
              <div className="h-8 w-24 rounded bg-slate-200" />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 md:py-28 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Everything You Need to Scale YouTube
            </h2>
            <p className="text-xl text-slate-600">
              Professional-grade tools designed for content creators who mean business
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard 
              icon={LayoutGrid}
              title="Kanban Workflow"
              description="Drag-and-drop pipeline from idea to publish. Track every video through research, scripting, filming, editing, and publishing stages."
            />
            <FeatureCard 
              icon={BarChart3}
              title="YouTube Analytics"
              description="Real-time performance metrics, CTR optimization, view trends, and revenue tracking. Make data-driven content decisions."
            />
            <FeatureCard 
              icon={Sparkles}
              title="AI Content Assistant"
              description="Generate SEO-optimized titles, descriptions, tags, and thumbnails. Powered by Gemini AI for maximum reach."
            />
            <FeatureCard 
              icon={Users}
              title="Team Collaboration"
              description="Role-based permissions for writers, editors, and managers. Assign tasks, track progress, and streamline communication."
            />
            <FeatureCard 
              icon={Calendar}
              title="Content Calendar"
              description="Plan and schedule weeks ahead. Visualize your publishing schedule and maintain consistent upload frequency."
            />
            <FeatureCard 
              icon={Target}
              title="SEO Research Tools"
              description="Keyword analysis, competitor tracking, and trend discovery. Find winning content ideas backed by data."
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 md:py-28 bg-slate-50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              From Idea to Published in 4 Steps
            </h2>
            <p className="text-xl text-slate-600">
              Streamlined workflow that saves hours every week
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { icon: FileText, step: "1", title: "Research & Plan", desc: "Use AI to find winning topics and plan content" },
              { icon: Video, step: "2", title: "Create & Edit", desc: "Collaborate with team through production pipeline" },
              { icon: Sparkles, step: "3", title: "Optimize & Schedule", desc: "AI-powered SEO optimization and scheduling" },
              { icon: TrendingUp, step: "4", title: "Publish & Analyze", desc: "Track performance and iterate for growth" },
            ].map((item, idx) => (
              <div key={idx} className="relative">
                <div className="text-center">
                  <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-teal-500 to-sky-500 text-white mb-4">
                    <item.icon className="h-8 w-8" />
                  </div>
                  <div className="absolute top-0 right-0 text-6xl font-bold text-slate-200 -z-10">
                    {item.step}
                  </div>
                  <h3 className="text-xl font-bold mb-2">{item.title}</h3>
                  <p className="text-slate-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 md:py-28 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-orange-100 border border-orange-200 mb-6">
              <span className="text-orange-600 font-bold text-sm">⚡ LIMITED TIME APPSUMO DEAL</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Lifetime Access, One-Time Payment
            </h2>
            <p className="text-xl text-slate-600">
              No monthly fees. No annual contracts. Pay once, own forever.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <PricingCard 
              tier="Tier 1"
              price="59"
              features={[
                "1 YouTube Channel",
                "50 Videos per month",
                "Kanban Workflow",
                "Basic Analytics",
                "AI Title Generator",
                "Email Support",
                "60-day Money-back Guarantee"
              ]}
            />
            <PricingCard 
              tier="Tier 2"
              price="119"
              isPopular={true}
              features={[
                "3 YouTube Channels",
                "200 Videos per month",
                "Advanced Kanban + Automation",
                "Full Analytics Suite",
                "AI Content Assistant (All Features)",
                "Team Collaboration (5 users)",
                "Priority Support",
                "60-day Money-back Guarantee"
              ]}
            />
            <PricingCard 
              tier="Tier 3"
              price="199"
              features={[
                "Unlimited Channels",
                "Unlimited Videos",
                "Everything in Tier 2",
                "White-label Reports",
                "API Access",
                "Team Collaboration (15 users)",
                "Dedicated Success Manager",
                "60-day Money-back Guarantee"
              ]}
            />
          </div>

          <div className="mt-12 text-center">
            <p className="text-lg text-slate-600 mb-4">
              <Shield className="inline h-5 w-5 text-green-600 mr-2" />
              All plans include lifetime updates and 60-day money-back guarantee
            </p>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 md:py-28 bg-slate-50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Loved by YouTubers Worldwide
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { name: "Sarah Chen", role: "Tech Reviewer, 250K subs", text: "Cut my video production time by 40%. The AI SEO tools alone are worth the price!" },
              { name: "Mike Rodriguez", role: "Gaming Channel, 500K subs", text: "Finally, a tool that handles the business side so I can focus on creating content." },
              { name: "Emma Watson", role: "Education Creator, 100K subs", text: "Team collaboration features are game-changing. My editor and writer stay in perfect sync." },
            ].map((testimonial, idx) => (
              <div key={idx} className="rounded-2xl border-2 border-slate-200 bg-white p-8">
                <div className="flex items-center gap-1 mb-4">
                  {[1,2,3,4,5].map(i => <Star key={i} className="h-4 w-4 fill-amber-400 text-amber-400" />)}
                </div>
                <p className="text-slate-700 mb-6 leading-relaxed">"{testimonial.text}"</p>
                <div>
                  <p className="font-bold text-slate-900">{testimonial.name}</p>
                  <p className="text-sm text-slate-600">{testimonial.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 md:py-28 bg-white">
        <div className="mx-auto max-w-3xl px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Frequently Asked Questions
            </h2>
          </div>

          <div className="space-y-2">
            <FAQ 
              question="What does 'lifetime access' mean?"
              answer="You pay once and get access forever. This includes all future updates, new features, and improvements. No hidden fees, no annual renewals."
            />
            <FAQ 
              question="Can I upgrade my tier later?"
              answer="Yes! You can upgrade to a higher tier at any time by paying the difference. Contact our support team for upgrade assistance."
            />
            <FAQ 
              question="Do you offer refunds?"
              answer="Absolutely. We offer a 60-day money-back guarantee, no questions asked. If Viewz isn't right for you, just email us for a full refund."
            />
            <FAQ 
              question="How does the AI content assistant work?"
              answer="Our AI (powered by Gemini) analyzes your niche, competitors, and trending topics to generate SEO-optimized titles, descriptions, and tags. It learns from your channel's performance to improve suggestions over time."
            />
            <FAQ 
              question="Can I use this for multiple channels?"
              answer="Yes! Tier 1 supports 1 channel, Tier 2 supports 3 channels, and Tier 3 supports unlimited channels. Perfect for agencies or multi-channel creators."
            />
            <FAQ 
              question="Is there a free trial?"
              answer="We provide a 60-day money-back guarantee instead of a traditional trial. Try Viewz risk-free and if it's not right for you, get a full refund."
            />
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 md:py-28 bg-gradient-to-br from-teal-600 via-sky-600 to-purple-600 text-white">
        <div className="mx-auto max-w-4xl px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
            Join 2,000+ Creators Managing 10,000+ Videos
          </h2>
          <p className="text-xl text-white/90 mb-10 max-w-2xl mx-auto">
            Stop juggling spreadsheets and scattered tools. Get the all-in-one YouTube production platform built for scale.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a 
              href="/onboarding"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-teal-700 rounded-xl font-bold text-lg hover:bg-slate-50 hover:shadow-2xl transition-all duration-200"
            >
              Claim Your Lifetime Deal <ArrowRight className="h-5 w-5" />
            </a>
          </div>
          <p className="mt-8 text-white/75">
            <Clock className="inline h-5 w-5 mr-2" />
            Limited AppSumo deal - prices increase after launch
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <LogoMark />
              <p className="mt-4 text-sm text-slate-600">
                Professional YouTube management platform for creators and teams.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                <li><a href="#features" className="hover:text-teal-600">Features</a></li>
                <li><a href="#pricing" className="hover:text-teal-600">Pricing</a></li>
                <li><a href="/public/roadmap" className="hover:text-teal-600">Roadmap</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                <li><a href="/public/about" className="hover:text-teal-600">About</a></li>
                <li><a href="/public/support" className="hover:text-teal-600">Support</a></li>
                <li><a href="/public/privacy" className="hover:text-teal-600">Privacy</a></li>
                <li><a href="/public/terms" className="hover:text-teal-600">Terms</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Connect</h4>
              <ul className="space-y-2 text-sm text-slate-600">
                <li><a href="#" className="hover:text-teal-600">Twitter</a></li>
                <li><a href="#" className="hover:text-teal-600">YouTube</a></li>
                <li><a href="#" className="hover:text-teal-600">LinkedIn</a></li>
                <li><a href="#" className="hover:text-teal-600">Discord</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-slate-200 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-600">
            <div>© {new Date().getFullYear()} ARA INC BD — Viewz. All rights reserved.</div>
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-600" />
              <span>Secure SSL Encryption</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
