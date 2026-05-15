"use client";

import Link from "next/link";
import { BookOpen, Crown, GraduationCap, LayoutDashboard, LogIn } from "lucide-react";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton
} from "@clerk/nextjs";

export function AppHeader({ active }: { active?: "home" | "dashboard" | "topics" | "weekly-exam" }) {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/50 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <GraduationCap className="h-6 w-6 text-brand-600" />
          <span className="text-lg font-bold tracking-tight text-slate-900">OlympiadReady</span>
        </Link>

        {/* Center nav — landing anchor links (signed-out) or app nav (signed-in) */}
        <SignedOut>
          <nav className="hidden flex-1 items-center justify-center gap-8 sm:flex">
            <a href="#features" className="text-sm font-medium text-slate-600 transition hover:text-brand-600">
              Features
            </a>
            <a href="#how-it-works" className="text-sm font-medium text-slate-600 transition hover:text-brand-600">
              How It Works
            </a>
            <a href="#testimonials" className="text-sm font-medium text-slate-600 transition hover:text-brand-600">
              Testimonials
            </a>
          </nav>
        </SignedOut>

        <SignedIn>
          <nav className="hidden flex-1 items-center justify-center gap-1 sm:flex">
            <Link
              href="/"
              className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                active === "home" ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              Practice
            </Link>
            <Link
              href="/topics"
              className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition ${
                active === "topics" ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              <BookOpen className="h-3.5 w-3.5" />
              Syllabus Map
            </Link>
            <Link
              href="/dashboard"
              className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition ${
                active === "dashboard" ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              <LayoutDashboard className="h-3.5 w-3.5" />
              Dashboard
            </Link>
            <Link
              href="/weekly-exam"
              className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition ${
                active === "weekly-exam" ? "bg-amber-50 text-amber-700" : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              <Crown className="h-3.5 w-3.5" />
              Weekly Exam
            </Link>
          </nav>
        </SignedIn>

        {/* Right side */}
        <div className="flex items-center gap-2">
          <SignedIn>
            <UserButton afterSignOutUrl="/" />
          </SignedIn>
          <SignedOut>
            <SignInButton mode="modal">
              <button className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50">
                <LogIn className="h-4 w-4" />
                <span className="hidden sm:inline">Sign in</span>
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="rounded-lg bg-brand-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-brand-700">
                <span className="hidden sm:inline">Sign up free</span>
                <span className="sm:hidden">Start free</span>
              </button>
            </SignUpButton>
          </SignedOut>
        </div>
      </div>
    </header>
  );
}
