"use client";

import Link from "next/link";
import { GraduationCap, LayoutDashboard, LogIn } from "lucide-react";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton
} from "@clerk/nextjs";

export function AppHeader({ active }: { active?: "home" | "dashboard" }) {
  return (
    <header className="flex w-full items-center justify-between">
      <Link href="/" className="flex items-center gap-2">
        <GraduationCap className="h-6 w-6 text-brand-600" />
        <span className="text-lg font-semibold tracking-tight">Olympiad Ready</span>
      </Link>

      <div className="flex items-center gap-2">
        <SignedIn>
          <Link
            href="/dashboard"
            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition ${
              active === "dashboard"
                ? "bg-brand-50 text-brand-700"
                : "text-slate-700 hover:bg-slate-100"
            }`}
          >
            <LayoutDashboard className="h-4 w-4" />
            Dashboard
          </Link>
          <UserButton afterSignOutUrl="/" />
        </SignedIn>
        <SignedOut>
          <SignInButton mode="modal">
            <button className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50">
              <LogIn className="h-4 w-4" />
              Sign in
            </button>
          </SignInButton>
          <SignUpButton mode="modal">
            <button className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-brand-700">
              Sign up
            </button>
          </SignUpButton>
        </SignedOut>
      </div>
    </header>
  );
}
