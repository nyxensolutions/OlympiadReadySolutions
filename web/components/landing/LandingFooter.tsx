"use client";

import Link from "next/link";
import { GraduationCap, Mail, MessageCircle } from "lucide-react";

export function LandingFooter() {
  return (
    <footer className="border-t border-slate-200 bg-white px-4 py-12 sm:py-16">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">

          {/* Brand */}
          <div className="lg:col-span-1">
            <Link href="/" className="mb-4 flex items-center gap-2">
              <GraduationCap className="h-6 w-6 text-brand-600" />
              <span className="text-lg font-bold text-slate-900">OlympiadReady</span>
            </Link>
            <p className="text-sm leading-relaxed text-slate-600">
              India&apos;s AI-powered Olympiad preparation platform for students in Classes 1–12.
              Fresh AI-generated questions, instant explanations, and mastery tracking — all in one place.
            </p>
            <div className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">
              <span className="h-1.5 w-1.5 rounded-full bg-brand-500" />
              Powered by AI — no repeats, ever
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="mb-4 font-semibold text-slate-900">Product</h3>
            <ul className="space-y-2.5 text-sm text-slate-600">
              <li><Link href="/#features" className="transition hover:text-brand-600">Features</Link></li>
              <li><Link href="/#how-it-works" className="transition hover:text-brand-600">How It Works</Link></li>
              <li><Link href="/topics" className="transition hover:text-brand-600">Syllabus Map</Link></li>
              <li><Link href="/weekly-exam" className="transition hover:text-brand-600">Weekly Exam</Link></li>
              <li><Link href="/dashboard" className="transition hover:text-brand-600">Dashboard</Link></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="mb-4 font-semibold text-slate-900">Contact Us</h3>
            <ul className="space-y-3 text-sm">
              <li>
                <a
                  href="https://wa.me/919953699143"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-slate-600 transition hover:text-emerald-600"
                >
                  <MessageCircle className="h-4 w-4 shrink-0 text-emerald-500" />
                  +91 99536 99143
                </a>
                <p className="ml-6 mt-0.5 text-xs text-slate-400">WhatsApp · Mon–Sat, 9 am–6 pm</p>
              </li>
              <li>
                <a
                  href="mailto:nyxencloud@gmail.com"
                  className="inline-flex items-center gap-2 text-slate-600 transition hover:text-brand-600"
                >
                  <Mail className="h-4 w-4 shrink-0 text-brand-500" />
                  nyxencloud@gmail.com
                </a>
                <p className="ml-6 mt-0.5 text-xs text-slate-400">Queries &amp; support</p>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="mb-4 font-semibold text-slate-900">Legal</h3>
            <ul className="space-y-2.5 text-sm text-slate-600">
              <li><Link href="/privacy" className="transition hover:text-brand-600">Privacy Policy</Link></li>
              <li><Link href="/terms"   className="transition hover:text-brand-600">Terms of Service</Link></li>
              <li><Link href="/cookies" className="transition hover:text-brand-600">Cookie Policy</Link></li>
              <li><Link href="/refund"  className="transition hover:text-brand-600">Refund Policy</Link></li>
            </ul>
          </div>
        </div>

        <div className="my-8 h-px bg-slate-200" />

        {/* Bottom bar */}
        <div className="flex flex-col items-center justify-between gap-3 text-center sm:flex-row sm:text-left">
          <div>
            <p className="text-sm text-slate-500">
              &copy; 2026 <span className="font-semibold text-slate-700">Nyxen Solutions</span>. All rights reserved.
            </p>
            <p className="mt-0.5 text-xs text-slate-400">
              OlympiadReady is developed &amp; managed by{" "}
              <a
                href="https://nyxensolutions.net"
                target="_blank"
                rel="noopener noreferrer"
                className="text-brand-600 hover:underline"
              >
                Nyxen Solutions
              </a>
              {" · "}
              <a href="mailto:nyxencloud@gmail.com" className="hover:text-brand-600">
                nyxencloud@gmail.com
              </a>
            </p>
          </div>
          <div className="flex gap-5 text-xs text-slate-500">
            <Link href="/privacy" className="hover:text-brand-600">Privacy</Link>
            <Link href="/terms"   className="hover:text-brand-600">Terms</Link>
            <Link href="/cookies" className="hover:text-brand-600">Cookies</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
