"use client";

import { useState, useRef } from "react";
import { X, Download, Award, Loader2 } from "lucide-react";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

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

const CERT_DATE = new Date().toLocaleDateString("en-US", {
  month: "long", day: "numeric", year: "numeric",
});

export function CertificateModal({ config, onClose, onPhysicalClaimed }: Props) {
  const [studentName, setStudentName] = useState("");
  const [nameSubmitted, setNameSubmitted] = useState(false);
  const [physicalRequested, setPhysicalRequested] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const certRef = useRef<HTMLDivElement>(null);

  const handleDownload = async () => {
    if (!studentName.trim() || !certRef.current) return;
    
    setIsDownloading(true);
    try {
      // Temporarily remove border radius/shadows for clean capture
      const el = certRef.current;
      const originalStyle = el.getAttribute("style") || "";
      el.style.borderRadius = "0px";
      el.style.boxShadow = "none";
      el.style.transform = "scale(1)";
      
      const canvas = await html2canvas(el, {
        scale: 3, // High resolution
        useCORS: true,
        logging: false,
        backgroundColor: "#ffffff",
      });
      
      // Restore styles
      el.setAttribute("style", originalStyle);
      
      const imgData = canvas.toDataURL("image/jpeg", 1.0);
      
      // A4 landscape dimensions: 297 x 210 mm
      const pdf = new jsPDF({
        orientation: "landscape",
        unit: "mm",
        format: "a4",
      });
      
      pdf.addImage(imgData, "JPEG", 0, 0, 297, 210);
      pdf.save(`OlympiadReady_Certificate_${studentName.trim().replace(/\s+/g, "_")}.pdf`);
    } catch (err) {
      console.error("Failed to generate PDF", err);
      alert("Failed to generate PDF. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  };

  function handlePhysicalRequest() {
    if (!studentName.trim()) return;
    onPhysicalClaimed?.(studentName.trim());
    setPhysicalRequested(true);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl overflow-hidden flex flex-col max-h-[95vh]">

        {/* Modal header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div className="flex items-center gap-2 text-blue-900">
            <Award size={20} />
            <span className="font-bold text-sm">Achievement Certificate</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 transition rounded-full p-1 hover:bg-slate-100">
            <X size={20} />
          </button>
        </div>

        {/* Name entry */}
        {!nameSubmitted && (
          <div className="px-6 py-5 bg-blue-50/50 border-b border-blue-100">
            <p className="text-sm text-blue-900 font-semibold mb-3">
              Enter your full name as it should appear on the certificate:
            </p>
            <div className="flex gap-3">
              <input
                type="text"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && studentName.trim() && setNameSubmitted(true)}
                placeholder="e.g. Arjun Sharma"
                className="flex-1 border-2 border-blue-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 text-slate-800 bg-white font-medium"
                autoFocus
              />
              <button
                onClick={() => studentName.trim() && setNameSubmitted(true)}
                disabled={!studentName.trim()}
                className="bg-blue-600 disabled:opacity-50 disabled:hover:bg-blue-600 text-white px-6 py-2.5 rounded-xl text-sm font-bold hover:bg-blue-700 transition shadow-md shadow-blue-600/20"
              >
                Preview Certificate
              </button>
            </div>
          </div>
        )}

        {/* Certificate preview wrapper */}
        <div className="flex-1 overflow-auto bg-slate-100 p-4 sm:p-8 flex items-start sm:items-center justify-center">
          <div className="relative shadow-2xl transition-all shrink-0" style={{ width: 840, height: 594 }}>
            {/* We inject the Google Font needed for the cursive name */}
            <link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@700&display=swap" rel="stylesheet" />
            
            <div 
              ref={certRef}
              className="absolute inset-0 bg-slate-50 overflow-hidden bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] [background-size:16px_16px]"
              style={{ width: 840, height: 594 }}
            >
              {/* Corner Shapes - Top Left */}
              <div className="absolute top-0 left-0 w-32 h-32">
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <polygon points="0,0 100,0 0,100" fill="#1e3a8a" />
                  <polygon points="0,0 80,0 0,80" fill="#eab308" />
                  <polygon points="0,0 60,0 0,60" fill="#fde047" />
                </svg>
              </div>

              {/* Corner Shapes - Bottom Right */}
              <div className="absolute bottom-0 right-0 w-32 h-32 rotate-180">
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <polygon points="0,0 100,0 0,100" fill="#1e3a8a" />
                  <polygon points="0,0 80,0 0,80" fill="#eab308" />
                  <polygon points="0,0 60,0 0,60" fill="#fde047" />
                </svg>
              </div>

              {/* Decorative Border */}
              <div className="absolute inset-6 border-2 border-amber-600/30 rounded" />
              <div className="absolute inset-8 border border-blue-900/10 rounded" />

              {/* Add Google Fonts specifically for Certificate */}
              <style dangerouslySetInnerHTML={{__html: `
                @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&display=swap');
              `}} />

              {/* Header Section (Centered) */}
              <div className="absolute top-10 left-0 right-0 flex flex-col items-center z-10">
                <h1 
                  className="text-6xl text-blue-900 tracking-widest uppercase m-0 font-bold" 
                  style={{ fontFamily: "'Cinzel', serif" }}
                >
                  Certificate
                </h1>
                <h2 className="text-base tracking-[0.3em] text-slate-700 mt-2 uppercase font-semibold" style={{ fontFamily: "'Cinzel', serif" }}>
                  Of Achievement
                </h2>
              </div>
              
              {/* Gold Seal / Badge (Absolute Top Right) */}
              <div className="absolute top-10 right-10 z-20">
                <div className="relative w-28 h-36 flex flex-col items-center">
                  
                  {/* Ribbon tails */}
                  <div className="absolute top-20 left-1/2 -translate-x-1/2 flex gap-1 z-0">
                    <svg viewBox="0 0 24 56" className="w-6 h-14 drop-shadow-sm">
                      <polygon points="0,0 24,0 24,56 12,46 0,56" fill="#1e3a8a" />
                    </svg>
                    <svg viewBox="0 0 24 56" className="w-6 h-14 drop-shadow-sm">
                      <polygon points="0,0 24,0 24,56 12,46 0,56" fill="#1e3a8a" />
                    </svg>
                  </div>

                  {/* Medallion */}
                  <div className="relative w-28 h-28 rounded-full bg-gradient-to-b from-[#fde047] via-[#eab308] to-[#a16207] p-1 shadow-[0_10px_20px_rgba(0,0,0,0.2)] z-10">
                    <div className="w-full h-full rounded-full border-[3px] border-[#fef08a] bg-gradient-to-br from-[#eab308] to-[#ca8a04] flex flex-col items-center relative overflow-hidden pt-3">
                      <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-[#fef08a]/40 to-transparent transform -rotate-45 pointer-events-none" />
                      
                      <div className="relative z-10 flex flex-col items-center w-full">
                        <div className="text-2xl mb-1 drop-shadow-md">{config.badgeEmoji}</div>
                        <div className="text-[11px] font-black text-[#422006] uppercase tracking-wide text-center leading-tight px-2 max-w-[85px]" style={{ fontFamily: "'Cinzel', serif" }}>
                          {config.badgeLabel}
                        </div>
                      </div>
                    </div>
                  </div>

                </div>
              </div>

              {/* Middle Content */}
              <div className="absolute top-40 left-0 right-0 bottom-32 flex flex-col justify-center items-center z-10 px-12 text-center">
                <p className="text-slate-600 text-sm font-medium italic mb-2">
                  This Certificate is Proudly Presented to:
                </p>

                <div 
                  className="text-7xl text-amber-600 my-2 px-12 pb-6 leading-normal"
                  style={{ fontFamily: "'Great Vibes', cursive", borderBottom: "1px solid #cbd5e1" }}
                >
                  {nameSubmitted && studentName.trim() ? studentName.trim() : "Your Name Here"}
                </div>

                <div className="mt-6 max-w-2xl">
                  <p className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-2">
                    For successfully earning the title of:
                  </p>
                  <p className="text-xl text-blue-900 font-bold mb-2">
                    {config.badgeLabel}
                  </p>
                  <p className="text-xs text-slate-600 leading-relaxed max-w-lg mx-auto">
                    {config.description}. Your dedication, skill, and continuous learning on OlympiadReady have been recognized with this prestigious honor.
                  </p>
                </div>
              </div>

              {/* Signatures & Date */}
              <div className="absolute bottom-12 left-0 right-0 flex justify-center gap-32 z-10 px-8">
                
                <div className="flex flex-col items-center">
                  <div className="h-16 flex items-end justify-center mb-2">
                    <img src="/logo_welcome.png" alt="OlympiadReady" className="max-h-full" />
                  </div>
                  <div className="w-48 border-t border-slate-400 pt-1 text-[10px] font-bold text-slate-500 tracking-wider uppercase text-center">
                    Official Platform
                  </div>
                </div>

                <div className="flex flex-col items-center">
                  <div className="h-16 flex items-end justify-center mb-2">
                    <div className="text-base font-bold text-slate-800 pb-1">
                      {CERT_DATE}
                    </div>
                  </div>
                  <div className="w-48 border-t border-slate-400 pt-1 text-[10px] font-bold text-slate-500 tracking-wider uppercase text-center">
                    Date Issued
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        {nameSubmitted && (
          <div className="px-6 py-4 border-t border-slate-100 bg-white flex flex-wrap gap-3 items-center justify-between">
            <button
              onClick={() => { setNameSubmitted(false); setStudentName(""); }}
              className="text-sm font-semibold text-slate-500 hover:text-slate-700 underline transition"
            >
              Edit Name
            </button>
            
            <div className="flex gap-3">
              {config.rewardType === "physical" && !physicalRequested && (
                <button
                  onClick={handlePhysicalRequest}
                  className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white font-bold py-2.5 px-5 rounded-xl transition text-sm shadow-md shadow-amber-500/20"
                >
                  🏅 Request Physical Medal
                </button>
              )}
              {physicalRequested && (
                <div className="flex items-center gap-2 text-emerald-700 bg-emerald-50 rounded-xl py-2.5 px-5 text-sm font-bold border border-emerald-200">
                  ✅ Medal Request Sent
                </div>
              )}
              
              <button
                onClick={handleDownload}
                disabled={isDownloading}
                className="flex items-center gap-2 bg-blue-900 hover:bg-blue-950 disabled:bg-blue-800 text-white font-bold py-2.5 px-6 rounded-xl transition text-sm shadow-lg shadow-blue-900/30"
              >
                {isDownloading ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Download size={16} />
                )}
                {isDownloading ? "Generating PDF..." : "Download PDF"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
