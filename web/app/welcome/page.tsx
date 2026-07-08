"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { BookOpen, Crown, FileText, Sparkles, Zap } from "lucide-react";

export default function WelcomePage() {
  const router = useRouter();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Fire Google Ads signup conversion
    if (typeof window !== "undefined") {
      (window as any).dataLayer = (window as any).dataLayer || [];
      const gtag = (window as any).gtag || function () { (window as any).dataLayer.push(arguments); };
      gtag('event', 'conversion', { send_to: 'AW-18206317015/sUnNCNPqjbgcENezuelD' });
    }
    // Animate in
    const t = setTimeout(() => setVisible(true), 60);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-brand-50 to-white flex flex-col items-center justify-center px-4 py-12">
      <div
        className={`w-full max-w-lg transition-all duration-500 ${
          visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        }`}
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mb-4">
            <Image src="/logo.png" alt="OlympiadReady" width={72} height={72} className="mx-auto" />
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900">You're in!</h1>
          <p className="mt-2 text-lg text-slate-600">
            Welcome to <span className="font-semibold text-brand-700">OlympiadReady</span> — India's #1 Olympiad prep platform.
          </p>
        </div>

        {/* Free tier value card */}
        <div className="rounded-2xl border border-brand-100 bg-white shadow-sm p-6 mb-4">
          <p className="text-sm font-semibold text-brand-700 uppercase tracking-wide mb-4">
            What's free for you right now
          </p>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <BookOpen className="h-5 w-5 text-brand-500 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-semibold text-slate-800">5 AI-generated practice papers</p>
                <p className="text-xs text-slate-500">Personalised to your grade and subject, with smart difficulty progression.</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Sparkles className="h-5 w-5 text-brand-500 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-semibold text-slate-800">AI explanations for every question</p>
                <p className="text-xs text-slate-500">Understand exactly why an answer is right — not just what the answer is.</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-brand-500 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-semibold text-slate-800">Download sample PDFs</p>
                <p className="text-xs text-slate-500">Get printable Olympiad papers for offline practice.</p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Zap className="h-5 w-5 text-brand-500 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-semibold text-slate-800">Streaks, leaderboards & badges</p>
                <p className="text-xs text-slate-500">Stay motivated and track your progress every day.</p>
              </div>
            </li>
          </ul>
        </div>

        {/* Upgrade teaser */}
        <div className="rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4 mb-6 flex items-start gap-3">
          <Crown className="h-5 w-5 text-amber-600 mt-0.5 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-amber-900">Want unlimited practice?</p>
            <p className="text-xs text-amber-700 mt-0.5">
              Upgrade to Pro for just <span className="font-bold">₹129/subject/month</span> — unlimited papers, all subjects, priority support.
            </p>
          </div>
        </div>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row gap-3">
          <Link
            href="/"
            className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white shadow hover:bg-brand-700 transition"
          >
            <BookOpen className="h-4 w-4" />
            Start Practising Free
          </Link>
          <Link
            href="/dashboard"
            className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl border border-amber-300 bg-white px-6 py-3 text-sm font-bold text-amber-700 hover:bg-amber-50 transition"
          >
            <Crown className="h-4 w-4" />
            See Upgrade Plans
          </Link>
        </div>

        <p className="mt-4 text-center text-xs text-slate-400">
          No credit card needed. Start with 5 free papers, upgrade any time.
        </p>
      </div>
    </div>
  );
}
