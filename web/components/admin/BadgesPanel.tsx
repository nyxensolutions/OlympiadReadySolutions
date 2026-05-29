"use client";

import { useEffect, useState } from "react";
import { Award, Medal, RefreshCw, ChevronDown, ChevronUp, Package, CheckCircle, Truck } from "lucide-react";
import { useAuth } from "@clerk/nextjs";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

interface BadgeMap { [key: string]: boolean; }

interface UserBadgeRow {
  userId: string;
  fullName: string;
  email: string;
  joinedAt: string;
  subscriptionTier: string;
  totalTests: number;
  bestPct: number;
  streak: number;
  earnedCount: number;
  totalBadges: number;
  badges: BadgeMap;
  physicalRewardEligible: boolean;
}

interface RewardClaim {
  claimId: string;
  userId: string;
  studentName: string;
  email: string;
  rewardType: string;
  status: string;
  requestedAt: string;
  shippedAt: string | null;
  adminNotes: string | null;
  trackingNumber: string | null;
}

const BADGE_META: Record<string, { emoji: string; label: string }> = {
  // Activity
  first_test:        { emoji: "🚀", label: "First Step" },
  five_tests:        { emoji: "🔁", label: "On a Roll" },
  ten_tests:         { emoji: "💪", label: "Dedicated" },
  twenty_five_tests: { emoji: "🎓", label: "Knowledge Seeker" },
  century:           { emoji: "💯", label: "Century" },
  // Accuracy
  sharpshooter:      { emoji: "🎯", label: "Sharpshooter" },
  perfect:           { emoji: "⭐", label: "Perfect Score" },
  on_fire:           { emoji: "🔴", label: "On Fire" },
  comeback:          { emoji: "📈", label: "Comeback King" },
  // Streaks
  streak_3:          { emoji: "🔥", label: "3-Day Streak" },
  streak_7:          { emoji: "🏅", label: "Week Warrior" },
  streak_30:         { emoji: "🗓️", label: "Iron Will" },
  // Speed
  speed:             { emoji: "⚡", label: "Speed Demon" },
  lightning:         { emoji: "🌩️", label: "Lightning" },
  // Breadth
  explorer:          { emoji: "🌍", label: "Explorer" },
  all_rounder:       { emoji: "🌟", label: "All-Rounder" },
  // Milestones
  mock_exam:         { emoji: "📋", label: "Olympiad Scholar" },
  mock_3:            { emoji: "🏆", label: "Mock Master" },
};

const STATUS_COLORS: Record<string, string> = {
  Pending:   "bg-yellow-100 text-yellow-800 border-yellow-200",
  Confirmed: "bg-blue-100 text-blue-800 border-blue-200",
  Shipped:   "bg-purple-100 text-purple-800 border-purple-200",
  Delivered: "bg-green-100 text-green-800 border-green-200",
  Cancelled: "bg-red-100 text-red-800 border-red-200",
};

export function BadgesPanel({ showToast }: { showToast: (t: "success" | "error", m: string) => void }) {
  const { getToken } = useAuth();
  const [activeSubTab, setActiveSubTab] = useState<"students" | "rewards">("students");
  const [users, setUsers] = useState<UserBadgeRow[]>([]);
  const [rewards, setRewards] = useState<RewardClaim[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedUser, setExpandedUser] = useState<string | null>(null);
  const [editingClaim, setEditingClaim] = useState<RewardClaim | null>(null);
  const [claimForm, setClaimForm] = useState({ status: "", adminNotes: "", trackingNumber: "" });

  async function loadUsers() {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/admin/badges`, { headers: { "Authorization": `Bearer ${await getToken()}` } });
      if (res.ok) setUsers(await res.json());
      else showToast("error", "Failed to load badge data");
    } finally {
      setLoading(false);
    }
  }

  async function loadRewards() {
    try {
      const res = await fetch(`${API_URL}/api/admin/physical-rewards`, { headers: { "Authorization": `Bearer ${await getToken()}` } });
      if (res.ok) setRewards(await res.json());
    } catch { /* silent */ }
  }

  useEffect(() => { loadUsers(); loadRewards(); }, []);

  async function saveClaimEdit() {
    if (!editingClaim) return;
    const res = await fetch(`${API_URL}/api/admin/physical-rewards/${editingClaim.claimId}`, {
      method: "PUT",
      headers: { "Authorization": `Bearer ${await getToken()}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        status: claimForm.status || null,
        adminNotes: claimForm.adminNotes || null,
        trackingNumber: claimForm.trackingNumber || null,
      }),
    });
    if (res.ok) {
      showToast("success", "Reward claim updated");
      setEditingClaim(null);
      loadRewards();
    } else {
      showToast("error", "Failed to update claim");
    }
  }

  async function createClaim(userId: string, fullName: string) {
    const res = await fetch(`${API_URL}/api/admin/physical-rewards/${userId}/claim`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${await getToken()}`, "Content-Type": "application/json" },
      body: JSON.stringify({ rewardType: "olympiad_legend", studentName: fullName }),
    });
    if (res.ok) {
      showToast("success", "Physical reward claim created");
      loadRewards();
      setActiveSubTab("rewards");
    } else {
      const err = await res.json().catch(() => ({}));
      showToast("error", err.error || "Failed to create claim");
    }
  }

  const eligibleCount = users.filter((u) => u.physicalRewardEligible).length;
  const pendingRewards = rewards.filter((r) => r.status === "Pending").length;

  return (
    <div>
      {/* Sub-tab bar */}
      <div className="flex gap-2 mb-6">
        <SubTabBtn
          active={activeSubTab === "students"}
          onClick={() => setActiveSubTab("students")}
          label="Student Achievements"
          badge={users.length > 0 ? String(users.length) : undefined}
        />
        <SubTabBtn
          active={activeSubTab === "rewards"}
          onClick={() => setActiveSubTab("rewards")}
          label="Physical Rewards"
          badge={pendingRewards > 0 ? String(pendingRewards) : undefined}
          badgeColor="bg-amber-500"
        />
        <button
          onClick={() => { loadUsers(); loadRewards(); }}
          className="ml-auto flex items-center gap-1.5 text-slate-400 hover:text-white text-xs px-3 py-1.5 rounded-lg border border-slate-700 hover:border-slate-500 transition"
        >
          <RefreshCw size={12} /> Refresh
        </button>
      </div>

      {/* Students tab */}
      {activeSubTab === "students" && (
        <div>
          {/* Summary cards */}
          <div className="grid grid-cols-3 gap-3 mb-5">
            <SummaryCard label="Total Students" value={users.length} color="indigo" />
            <SummaryCard label="Olympiad Legends" value={eligibleCount} color="amber" />
            <SummaryCard label="Avg Badges" value={users.length > 0 ? (users.reduce((a, u) => a + u.earnedCount, 0) / users.length).toFixed(1) : "0"} color="emerald" />
          </div>

          {loading && (
            <div className="text-center text-slate-400 py-8 text-sm">Loading badge data…</div>
          )}

          {!loading && users.length === 0 && (
            <div className="text-center text-slate-500 py-8 text-sm">No students yet.</div>
          )}

          <div className="space-y-2">
            {users.map((u) => (
              <div key={u.userId} className={`rounded-xl border transition ${u.physicalRewardEligible ? "border-amber-500/40 bg-amber-950/20" : "border-slate-700 bg-slate-800"}`}>
                {/* Row header */}
                <button
                  className="w-full text-left flex items-center gap-3 px-4 py-3"
                  onClick={() => setExpandedUser(expandedUser === u.userId ? null : u.userId)}
                >
                  {/* Avatar */}
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${u.physicalRewardEligible ? "bg-amber-500 text-white" : "bg-indigo-600 text-white"}`}>
                    {(u.fullName || u.email).charAt(0).toUpperCase()}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-white truncate">{u.fullName || u.email}</span>
                      {u.physicalRewardEligible && <span className="text-xs bg-amber-500 text-white px-1.5 py-0.5 rounded-full font-medium shrink-0">🏆 Legend</span>}
                      <span className={`text-xs px-1.5 py-0.5 rounded-full shrink-0 ${u.subscriptionTier === "Free" ? "bg-slate-700 text-slate-400" : "bg-indigo-800 text-indigo-200"}`}>
                        {u.subscriptionTier}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 truncate">{u.email}</div>
                  </div>

                  {/* Stats */}
                  <div className="hidden sm:flex items-center gap-4 text-xs text-slate-400 shrink-0">
                    <span title="Tests taken">📝 {u.totalTests}</span>
                    <span title="Best score">🎯 {u.bestPct}%</span>
                    <span title="Streak">🔥 {u.streak}d</span>
                  </div>

                  {/* Badge progress */}
                  <div className="flex items-center gap-2 shrink-0">
                    <div className="text-xs font-semibold text-white">{u.earnedCount}/{u.totalBadges}</div>
                    <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${u.physicalRewardEligible ? "bg-amber-400" : "bg-indigo-500"}`}
                        style={{ width: `${(u.earnedCount / u.totalBadges) * 100}%` }}
                      />
                    </div>
                    {expandedUser === u.userId ? <ChevronUp size={14} className="text-slate-400" /> : <ChevronDown size={14} className="text-slate-400" />}
                  </div>
                </button>

                {/* Expanded badge detail */}
                {expandedUser === u.userId && (
                  <div className="px-4 pb-4 border-t border-slate-700 pt-3">
                    <div className="flex flex-wrap gap-2 mb-3">
                      {Object.entries(BADGE_META).map(([id, meta]) => {
                        const earned = u.badges[id] ?? false;
                        return (
                          <div key={id} className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs border transition ${earned ? "bg-indigo-900/50 border-indigo-600 text-white" : "bg-slate-700/50 border-slate-600 text-slate-500"}`}>
                            <span className={earned ? "" : "grayscale opacity-40"}>{meta.emoji}</span>
                            {meta.label}
                          </div>
                        );
                      })}
                    </div>

                    {u.physicalRewardEligible && (
                      <button
                        onClick={() => createClaim(u.userId, u.fullName)}
                        className="flex items-center gap-1.5 bg-amber-600 hover:bg-amber-500 text-white text-xs px-3 py-1.5 rounded-lg font-medium transition"
                      >
                        <Package size={12} /> Create Physical Reward Claim
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Physical rewards tab */}
      {activeSubTab === "rewards" && (
        <div>
          {rewards.length === 0 && (
            <div className="text-center text-slate-500 py-10 text-sm">
              No physical reward claims yet.<br />
              <span className="text-xs">They appear here when a student or admin creates a claim.</span>
            </div>
          )}

          <div className="space-y-3">
            {rewards.map((r) => (
              <div key={r.claimId} className="bg-slate-800 border border-slate-700 rounded-xl p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className="text-sm font-medium text-white">{r.studentName}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${STATUS_COLORS[r.status] ?? "bg-slate-700 text-slate-300 border-slate-600"}`}>
                        {r.status}
                      </span>
                      <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full">
                        {r.rewardType.replace(/_/g, " ")}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">{r.email}</div>
                    <div className="text-xs text-slate-500 mt-1">
                      Requested: {new Date(r.requestedAt).toLocaleDateString("en-IN")}
                      {r.shippedAt && ` · Shipped: ${new Date(r.shippedAt).toLocaleDateString("en-IN")}`}
                      {r.trackingNumber && ` · Tracking: ${r.trackingNumber}`}
                    </div>
                    {r.adminNotes && (
                      <div className="text-xs text-slate-400 mt-1 italic">Note: {r.adminNotes}</div>
                    )}
                  </div>

                  <button
                    onClick={() => {
                      setEditingClaim(r);
                      setClaimForm({ status: r.status, adminNotes: r.adminNotes ?? "", trackingNumber: r.trackingNumber ?? "" });
                    }}
                    className="text-xs text-indigo-400 hover:text-indigo-300 shrink-0 px-2 py-1 rounded border border-indigo-800 hover:border-indigo-600 transition"
                  >
                    Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Edit reward modal */}
      {editingClaim && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="bg-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl border border-slate-700">
            <h3 className="text-white font-semibold mb-4">Update Reward Claim</h3>
            <div className="text-xs text-slate-400 mb-4">
              Student: <span className="text-white">{editingClaim.studentName}</span> · {editingClaim.email}
            </div>

            <div className="space-y-3">
              <div>
                <label className="label">Status</label>
                <select
                  value={claimForm.status}
                  onChange={(e) => setClaimForm((f) => ({ ...f, status: e.target.value }))}
                  className="select"
                >
                  {["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"].map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Tracking Number</label>
                <input
                  value={claimForm.trackingNumber}
                  onChange={(e) => setClaimForm((f) => ({ ...f, trackingNumber: e.target.value }))}
                  placeholder="e.g. IN123456789"
                  className="input"
                />
              </div>
              <div>
                <label className="label">Admin Notes</label>
                <textarea
                  value={claimForm.adminNotes}
                  onChange={(e) => setClaimForm((f) => ({ ...f, adminNotes: e.target.value }))}
                  placeholder="Internal notes (not shown to student)"
                  rows={3}
                  className="input resize-none"
                />
              </div>
            </div>

            <div className="flex gap-2 mt-5">
              <button onClick={saveClaimEdit} className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl text-sm font-medium transition">
                Save Changes
              </button>
              <button onClick={() => setEditingClaim(null)} className="px-4 py-2.5 rounded-xl border border-slate-600 text-slate-300 hover:bg-slate-700 text-sm transition">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SubTabBtn({ active, onClick, label, badge, badgeColor = "bg-indigo-500" }: {
  active: boolean; onClick: () => void; label: string; badge?: string; badgeColor?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${active ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700"}`}
    >
      {label}
      {badge && (
        <span className={`${badgeColor} text-white text-xs px-1.5 py-0.5 rounded-full min-w-[18px] text-center`}>{badge}</span>
      )}
    </button>
  );
}

function SummaryCard({ label, value, color }: { label: string; value: number | string; color: "indigo" | "amber" | "emerald" }) {
  const colors = {
    indigo: "bg-indigo-900/40 border-indigo-700 text-indigo-300",
    amber: "bg-amber-900/40 border-amber-700 text-amber-300",
    emerald: "bg-emerald-900/40 border-emerald-700 text-emerald-300",
  };
  return (
    <div className={`${colors[color]} border rounded-xl p-3 text-center`}>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-xs mt-0.5">{label}</div>
    </div>
  );
}
