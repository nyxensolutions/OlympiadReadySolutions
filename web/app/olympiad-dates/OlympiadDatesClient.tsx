"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Calendar, ExternalLink, Filter, Loader2,
  AlertCircle, Clock, GraduationCap, Search, Info
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

const ORG_COLORS: Record<string, { bg: string; border: string; badge: string; icon: string }> = {
  HBCSE:       { bg: "bg-blue-50",    border: "border-blue-200",    badge: "bg-blue-100 text-blue-800",     icon: "🏛️" },
  SOF:         { bg: "bg-amber-50",   border: "border-amber-200",   badge: "bg-amber-100 text-amber-800",   icon: "🌟" },
  SilverZone:  { bg: "bg-slate-50",   border: "border-slate-200",   badge: "bg-slate-100 text-slate-700",   icon: "🥈" },
  Unified:     { bg: "bg-orange-50",  border: "border-orange-200",  badge: "bg-orange-100 text-orange-800", icon: "🎯" },
  CREST:       { bg: "bg-purple-50",  border: "border-purple-200",  badge: "bg-purple-100 text-purple-800", icon: "🏅" },
  SEAMO:       { bg: "bg-rose-50",    border: "border-rose-200",    badge: "bg-rose-100 text-rose-800",     icon: "📐" },
  ICO:         { bg: "bg-emerald-50", border: "border-emerald-200", badge: "bg-emerald-100 text-emerald-800", icon: "💻" },
  Unicus:      { bg: "bg-cyan-50",    border: "border-cyan-200",    badge: "bg-cyan-100 text-cyan-800",     icon: "🦄" },
};

const SUBJECT_COLORS: Record<string, string> = {
  Math: "bg-amber-100 text-amber-700",
  Science: "bg-emerald-100 text-emerald-700",
  English: "bg-sky-100 text-sky-700",
  Computers: "bg-indigo-100 text-indigo-700",
  "General Knowledge": "bg-purple-100 text-purple-700",
  Hindi: "bg-orange-100 text-orange-700",
};

function getStatusBadge(entry: ScheduleEntry): { label: string; cls: string } | null {
  const now = new Date();
  if (!entry.examDateFrom) return null;
  const from = new Date(entry.examDateFrom);
  const to = entry.examDateTo ? new Date(entry.examDateTo) : from;
  const diffDays = Math.ceil((from.getTime() - now.getTime()) / 86400000);

  if (now >= from && now <= to)
    return { label: "Ongoing", cls: "bg-emerald-100 text-emerald-700 border-emerald-200" };
  if (diffDays < 0)
    return { label: "Completed", cls: "bg-slate-100 text-slate-500 border-slate-200" };
  if (diffDays <= 30)
    return { label: `${diffDays}d away`, cls: "bg-red-100 text-red-700 border-red-200" };
  if (diffDays <= 90)
    return { label: `~${Math.ceil(diffDays / 30)}mo away`, cls: "bg-amber-100 text-amber-700 border-amber-200" };
  return { label: "Upcoming", cls: "bg-blue-100 text-blue-700 border-blue-200" };
}

export default function OlympiadDatesPage() {
  const [entries, setEntries] = useState<ScheduleEntry[]>([]);
  const [orgs, setOrgs] = useState<OrgEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filterOrg, setFilterOrg] = useState<string>("all");
  const [filterSubject, setFilterSubject] = useState<string>("all");
  const [search, setSearch] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
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
    } finally {
      setLoading(false);
    }
  }, [filterOrg, filterSubject]);

  useEffect(() => { void fetchData(); }, [fetchData]);

  const filtered = entries.filter((e) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      e.name.toLowerCase().includes(q) ||
      e.fullName.toLowerCase().includes(q) ||
      e.org.toLowerCase().includes(q) ||
      (e.subject ?? "").toLowerCase().includes(q)
    );
  });

  // Group by org for rendering
  const grouped = filtered.reduce<Record<string, ScheduleEntry[]>>((acc, e) => {
    (acc[e.org] ??= []).push(e);
    return acc;
  }, {});

  const subjects = Array.from(new Set(entries.map((e) => e.subject))).sort();

  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader active="olympiad-dates" />

      {/* Hero */}
      <div className="bg-gradient-to-br from-indigo-700 via-indigo-600 to-purple-600 px-4 py-12 text-white">
        <div className="mx-auto max-w-5xl">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-white/10 p-2.5">
              <Calendar className="h-7 w-7" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-indigo-200">Academic Year 2026–27</p>
              <h1 className="text-2xl font-extrabold sm:text-3xl">Olympiad Dates & Schedule</h1>
            </div>
          </div>
          <p className="mt-3 max-w-xl text-sm text-indigo-100">
            Important dates for all major Indian School Olympiads — HBCSE, SOF, SilverZone, Unified Council and more.
            Dates are curated from official sources and verified regularly.
          </p>

          {/* Disclaimer */}
          <div className="mt-4 flex items-start gap-2 rounded-xl bg-white/10 px-4 py-3 text-xs text-indigo-100">
            <Info className="mt-0.5 h-4 w-4 shrink-0" />
            <p>
              Dates shown are based on past patterns and official announcements for 2026–27. Always verify from the
              official olympiad website before registering. Click any card&apos;s link for the latest information.
            </p>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-4 py-8">
        {/* Filters */}
        <div className="mb-6 flex flex-wrap items-end gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search olympiads…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20"
            />
          </div>

          {/* Org filter */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-slate-500 flex items-center gap-1">
              <Filter className="h-3 w-3" /> Organisation
            </label>
            <select
              value={filterOrg}
              onChange={(e) => setFilterOrg(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-brand-600 focus:outline-none"
            >
              <option value="all">All Organisations</option>
              {orgs.map((o) => (
                <option key={o.org} value={o.org}>{o.org} — {o.orgFull}</option>
              ))}
            </select>
          </div>

          {/* Subject filter */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-slate-500">Subject</label>
            <select
              value={filterSubject}
              onChange={(e) => setFilterSubject(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-brand-600 focus:outline-none"
            >
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
              <p className="text-xs mt-0.5">Make sure the backend is running and the olympiad schedule has been seeded via the admin endpoint.</p>
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center">
            <Calendar className="mx-auto h-10 w-10 text-slate-300" />
            <p className="mt-3 font-semibold text-slate-500">No results found</p>
            <p className="text-sm text-slate-400">Try adjusting your filters or search query.</p>
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(grouped).map(([org, rows]) => {
              const colors = ORG_COLORS[org] ?? ORG_COLORS.SOF;
              const orgFull = rows[0]?.orgFull ?? org;
              return (
                <div key={org}>
                  {/* Org header */}
                  <div className={`mb-3 flex items-center gap-3 rounded-xl border ${colors.border} ${colors.bg} px-4 py-3`}>
                    <span className="text-2xl">{colors.icon}</span>
                    <div>
                      <h2 className="font-bold text-slate-900">{org}</h2>
                      <p className="text-xs text-slate-500">{orgFull}</p>
                    </div>
                    <span className={`ml-auto rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${colors.badge}`}>
                      {rows.length} exam{rows.length !== 1 ? "s" : ""}
                    </span>
                  </div>

                  {/* Cards grid */}
                  <div className="grid gap-4 sm:grid-cols-2">
                    {rows.map((entry) => {
                      const status = getStatusBadge(entry);
                      const subjectBadge = SUBJECT_COLORS[entry.subject] ?? "bg-slate-100 text-slate-600";
                      return (
                        <div
                          key={entry.id}
                          className={`relative overflow-hidden rounded-2xl border ${colors.border} bg-white shadow-sm transition hover:shadow-md`}
                        >
                          {/* Status stripe */}
                          <div className={`h-1 w-full ${
                            status?.label === "Ongoing" ? "bg-emerald-500" :
                            status?.label === "Completed" ? "bg-slate-300" :
                            status?.label?.includes("d away") ? "bg-red-500" :
                            "bg-indigo-400"
                          }`} />

                          <div className="p-4">
                            {/* Title row */}
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <h3 className="font-bold text-slate-900">{entry.name}</h3>
                                <p className="text-[11px] text-slate-500">{entry.fullName}</p>
                              </div>
                              {status && (
                                <span className={`shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-bold ${status.cls}`}>
                                  {status.label}
                                </span>
                              )}
                            </div>

                            {/* Badges */}
                            <div className="mt-2 flex flex-wrap items-center gap-1.5">
                              <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${subjectBadge}`}>
                                {entry.subject}
                              </span>
                              {entry.stage && (
                                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] text-slate-600">
                                  {entry.stage}
                                </span>
                              )}
                              {(entry.gradeMin || entry.gradeMax) && (
                                <span className="flex items-center gap-0.5 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] text-slate-600">
                                  <GraduationCap className="h-2.5 w-2.5" />
                                  {entry.gradeMin === entry.gradeMax
                                    ? `Class ${entry.gradeMin}`
                                    : `Class ${entry.gradeMin}–${entry.gradeMax}`}
                                </span>
                              )}
                            </div>

                            {/* Timeline */}
                            <div className="mt-3 space-y-1.5">
                              {entry.registrationWindow && (
                                <div className="flex items-start gap-2 text-xs">
                                  <span className="mt-0.5 rounded bg-emerald-100 px-1.5 py-0.5 text-[9px] font-bold text-emerald-700 shrink-0">REG</span>
                                  <span className="text-slate-600">{entry.registrationWindow}</span>
                                </div>
                              )}
                              {entry.examDateText && (
                                <div className="flex items-start gap-2 text-xs">
                                  <span className="mt-0.5 rounded bg-brand-100 px-1.5 py-0.5 text-[9px] font-bold text-brand-700 shrink-0">EXAM</span>
                                  <span className="text-slate-700 font-medium">{entry.examDateText}</span>
                                </div>
                              )}
                              {entry.resultDateText && (
                                <div className="flex items-start gap-2 text-xs">
                                  <span className="mt-0.5 rounded bg-amber-100 px-1.5 py-0.5 text-[9px] font-bold text-amber-700 shrink-0">RESULT</span>
                                  <span className="text-slate-600">{entry.resultDateText}</span>
                                </div>
                              )}
                            </div>

                            {/* Notes */}
                            {entry.notes && (
                              <div className="mt-3 flex items-start gap-1.5 rounded-lg bg-slate-50 px-2.5 py-2 text-[11px] text-slate-500">
                                <Clock className="mt-0.5 h-3 w-3 shrink-0" />
                                <span>{entry.notes}</span>
                              </div>
                            )}

                            {/* Official link */}
                            {entry.officialWebsite && (
                              <a
                                href={entry.officialWebsite}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="mt-3 inline-flex items-center gap-1 text-[11px] font-medium text-brand-600 hover:text-brand-800"
                              >
                                <ExternalLink className="h-3 w-3" />
                                Official Website
                              </a>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Footer note */}
        {!loading && !error && filtered.length > 0 && (
          <div className="mt-10 flex items-start gap-2 rounded-xl border border-slate-200 bg-white px-4 py-4 text-xs text-slate-500">
            <Info className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
            <p>
              Schedule data for Academic Year 2026–27, curated from official sources.
              Dates may vary — always check the official olympiad website before registering.
              Data last verified: {entries[0]?.lastVerified
                ? new Date(entries[0].lastVerified).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" })
                : "recently"}.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
