"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Calendar, ExternalLink, Filter, Loader2,
  AlertCircle, GraduationCap, Search, Info, Star, ChevronDown, ChevronUp,
} from "lucide-react";
import { AppHeader } from "@/components/AppHeader";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

type ScheduleEntry = {
  id: number;
  org: string;
  orgFull: string;
  name: string;
  fullName: string;
  subject: string;
  stage: string | null;
  gradeMin: number | null;
  gradeMax: number | null;
  registrationWindow: string | null;
  examDateText: string | null;
  examDateFrom: string | null;
  examDateTo: string | null;
  resultDateText: string | null;
  officialWebsite: string | null;
  notes: string | null;
  academicYear: number;
  lastVerified: string;
};

type OrgEntry = { org: string; orgFull: string };

// SOF is always pinned first; rest sorted alphabetically
const ORG_ORDER = ["SOF", "SilverZone", "Unicus", "AmarUjala", "Unified", "CREST", "HBCSE", "SEAMO", "ICO"];

const ORG_META: Record<string, { icon: string; accent: string; accentLight: string; accentText: string; description: string }> = {
  SOF:        { icon: "🌟", accent: "bg-amber-500",  accentLight: "bg-amber-50",  accentText: "text-amber-700",  description: "India's largest school Olympiad organisation" },
  SilverZone: { icon: "🥈", accent: "bg-slate-500",  accentLight: "bg-slate-50",  accentText: "text-slate-700",  description: "Competitive Olympiads for Classes 1–12" },
  Unicus:     { icon: "🦄", accent: "bg-cyan-500",   accentLight: "bg-cyan-50",   accentText: "text-cyan-700",   description: "Summer & academic year Olympiads" },
  AmarUjala:  { icon: "📰", accent: "bg-red-500",    accentLight: "bg-red-50",    accentText: "text-red-700",    description: "New 2026-27 — National Olympiads by Amar Ujala media group" },
  Unified:    { icon: "🎯", accent: "bg-orange-500", accentLight: "bg-orange-50", accentText: "text-orange-700", description: "Diagnostic-style national talent search exams" },
  CREST:      { icon: "🏅", accent: "bg-purple-500", accentLight: "bg-purple-50", accentText: "text-purple-700", description: "Online on-demand Olympiads — book your own slot" },
  HBCSE:      { icon: "🏛️", accent: "bg-blue-600",   accentLight: "bg-blue-50",   accentText: "text-blue-700",   description: "Govt. pathway Olympiads for national & international representation" },
  SEAMO:      { icon: "📐", accent: "bg-rose-500",   accentLight: "bg-rose-50",   accentText: "text-rose-700",   description: "Southeast Asian Mathematical Olympiad" },
  ICO:        { icon: "💻", accent: "bg-emerald-600",accentLight: "bg-emerald-50",accentText: "text-emerald-700",description: "Indian Computing Olympiad — IOI pathway" },
};

const SUBJECT_COLORS: Record<string, string> = {
  Math:               "bg-amber-100 text-amber-700",
  Science:            "bg-emerald-100 text-emerald-700",
  English:            "bg-sky-100 text-sky-700",
  Computers:          "bg-indigo-100 text-indigo-700",
  "General Knowledge":"bg-purple-100 text-purple-700",
  Hindi:              "bg-orange-100 text-orange-700",
  "Logical Reasoning":"bg-pink-100 text-pink-700",
  Multiple:           "bg-slate-100 text-slate-600",
};

function getStatus(entry: ScheduleEntry): { label: string; color: string; bar: string } {
  const now = new Date();
  if (!entry.examDateFrom) return { label: "TBA", color: "text-slate-400 bg-slate-100", bar: "bg-slate-200" };
  const from = new Date(entry.examDateFrom);
  const to = entry.examDateTo ? new Date(entry.examDateTo) : from;
  const diffDays = Math.ceil((from.getTime() - now.getTime()) / 86400000);

  if (now >= from && now <= to) return { label: "Ongoing", color: "text-emerald-700 bg-emerald-100", bar: "bg-emerald-500" };
  if (diffDays < 0)             return { label: "Completed", color: "text-slate-400 bg-slate-100", bar: "bg-slate-300" };
  if (diffDays <= 30)           return { label: `${diffDays}d away`, color: "text-red-700 bg-red-100", bar: "bg-red-500" };
  if (diffDays <= 90)           return { label: `~${Math.ceil(diffDays / 30)}mo`, color: "text-amber-700 bg-amber-100", bar: "bg-amber-400" };
  return { label: "Upcoming", color: "text-blue-700 bg-blue-100", bar: "bg-blue-400" };
}

function ExamCard({ entry }: { entry: ScheduleEntry }) {
  const status = getStatus(entry);
  const subjectCls = SUBJECT_COLORS[entry.subject] ?? "bg-slate-100 text-slate-600";
  const isCompleted = status.label === "Completed";

  return (
    <div className={`relative flex flex-col rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md overflow-hidden ${isCompleted ? "opacity-60" : ""}`}>
      {/* colour bar */}
      <div className={`h-1 w-full ${status.bar}`} />

      <div className="flex flex-col flex-1 p-4 gap-3">
        {/* header */}
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="font-bold text-slate-900 text-sm leading-snug">{entry.name}</p>
            <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">{entry.fullName}</p>
          </div>
          <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold ${status.color}`}>
            {status.label}
          </span>
        </div>

        {/* chips */}
        <div className="flex flex-wrap gap-1.5">
          <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${subjectCls}`}>{entry.subject}</span>
          {entry.stage && (
            <span className="rounded-full bg-slate-100 text-slate-500 px-2 py-0.5 text-[10px]">{entry.stage}</span>
          )}
          {(entry.gradeMin || entry.gradeMax) && (
            <span className="flex items-center gap-0.5 rounded-full bg-slate-100 text-slate-500 px-2 py-0.5 text-[10px]">
              <GraduationCap className="h-2.5 w-2.5" />
              {entry.gradeMin === entry.gradeMax ? `Cl. ${entry.gradeMin}` : `Cl. ${entry.gradeMin}–${entry.gradeMax}`}
            </span>
          )}
        </div>

        {/* timeline rows */}
        <div className="flex flex-col gap-1.5 text-xs">
          {entry.registrationWindow && (
            <div className="flex items-start gap-2">
              <span className="shrink-0 mt-0.5 rounded bg-emerald-100 text-emerald-700 px-1.5 py-0.5 text-[9px] font-bold">REG</span>
              <span className="text-slate-500">{entry.registrationWindow}</span>
            </div>
          )}
          {entry.examDateText && (
            <div className="flex items-start gap-2">
              <span className="shrink-0 mt-0.5 rounded bg-indigo-100 text-indigo-700 px-1.5 py-0.5 text-[9px] font-bold">EXAM</span>
              <span className="text-slate-800 font-semibold">{entry.examDateText}</span>
            </div>
          )}
          {entry.resultDateText && (
            <div className="flex items-start gap-2">
              <span className="shrink-0 mt-0.5 rounded bg-amber-100 text-amber-700 px-1.5 py-0.5 text-[9px] font-bold">RESULT</span>
              <span className="text-slate-500">{entry.resultDateText}</span>
            </div>
          )}
        </div>

        {/* notes */}
        {entry.notes && (
          <p className="text-[11px] text-slate-400 bg-slate-50 rounded-lg px-2.5 py-2 leading-relaxed">{entry.notes}</p>
        )}

        {/* link */}
        {entry.officialWebsite && (
          <a href={entry.officialWebsite} target="_blank" rel="noopener noreferrer"
            className="mt-auto inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 transition">
            <ExternalLink className="h-3 w-3" /> Official Website
          </a>
        )}
      </div>
    </div>
  );
}

function OrgSection({ org, rows, defaultOpen }: { org: string; rows: ScheduleEntry[]; defaultOpen: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  const meta = ORG_META[org] ?? { icon: "🏆", accent: "bg-indigo-500", accentLight: "bg-indigo-50", accentText: "text-indigo-700", description: "" };
  const orgFull = rows[0]?.orgFull ?? org;
  const isNew = org === "AmarUjala";

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      {/* org header — clickable to collapse */}
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-4 px-5 py-4 hover:bg-slate-50 transition text-left"
      >
        <div className={`w-10 h-10 rounded-xl ${meta.accent} flex items-center justify-center text-xl shrink-0 shadow-sm`}>
          {meta.icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-bold text-slate-900 text-base">{org === "AmarUjala" ? "Amar Ujala" : org}</span>
            {isNew && (
              <span className="rounded-full bg-red-100 text-red-600 text-[10px] font-bold px-2 py-0.5 border border-red-200 animate-pulse">
                NEW 2026
              </span>
            )}
            {org === "SOF" && (
              <span className="flex items-center gap-0.5 rounded-full bg-amber-100 text-amber-700 text-[10px] font-bold px-2 py-0.5">
                <Star className="h-2.5 w-2.5 fill-amber-500 stroke-amber-500" /> Most Popular
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-0.5 truncate">{meta.description || orgFull}</p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${meta.accentLight} ${meta.accentText}`}>
            {rows.length} exam{rows.length !== 1 ? "s" : ""}
          </span>
          {open ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
        </div>
      </button>

      {open && (
        <div className="px-5 pb-5">
          <div className="h-px bg-slate-100 mb-4" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {rows.map((entry) => <ExamCard key={entry.id} entry={entry} />)}
          </div>
          {org === "SOF" && (
            <p className="mt-3 text-[11px] text-slate-400 flex items-center gap-1">
              <Info className="h-3 w-3 shrink-0" />
              SOF Olympiads are school-registered. Contact your school to participate.
            </p>
          )}
          {org === "AmarUjala" && (
            <p className="mt-3 text-[11px] text-slate-400 flex items-center gap-1">
              <Info className="h-3 w-3 shrink-0" />
              Individual registration — no school required. Early-bird pricing ends 15 Jul 2026.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default function OlympiadDatesPage() {
  const [entries, setEntries] = useState<ScheduleEntry[]>([]);
  const [orgs, setOrgs] = useState<OrgEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterOrg, setFilterOrg] = useState("all");
  const [filterSubject, setFilterSubject] = useState("all");
  const [search, setSearch] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const params = new URLSearchParams({ year: "2026" });
      if (filterOrg !== "all") params.set("org", filterOrg);
      if (filterSubject !== "all") params.set("subject", filterSubject);
      const [entriesRes, orgsRes] = await Promise.all([
        fetch(`${API_URL}/api/olympiad-dates?${params}`),
        fetch(`${API_URL}/api/olympiad-dates/orgs`),
      ]);
      if (!entriesRes.ok) throw new Error("Could not load schedule data.");
      setEntries(await entriesRes.json());
      if (orgsRes.ok) setOrgs(await orgsRes.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load data.");
    } finally { setLoading(false); }
  }, [filterOrg, filterSubject]);

  useEffect(() => { void fetchData(); }, [fetchData]);

  const filtered = entries.filter((e) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return e.name.toLowerCase().includes(q) || e.fullName.toLowerCase().includes(q) ||
      e.org.toLowerCase().includes(q) || (e.subject ?? "").toLowerCase().includes(q);
  });

  // Group + sort: SOF first, then ORG_ORDER, then any unknown orgs alpha
  const grouped = filtered.reduce<Record<string, ScheduleEntry[]>>((acc, e) => {
    (acc[e.org] ??= []).push(e); return acc;
  }, {});
  const sortedOrgs = Object.keys(grouped).sort((a, b) => {
    const ai = ORG_ORDER.indexOf(a);
    const bi = ORG_ORDER.indexOf(b);
    if (ai === -1 && bi === -1) return a.localeCompare(b);
    if (ai === -1) return 1;
    if (bi === -1) return -1;
    return ai - bi;
  });

  const subjects = Array.from(new Set(entries.map((e) => e.subject))).sort();
  const totalExams = filtered.length;
  const upcomingCount = filtered.filter(e => {
    if (!e.examDateFrom) return false;
    return new Date(e.examDateFrom) > new Date();
  }).length;

  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader active="olympiad-dates" />

      {/* Hero */}
      <div className="bg-gradient-to-br from-indigo-700 via-indigo-600 to-purple-700 px-4 py-10 text-white">
        <div className="mx-auto max-w-5xl">
          <div className="flex items-center gap-3 mb-3">
            <div className="rounded-xl bg-white/15 p-2.5">
              <Calendar className="h-6 w-6" />
            </div>
            <div>
              <p className="text-[11px] font-bold uppercase tracking-widest text-indigo-200">Academic Year 2026–27</p>
              <h1 className="text-2xl font-extrabold sm:text-3xl">Olympiad Dates & Schedule</h1>
            </div>
          </div>
          <p className="text-sm text-indigo-100 max-w-xl mb-5">
            All major Indian school Olympiad dates in one place — SOF, SilverZone, HBCSE, Unicus, Amar Ujala and more. Verified from official sources.
          </p>

          {/* Stats bar */}
          <div className="flex flex-wrap gap-4">
            <div className="rounded-xl bg-white/10 px-4 py-2.5 text-center min-w-[100px]">
              <p className="text-2xl font-extrabold">{sortedOrgs.length}</p>
              <p className="text-[11px] text-indigo-200 font-medium">Organisations</p>
            </div>
            <div className="rounded-xl bg-white/10 px-4 py-2.5 text-center min-w-[100px]">
              <p className="text-2xl font-extrabold">{totalExams}</p>
              <p className="text-[11px] text-indigo-200 font-medium">Total Exams</p>
            </div>
            <div className="rounded-xl bg-white/10 px-4 py-2.5 text-center min-w-[100px]">
              <p className="text-2xl font-extrabold">{upcomingCount}</p>
              <p className="text-[11px] text-indigo-200 font-medium">Upcoming</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-4 py-6">

        {/* Filters */}
        <div className="mb-6 flex flex-wrap items-end gap-3 bg-white rounded-2xl border border-slate-200 shadow-sm px-4 py-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input type="text" placeholder="Search olympiads, subjects…" value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-200" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] font-bold uppercase text-slate-400 flex items-center gap-1"><Filter className="h-3 w-3" /> Organisation</label>
            <select value={filterOrg} onChange={(e) => setFilterOrg(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none">
              <option value="all">All Organisations</option>
              {orgs.map((o) => <option key={o.org} value={o.org}>{o.org === "AmarUjala" ? "Amar Ujala" : o.org}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] font-bold uppercase text-slate-400">Subject</label>
            <select value={filterSubject} onChange={(e) => setFilterSubject(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none">
              <option value="all">All Subjects</option>
              {subjects.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center gap-2 py-24 text-slate-400">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="text-sm">Loading schedule data…</span>
          </div>
        ) : error ? (
          <div className="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700">
            <AlertCircle className="h-5 w-5 shrink-0" />
            <div>
              <p className="font-semibold">Could not load schedule data</p>
              <p className="text-xs mt-0.5">{error}</p>
            </div>
          </div>
        ) : sortedOrgs.length === 0 ? (
          <div className="py-16 text-center">
            <Calendar className="mx-auto h-10 w-10 text-slate-300" />
            <p className="mt-3 font-semibold text-slate-500">No results found</p>
            <p className="text-sm text-slate-400">Try adjusting your filters.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {sortedOrgs.map((org, i) => (
              <OrgSection key={org} org={org} rows={grouped[org]} defaultOpen={i < 2} />
            ))}
          </div>
        )}

        {/* Disclaimer */}
        {!loading && !error && sortedOrgs.length > 0 && (
          <div className="mt-8 flex items-start gap-2 rounded-xl border border-slate-200 bg-white px-4 py-4 text-xs text-slate-500">
            <Info className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
            <p>
              Schedule data for Academic Year 2026–27, curated from official sources. Dates may change — always verify on the official website before registering.
              {entries[0]?.lastVerified && (
                <> Last verified: {new Date(entries[0].lastVerified).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" })}.</>
              )}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
