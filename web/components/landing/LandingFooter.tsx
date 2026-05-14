"use client";

import Link from "next/link";
import { GraduationCap, Linkedin, Mail, Twitter } from "lucide-react";

export function LandingFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-slate-200 bg-white px-4 py-12 sm:py-16">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-8 sm:grid-cols-4">
          {/* Brand */}
          <div>
            <Link href="/" className="mb-4 flex items-center gap-2">
              <GraduationCap className="h-6 w-6 text-brand-600" />
              <span className="text-lg font-bold text-slate-900">OlympiadReady</span>
            </Link>
            <p className="text-sm text-slate-600">
              India&apos;s first AI-powered Olympiad preparation platform for students
              in Classes 1–12.
            </p>
          </div>

          {/* Product */}
          <div>
            <h3 className="mb-4 font-semibold text-slate-900">Product</h3>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>
                <a href="#features" className="transition hover:text-brand-600">
                  Features
                </a>
              </li>
              <li>
                <a href="#how-it-works" className="transition hover:text-brand-600">
                  How It Works
                </a>
              </li>
              <li>
                <a href="#testimonials" className="transition hover:text-brand-600">
                  Testimonials
                </a>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="mb-4 font-semibold text-slate-900">Company</h3>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>
                <Link href="/about" className="transition hover:text-brand-600">
                  About
                </Link>
              </li>
              <li>
                <Link href="/blog" className="transition hover:text-brand-600">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="/contact" className="transition hover:text-brand-600">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Social */}
          <div>
            <h3 className="mb-4 font-semibold text-slate-900">Follow us</h3>
            <div className="flex gap-3">
              <a
                href="#twitter"
                aria-label="Twitter"
                className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-600 transition hover:bg-brand-50 hover:text-brand-600"
              >
                <Twitter className="h-4 w-4" />
              </a>
              <a
                href="#linkedin"
                aria-label="LinkedIn"
                className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-600 transition hover:bg-brand-50 hover:text-brand-600"
              >
                <Linkedin className="h-4 w-4" />
              </a>
              <a
                href="mailto:hello@olympiadready.com"
                aria-label="Email"
                className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-600 transition hover:bg-brand-50 hover:text-brand-600"
              >
                <Mail className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>

        <div className="my-8 h-px bg-slate-200" />

        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p className="text-sm text-slate-600">
            &copy; {year} OlympiadReady. All rights reserved.
          </p>
          <div className="flex gap-6 text-sm">
            <Link href="/privacy" className="text-slate-600 transition hover:text-brand-600">
              Privacy
            </Link>
            <Link href="/terms" className="text-slate-600 transition hover:text-brand-600">
              Terms
            </Link>
            <Link href="/cookies" className="text-slate-600 transition hover:text-brand-600">
              Cookies
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
