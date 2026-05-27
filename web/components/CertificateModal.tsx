"use client";

import { useState } from "react";
import { X, Download, Award } from "lucide-react";

export interface CertificateConfig {
  badgeId: string;
  badgeLabel: string;
  badgeEmoji: string;
  description: string;
  rewardType: "digital" | "physical";
}

interface Props {
  config: CertificateConfig;
  onClose: () => void;
  onPhysicalClaimed?: (studentName: string) => void;
}

const CERT_DATE = new Date().toLocaleDateString("en-IN", {
  day: "numeric", month: "long", year: "numeric",
});

export function CertificateModal({ config, onClose, onPhysicalClaimed }: Props) {
  const [studentName, setStudentName] = useState("");
  const [nameSubmitted, setNameSubmitted] = useState(false);
  const [physicalRequested, setPhysicalRequested] = useState(false);

  function handleDownload() {
    if (!studentName.trim()) return;
    // Open certificate in new tab and trigger print-to-PDF
    const win = window.open("", "_blank");
    if (!win) return;
    win.document.write(buildPrintHTML(studentName.trim(), config, CERT_DATE));
    win.document.close();
    win.focus();
    setTimeout(() => win.print(), 400);
  }

  function handlePhysicalRequest() {
    if (!studentName.trim()) return;
    onPhysicalClaimed?.(studentName.trim());
    setPhysicalRequested(true);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[95vh]">

        {/* Modal header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div className="flex items-center gap-2 text-indigo-700">
            <Award size={18} />
            <span className="font-semibold text-sm">Achievement Certificate</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 transition rounded-full p-1 hover:bg-slate-100">
            <X size={18} />
          </button>
        </div>

        {/* Name entry */}
        {!nameSubmitted && (
          <div className="px-6 py-4 bg-indigo-50 border-b border-indigo-100">
            <p className="text-sm text-indigo-800 font-medium mb-2">
              Enter your full name as it should appear on the certificate:
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && studentName.trim() && setNameSubmitted(true)}
                placeholder="e.g. Arjun Sharma"
                className="flex-1 border border-indigo-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-400 text-gray-800 bg-white"
                autoFocus
              />
              <button
                onClick={() => studentName.trim() && setNameSubmitted(true)}
                disabled={!studentName.trim()}
                className="bg-indigo-600 disabled:opacity-40 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
              >
                Preview
              </button>
            </div>
          </div>
        )}

        {/* Certificate preview */}
        <div className="flex-1 overflow-auto bg-slate-100 p-6 flex items-center justify-center">
          <div className="w-full" style={{ maxWidth: 720 }}>
            <CertificatePaper
              studentName={nameSubmitted && studentName.trim() ? studentName.trim() : "Your Name"}
              badgeEmoji={config.badgeEmoji}
              badgeLabel={config.badgeLabel}
              description={config.description}
              date={CERT_DATE}
              preview
            />
          </div>
        </div>

        {/* Actions */}
        {nameSubmitted && (
          <div className="px-6 py-4 border-t border-slate-100 bg-white flex flex-wrap gap-2 items-center">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 px-5 rounded-xl transition text-sm"
            >
              <Download size={15} />
              Download Certificate (PDF)
            </button>

            {config.rewardType === "physical" && !physicalRequested && (
              <button
                onClick={handlePhysicalRequest}
                className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white font-medium py-2.5 px-5 rounded-xl transition text-sm"
              >
                🏅 Request Physical Medal
              </button>
            )}
            {physicalRequested && (
              <div className="flex items-center gap-2 text-green-700 bg-green-50 rounded-xl py-2.5 px-4 text-sm font-medium border border-green-200">
                ✅ Physical reward request sent!
              </div>
            )}

            <button
              onClick={() => { setNameSubmitted(false); setStudentName(""); }}
              className="ml-auto text-sm text-slate-500 hover:text-slate-700 underline transition"
            >
              Edit name
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── In-modal preview (React component) ───────────────────────────────────────

function CertificatePaper({
  studentName, badgeEmoji, badgeLabel, description, date, preview,
}: {
  studentName: string; badgeEmoji: string; badgeLabel: string;
  description: string; date: string; preview?: boolean;
}) {
  const base = preview ? { fontSize: "14px" } : {};

  return (
    <div style={{
      ...base,
      background: "#ffffff",
      width: "100%",
      aspectRatio: "1.414",       // A4 landscape
      position: "relative",
      overflow: "hidden",
      boxShadow: "0 8px 40px rgba(0,0,0,0.14)",
      borderRadius: preview ? 12 : 0,
      display: "flex",
      fontFamily: "'Segoe UI', Arial, sans-serif",
    }}>

      {/* Left accent bar with floating lines */}
      <div style={{
        width: "7px",
        background: "linear-gradient(180deg, #4f46e5 0%, #6366f1 50%, #818cf8 100%)",
        flexShrink: 0,
      }} />

      {/* Decorative vertical lines strip */}
      <div style={{
        width: "32px",
        background: "#f8f7ff",
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: "6px",
        paddingTop: "24px",
        paddingBottom: "24px",
      }}>
        {Array.from({ length: 18 }).map((_, i) => (
          <div key={i} style={{
            width: "4px",
            height: i % 3 === 0 ? "24px" : "12px",
            background: i % 3 === 0 ? "#6366f1" : "#c7d2fe",
            borderRadius: "2px",
            opacity: 0.7,
          }} />
        ))}
      </div>

      {/* Main content */}
      <div style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "28px 40px 24px",
        boxSizing: "border-box",
      }}>

        {/* Top: logo + platform name */}
        <div style={{ textAlign: "center", width: "100%" }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/logo_welcome_full.png"
            alt="OlympiadReady"
            style={{ height: preview ? "38px" : "48px", objectFit: "contain", display: "block", margin: "0 auto" }}
          />
          <div style={{
            marginTop: "10px",
            width: "60px",
            height: "2px",
            background: "linear-gradient(90deg, transparent, #6366f1, transparent)",
            margin: "10px auto 0",
          }} />
        </div>

        {/* Middle: certificate body */}
        <div style={{ textAlign: "center", flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", gap: "8px" }}>
          <p style={{ fontSize: "0.6em", letterSpacing: "0.25em", color: "#6366f1", textTransform: "uppercase", fontWeight: 600, margin: 0 }}>
            Certificate of Achievement
          </p>

          <p style={{ fontSize: "0.75em", color: "#64748b", fontStyle: "italic", margin: "2px 0 0" }}>
            This is to proudly certify that
          </p>

          <div style={{
            fontSize: "1.7em",
            fontWeight: 700,
            color: "#1e1b4b",
            letterSpacing: "0.01em",
            borderBottom: "2px solid #e0e7ff",
            paddingBottom: "6px",
            margin: "4px 20px 4px",
            lineHeight: 1.2,
          }}>
            {studentName}
          </div>

          <p style={{ fontSize: "0.7em", color: "#64748b", fontStyle: "italic", margin: "2px 0" }}>
            has successfully earned the achievement
          </p>

          {/* Badge box */}
          <div style={{
            display: "inline-flex",
            alignSelf: "center",
            alignItems: "center",
            gap: "10px",
            background: "#f0f0ff",
            border: "1.5px solid #c7d2fe",
            borderRadius: "10px",
            padding: "8px 20px",
            margin: "4px 0",
          }}>
            <span style={{ fontSize: "1.6em" }}>{badgeEmoji}</span>
            <div style={{ textAlign: "left" }}>
              <div style={{ fontSize: "0.85em", fontWeight: 700, color: "#4338ca", margin: 0 }}>{badgeLabel}</div>
              <div style={{ fontSize: "0.6em", color: "#6366f1", margin: "1px 0 0" }}>{description}</div>
            </div>
          </div>
        </div>

        {/* Bottom: date + website */}
        <div style={{ width: "100%", display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}>
          <div style={{ fontSize: "0.6em", color: "#94a3b8" }}>
            <div style={{ fontWeight: 600, color: "#64748b" }}>Date Awarded</div>
            <div>{date}</div>
          </div>

          {/* Seal */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "4px" }}>
            <div style={{
              width: preview ? "52px" : "64px",
              height: preview ? "52px" : "64px",
              borderRadius: "50%",
              background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 3px 12px rgba(79,70,229,0.35)",
              border: "3px solid #c7d2fe",
            }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/apple-touch-icon.png"
                alt="OR"
                style={{ width: preview ? "28px" : "36px", height: preview ? "28px" : "36px", objectFit: "contain", borderRadius: "50%" }}
              />
            </div>
            <div style={{ fontSize: "0.5em", color: "#6366f1", letterSpacing: "0.15em", textTransform: "uppercase", fontWeight: 700 }}>
              Verified
            </div>
          </div>

          <div style={{ fontSize: "0.6em", color: "#94a3b8", textAlign: "right" }}>
            <div style={{ fontWeight: 600, color: "#64748b" }}>Platform</div>
            <div>olympiadready.com</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Print HTML builder ────────────────────────────────────────────────────────

function buildPrintHTML(name: string, config: CertificateConfig, date: string): string {
  const { badgeEmoji, badgeLabel, description } = config;
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>OlympiadReady Certificate — ${badgeLabel}</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  @page { size: A4 landscape; margin: 0; }
  body { width:297mm; height:210mm; overflow:hidden; font-family:'Segoe UI',Arial,sans-serif; background:#fff; }
  .wrap { display:flex; width:100%; height:100%; }
  .accent { width:10px; background:linear-gradient(180deg,#4f46e5 0%,#6366f1 50%,#818cf8 100%); flex-shrink:0; }
  .lines  { width:40px; background:#f8f7ff; flex-shrink:0; display:flex; flex-direction:column;
            justify-content:center; align-items:center; gap:7px; padding:32px 0; }
  .line-tall  { width:5px; height:30px; background:#6366f1; border-radius:3px; opacity:0.7; }
  .line-short { width:5px; height:14px; background:#c7d2fe; border-radius:3px; opacity:0.7; }
  .main { flex:1; display:flex; flex-direction:column; align-items:center;
          justify-content:space-between; padding:36px 56px 32px; }
  .top  { text-align:center; }
  .logo { height:56px; object-fit:contain; display:block; margin:0 auto; }
  .divider { width:70px; height:2px; background:linear-gradient(90deg,transparent,#6366f1,transparent);
             margin:12px auto 0; }
  .mid  { text-align:center; display:flex; flex-direction:column; align-items:center; gap:10px; }
  .label { font-size:9pt; letter-spacing:3px; color:#6366f1; text-transform:uppercase; font-weight:700; }
  .sub   { font-size:10pt; color:#64748b; font-style:italic; }
  .name  { font-size:28pt; font-weight:700; color:#1e1b4b; letter-spacing:0.5px;
           border-bottom:2px solid #e0e7ff; padding-bottom:8px; margin:4px 0; line-height:1.2; }
  .badge-box { display:inline-flex; align-items:center; gap:14px; background:#f0f0ff;
               border:1.5px solid #c7d2fe; border-radius:12px; padding:10px 28px; }
  .badge-emoji { font-size:26pt; }
  .badge-label { font-size:13pt; font-weight:700; color:#4338ca; }
  .badge-desc  { font-size:8pt; color:#6366f1; margin-top:2px; }
  .bot { width:100%; display:flex; align-items:flex-end; justify-content:space-between; }
  .bot-col { font-size:8pt; color:#94a3b8; }
  .bot-col strong { display:block; color:#64748b; font-size:8.5pt; margin-bottom:1px; }
  .seal { display:flex; flex-direction:column; align-items:center; gap:5px; }
  .seal-circle { width:80px; height:80px; border-radius:50%;
                 background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%);
                 display:flex; align-items:center; justify-content:center;
                 box-shadow:0 4px 16px rgba(79,70,229,0.4); border:3px solid #c7d2fe; }
  .seal-img { width:48px; height:48px; object-fit:contain; border-radius:50%; }
  .seal-text { font-size:7pt; color:#6366f1; letter-spacing:2px; text-transform:uppercase; font-weight:700; }
</style>
</head>
<body>
<div class="wrap">
  <div class="accent"></div>
  <div class="lines">
    ${Array.from({length:20}).map((_,i)=>`<div class="${i%3===0?'line-tall':'line-short'}"></div>`).join('')}
  </div>
  <div class="main">
    <div class="top">
      <img class="logo" src="/logo_welcome_full.png" alt="OlympiadReady"/>
      <div class="divider"></div>
    </div>
    <div class="mid">
      <div class="label">Certificate of Achievement</div>
      <div class="sub">This is to proudly certify that</div>
      <div class="name">${name}</div>
      <div class="sub">has successfully earned the achievement</div>
      <div class="badge-box">
        <div class="badge-emoji">${badgeEmoji}</div>
        <div>
          <div class="badge-label">${badgeLabel}</div>
          <div class="badge-desc">${description}</div>
        </div>
      </div>
    </div>
    <div class="bot">
      <div class="bot-col"><strong>Date Awarded</strong>${date}</div>
      <div class="seal">
        <div class="seal-circle">
          <img class="seal-img" src="/apple-touch-icon.png" alt="OR"/>
        </div>
        <div class="seal-text">Verified</div>
      </div>
      <div class="bot-col" style="text-align:right"><strong>Platform</strong>olympiadready.com</div>
    </div>
  </div>
</div>
</body>
</html>`;
}
