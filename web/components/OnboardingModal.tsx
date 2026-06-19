"use client";

import Image from "next/image";
import { useState, useEffect } from "react";
import { Loader2, Sparkles, ChevronRight, BookOpen, GraduationCap, Medal, School, CheckCircle2, XCircle } from "lucide-react";
import { SUBJECTS } from "@/lib/types";
import type { OlympiadId } from "./OlympiadSelector";

type Step = "intro" | "class" | "subject" | "olympiad" | "school" | "customizing";

export type OnboardingData = {
  grade: number;
  subject: string;
  olympiadId: OlympiadId;
  schoolInviteCode?: string;
};

type SchoolPreview = {
  name: string;
  city: string;
  logoUrl?: string;
  pilotActive: boolean;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

export function OnboardingModal({ onComplete }: { onComplete: (data: OnboardingData) => void }) {
  const [step, setStep] = useState<Step>("intro");
  const [grade, setGrade] = useState<number | null>(null);
  const [subject, setSubject] = useState<string | null>(null);
  const [olympiadDisplay, setOlympiadDisplay] = useState<string | null>(null);

  // School code state
  const [codeInput, setCodeInput] = useState("");
  const [codeStatus, setCodeStatus] = useState<"idle" | "checking" | "valid" | "invalid">("idle");
  const [schoolPreview, setSchoolPreview] = useState<SchoolPreview | null>(null);
  const [codeError, setCodeError] = useState("");

  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = "unset"; };
  }, []);

  const mapOlympiadId = (display: string): OlympiadId => {
    switch (display) {
      case "SOF IMO": return "sof_imo";
      case "SOF NSO": return "sof_nso";
      case "Homi Bhabha": return "hbcse";
      case "SilverZone": return "silverzone_math";
      case "NSTSE": return "unified_nstse";
      default: return "open";
    }
  };

  const handleOlympiadSelect = (selectedOly: string) => {
    setOlympiadDisplay(selectedOly);
    setStep("school");
  };

  const handleCheckCode = async () => {
    const code = codeInput.trim().toUpperCase();
    if (!code) return;
    setCodeStatus("checking");
    setCodeError("");
    try {
      const res = await fetch(`${API_URL}/api/schools/validate/${code}`);
      if (res.ok) {
        const data = await res.json();
        setSchoolPreview(data);
        setCodeStatus("valid");
      } else {
        const err = await res.json().catch(() => ({}));
        setCodeError(err.message ?? "Invalid invite code.");
        setCodeStatus("invalid");
      }
    } catch {
      setCodeError("Could not verify code. Try again.");
      setCodeStatus("invalid");
    }
  };

  const handleFinish = (withCode?: string) => {
    setStep("customizing");
    setTimeout(() => {
      onComplete({
        grade: grade ?? 6,
        subject: subject ?? "Mathematics",
        olympiadId: mapOlympiadId(olympiadDisplay ?? ""),
        schoolInviteCode: withCode,
      });
    }, 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm transition-opacity">
      <div className="relative w-full max-w-lg overflow-hidden rounded-3xl border border-white/20 bg-white shadow-2xl transition-all">

        {step === "intro" && (
          <div className="p-10 text-center animate-in fade-in zoom-in duration-300">
            <div className="mx-auto mb-6 flex justify-center">
              <Image
                src="/logo_welcome.png"
                alt="OlympiadReady Welcome"
                width={280}
                height={140}
                quality={100}
                className="object-contain h-auto w-auto max-h-32"
                priority
              />
            </div>
            <h2 className="text-2xl font-extrabold text-slate-900">Welcome to OlympiadReady!</h2>
            <p className="mt-3 text-sm text-slate-600 leading-relaxed">
              Before you start practicing, let&apos;s customize your dashboard so you get the most relevant AI-generated questions.
            </p>
            <button
              onClick={() => setStep("class")}
              className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-cta-600 px-5 py-3.5 text-sm font-bold text-white shadow-lg shadow-cta-600/30 transition hover:bg-cta-700 hover:scale-[1.02]"
            >
              Let&apos;s Go <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        )}

        {step === "class" && (
          <div className="p-8 animate-in slide-in-from-right-8 fade-in duration-300">
            <div className="flex items-center gap-3 mb-6">
              <div className="rounded-lg bg-blue-100 p-2 text-blue-600">
                <GraduationCap className="h-5 w-5" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">What class are you in?</h2>
            </div>
            <div className="grid grid-cols-4 gap-3 mt-4">
              {Array.from({ length: 12 }, (_, i) => i + 1).map((g) => (
                <button
                  key={g}
                  onClick={() => { setGrade(g); setTimeout(() => setStep("subject"), 300); }}
                  className={`flex h-12 flex-col items-center justify-center rounded-xl border-2 transition-all ${
                    grade === g
                      ? "border-brand-600 bg-brand-50 text-brand-700 scale-105"
                      : "border-slate-100 bg-slate-50 text-slate-600 hover:border-brand-200 hover:bg-white"
                  }`}
                >
                  <span className="text-lg font-bold">{g}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === "subject" && (
          <div className="p-8 animate-in slide-in-from-right-8 fade-in duration-300">
            <div className="flex items-center gap-3 mb-6">
              <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
                <BookOpen className="h-5 w-5" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">Your favorite subject?</h2>
            </div>
            <div className="grid grid-cols-2 gap-3 mt-4">
              {SUBJECTS.map((s) => (
                <button
                  key={s}
                  onClick={() => { setSubject(s); setTimeout(() => setStep("olympiad"), 300); }}
                  className={`flex items-center justify-center rounded-xl border-2 p-4 transition-all ${
                    subject === s
                      ? "border-emerald-600 bg-emerald-50 text-emerald-700 scale-105 shadow-sm"
                      : "border-slate-100 bg-slate-50 text-slate-600 hover:border-emerald-200 hover:bg-white"
                  }`}
                >
                  <span className="font-semibold">{s}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === "olympiad" && (
          <div className="p-8 animate-in slide-in-from-right-8 fade-in duration-300">
            <div className="flex items-center gap-3 mb-6">
              <div className="rounded-lg bg-amber-100 p-2 text-amber-600">
                <Medal className="h-5 w-5" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">Target Olympiad?</h2>
            </div>
            <div className="grid grid-cols-2 gap-3 mt-4">
              {["SOF IMO", "SOF NSO", "Homi Bhabha", "SilverZone", "NSTSE", "Not Sure Yet"].map((oly) => (
                <button
                  key={oly}
                  onClick={() => handleOlympiadSelect(oly)}
                  className={`flex items-center justify-center rounded-xl border-2 p-3 text-sm transition-all ${
                    olympiadDisplay === oly
                      ? "border-amber-500 bg-amber-50 text-amber-700 scale-105 shadow-sm"
                      : "border-slate-100 bg-slate-50 text-slate-600 hover:border-amber-200 hover:bg-white"
                  }`}
                >
                  <span className="font-semibold text-center">{oly}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === "school" && (
          <div className="p-8 animate-in slide-in-from-right-8 fade-in duration-300">
            <div className="flex items-center gap-3 mb-2">
              <div className="rounded-lg bg-violet-100 p-2 text-violet-600">
                <School className="h-5 w-5" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">School invite code?</h2>
            </div>
            <p className="text-sm text-slate-500 mb-6">
              If your school shared a code with you, enter it here for free access. Skip if you&apos;re signing up on your own.
            </p>

            {codeStatus === "valid" && schoolPreview ? (
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 mb-4">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
                  <div>
                    <p className="font-bold text-slate-900">{schoolPreview.name}</p>
                    <p className="text-xs text-slate-500">{schoolPreview.city}{schoolPreview.pilotActive ? " · Free access active" : ""}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={codeInput}
                  onChange={(e) => { setCodeInput(e.target.value.toUpperCase()); setCodeStatus("idle"); setCodeError(""); }}
                  onKeyDown={(e) => e.key === "Enter" && handleCheckCode()}
                  placeholder="e.g. RYAN-DEL-26"
                  className="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm font-mono uppercase tracking-wider text-slate-900 placeholder:normal-case placeholder:tracking-normal focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                />
                <button
                  onClick={handleCheckCode}
                  disabled={!codeInput.trim() || codeStatus === "checking"}
                  className="rounded-xl bg-brand-600 px-4 py-3 text-sm font-bold text-white transition hover:bg-brand-700 disabled:opacity-50"
                >
                  {codeStatus === "checking" ? <Loader2 className="h-4 w-4 animate-spin" /> : "Apply"}
                </button>
              </div>
            )}

            {codeStatus === "invalid" && (
              <div className="flex items-center gap-2 text-red-600 text-sm mb-3">
                <XCircle className="h-4 w-4 shrink-0" />
                <span>{codeError}</span>
              </div>
            )}

            <div className="flex flex-col gap-2 mt-4">
              {codeStatus === "valid" ? (
                <button
                  onClick={() => handleFinish(codeInput.trim().toUpperCase())}
                  className="w-full rounded-xl bg-cta-600 py-3 text-sm font-bold text-white shadow-lg shadow-cta-600/30 transition hover:bg-cta-700"
                >
                  Continue with {schoolPreview?.name}
                </button>
              ) : (
                <button
                  onClick={() => handleFinish(undefined)}
                  className="w-full rounded-xl bg-cta-600 py-3 text-sm font-bold text-white shadow-lg shadow-cta-600/30 transition hover:bg-cta-700"
                >
                  <Sparkles className="inline h-4 w-4 mr-1" />
                  Start practising free
                </button>
              )}
              <button
                onClick={() => handleFinish(undefined)}
                className="w-full rounded-xl border border-slate-200 py-3 text-sm font-medium text-slate-500 transition hover:bg-slate-50"
              >
                Skip — I don&apos;t have a code
              </button>
            </div>
          </div>
        )}

        {step === "customizing" && (
          <div className="p-12 text-center animate-in fade-in zoom-in duration-500">
            <Loader2 className="mx-auto h-12 w-12 animate-spin text-brand-600 mb-6" />
            <h2 className="text-2xl font-bold text-slate-900">Customizing your dashboard...</h2>
            <p className="mt-2 text-sm text-slate-500">Setting up {subject} for Class {grade}</p>
          </div>
        )}

      </div>
    </div>
  );
}
