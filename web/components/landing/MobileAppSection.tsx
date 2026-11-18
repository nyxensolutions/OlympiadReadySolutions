"use client";

import Image from "next/image";
import { QRCodeSVG } from "qrcode.react";
import { Smartphone, Star, Download } from "lucide-react";

const PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.nyxensolutions.olympiadready";

/** Pure-CSS phone device mockup wrapping any screen image */
function PhoneMockup({
  src, alt, width, height, anim,
}: {
  src: string; alt: string; width: number; height: number; anim: string;
}) {
  return (
    <div className={`relative shrink-0 ${anim}`} style={{ width, height }}>
      {/* Drop shadow behind device */}
      <div
        className="absolute inset-0 rounded-[2.4rem] bg-black/40 blur-xl"
        style={{ transform: "translateY(10px) scale(0.92)" }}
      />

      {/* Phone body */}
      <div
        className="relative flex h-full flex-col overflow-hidden rounded-[2.2rem] border-[3px] border-slate-600"
        style={{ background: "#0f172a" }}
      >
        {/* Top bar: speaker + front camera */}
        <div className="flex shrink-0 items-center justify-center gap-2 px-4 py-2">
          <div className="h-1 w-10 rounded-full bg-slate-700" />
          <div className="h-2.5 w-2.5 rounded-full bg-slate-700" />
        </div>

        {/* Screen */}
        <div className="relative min-h-0 flex-1 overflow-hidden">
          <Image
            src={src}
            alt={alt}
            fill
            sizes={`${width}px`}
            className="object-cover object-top"
          />
        </div>

        {/* Home indicator */}
        <div className="flex shrink-0 items-center justify-center py-1.5">
          <div className="h-1 w-10 rounded-full bg-slate-600" />
        </div>
      </div>

      {/* Side button — power */}
      <div
        className="absolute rounded-r-sm bg-slate-600"
        style={{ right: -4, top: "28%", width: 3, height: 28 }}
      />
      {/* Side buttons — volume */}
      <div
        className="absolute rounded-l-sm bg-slate-600"
        style={{ left: -4, top: "22%", width: 3, height: 20 }}
      />
      <div
        className="absolute rounded-l-sm bg-slate-600"
        style={{ left: -4, top: "32%", width: 3, height: 20 }}
      />

      {/* Screen glare */}
      <div className="pointer-events-none absolute inset-0 rounded-[2.2rem] bg-gradient-to-br from-white/8 via-transparent to-transparent" />
    </div>
  );
}

export function MobileAppSection() {
  return (
    <section id="mobile-app" className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-brand-950 to-slate-900 px-4 py-16 sm:py-20 text-white">

      {/* Background blobs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-20 top-0 h-72 w-72 rounded-full bg-brand-600/20 blur-3xl" />
        <div className="absolute -right-20 bottom-0 h-72 w-72 rounded-full bg-violet-600/20 blur-3xl" />
        <div className="absolute left-1/2 top-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-600/10 blur-3xl" />
      </div>
      <div className="doodle-overlay absolute inset-0 bg-[url('/kids-ui/decor/doodles.png')] bg-cover bg-center opacity-30" />

      <div className="relative mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-12 text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-green-400/30 bg-green-500/10 px-4 py-1.5">
            <Smartphone className="h-4 w-4 text-green-400" />
            <span className="text-sm font-bold text-green-300">Now on Android — Free Download</span>
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight sm:text-4xl lg:text-5xl">
            Practice Olympiads on the go 📱
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-base text-white/70 sm:text-lg">
            The full OlympiadReady experience — AI practice papers, doubt solver, mock exams — now in your pocket.
          </p>
        </div>

        {/* Main layout */}
        <div className="flex flex-col items-center gap-12 lg:flex-row lg:items-center lg:justify-between lg:gap-8">

          {/* ── Three phones ── */}
          <div className="relative flex w-full items-end justify-center gap-4 pb-10 sm:gap-6 lg:w-auto lg:flex-1">

            {/* Left phone — bounces DOWN */}
            <PhoneMockup
              src="/app-screenshots/screen1.jpg"
              alt="Practice session on OlympiadReady app"
              width={130}
              height={260}
              anim="animate-bounce-down"
            />

            {/* Center phone (login/splash) — bounces UP, slightly larger */}
            <PhoneMockup
              src="/app-screenshots/login.jpg"
              alt="OlympiadReady app login screen"
              width={148}
              height={300}
              anim="animate-bounce-up"
            />

            {/* Right phone — bounces DOWN (offset) */}
            <PhoneMockup
              src="/app-screenshots/screen3.jpg"
              alt="Subject coverage on OlympiadReady app"
              width={130}
              height={260}
              anim="animate-bounce-down-2"
            />

            {/* Free badge */}
            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full border border-white/20 bg-slate-800/80 px-4 py-1.5 text-xs font-semibold text-white/80 backdrop-blur-sm">
              <Download className="mr-1.5 inline h-3.5 w-3.5 text-green-400" />
              Free on Google Play
            </div>
          </div>

          {/* ── Copy + CTA + QR ── */}
          <div className="w-full max-w-sm space-y-6 text-center lg:w-auto lg:text-left lg:flex-1">

            <ul className="space-y-3 text-left">
              {[
                { icon: "🧠", text: "AI-generated questions, fresh every time" },
                { icon: "🏆", text: "Mock exams with OMR simulation" },
                { icon: "💬", text: "AI Doubt Chatbot per question" },
                { icon: "📊", text: "Progress tracking & performance insights" },
                { icon: "📚", text: "IMO, ISO, IEO, IGKO, Spell Bee & more" },
              ].map(({ icon, text }) => (
                <li key={text} className="flex items-center gap-3 text-sm text-white/80 sm:text-base">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/10 text-base">{icon}</span>
                  {text}
                </li>
              ))}
            </ul>

            {/* Rating */}
            <div className="inline-flex items-center gap-2 rounded-2xl border border-yellow-400/30 bg-yellow-400/10 px-4 py-2.5">
              <div className="flex gap-0.5">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <span className="text-sm font-semibold text-yellow-200">Rated 5★ on Google Play</span>
            </div>

            {/* Play Store + QR */}
            <div className="flex flex-wrap items-center justify-center gap-4 lg:justify-start">
              <a
                href={PLAY_STORE_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-3 rounded-2xl bg-white px-6 py-3.5 text-slate-900 shadow-lg transition hover:scale-105 hover:shadow-xl active:scale-95"
              >
                <svg viewBox="0 0 512 512" className="h-7 w-7" aria-hidden="true">
                  <path d="M48 59.5v393c0 17 19.4 26.8 32.9 16.4l176-137.3V180.4L80.9 43.1C67.4 32.7 48 42.5 48 59.5z" fill="#32BBFF"/>
                  <path d="M313 256l-56.1-43.7L80.9 43.1C67.4 32.7 48 42.5 48 59.5l209 196.5L313 256z" fill="#32BBFF"/>
                  <path d="M256.9 212.3L80.9 43.1C67.4 32.7 48 42.5 48 59.5v.9l208.9 196 56-43.7-56-0.4z" fill="#2C9FD9"/>
                  <path d="M48 452.5c0 17 19.4 26.8 32.9 16.4l176-137.3-56-43.7L48 452.5z" fill="#29CC5E"/>
                  <path d="M370.4 224.7l-57.4-44.3-56.1 43.7 56.1 43.7 57.5-44.1c9.9-7.6 9.9-22 0-29.6l-.1.6z" fill="#FFD729"/>
                  <path d="M80.9 468.9C67.4 479.3 48 469.5 48 452.5l209-196.5 56 43.7-232.1 169.2z" fill="#40EF7E"/>
                  <path d="M313 256l57.4 44.1c9.9-7.6 9.9-22.1 0-29.7L313 256z" fill="#FFB900"/>
                </svg>
                <div className="text-left">
                  <p className="text-xs font-medium text-slate-500 leading-none">Get it on</p>
                  <p className="text-lg font-bold leading-tight">Google Play</p>
                </div>
              </a>

              {/* QR on desktop only */}
              <div className="hidden lg:flex flex-col items-center gap-2">
                <div className="rounded-2xl border border-white/10 bg-white p-2.5 shadow-xl">
                  <QRCodeSVG value={PLAY_STORE_URL} size={80} bgColor="#ffffff" fgColor="#1e293b" level="M" />
                </div>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-white/40">Scan to download</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
