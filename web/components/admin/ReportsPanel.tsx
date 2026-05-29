import { useEffect, useState } from "react";
import { Check, X, AlertOctagon, Loader2 } from "lucide-react";
import { useAuth } from "@clerk/nextjs";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

type Report = {
  reportId: string;
  userId: string;
  userEmail: string;
  userFullName: string;
  questionBankId: string;
  questionText: string;
  category: string;
  description: string;
  status: string;
  adminReason: string | null;
  reportedAt: string;
  resolvedAt: string | null;
};

export function ReportsPanel({ showToast }: { showToast: (type: "success" | "error", msg: string) => void }) {
  const { getToken } = useAuth();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [showRejectModal, setShowRejectModal] = useState<string | null>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  async function fetchReports() {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/admin/reports`, {
        headers: { "Authorization": `Bearer ${await getToken()}` }
      });
      if (res.ok) {
        const data = await res.json();
        setReports(data);
      }
    } catch (e) {
      showToast("error", "Failed to fetch reports");
    } finally {
      setLoading(false);
    }
  }

  async function resolveReport(id: string, status: "Accepted" | "Rejected", reason?: string) {
    setResolvingId(id);
    try {
      const res = await fetch(`${API_URL}/api/admin/reports/${id}/resolve`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${await getToken()}`
        },
        body: JSON.stringify({ status, adminReason: reason })
      });
      if (res.ok) {
        showToast("success", `Report ${status.toLowerCase()} successfully`);
        setReports(prev => prev.map(r => r.reportId === id ? { ...r, status, adminReason: reason || null, resolvedAt: new Date().toISOString() } : r));
        setShowRejectModal(null);
        setRejectReason("");
      } else {
        showToast("error", "Failed to resolve report");
      }
    } catch (e) {
      showToast("error", "Network error");
    } finally {
      setResolvingId(null);
    }
  }

  if (loading) return (
    <div className="flex justify-center p-10"><Loader2 className="animate-spin text-slate-500 h-8 w-8" /></div>
  );

  return (
    <div className="space-y-4">
      {reports.length === 0 ? (
        <div className="text-center py-12 bg-slate-800 rounded-2xl border border-slate-700">
          <AlertOctagon className="h-12 w-12 text-slate-500 mx-auto mb-3 opacity-50" />
          <p className="text-slate-400">No question reports found.</p>
        </div>
      ) : (
        reports.map(r => (
          <div key={r.reportId} className="bg-slate-800 rounded-2xl p-5 border border-slate-700 space-y-4">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                    r.status === 'Pending' ? 'bg-amber-900/50 text-amber-400' :
                    r.status === 'Accepted' ? 'bg-emerald-900/50 text-emerald-400' :
                    'bg-slate-700 text-slate-400'
                  }`}>
                    {r.status}
                  </span>
                  <span className="text-slate-400 text-xs">{new Date(r.reportedAt).toLocaleString()}</span>
                </div>
                <p className="text-sm font-semibold text-white">Reported by: <span className="text-indigo-300">{r.userFullName || r.userEmail}</span></p>
                <p className="text-xs text-slate-400 font-mono mt-1">User ID: {r.userId}</p>
              </div>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-xl">
              <p className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-2">Question Text</p>
              <p className="text-slate-300 text-sm">{r.questionText}</p>
            </div>

            <div className="bg-rose-900/20 border border-rose-900/50 p-4 rounded-xl">
              <p className="text-xs text-rose-400 font-bold uppercase tracking-wider mb-2">{r.category}</p>
              <p className="text-rose-200 text-sm">{r.description}</p>
            </div>

            {r.status === 'Pending' && (
              <div className="flex gap-2 justify-end pt-2">
                <button
                  onClick={() => setShowRejectModal(r.reportId)}
                  disabled={resolvingId === r.reportId}
                  className="px-4 py-2 text-sm font-semibold text-slate-300 bg-slate-700 hover:bg-slate-600 rounded-lg transition"
                >
                  Reject
                </button>
                <button
                  onClick={() => resolveReport(r.reportId, "Accepted")}
                  disabled={resolvingId === r.reportId}
                  className="px-4 py-2 text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg transition"
                >
                  {resolvingId === r.reportId ? <Loader2 className="h-4 w-4 animate-spin inline" /> : "Accept & Notify"}
                </button>
              </div>
            )}

            {r.status !== 'Pending' && r.adminReason && (
              <div className="bg-slate-700/50 p-3 rounded-lg text-sm text-slate-300 mt-2">
                <span className="font-semibold text-slate-400">Admin Reason:</span> {r.adminReason}
              </div>
            )}
          </div>
        ))
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-2xl w-full max-w-md border border-slate-700 overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-slate-700 flex justify-between items-center">
              <h3 className="font-bold text-white">Reject Report</h3>
              <button onClick={() => setShowRejectModal(null)} className="text-slate-400 hover:text-white">
                <X size={20} />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Reason for Rejection</label>
                <textarea
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:outline-none focus:border-indigo-500"
                  rows={3}
                  placeholder="Explain why this report is invalid..."
                />
              </div>
              <div className="flex gap-3 justify-end">
                <button onClick={() => setShowRejectModal(null)} className="px-4 py-2 rounded-xl text-slate-300 hover:bg-slate-700">Cancel</button>
                <button
                  onClick={() => resolveReport(showRejectModal, "Rejected", rejectReason)}
                  disabled={!rejectReason.trim()}
                  className="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold disabled:opacity-50"
                >
                  Confirm Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
