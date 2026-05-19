"use client";

import Link from "next/link";
import Image from "next/image";
import { BookOpen, Calendar, Crown, FileText, LayoutDashboard, LogIn, Menu, X } from "lucide-react";
import { useState } from "react";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton
} from "@clerk/nextjs";

export type ActivePage =
  | "home"
  | "dashboard"
  | "topics"
  | "weekly-exam"
  | "practice-papers"
  | "olympiad-dates";

export function AppHeader({ active }: { active?: ActivePage }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/50 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <div className="relative h-12 w-12 shrink-0">
            <Image
              src="/logo.png"
              alt="OlympiadReady"
              fill
              sizes="48px"
              className="object-contain"
              priority
            />
          </div>
          <span className="text-lg font-bold tracking-tight text-slate-900">OlympiadReady</span>
        </Link>

        {/* Center nav — signed-out: anchor links; signed-in: app nav */}
        <SignedOut>
          <nav className="hidden flex-1 items-center justify-center gap-6 sm:flex">
            <a href="#features" className="text-sm font-medium text-slate-600 transition hover:text-brand-600">Features</a>
            <a href="#how-it-works" className="text-sm font-medium text-slate-600 transition hover:text-brand-600">How It Works</a>
            <Link href="/olympiad-dates" className={`text-sm font-medium transition ${active === "olympiad-dates" ? "text-brand-600" : "text-slate-600 hover:text-brand-600"}`}>
              Olympiad Dates
            </Link>
          </nav>
        </SignedOut>

        <SignedIn>
          {/* Desktop nav */}
          <nav className="hidden flex-1 items-center justify-center gap-0.5 sm:flex flex-wrap">
            <NavLink href="/" label="Practice" active={active === "home"} />
            <NavLink href="/topics" label="Syllabus Map" icon={<BookOpen className="h-3.5 w-3.5" />} active={active === "topics"} />
            <NavLink href="/dashboard" label="Dashboard" icon={<LayoutDashboard className="h-3.5 w-3.5" />} active={active === "dashboard"} />
            <NavLink href="/practice-papers" label="Question Papers" icon={<FileText className="h-3.5 w-3.5" />} active={active === "practice-papers"} accent />
            <NavLink href="/olympiad-dates" label="Dates" icon={<Calendar className="h-3.5 w-3.5" />} active={active === "olympiad-dates"} />
            <NavLink href="/weekly-exam" label="Weekly Exam" icon={<Crown className="h-3.5 w-3.5" />} active={active === "weekly-exam"} amber />
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

          {/* Mobile menu toggle */}
          <button
            type="button"
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 sm:hidden"
            onClick={() => setMobileOpen((v) => !v)}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="border-t border-slate-200 bg-white px-4 py-3 sm:hidden">
          <SignedOut>
            <div className="flex flex-col gap-1">
              <a href="#features" className="rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" onClick={() => setMobileOpen(false)}>Features</a>
              <a href="#how-it-works" className="rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" onClick={() => setMobileOpen(false)}>How It Works</a>
              <Link href="/olympiad-dates" className="rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" onClick={() => setMobileOpen(false)}>Olympiad Dates</Link>
            </div>
          </SignedOut>
          <SignedIn>
            <div className="flex flex-col gap-1">
              <MobileNavLink href="/" label="Practice" onClick={() => setMobileOpen(false)} />
              <MobileNavLink href="/topics" label="Syllabus Map" onClick={() => setMobileOpen(false)} />
              <MobileNavLink href="/dashboard" label="Dashboard" onClick={() => setMobileOpen(false)} />
              <MobileNavLink href="/practice-papers" label="Practice Papers" onClick={() => setMobileOpen(false)} />
              <MobileNavLink href="/olympiad-dates" label="Olympiad Dates" onClick={() => setMobileOpen(false)} />
              <MobileNavLink href="/weekly-exam" label="Weekly Exam" onClick={() => setMobileOpen(false)} />
            </div>
          </SignedIn>
        </div>
      )}
    </header>
  );
}

function NavLink({
  href, label, icon, active, accent, amber
}: {
  href: string; label: string; icon?: React.ReactNode; active?: boolean; accent?: boolean; amber?: boolean;
}) {
  const base = "inline-flex items-center gap-1.5 rounded-lg px-2.5 py-2 text-sm font-medium transition whitespace-nowrap";
  const cls = active
    ? amber
      ? `${base} bg-amber-50 text-amber-700`
      : accent
      ? `${base} bg-brand-50 text-brand-700`
      : `${base} bg-brand-50 text-brand-700`
    : amber
    ? `${base} text-slate-600 hover:bg-amber-50 hover:text-amber-700`
    : accent
    ? `${base} text-slate-600 hover:bg-brand-50 hover:text-brand-700`
    : `${base} text-slate-600 hover:bg-slate-100 hover:text-slate-900`;

  return (
    <Link href={href} className={cls}>
      {icon}
      {label}
    </Link>
  );
}

function MobileNavLink({ href, label, onClick }: { href: string; label: string; onClick?: () => void }) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className="rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
    >
      {label}
    </Link>
  );
}
