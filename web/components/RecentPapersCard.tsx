"use client";

import { FileText } from "lucide-react";
import type { DashboardSummary } from "@/lib/types";

type Paper = DashboardSummary["papers"][number];

export function RecentPapersCard({ papers }: { papers: Paper[] }) {
  if (papers.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No papers yet. Generate one from the home page.
      </p>
    );
  }

  return (
    <ul className="divide-y divide-slate-100">
      {papers.map((p) => (
        <li key={p.paperId} className="flex items-start gap-3 py-2.5">
          <FileText className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-slate-900">{p.title}</p>
            <p className="text-xs text-slate-500">
              {new Date(p.createdAt).toLocaleString()} · {p.subject} · {p.difficulty}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}
