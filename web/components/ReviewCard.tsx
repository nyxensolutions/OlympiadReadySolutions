"use client";

import { useState } from "react";
import { BookOpen, CheckCircle2, ChevronDown, ChevronUp, Flag, Sparkles, XCircle, MessageCircle, Send, Loader2 } from "lucide-react";
import { useAuth } from "@clerk/nextjs";
import type { Question } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

function isImageOption(opt: string) {
  return opt.startsWith("http://") || opt.startsWith("https://") || opt.startsWith("/question-images/");
}

export function ReviewCard({
  question,
  index,
  userAnswer,
  flagged,
  subject,
  grade,
  tutorQuota,
  simulationMode,
  onQuotaUpdate
}: {
  question: Question;
  index: number;
  userAnswer: string | null;
  flagged: boolean;
  subject?: string;
  grade?: number;
  tutorQuota?: { hasPaidAccess: boolean; freeChatsUsed: number } | null;
  simulationMode?: boolean;
  onQuotaUpdate?: (newCount: number) => void;
}) {
  const correct = userAnswer === question.answer;
  const unanswered = userAnswer === null;
  // Auto-expand explanation for wrong/unanswered
  const [open, setOpen] = useState(!correct);
  
  // Chatbot states
  const { getToken } = useAuth();
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<{role: string, content: string}[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  
  // Initialize from tutorQuota but allow local override after messages
  const [localChatsUsed, setLocalChatsUsed] = useState<number | null>(null);
  
  const displayChatsUsed = localChatsUsed ?? tutorQuota?.freeChatsUsed ?? 0;
  const hasPaidAccess = tutorQuota?.hasPaidAccess ?? false;
  const isFreeLimitReached = !hasPaidAccess && displayChatsUsed >= 5;

  async function submitChat(e: React.FormEvent) {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;
    
    const userMsg = chatInput.trim();
    setChatInput("");
    setChatError(null);
    setChatMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setChatLoading(true);
    
    try {
      const token = await getToken();
      const res = await fetch(`${API_URL}/api/tutor/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          subject: subject || "Mathematics",
          grade: grade || 1,
          questionText: question.q || "",
          options: question.options ? question.options.join("\n") : "",
          correctAnswer: question.answer || "",
          explanation: question.explanation || "",
          userPick: userAnswer || "Not attempted",
          history: chatMessages || [],
          userMessage: userMsg || ""
        })
      });
      
      const data = await res.json();
      if (!res.ok) {
         if (data.errors) {
            console.error("Validation errors:", data.errors);
            throw new Error(JSON.stringify(data.errors));
         }
         throw new Error(data.message || data.title || "Failed to contact AI Tutor.");
      }
      
      if (data.freeChatsUsed !== undefined) {
        setLocalChatsUsed(data.freeChatsUsed);
        if (onQuotaUpdate) {
            onQuotaUpdate(data.freeChatsUsed);
        }
      }
      setChatMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Error connecting to tutor.");
    } finally {
      setChatLoading(false);
    }
  }

  return (
    <article
      className={`overflow-hidden rounded-xl border bg-white shadow-sm ${
        unanswered
          ? "border-slate-200"
          : correct
          ? "border-emerald-200"
          : "border-red-200"
      }`}
    >
      <div className={`h-1 w-full ${
        unanswered ? "bg-slate-200" : correct ? "bg-emerald-400" : "bg-red-400"
      }`} />

      <div className="p-5">
        <div className="flex items-start gap-3">
          <span
            className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
              unanswered
                ? "bg-slate-100 text-slate-600"
                : correct
                ? "bg-emerald-100 text-emerald-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {index + 1}
          </span>
          <div className="flex-1">
            <p className="text-base font-medium leading-relaxed text-slate-900">
              {question.q}
            </p>
            {question.imageUrl && (
              <div className="mt-4 mb-2 overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={question.imageUrl} alt="Question visual" className="max-h-48 object-contain p-2" />
              </div>
            )}
            <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs">
              {unanswered ? (
                <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600">
                  Not attempted
                </span>
              ) : correct ? (
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 font-medium text-emerald-700">
                  <CheckCircle2 className="h-3 w-3" /> Correct
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 font-medium text-red-700">
                  <XCircle className="h-3 w-3" /> Incorrect
                </span>
              )}
              {flagged && (
                <span className="inline-flex items-center gap-1 rounded-full bg-achiever-50 px-2 py-0.5 font-medium text-achiever-700">
                  <Flag className="h-3 w-3" /> Flagged
                </span>
              )}
              {question.topic && (
                <span className="inline-flex items-center gap-1 rounded-full bg-brand-50 px-2 py-0.5 font-medium text-brand-700">
                  <BookOpen className="h-3 w-3" />
                  {question.topic}
                </span>
              )}
            </div>
          </div>
        </div>

        <ul className="mt-4 grid gap-2 sm:grid-cols-2">
          {question.options.map((opt, i) => {
            const isCorrect = opt === question.answer;
            const isUser = opt === userAnswer;
            let cls = "border-slate-200 bg-slate-50 text-slate-700";
            if (isCorrect) cls = "border-emerald-300 bg-emerald-50 text-emerald-900";
            else if (isUser) cls = "border-red-300 bg-red-50 text-red-900";
            return (
              <li
                key={i}
                className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${cls}`}
              >
                <span className="font-mono text-xs text-slate-500">
                  {String.fromCharCode(65 + i)}.
                </span>
                {isImageOption(opt) ? (
                  <div className="flex-1 overflow-hidden rounded bg-white">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={opt} alt={`Option ${String.fromCharCode(65 + i)}`} className="max-h-24 object-contain" />
                  </div>
                ) : (
                  <span className="flex-1">{opt}</span>
                )}
                {isCorrect && <CheckCircle2 className="ml-auto h-4 w-4 shrink-0 text-emerald-600" />}
                {isUser && !isCorrect && <XCircle className="ml-auto h-4 w-4 shrink-0 text-red-500" />}
              </li>
            );
          })}
        </ul>

        {/* Action Buttons Row */}
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="inline-flex items-center gap-1.5 rounded-lg bg-slate-50 px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            {open ? (
              <>Hide explanation <ChevronUp className="h-4 w-4" /></>
            ) : (
              <>Show explanation <ChevronDown className="h-4 w-4" /></>
            )}
          </button>
          
          {!simulationMode && (
            <div 
              title={isFreeLimitReached ? "Your free chats quota is over. Please purchase a subject subscription to continue." : undefined}
            >
              <button
                type="button"
                disabled={isFreeLimitReached}
                onClick={() => {
                  setOpen(true);
                  setChatOpen((v) => !v);
                }}
                className="inline-flex items-center gap-1.5 rounded-lg border border-brand-200 bg-brand-50 px-3 py-1.5 text-sm font-medium text-brand-700 transition hover:bg-brand-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <MessageCircle className="h-4 w-4" />
                {chatOpen ? "Close AI Tutor" : "Ask AI Tutor"}
              </button>
            </div>
          )}
        </div>

        {open && (
          <div className={`mt-3 rounded-xl border p-4 text-sm leading-relaxed ${
            correct
              ? "border-emerald-200 bg-emerald-50 text-emerald-900"
              : "border-indigo-200 bg-indigo-50 text-indigo-900"
          }`}>
            <div className="mb-2 flex items-center gap-1.5">
              <Sparkles className={`h-3.5 w-3.5 ${correct ? "text-emerald-600" : "text-brand-600"}`} />
              <span className={`text-xs font-bold uppercase tracking-wide ${
                correct ? "text-emerald-700" : "text-brand-700"
              }`}>
                AI Explanation
              </span>
            </div>
            {isImageOption(question.explanation ?? "") ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={question.explanation} alt="Explanation diagram"
                className="mt-1 max-h-40 rounded-xl object-contain border border-slate-200 bg-slate-50 p-1" />
            ) : (
              <p>{question.explanation}</p>
            )}
          </div>
        )}

        {/* AI Tutor Chat Window */}
        {chatOpen && (
          <div className="mt-3 overflow-hidden rounded-xl border border-brand-200 bg-white shadow-sm">
            <div className="bg-brand-50 px-4 py-3 border-b border-brand-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-brand-600 text-white">
                  <Sparkles className="h-3 w-3" />
                </div>
                <span className="text-sm font-bold text-brand-900">AI Tutor</span>
              </div>
              {hasPaidAccess ? (
                <span className="text-xs font-medium text-brand-600">Unlimited chats (Pro)</span>
              ) : (
                <span className="text-xs font-medium text-brand-600">Free chats used: {displayChatsUsed}/5</span>
              )}
            </div>
            
            <div className="max-h-64 overflow-y-auto p-4 space-y-4 bg-slate-50">
              {chatMessages.length === 0 && (
                <div className="text-center text-sm text-slate-500 py-4">
                  Ask me anything about this question! For example: 
                  <br/><br/>
                  <span className="italic">"Why isn't option B correct?"</span><br/>
                  <span className="italic">"Can you explain the formula again?"</span>
                </div>
              )}
              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`rounded-xl px-4 py-2.5 max-w-[85%] text-sm ${
                    msg.role === 'user' 
                      ? 'bg-slate-800 text-white rounded-br-none' 
                      : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none shadow-sm'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="rounded-xl px-4 py-2.5 bg-white border border-slate-200 rounded-bl-none shadow-sm">
                    <Loader2 className="h-4 w-4 animate-spin text-brand-500" />
                  </div>
                </div>
              )}
              {chatError && (
                <div className="text-center text-sm font-medium text-red-600 bg-red-50 p-3 rounded-lg border border-red-200">
                  {chatError}
                </div>
              )}
            </div>

            <form onSubmit={submitChat} className="border-t border-slate-200 bg-white p-3 flex items-center gap-2">
              <input
                type="text"
                placeholder="Type your doubt here..."
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                disabled={chatLoading}
                className="flex-1 rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!chatInput.trim() || chatLoading}
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white transition hover:bg-brand-700 disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        )}
      </div>
    </article>
  );
}
