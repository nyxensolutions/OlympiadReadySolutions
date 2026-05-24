"use client";

import Link from "next/link";
import Image from "next/image";
import { BookOpen, Calendar, Crown, FileText, LayoutDashboard, LogIn, Menu, MicVocal, Receipt, X, Sparkles, Target } from "lucide-react";
import { useState } from "react";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton
} from "@clerk/nextjs";
import { PurchasesPanel } from "./PurchasesPanel";
import { UpgradeModal } from "./UpgradeModal";

export type ActivePage =
  | "home"
  | "dashboard"
  | "topics"
  | "weekly-exam"
  | "practice-papers"
  | "olympiad-dates"
  | "spell-bee";

export function AppHeader({ active }: { active?: ActivePage }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [upgradeOpen, setUpgradeOpen] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-slate-200/50 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <div className="relative h-10 w-10 sm:h-12 sm:w-12 shrink-0">
            <Image
              src="/logo.png"
              alt="OlympiadReady"
              fill
              sizes="(max-width: 640px) 40px, 48px"
              className="object-contain"
              priority
            />
          </div>
          <span className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 shrink-0">OlympiadReady</span>
        </Link>

        {/* Center nav — signed-out: anchor links; signed-in: app nav */}
        <SignedOut>
          <nav className="hidden flex-1 items-center justify-center gap-6 sm:flex ml-8">
            <Link href="/#features" className="text-sm font-medium text-slate-600 transition hover:text-brand-600">Features</Link>
            <Link href="/#how-it-works" className="text-sm font-medium text-slate-600 transition hover:text-brand-600">How It Works</Link>
            <Link href="/olympiad-dates" className={`text-sm font-medium transition ${active === "olympiad-dates" ? "text-brand-600" : "text-slate-600 hover:text-brand-600"}`}>
              Olympiad Dates
            </Link>
            <Link href="/#try-it" className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 px-3 py-1.5 text-sm font-semibold text-brand-700 transition hover:bg-brand-100 whitespace-nowrap">
              <Sparkles className="h-4 w-4" /> Try It
            </Link>
          </nav>
        </SignedOut>

        <SignedIn>
          {/* Desktop nav */}
          <nav className="hidden flex-1 items-center justify-start gap-0.5 lg:gap-1 sm:flex ml-2 lg:ml-4">
            <NavLink href="/" label="Practice" icon={<Target className="h-3.5 w-3.5" />} active={active === "home"} />
            <NavLink href="/topics" label="Syllabus Map" icon={<BookOpen className="h-3.5 w-3.5" />} active={active === "topics"} />
            <NavLink href="/dashboard" label="Dashboard" icon={<LayoutDashboard className="h-3.5 w-3.5" />} active={active === "dashboard"} />
            <NavLink href="/practice-papers" label="Question Papers" icon={<FileText className="h-3.5 w-3.5" />} active={active === "practice-papers"} accent />
            <NavLink href="/mock-exams" label="Mock Exams" icon={<Crown className="h-3.5 w-3.5" />} active={active === "mock-exams"} amber />
            <NavLink href="/spell-bee" label="Spell Bee" icon={<MicVocal className="h-3.5 w-3.5" />} active={active === "spell-bee"} violet />
          </nav>
        </SignedIn>

        {/* Right side */}
        <div className="flex items-center gap-1.5 shrink-0 ml-4">
          <SignedIn>
            <button
              type="button"
              onClick={() => setUpgradeOpen(true)}
              title="Upgrade to Pro"
              className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-achiever-300 bg-achiever-50 px-3 py-1.5 text-xs font-semibold text-achiever-700 transition hover:bg-achiever-100 hover:shadow-sm shrink-0 whitespace-nowrap"
            >
              <Crown className="h-3.5 w-3.5 shrink-0" />
              Go Pro
            </button>
            <Link
              href="/dashboard#purchases"
              title="My Purchases"
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-brand-600 shrink-0 whitespace-nowrap"
            >
              <Receipt className="h-4 w-4 shrink-0" />
              <span className="hidden lg:inline text-xs">Purchases</span>
            </Link>
            <UserButton afterSignOutUrl="/" />
          </SignedIn>
          <SignedOut>
            <SignInButton mode="modal">
              <span role="button" className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 whitespace-nowrap cursor-pointer">
                <LogIn className="h-4 w-4" />
                <span className="hidden sm:inline">Sign in</span>
              </span>
            </SignInButton>
            <SignUpButton mode="modal">
              <span role="button" className="rounded-lg bg-brand-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-brand-700 whitespace-nowrap cursor-pointer">
                <span className="hidden sm:inline">Sign up free</span>
                <span className="sm:hidden">Start free</span>
              </span>
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
              <Link href="/#try-it" className="rounded-lg px-3 py-2 text-sm font-semibold text-brand-700 bg-brand-50 hover:bg-brand-100 flex items-center gap-2" onClick={() => setMobileOpen(false)}><Sparkles className="h-4 w-4" /> Try It</Link>
              <Link href="/#features" className="rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" onClick={() => setMobileOpen(false)}>Features</Link>
              <Link href="/#how-it-works" className="rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" onClick={() => setMobileOpen(false)}>How It Works</Link>
              <Link href="/olympiad-dates" className="rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" onClick={() => setMobileOpen(false)}>Olympiad Dates</Link>
            </div>
          </SignedOut>
          <SignedIn>
            <div className="flex flex-col gap-1">
              <MobileNavLink href="/" label="Practice" onClick={() => setMobileOpen(false)} active={active === "home"} />
              <MobileNavLink href="/topics" label="Syllabus Map" onClick={() => setMobileOpen(false)} />
              <MobileNavLink href="/dashboard" label="Dashboard" onClick={() => setMobileOpen(false)} />
              <MobileNavLink href="/practice-papers" label="Practice Papers" onClick={() => setMobileOpen(false)} />
              <MobileNavLink href="/mock-exams" label="Mock Exams" onClick={() => setMobileOpen(false)} />
              <MobileNavLink href="/spell-bee" label="Spell Bee 🐝" onClick={() => setMobileOpen(false)} />
              <button
                type="button"
                onClick={() => { setMobileOpen(false); setUpgradeOpen(true); }}
                className="mt-1 flex items-center gap-2 rounded-lg border border-achiever-300 bg-achiever-50 px-3 py-2.5 text-sm font-semibold text-achiever-700 hover:bg-achiever-100"
              >
                <Crown className="h-4 w-4" /> Upgrade to Pro
              </button>
            </div>
          </SignedIn>
        </div>
      )}
    </header>

    {upgradeOpen && (
      <UpgradeModal
        open={upgradeOpen}
        onClose={() => setUpgradeOpen(false)}
        onUpgraded={() => setUpgradeOpen(false)}
        reason="Unlock Level 2 practice, unlimited papers, detailed AI explanations and more."
      />
    )}
    </>
  );
}

function NavLink({
  href, label, icon, active, accent, amber, violet
}: {
  href: string; label: string; icon?: React.ReactNode; active?: boolean; accent?: boolean; amber?: boolean; violet?: boolean;
}) {
  const base = "inline-flex shrink-0 items-center gap-1 rounded-lg px-1.5 lg:px-2 py-1.5 text-xs lg:text-[13px] font-medium transition whitespace-nowrap";
  const cls = active
    ? violet
      ? `${base} bg-violet-50 text-violet-700`
      : amber
      ? `${base} bg-amber-50 text-amber-700`
      : accent
      ? `${base} bg-brand-50 text-brand-700`
      : `${base} bg-brand-50 text-brand-700`
    : violet
    ? `${base} text-slate-600 hover:bg-violet-50 hover:text-violet-700`
    : amber
    ? `${base} text-slate-600 hover:bg-amber-50 hover:text-amber-700`
    : accent
    ? `${base} text-slate-600 hover:bg-brand-50 hover:text-brand-700`
    : `${base} text-slate-600 hover:bg-slate-100 hover:text-slate-900`;

  return (
    <Link 
      href={href} 
      className={cls}
      onClick={(e) => {
        if (active) {
          e.preventDefault();
          window.location.reload();
        }
      }}
    >
      {icon}
      {label}
    </Link>
  );
}

function MobileNavLink({ href, label, onClick, active }: { href: string; label: string; onClick?: () => void; active?: boolean }) {
  return (
    <Link
      href={href}
      onClick={(e) => {
        if (active) {
          e.preventDefault();
          window.location.reload();
        } else if (onClick) {
          onClick();
        }
      }}
      className="rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
    >
      {label}
    </Link>
  );
}
