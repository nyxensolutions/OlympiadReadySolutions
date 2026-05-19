"use client";

import Link from "next/link";
import { ArrowLeft, Shield } from "lucide-react";

interface LegalPageLayoutProps {
  title: string;
  lastUpdated: string;
  children: React.ReactNode;
}

export function LegalPageLayout({ title, lastUpdated, children }: LegalPageLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top bar */}
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-3xl items-center gap-3 px-4 py-4">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Link>
          <div className="flex items-center gap-2 ml-2">
            <Shield className="h-5 w-5 text-brand-600" />
            <span className="text-sm font-semibold text-slate-700">OlympiadReady Legal</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <main className="mx-auto max-w-3xl px-4 py-10 sm:py-16">
        <div className="rounded-2xl border border-slate-200 bg-white px-8 py-10 shadow-sm sm:px-12">
          <div className="mb-8 border-b border-slate-100 pb-6">
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">{title}</h1>
            <p className="mt-2 text-sm text-slate-500">Last updated: {lastUpdated}</p>
            <p className="mt-1 text-xs text-slate-400">
              This policy applies to OlympiadReady, a product of{" "}
              <a href="https://nyxensolutions.net" target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:underline">
                Nyxen Solutions
              </a>
              .
            </p>
          </div>
          <div className="prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-slate-800 prose-h2:mt-8 prose-h2:text-xl prose-h3:text-base prose-p:text-slate-600 prose-p:leading-relaxed prose-li:text-slate-600 prose-a:text-brand-600">
            {children}
          </div>
        </div>
      </main>

      {/* Footer strip */}
      <div className="border-t border-slate-200 py-6 text-center text-xs text-slate-400">
        © {new Date().getFullYear()} Nyxen Solutions · All rights reserved ·{" "}
        <Link href="/privacy" className="hover:text-brand-600">Privacy</Link>{" · "}
        <Link href="/terms" className="hover:text-brand-600">Terms</Link>{" · "}
        <Link href="/cookies" className="hover:text-brand-600">Cookies</Link>{" · "}
        <Link href="/refund" className="hover:text-brand-600">Refund</Link>
      </div>
    </div>
  );
}
