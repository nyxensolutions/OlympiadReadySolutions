"use client";

import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { Mail, MessageCircle, GraduationCap, Building2, Send, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <AppHeader active="home" />
      <Suspense fallback={<div className="flex items-center justify-center py-24"><Loader2 className="h-6 w-6 animate-spin text-brand-600" /></div>}>
        <ContactBody />
      </Suspense>
    </div>
  );
}

function ContactBody() {
  const searchParams = useSearchParams();
  const isSchool = searchParams.get("type") === "school";

  const [form, setForm] = useState({
    name: "",
    email: "",
    message: "",
    schoolName: "",
    city: "",
    studentCount: "",
  });
  const [busy, setBusy]     = useState(false);
  const [status, setStatus] = useState<"idle" | "ok" | "err">("idle");
  const [errMsg, setErrMsg] = useState("");

  function update(key: string, val: string) {
    setForm((p) => ({ ...p, [key]: val }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setStatus("idle");
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, type: isSchool ? "school" : "general" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to send.");
      setStatus("ok");
      setForm({ name: "", email: "", message: "", schoolName: "", city: "", studentCount: "" });
    } catch (err) {
      setErrMsg(err instanceof Error ? err.message : "Something went wrong.");
      setStatus("err");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      {/* Hero */}
      <div className="bg-gradient-hero px-4 py-12 text-white">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/15">
            {isSchool ? <Building2 className="h-7 w-7" /> : <Mail className="h-7 w-7" />}
          </div>
          <h1 className="text-3xl font-extrabold sm:text-4xl">
            {isSchool ? "School & Institution Inquiry" : "Get in Touch"}
          </h1>
          <p className="mt-3 text-brand-100 text-sm max-w-xl mx-auto">
            {isSchool
              ? "Interested in OlympiadReady for your school or institution? Tell us about your requirements and we'll get back to you with a custom plan."
              : "Have a question, feedback, or need support? We'd love to hear from you. We typically respond within one business day."}
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-4 py-10 grid gap-8 lg:grid-cols-3">

        {/* Sidebar */}
        <div className="space-y-5">
          <div className="rounded-2xl border border-slate-200 bg-white p-5">
            <h3 className="font-bold text-slate-900 mb-4">Contact Details</h3>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <MessageCircle className="h-5 w-5 text-emerald-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-slate-800">WhatsApp</p>
                  <a href="https://wa.me/919953699143" target="_blank" rel="noopener noreferrer"
                    className="text-sm text-emerald-600 hover:underline">+91 99536 99143</a>
                  <p className="text-xs text-slate-400 mt-0.5">Mon–Sat, 9 am–6 pm</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Mail className="h-5 w-5 text-brand-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-slate-800">Email</p>
                  <a href="mailto:nyxencloud@gmail.com"
                    className="text-sm text-brand-600 hover:underline">nyxencloud@gmail.com</a>
                  <p className="text-xs text-slate-400 mt-0.5">We reply within 1 business day</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <GraduationCap className="h-5 w-5 text-purple-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-slate-800">OlympiadReady</p>
                  <p className="text-xs text-slate-500">by Nyxen Solutions</p>
                </div>
              </div>
            </div>
          </div>

          {isSchool && (
            <div className="rounded-2xl border border-purple-200 bg-purple-50 p-5">
              <h4 className="font-bold text-purple-900 text-sm mb-2">School Pricing Includes</h4>
              <ul className="space-y-1.5 text-xs text-purple-800">
                {["Custom per-student pricing", "All subjects for all grades", "Dedicated support", "Usage dashboard", "Bulk invoice / GST billing"].map(f => (
                  <li key={f} className="flex items-center gap-1.5">
                    <CheckCircle2 className="h-3.5 w-3.5 text-purple-500 shrink-0" /> {f}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Form */}
        <div className="lg:col-span-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            {status === "ok" ? (
              <div className="flex flex-col items-center gap-3 py-12 text-center">
                <CheckCircle2 className="h-12 w-12 text-emerald-500" />
                <h3 className="text-lg font-bold text-slate-900">Message sent!</h3>
                <p className="text-sm text-slate-500 max-w-sm">
                  Thank you for reaching out. We'll get back to you at <span className="font-semibold">{form.email || "your email"}</span> within one business day.
                </p>
                <button onClick={() => setStatus("idle")}
                  className="mt-4 rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
                  Send another message
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <h2 className="text-lg font-bold text-slate-900">
                  {isSchool ? "School Inquiry Form" : "Send us a message"}
                </h2>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Your Name *</label>
                    <input required value={form.name} onChange={e => update("name", e.target.value)}
                      placeholder="Full name"
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address *</label>
                    <input required type="email" value={form.email} onChange={e => update("email", e.target.value)}
                      placeholder="you@example.com"
                      className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500" />
                  </div>
                </div>

                {isSchool && (
                  <div className="grid gap-4 sm:grid-cols-3">
                    <div className="sm:col-span-1">
                      <label className="block text-xs font-semibold text-slate-700 mb-1">School Name</label>
                      <input value={form.schoolName} onChange={e => update("schoolName", e.target.value)}
                        placeholder="School / institution name"
                        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">City</label>
                      <input value={form.city} onChange={e => update("city", e.target.value)}
                        placeholder="City"
                        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">Est. Students</label>
                      <input value={form.studentCount} onChange={e => update("studentCount", e.target.value)}
                        placeholder="e.g. 200"
                        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500" />
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    {isSchool ? "Tell us about your requirements *" : "Message *"}
                  </label>
                  <textarea required value={form.message} onChange={e => update("message", e.target.value)}
                    rows={5}
                    placeholder={isSchool
                      ? "Tell us about your school, grades, subjects needed, and any specific requirements…"
                      : "How can we help you?"}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 resize-none" />
                </div>

                {status === "err" && (
                  <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                    <AlertCircle className="h-4 w-4 shrink-0" /> {errMsg}
                  </div>
                )}

                <button type="submit" disabled={busy}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-3 text-sm font-semibold text-white shadow hover:bg-brand-700 disabled:opacity-60 transition-all">
                  {busy
                    ? <><Loader2 className="h-4 w-4 animate-spin" /> Sending…</>
                    : <><Send className="h-4 w-4" /> {isSchool ? "Send School Inquiry" : "Send Message"}</>}
                </button>

                <p className="text-center text-xs text-slate-400">
                  We'll reply to <strong>{form.email || "your email"}</strong> within 1 business day.
                </p>
              </form>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
