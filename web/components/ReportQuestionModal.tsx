"use client";

import { useState } from "react";
import { AlertCircle, CheckCircle2, Loader2, X } from "lucide-react";
import { useAuth } from "@clerk/nextjs";

export function ReportQuestionModal({ 
  questionId, 
  questionText,
  onClose 
}: { 
  questionId: string;
  questionText: string;
  onClose: () => void;
}) {
  const [category, setCategory] = useState("Wrong question");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const { getToken } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) return;

    setStatus("submitting");
    try {
      // In a real app, you would use your API client/auth header setup here
      const token = await getToken();
      
      const res = await fetch("/api/reports", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          questionBankId: questionId,
          category,
          description,
          questionText
        })
      });

      if (!res.ok) throw new Error("Failed to submit report");
      
      setStatus("success");
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err: any) {
      setErrorMsg(err.message || "An error occurred");
      setStatus("error");
    }
  };

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-lg transform rounded-2xl border border-slate-100 bg-white shadow-2xl transition-all duration-300 scale-in overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50/50 px-6 py-4">
          <div className="flex items-center gap-2 text-rose-600">
            <AlertCircle className="h-5 w-5" />
            <h3 className="text-lg font-bold">Report an Issue</h3>
          </div>
          <button onClick={onClose} className="rounded-full p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition">
            <X className="h-5 w-5" />
          </button>
        </div>

        {status === "success" ? (
          <div className="p-8 text-center animate-in zoom-in duration-300">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 mb-4">
              <CheckCircle2 className="h-8 w-8 text-emerald-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Report Submitted</h3>
            <p className="mt-2 text-sm text-slate-600">
              Thank you for helping us maintain high quality questions! Our team will review this shortly.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-6">
            <div className="mb-5 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700 max-h-32 overflow-y-auto">
              <p className="font-semibold text-slate-900 mb-1 text-xs uppercase tracking-wide">Question Text</p>
              {questionText}
            </div>

            <div className="space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-semibold text-slate-700">Issue Category</label>
                <select 
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
                >
                  <option value="Wrong question">Wrong question / Typos</option>
                  <option value="Missing correct options">Missing correct options</option>
                  <option value="Wrong answer shown as correct">Wrong answer shown as correct</option>
                  <option value="Incorrect explanation">Incorrect explanation</option>
                  <option value="Out of syllabus">Out of syllabus</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-semibold text-slate-700">Description <span className="text-rose-500">*</span></label>
                <textarea 
                  required
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Please provide details about what is wrong..."
                  className="w-full resize-none rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
                />
              </div>

              {status === "error" && (
                <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-100">
                  {errorMsg}
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="rounded-xl px-5 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-100 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={status === "submitting" || !description.trim()}
                className="inline-flex items-center justify-center rounded-xl bg-rose-600 px-6 py-2.5 text-sm font-bold text-white shadow-md transition hover:bg-rose-700 disabled:opacity-50"
              >
                {status === "submitting" ? <Loader2 className="h-4 w-4 animate-spin" /> : "Submit Report"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
