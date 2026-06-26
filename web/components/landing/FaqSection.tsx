"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { LANDING_FAQS } from "./faq-data";

export function FaqSection() {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section className="bg-white px-4 py-20">
      <div className="mx-auto max-w-3xl">
        <div className="mb-10 text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-brand-600">FAQ</p>
          <h2 className="mt-2 text-3xl font-bold text-slate-900 sm:text-4xl">
            Frequently asked questions
          </h2>
          <p className="mt-3 text-slate-500">Everything parents and students ask before getting started.</p>
        </div>

        <div className="divide-y divide-slate-100 rounded-2xl border border-slate-200 bg-white shadow-sm">
          {LANDING_FAQS.map((faq, i) => (
            <div key={i}>
              <button
                type="button"
                onClick={() => setOpen(open === i ? null : i)}
                className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
                aria-expanded={open === i}
              >
                <span className="font-semibold text-slate-900">{faq.q}</span>
                <ChevronDown
                  className={`h-5 w-5 shrink-0 text-slate-400 transition-transform duration-200 ${open === i ? "rotate-180" : ""}`}
                />
              </button>
              {open === i && (
                <div className="px-6 pb-5 text-[15px] leading-7 text-slate-600">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
