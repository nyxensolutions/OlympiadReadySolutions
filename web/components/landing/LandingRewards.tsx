"use client";

import Link from "next/link";

const REWARD_TIERS = [
  {
    icon: "🎓",
    name: "Digital Certificate",
    condition: "Earn any badge",
    color: "from-indigo-500 to-blue-500",
    bg: "bg-indigo-50",
    border: "border-indigo-100",
    text: "text-indigo-700",
    badges: ["🚀", "🎯", "⭐", "🔥"],
    detail: "A personalised, print-ready PDF certificate for every badge you unlock.",
  },
  {
    icon: "🏅",
    name: "Title & Leaderboard Rank",
    condition: "Earn 3+ badges",
    color: "from-amber-400 to-orange-500",
    bg: "bg-amber-50",
    border: "border-amber-100",
    text: "text-amber-700",
    badges: ["Rising Star", "Knowledge Seeker", "Olympiad Contender", "Champion Scholar"],
    isTitles: true,
    detail: "Your earned title appears on the public leaderboard beneath your name.",
  },
  {
    icon: "🏆",
    name: "Physical Medal",
    condition: "Earn ALL 18 badges",
    color: "from-purple-500 to-indigo-600",
    bg: "bg-purple-50",
    border: "border-purple-100",
    text: "text-purple-700",
    badges: ["💪", "💯", "🔥", "🌟"],
    detail: "Become an Olympiad Legend and receive a physical medal shipped to your address.",
    highlight: true,
  },
];

const BADGE_SHOWCASE = [
  { emoji: "🚀", label: "First Step",       hint: "Complete 1 test" },
  { emoji: "🎯", label: "Sharpshooter",     hint: "Score 90%+" },
  { emoji: "⭐", label: "Perfect Score",     hint: "100% on any test" },
  { emoji: "🔥", label: "3-Day Streak",      hint: "3 days in a row" },
  { emoji: "⚡", label: "Speed Demon",       hint: "10Q under 5 min" },
  { emoji: "🌟", label: "All-Rounder",       hint: "90%+ in 3 subjects" },
  { emoji: "🏆", label: "Mock Master",       hint: "3 full mock exams" },
  { emoji: "💯", label: "Century",           hint: "100 tests completed" },
];

export function LandingRewards() {
  return (
    <section className="bg-white py-16 border-t border-slate-100">
      <div className="mx-auto max-w-5xl px-4">

        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 rounded-full border border-purple-200 bg-purple-50 px-4 py-1.5 text-sm font-semibold text-purple-700 mb-3">
            🎖️ Badges & Rewards
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 sm:text-3xl">
            Learn, earn, and get rewarded
          </h2>
          <p className="mt-2 text-sm text-slate-500 max-w-xl mx-auto">
            Every test you complete earns you badges. Collect them all to unlock titles, certificates, and real physical rewards.
          </p>
        </div>

        {/* Badge showcase */}
        <div className="flex flex-wrap justify-center gap-3 mb-10">
          {BADGE_SHOWCASE.map((b) => (
            <div
              key={b.label}
              className="flex flex-col items-center gap-1 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 w-24 text-center hover:border-indigo-300 hover:bg-indigo-50 transition"
            >
              <span className="text-2xl">{b.emoji}</span>
              <span className="text-[11px] font-semibold text-slate-700 leading-tight">{b.label}</span>
              <span className="text-[10px] text-slate-400 leading-tight">{b.hint}</span>
            </div>
          ))}
          <div className="flex flex-col items-center justify-center gap-1 bg-indigo-600 border border-indigo-600 rounded-xl px-3 py-2.5 w-24 text-center">
            <span className="text-2xl">+</span>
            <span className="text-[11px] font-semibold text-white leading-tight">10 more</span>
            <span className="text-[10px] text-indigo-200 leading-tight">badges to earn</span>
          </div>
        </div>

        {/* Reward tiers */}
        <div className="grid gap-4 sm:grid-cols-3">
          {REWARD_TIERS.map((tier) => (
            <div
              key={tier.name}
              className={`relative rounded-2xl border p-5 flex flex-col gap-3 ${tier.bg} ${tier.border} ${tier.highlight ? "ring-2 ring-purple-400 shadow-lg" : ""}`}
            >
              {tier.highlight && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-[10px] font-bold px-3 py-0.5 rounded-full uppercase tracking-wider">
                  Ultimate Reward
                </div>
              )}

              {/* Icon + name */}
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${tier.color} flex items-center justify-center text-xl shadow-sm`}>
                  {tier.icon}
                </div>
                <div>
                  <div className={`text-sm font-bold ${tier.text}`}>{tier.name}</div>
                  <div className="text-[11px] text-slate-500">{tier.condition}</div>
                </div>
              </div>

              {/* Sample badges / titles */}
              <div className="flex flex-wrap gap-1.5">
                {tier.isTitles
                  ? tier.badges.map((t) => (
                      <span key={t} className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${tier.bg} ${tier.text} ring-1 ring-current/30`}>
                        {t}
                      </span>
                    ))
                  : tier.badges.map((emoji) => (
                      <span key={emoji} className="text-lg">{emoji}</span>
                    ))}
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">{tier.detail}</p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-8 text-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-3 rounded-xl transition text-sm shadow-sm"
          >
            Start earning badges →
          </Link>
          <p className="mt-2 text-xs text-slate-400">
            Already have an account? Your badges are waiting on your dashboard.
          </p>
        </div>
      </div>
    </section>
  );
}
