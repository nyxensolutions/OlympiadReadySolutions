"use client";

import { BookOpen, Star, Trophy, Users } from "lucide-react";

const STATS = [
  { icon: <BookOpen className="h-6 w-6" />, value: "50,000+", label: "Curated Questions",      color: "text-blue-300"   },
  { icon: <Users   className="h-6 w-6" />, value: "500+",     label: "Students Practising",    color: "text-green-300"  },
  { icon: <Trophy  className="h-6 w-6" />, value: "9",         label: "Olympiad Categories",   color: "text-yellow-300" },
  { icon: <Star    className="h-6 w-6" />, value: "Class 1–12",label: "All Subjects & Levels", color: "text-pink-300"   },
];

export function SocialProofSection() {
  return (
    <section className="bg-gradient-to-r from-brand-900 via-brand-800 to-brand-700 px-4 py-14 text-white">
      <div className="mx-auto max-w-5xl">
        <p className="mb-8 text-center text-xs font-bold uppercase tracking-[0.2em] text-blue-300">
          ✨ Trusted by students across India ✨
        </p>
        <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
          {STATS.map(({ icon, value, label, color }) => (
            <div key={label} className="flex flex-col items-center gap-2 text-center">
              <div className={`${color} animate-bounce-gentle`}>{icon}</div>
              <span className={`stat-num text-3xl font-extrabold ${color}`}>{value}</span>
              <span className="text-xs font-semibold text-white/60">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
