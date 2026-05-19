"use client";

import Image from "next/image";
import { useState, useEffect } from "react";
import { Loader2, Sparkles, ChevronRight, BookOpen, GraduationCap, Medal } from "lucide-react";
import { SUBJECTS } from "@/lib/types";
import type { OlympiadId } from "./OlympiadSelector";

type Step = "intro" | "class" | "subject" | "olympiad" | "customizing";

export type OnboardingData = {
  grade: number;
  subject: string;
  olympiadId: OlympiadId;
};

export function OnboardingModal({ onComplete }: { onComplete: (data: OnboardingData) => void }) {
  const [step, setStep] = useState<Step>("intro");
  const [grade, setGrade] = useState<number | null>(null);
  const [subject, setSubject] = useState<string | null>(null);
  const [olympiadDisplay, setOlympiadDisplay] = useState<string | null>(null);

  // Prevent scrolling when modal is open
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "unset";
    };
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

  const handleCustomizing = (selectedOly: string) => {
    setOlympiadDisplay(selectedOly);
    setStep("customizing");
    setTimeout(() => {
      onComplete({
        grade: grade ?? 6,
        subject: subject ?? "Math",
        olympiadId: mapOlympiadId(selectedOly)
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
              Before you start practicing, let's customize your dashboard so you get the most relevant AI-generated questions.
            </p>
            <button
              onClick={() => setStep("class")}
              className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-cta-600 px-5 py-3.5 text-sm font-bold text-white shadow-lg shadow-cta-600/30 transition hover:bg-cta-700 hover:scale-[1.02]"
            >
              Let's Go <ChevronRight className="h-4 w-4" />
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
                  onClick={() => {
                    setGrade(g);
                    setTimeout(() => setStep("subject"), 300);
                  }}
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
                  onClick={() => {
                    setSubject(s);
                    setTimeout(() => setStep("olympiad"), 300);
                  }}
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
                  onClick={() => {
                    handleCustomizing(oly);
                  }}
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
