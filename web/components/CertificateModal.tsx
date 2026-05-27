"use client";

import { useRef, useState } from "react";
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
  const certRef = useRef<HTMLDivElement>(null);

  function handlePrint() {
    if (!studentName.trim()) return;
    setNameSubmitted(true);
    setTimeout(() => window.print(), 150);
  }

  function handlePhysicalRequest() {
    if (!studentName.trim()) return;
    onPhysicalClaimed?.(studentName.trim());
    setPhysicalRequested(true);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 no-print">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-indigo-700 text-white">
          <div className="flex items-center gap-2">
            <Award size={20} />
            <span className="font-semibold">Achievement Certificate</span>
          </div>
          <button onClick={onClose} className="hover:bg-white/20 rounded-full p-1 transition">
            <X size={18} />
          </button>
        </div>

        {/* Name entry */}
        {!nameSubmitted && (
          <div className="px-6 py-4 bg-indigo-50 border-b border-indigo-100">
            <p className="text-sm text-indigo-800 mb-2 font-medium">
              Enter your full name as it should appear on the certificate:
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && studentName.trim() && setNameSubmitted(true)}
                placeholder="e.g. Arjun Sharma"
                className="flex-1 border border-indigo-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-400 text-gray-800"
                autoFocus
              />
              <button
                onClick={() => studentName.trim() && setNameSubmitted(true)}
                disabled={!studentName.trim()}
                className="bg-indigo-600 disabled:opacity-40 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
              >
                Preview
              </button>
            </div>
          </div>
        )}

        {/* Certificate preview */}
        <div className="p-4 bg-gray-100">
          <div ref={certRef} id="certificate-print-area" className="certificate-paper">
            <CertificatePaper
              studentName={nameSubmitted && studentName.trim() ? studentName.trim() : "Your Name"}
              badgeEmoji={config.badgeEmoji}
              badgeLabel={config.badgeLabel}
              description={config.description}
              date={CERT_DATE}
            />
          </div>
        </div>

        {/* Actions */}
        {nameSubmitted && (
          <div className="px-6 py-4 bg-gray-50 border-t flex flex-col sm:flex-row gap-2">
            <button
              onClick={handlePrint}
              className="flex-1 flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-xl transition text-sm"
            >
              <Download size={15} />
              Download / Print Certificate
            </button>
            {config.rewardType === "physical" && !physicalRequested && (
              <button
                onClick={handlePhysicalRequest}
                className="flex-1 flex items-center justify-center gap-2 bg-amber-500 hover:bg-amber-600 text-white font-medium py-2.5 rounded-xl transition text-sm"
              >
                🏅 Request Physical Medal
              </button>
            )}
            {physicalRequested && (
              <div className="flex-1 flex items-center justify-center text-green-700 bg-green-50 rounded-xl py-2.5 text-sm font-medium border border-green-200">
                ✅ Physical reward request sent!
              </div>
            )}
            <button
              onClick={() => { setNameSubmitted(false); setStudentName(""); }}
              className="sm:w-auto px-4 py-2.5 rounded-xl border border-gray-300 text-gray-600 hover:bg-gray-100 text-sm transition"
            >
              Edit Name
            </button>
          </div>
        )}
      </div>

      <style jsx global>{`
        @media print {
          body > * { display: none !important; }
          #certificate-print-area { display: block !important; }
          #certificate-print-area * { visibility: visible; }
          .no-print { display: none !important; }
          @page { margin: 0; size: A4 landscape; }
        }
        .certificate-paper {
          background: white;
          aspect-ratio: 1.414;
          position: relative;
          overflow: hidden;
          border-radius: 8px;
          box-shadow: 0 4px 24px rgba(0,0,0,0.12);
        }
      `}</style>
    </div>
  );
}

function CertificatePaper({
  studentName, badgeEmoji, badgeLabel, description, date,
}: {
  studentName: string; badgeEmoji: string; badgeLabel: string; description: string; date: string;
}) {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: "linear-gradient(135deg, #fdf6e3 0%, #fffdf5 50%, #fdf6e3 100%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "32px 40px",
        position: "relative",
        fontFamily: "'Georgia', 'Times New Roman', serif",
        boxSizing: "border-box",
      }}
    >
      {/* Decorative border */}
      <div style={{
        position: "absolute", inset: 10,
        border: "3px solid #b8972a",
        borderRadius: 8,
        pointerEvents: "none",
      }} />
      <div style={{
        position: "absolute", inset: 14,
        border: "1px solid #d4af37",
        borderRadius: 6,
        pointerEvents: "none",
      }} />

      {/* Corner ornaments */}
      {["topleft","topright","bottomleft","bottomright"].map((pos) => (
        <div key={pos} style={{
          position: "absolute",
          fontSize: 22, color: "#b8972a",
          top: pos.startsWith("top") ? 18 : undefined,
          bottom: pos.startsWith("bottom") ? 18 : undefined,
          left: pos.endsWith("left") ? 18 : undefined,
          right: pos.endsWith("right") ? 18 : undefined,
        }}>✦</div>
      ))}

      {/* Logo / Platform */}
      <div style={{ textAlign: "center", marginBottom: 8 }}>
        <div style={{ fontSize: 11, letterSpacing: 4, color: "#7c5c10", textTransform: "uppercase", fontFamily: "sans-serif" }}>
          OlympiadReady
        </div>
        <div style={{ width: 60, height: 2, background: "linear-gradient(90deg,transparent,#b8972a,transparent)", margin: "6px auto" }} />
      </div>

      {/* Title */}
      <div style={{ fontSize: 10, letterSpacing: 5, color: "#9a7b1a", textTransform: "uppercase", fontFamily: "sans-serif", marginBottom: 6 }}>
        Certificate of Achievement
      </div>

      {/* "This is to certify" */}
      <div style={{ fontSize: 13, color: "#5a4a2a", fontStyle: "italic", marginBottom: 4 }}>
        This is to proudly certify that
      </div>

      {/* Student name */}
      <div style={{
        fontSize: 30, fontWeight: "bold", color: "#2d1f0a",
        letterSpacing: 1, marginBottom: 4,
        borderBottom: "2px solid #d4af37", paddingBottom: 4, paddingLeft: 16, paddingRight: 16,
      }}>
        {studentName}
      </div>

      {/* Achievement text */}
      <div style={{ fontSize: 12, color: "#5a4a2a", fontStyle: "italic", marginBottom: 10, textAlign: "center" }}>
        has earned the distinguished achievement of
      </div>

      {/* Badge */}
      <div style={{
        background: "linear-gradient(135deg, #fff9e6, #fef3c7)",
        border: "2px solid #d4af37",
        borderRadius: 12,
        padding: "10px 24px",
        textAlign: "center",
        marginBottom: 10,
      }}>
        <div style={{ fontSize: 32, marginBottom: 2 }}>{badgeEmoji}</div>
        <div style={{ fontSize: 16, fontWeight: "bold", color: "#92400e", letterSpacing: 1 }}>{badgeLabel}</div>
        <div style={{ fontSize: 10, color: "#78480e", fontFamily: "sans-serif", marginTop: 2 }}>{description}</div>
      </div>

      {/* Footer */}
      <div style={{ fontSize: 10, color: "#9a7b1a", fontFamily: "sans-serif", textAlign: "center", marginTop: 6 }}>
        <div>Awarded on {date}</div>
        <div style={{ marginTop: 2, letterSpacing: 1, textTransform: "uppercase", fontSize: 9, color: "#b8972a" }}>
          www.olympiadready.com
        </div>
      </div>

      {/* Seal */}
      <div style={{
        position: "absolute", bottom: 30, right: 48,
        width: 64, height: 64,
        borderRadius: "50%",
        background: "radial-gradient(circle, #b8972a 0%, #8b6914 100%)",
        display: "flex", alignItems: "center", justifyContent: "center",
        flexDirection: "column", boxShadow: "0 2px 8px rgba(184,151,42,0.4)",
        border: "3px solid #d4af37",
      }}>
        <div style={{ fontSize: 20 }}>🏆</div>
        <div style={{ fontSize: 6, color: "#fff9e6", letterSpacing: 1, textAlign: "center", fontFamily: "sans-serif" }}>VERIFIED</div>
      </div>
    </div>
  );
}
