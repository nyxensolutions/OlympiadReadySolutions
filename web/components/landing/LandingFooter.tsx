"use client";

import Link from "next/link";
import { GraduationCap, Mail, MessageCircle, Instagram, Facebook } from "lucide-react";

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

            {/* Social */}
            <div className="mt-5 flex items-center gap-3">
              <a
                href="https://www.instagram.com/olympiad.ready/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="OlympiadReady on Instagram"
                className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-500 transition hover:border-brand-200 hover:bg-brand-50 hover:text-brand-600"
              >
                <Instagram className="h-4 w-4" />
              </a>
              <a
                href="https://x.com/nyxensolutions"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="OlympiadReady on X"
                className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-500 transition hover:border-brand-200 hover:bg-brand-50 hover:text-brand-600"
              >
                <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="currentColor" aria-hidden="true">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.66l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231 5.45-6.231Zm-1.161 17.52h1.833L7.084 4.126H5.117l11.966 15.644Z" />
                </svg>
              </a>
              <a
                href="https://www.facebook.com/people/OlympiadReady/61590546326909/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="OlympiadReady on Facebook"
                className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-500 transition hover:border-brand-200 hover:bg-brand-50 hover:text-brand-600"
              >
                <Facebook className="h-4 w-4" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="mb-4 font-semibold text-slate-900">Product</h3>
            <ul className="space-y-2.5 text-sm text-slate-600">
              <li><Link href="/#features" className="transition hover:text-brand-600">Features</Link></li>
              <li><Link href="/#how-it-works" className="transition hover:text-brand-600">How It Works</Link></li>
              <li><Link href="/topics" className="transition hover:text-brand-600">Syllabus Map</Link></li>
              <li><Link href="/practice-papers" className="transition hover:text-brand-600">Practice Papers</Link></li>
              <li><Link href="/mock-exams" className="transition hover:text-brand-600">Mock Exams</Link></li>
              <li><Link href="/olympiad-dates" className="transition hover:text-brand-600">Olympiad Dates</Link></li>
              <li><Link href="/blog" className="transition hover:text-brand-600">Blog</Link></li>
              <li><Link href="/dashboard" className="transition hover:text-brand-600">Dashboard</Link></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="mb-4 font-semibold text-slate-900">Contact Us</h3>
            <ul className="space-y-3 text-sm">
              <li>
                <Link href="/contact" className="inline-flex items-center gap-2 text-slate-600 transition hover:text-brand-600">
                  <Mail className="h-4 w-4 shrink-0 text-brand-500" />
                  Send us a message
                </Link>
                <p className="ml-6 mt-0.5 text-xs text-slate-400">General queries &amp; support</p>
              </li>
              <li>
                <Link href="/contact?type=school" className="inline-flex items-center gap-2 text-slate-600 transition hover:text-purple-600">
                  <MessageCircle className="h-4 w-4 shrink-0 text-purple-500" />
                  School &amp; institution pricing
                </Link>
                <p className="ml-6 mt-0.5 text-xs text-slate-400">Custom packages for schools</p>
              </li>
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
