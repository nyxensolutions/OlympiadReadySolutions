"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useAuth } from "@clerk/nextjs";
import {
  Upload, X, CheckCircle, AlertCircle, Eye, EyeOff, ImageIcon, Type,
  Link, Search, PlusCircle, Trash2, RotateCcw, ArrowRight, Database,
  Pencil, Save, ChevronDown, ChevronUp, Award,
} from "lucide-react";
import { BadgesPanel } from "@/components/admin/BadgesPanel";
import { ReportsPanel } from "@/components/admin/ReportsPanel";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

const SUBJECTS = [
  "Mathematics", "Science", "English", "Hindi", "General Knowledge",
  "Social Studies", "Logical Reasoning", "Cyber", "Commerce", "AI", "Spell Bee",
];
const DIFFICULTIES = ["Foundation", "Advanced", "Olympiad"];
const GRADES = Array.from({ length: 12 }, (_, i) => i + 1);
const ANSWER_LABELS = ["A", "B", "C", "D"] as const;
type AnswerLabel = "A" | "B" | "C" | "D";
type QuestionMode = "standard" | "image-options";
type TabId = "add" | "browse" | "badges" | "reports";

interface StoredImage { url: string; preview: string; }
interface Toast { type: "success" | "error"; message: string; }
interface BankQuestion {
  questionBankId: string; subject: string; grade: number; difficulty: string;
  topic: string; subTopic?: string; questionText: string; imageUrl?: string;
  options: string[]; correctAnswer: string; explanation: string;
}
interface LastAdded { subject: string; grade: number; topic: string; questionText: string; }

function isValidUrl(s: string) { try { new URL(s); return true; } catch { return false; } }
function isImgUrl(s: string) {
  return s.startsWith("http://") || s.startsWith("https://") || s.startsWith("/question-images/");
}
function detectMode(q: BankQuestion): QuestionMode {
  return q.options.some(isImgUrl) ? "image-options" : "standard";
}

// ─────────────────────────────────────────────────────────────────────────────

export default function AdminPage() {
  const { getToken, isLoaded, userId, signOut } = useAuth();
  const [authed, setAuthed] = useState(true); // Auto-authed by clerk
  const [toast, setToast] = useState<Toast | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>("add");
  const [stats, setStats] = useState<{ total: number } | null>(null);
  const [lastAdded, setLastAdded] = useState<LastAdded | null>(null);

  const [browseFilters, setBrowseFilters] = useState({
    subject: "", grade: "" as number | "", difficulty: "", topic: "", search: "", hasImage: false,
  });
  const [triggerSearch, setTriggerSearch] = useState(0);

  // Global edit modal state
  const [editingQuestion, setEditingQuestion] = useState<BankQuestion | null>(null);
  // Patch edited question in-place inside BrowsePanel without resetting the list
  const [pendingUpdate, setPendingUpdate] = useState<BankQuestion | null>(null);

  function showToast(type: Toast["type"], message: string) {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4500);
  }

  useEffect(() => {
    if (isLoaded) loadStats();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded]);

  async function loadStats() {
    try {
      const res = await fetch(`${API_URL}/api/admin/questions?pageSize=1`, {
        headers: { "Authorization": `Bearer ${await getToken()}` },
      });
      if (res.ok) { const d = await res.json(); setStats({ total: d.total }); }
    } catch { /* silent */ }
  }

  function goToBrowse(filters: Partial<typeof browseFilters>) {
    setBrowseFilters((f) => ({ ...f, ...filters }));
    setActiveTab("browse");
    setTriggerSearch((n) => n + 1);
  }

  if (!isLoaded) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-4 md:p-8">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-xl shadow-lg text-sm font-medium
          ${toast.type === "success" ? "bg-emerald-600" : "bg-red-600"} text-white`}>
          {toast.type === "success" ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          {toast.message}
        </div>
      )}

      {/* Edit Modal */}
      {editingQuestion && (
        <EditModal
          question={editingQuestion}
          
          showToast={showToast}
          onClose={() => setEditingQuestion(null)}
          onSaved={(updated) => {
            setEditingQuestion(null);
            showToast("success", "Question updated!");
            // Patch in-place — no list reset, no scroll jump
            setPendingUpdate(updated);
          }}
        />
      )}

      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">Question Bank CMS</h1>
            {stats && (
              <div className="flex items-center gap-1.5 mt-1 text-xs text-slate-400">
                <Database size={12} />
                <span>{stats.total.toLocaleString()} questions in bank</span>
              </div>
            )}
          </div>
          <button onClick={() => signOut()} className="text-xs text-slate-400 hover:text-white underline">
            Sign out
          </button>
        </div>

        {/* Tab bar */}
        <div className="flex gap-1 bg-slate-800 p-1 rounded-xl mb-6 flex-wrap">
          <TabBtn id="add" active={activeTab === "add"} onClick={() => setActiveTab("add")}
            icon={<PlusCircle size={15} />} label="Add Question" />
          <TabBtn id="browse" active={activeTab === "browse"} onClick={() => setActiveTab("browse")}
            icon={<Search size={15} />} label="Browse & Manage" />
          <TabBtn id="badges" active={activeTab === "badges"} onClick={() => setActiveTab("badges")}
            icon={<Award size={15} />} label="Badges & Rewards" />
          <TabBtn id="reports" active={activeTab === "reports"} onClick={() => setActiveTab("reports")}
            icon={<AlertCircle size={15} />} label="Reports" />
        </div>

        {activeTab === "add" && (
          <AddQuestionForm
            
            showToast={showToast}
            onAdded={(info) => { setLastAdded(info); loadStats(); }}
            goToBrowse={goToBrowse}
            lastAdded={lastAdded}
            onDismissAdded={() => setLastAdded(null)}
          />
        )}

        {activeTab === "badges" && (
          <BadgesPanel  showToast={showToast} />
        )}

        {activeTab === "reports" && (
          <ReportsPanel  showToast={showToast} />
        )}

        {activeTab === "browse" && (
          <BrowsePanel

            showToast={showToast}
            filters={browseFilters}
            setFilters={setBrowseFilters}
            triggerSearch={triggerSearch}
            onDeleted={() => loadStats()}
            onEdit={(q) => setEditingQuestion(q)}
            pendingUpdate={pendingUpdate}
            onUpdateConsumed={() => setPendingUpdate(null)}
          />
        )}
      </div>

      <style jsx global>{`
        .label  { display:block; font-size:.75rem; font-weight:600; color:rgb(148 163 184); text-transform:uppercase; letter-spacing:.05em; margin-bottom:.4rem; }
        .input  { width:100%; background:rgb(51 65 85); color:white; border-radius:.5rem; padding:.625rem .875rem; outline:none; border:1px solid transparent; transition:border-color .15s; }
        .input:focus  { border-color:rgb(99 102 241); }
        .input::placeholder { color:rgb(100 116 139); }
        .select { width:100%; background:rgb(51 65 85); color:white; border-radius:.5rem; padding:.625rem .875rem; outline:none; border:1px solid transparent; }
        .select:focus { border-color:rgb(99 102 241); }
      `}</style>
    </div>
  );
}

// ─── Tab button ───────────────────────────────────────────────────────────────
function TabBtn({ id, active, onClick, icon, label }: {
  id: string; active: boolean; onClick: () => void; icon: React.ReactNode; label: string;
}) {
  return (
    <button type="button" onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition
        ${active ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-white"}`}>
      {icon} {label}
    </button>
  );
}

// ─── Shared question form fields (used by both Add and Edit) ──────────────────
interface QuestionFormState {
  mode: QuestionMode;
  subject: string; grade: number; difficulty: string;
  topic: string; subTopic: string; questionText: string; explanation: string;
  correctAnswer: AnswerLabel;
  questionImage: StoredImage | null;
  textOptions: string[];
  optionImages: (StoredImage | null)[];
}

function useQuestionForm(initial?: Partial<QuestionFormState>) {
  const [mode, setMode] = useState<QuestionMode>(initial?.mode ?? "standard");
  const [subject, setSubject] = useState(initial?.subject ?? SUBJECTS[0]);
  const [grade, setGrade] = useState(initial?.grade ?? 1);
  const [difficulty, setDifficulty] = useState(initial?.difficulty ?? DIFFICULTIES[0]);
  const [topic, setTopic] = useState(initial?.topic ?? "");
  const [subTopic, setSubTopic] = useState(initial?.subTopic ?? "");
  const [questionText, setQuestionText] = useState(initial?.questionText ?? "");
  const [explanation, setExplanation] = useState(initial?.explanation ?? "");
  const [correctAnswer, setCorrectAnswer] = useState<AnswerLabel>(initial?.correctAnswer ?? "A");
  const [questionImage, setQuestionImage] = useState<StoredImage | null>(initial?.questionImage ?? null);
  const [textOptions, setTextOptions] = useState(initial?.textOptions ?? ["", "", "", ""]);
  const [optionImages, setOptionImages] = useState<(StoredImage | null)[]>(initial?.optionImages ?? [null, null, null, null]);

  return {
    mode, setMode, subject, setSubject, grade, setGrade,
    difficulty, setDifficulty, topic, setTopic, subTopic, setSubTopic,
    questionText, setQuestionText, explanation, setExplanation,
    correctAnswer, setCorrectAnswer, questionImage, setQuestionImage,
    textOptions, setTextOptions, optionImages, setOptionImages,
  };
}

// ─── Edit Modal ───────────────────────────────────────────────────────────────
function EditModal({ question, showToast, onClose, onSaved }: {
  question: BankQuestion;
  
  showToast: (t: Toast["type"], m: string) => void;
  onClose: () => void;
  onSaved: (updated: BankQuestion) => void;
}) {
  const { getToken } = useAuth();
  const initialMode = detectMode(question);
  const initialOptImages: (StoredImage | null)[] = initialMode === "image-options"
    ? question.options.map((o) => ({ url: o, preview: o }))
    : [null, null, null, null];
  const initialTextOpts = initialMode === "standard" ? question.options : ["", "", "", ""];

  const form = useQuestionForm({
    mode: initialMode,
    subject: question.subject,
    grade: question.grade,
    difficulty: question.difficulty,
    topic: question.topic,
    subTopic: question.subTopic ?? "",
    questionText: question.questionText,
    explanation: question.explanation,
    correctAnswer: question.correctAnswer as AnswerLabel,
    questionImage: question.imageUrl ? { url: question.imageUrl, preview: question.imageUrl } : null,
    textOptions: initialTextOpts,
    optionImages: initialOptImages,
  });

  const [uploading, setUploading] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState(false);

  const questionImgRef = useRef<HTMLInputElement>(null);
  const optionImgRefs = [useRef<HTMLInputElement>(null), useRef<HTMLInputElement>(null),
                         useRef<HTMLInputElement>(null), useRef<HTMLInputElement>(null)];

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  async function uploadFile(file: File, key: string): Promise<string | null> {
    setUploading((u) => ({ ...u, [key]: true }));
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API_URL}/api/admin/upload-image`, {
        method: "POST", headers: { "Authorization": `Bearer ${await getToken()}` }, body: fd,
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); showToast("error", e.error ?? "Upload failed"); return null; }
      return (await res.json()).url;
    } catch { showToast("error", "Network error"); return null; }
    finally { setUploading((u) => ({ ...u, [key]: false })); }
  }

  async function onFileChosen(file: File, key: string, onSuccess: (img: StoredImage) => void) {
    const preview = URL.createObjectURL(file);
    const url = await uploadFile(file, key);
    if (url) onSuccess({ url, preview });
  }

  function onUrlConfirmed(url: string, onSuccess: (img: StoredImage) => void) {
    if (!isValidUrl(url)) { showToast("error", "Please enter a valid URL"); return; }
    onSuccess({ url, preview: url });
  }

  async function handleSave() {
    if (!form.topic.trim()) { showToast("error", "Topic is required"); return; }
    if (!form.questionText.trim()) { showToast("error", "Question text is required"); return; }

    let options: string[];
    if (form.mode === "standard") {
      if (form.textOptions.some((o) => !o.trim())) { showToast("error", "All 4 text options are required"); return; }
      options = form.textOptions.map((o) => o.trim());
    } else {
      if (form.optionImages.some((o) => !o)) { showToast("error", "All 4 option images are required"); return; }
      options = form.optionImages.map((o) => o!.url);
    }

    const payload = {
      subject: form.subject, grade: form.grade, difficulty: form.difficulty,
      topic: form.topic.trim(), subTopic: form.subTopic.trim() || undefined,
      questionText: form.questionText.trim(),
      imageUrl: form.questionImage?.url ?? null,
      options, correctAnswer: form.correctAnswer,
      explanation: form.explanation.trim(),
    };

    setSaving(true);
    try {
      const res = await fetch(`${API_URL}/api/admin/questions/${question.questionBankId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${await getToken()}` },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) { showToast("error", data.error ?? "Update failed"); return; }
      onSaved({ ...question, ...payload, options, imageUrl: payload.imageUrl ?? undefined });
    } catch { showToast("error", "Network error"); }
    finally { setSaving(false); }
  }

  return (
    // Backdrop
    <div className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm flex items-start justify-center overflow-y-auto p-4 pt-10 pb-16">
      <div className="w-full max-w-2xl bg-slate-800 rounded-2xl shadow-2xl border border-slate-700">
        {/* Modal header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700">
          <div className="flex items-center gap-2 text-white font-semibold">
            <Pencil size={16} className="text-indigo-400" />
            Edit Question
            <span className="text-xs font-normal text-slate-400 ml-1">ID: {question.questionBankId.slice(0, 8)}…</span>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-700 transition">
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-5">
          {/* Mode toggle */}
          <div>
            <p className="label mb-2">Question Type</p>
            <div className="flex gap-3">
              <ModeButton active={form.mode === "standard"} onClick={() => form.setMode("standard")}
                icon={<Type size={16} />} label="Text answers" sub="4 text answer options. Question can optionally include an image." />
              <ModeButton active={form.mode === "image-options"} onClick={() => form.setMode("image-options")}
                icon={<ImageIcon size={16} />} label="Image answers" sub="4 image answer options. Question can optionally include an image too." />
            </div>
          </div>

          {/* Metadata */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Subject</label>
              <select value={form.subject} onChange={(e) => form.setSubject(e.target.value)} className="select">
                {SUBJECTS.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Grade</label>
              <select value={form.grade} onChange={(e) => form.setGrade(Number(e.target.value))} className="select">
                {GRADES.map((g) => <option key={g} value={g}>Grade {g}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Difficulty</label>
              <select value={form.difficulty} onChange={(e) => form.setDifficulty(e.target.value)} className="select">
                {DIFFICULTIES.map((d) => <option key={d}>{d}</option>)}
              </select>
            </div>
            <div className="col-span-2">
              <label className="label">Topic *</label>
              <input value={form.topic} onChange={(e) => form.setTopic(e.target.value)} className="input" />
            </div>
            <div>
              <label className="label">SubTopic</label>
              <input value={form.subTopic} onChange={(e) => form.setSubTopic(e.target.value)} className="input" />
            </div>
          </div>

          {/* Question text */}
          <div>
            <label className="label">Question Text *</label>
            <textarea value={form.questionText} onChange={(e) => form.setQuestionText(e.target.value)}
              rows={3} className="input resize-none" />
          </div>

          {/* Question image — available for both text-answer and image-answer modes */}
          <div>
            <label className="label">Question Image <span className="text-slate-500">(optional)</span></label>
            {form.questionImage
              ? <ImagePreview img={form.questionImage}
                  onRemove={() => { form.setQuestionImage(null); if (questionImgRef.current) questionImgRef.current.value = ""; }} />
              : <ImageInput slotKey="edit-question" inputRef={questionImgRef} uploading={!!uploading["edit-question"]}
                  onFile={(f) => onFileChosen(f, "edit-question", form.setQuestionImage)}
                  onUrl={(url) => onUrlConfirmed(url, form.setQuestionImage)} />
            }
          </div>

          {/* Options */}
          <div>
            <p className="label mb-3">Answer Options *</p>
            {form.mode === "standard" ? (
              <div className="space-y-3">
                {ANSWER_LABELS.map((lbl, i) => (
                  <div key={lbl} className="flex items-center gap-3">
                    <AnswerCircle letter={lbl} active={form.correctAnswer === lbl} onClick={() => form.setCorrectAnswer(lbl)} />
                    <input value={form.textOptions[i]}
                      onChange={(e) => { const n = [...form.textOptions]; n[i] = e.target.value; form.setTextOptions(n); }}
                      placeholder={`Option ${lbl}`} className="input flex-1" />
                  </div>
                ))}
                <p className="text-xs text-slate-400 mt-1">Click the letter circle to mark the correct answer.</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {ANSWER_LABELS.map((lbl, i) => (
                  <div key={lbl} className="space-y-2">
                    <div className="flex items-center gap-2">
                      <AnswerCircle letter={lbl} active={form.correctAnswer === lbl}
                        onClick={() => form.setCorrectAnswer(lbl)} small />
                      <span className="text-sm text-slate-300">Option {lbl}</span>
                    </div>
                    {form.optionImages[i]
                      ? <ImagePreview img={form.optionImages[i]!} compact
                          onRemove={() => {
                            form.setOptionImages((prev) => { const n = [...prev]; n[i] = null; return n; });
                            if (optionImgRefs[i].current) optionImgRefs[i].current!.value = "";
                          }} />
                      : <ImageInput slotKey={`edit-opt-${i}`} inputRef={optionImgRefs[i]}
                          uploading={!!uploading[`edit-opt-${i}`]} compact
                          onFile={(f) => onFileChosen(f, `edit-opt-${i}`, (img) =>
                            form.setOptionImages((prev) => { const n = [...prev]; n[i] = img; return n; }))}
                          onUrl={(url) => onUrlConfirmed(url, (img) =>
                            form.setOptionImages((prev) => { const n = [...prev]; n[i] = img; return n; }))} />
                    }
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Explanation */}
          <div>
            <label className="label">Explanation</label>
            <textarea value={form.explanation} onChange={(e) => form.setExplanation(e.target.value)}
              rows={2} className="input resize-none" placeholder="Why is this the correct answer?" />
          </div>

          {/* Action buttons */}
          <div className="flex gap-3 pt-1">
            <button onClick={handleSave} disabled={saving}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white font-semibold py-3 rounded-xl transition flex items-center justify-center gap-2">
              {saving
                ? <><span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />Saving…</>
                : <><Save size={16} /> Save Changes</>}
            </button>
            <button onClick={onClose}
              className="px-6 py-3 rounded-xl border border-slate-600 text-slate-300 hover:bg-slate-700 transition">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Add Question Form ────────────────────────────────────────────────────────
function AddQuestionForm({ showToast, onAdded, goToBrowse, lastAdded, onDismissAdded }: {
  
  showToast: (t: Toast["type"], m: string) => void;
  onAdded: (info: LastAdded) => void;
  goToBrowse: (filters: Record<string, unknown>) => void;
  lastAdded: LastAdded | null;
  onDismissAdded: () => void;
}) {
  const { getToken } = useAuth();
  const form = useQuestionForm();
  const [uploading, setUploading] = useState<Record<string, boolean>>({});
  const [submitting, setSubmitting] = useState(false);

  const questionImgRef = useRef<HTMLInputElement>(null);
  const optionImgRefs = [useRef<HTMLInputElement>(null), useRef<HTMLInputElement>(null),
                         useRef<HTMLInputElement>(null), useRef<HTMLInputElement>(null)];

  async function uploadFile(file: File, key: string): Promise<string | null> {
    setUploading((u) => ({ ...u, [key]: true }));
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API_URL}/api/admin/upload-image`, {
        method: "POST", headers: { "Authorization": `Bearer ${await getToken()}` }, body: fd,
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); showToast("error", e.error ?? "Upload failed"); return null; }
      return (await res.json()).url;
    } catch { showToast("error", "Network error during upload"); return null; }
    finally { setUploading((u) => ({ ...u, [key]: false })); }
  }

  async function onFileChosen(file: File, key: string, onSuccess: (img: StoredImage) => void) {
    const preview = URL.createObjectURL(file);
    const url = await uploadFile(file, key);
    if (url) onSuccess({ url, preview });
  }

  function onUrlConfirmed(url: string, onSuccess: (img: StoredImage) => void) {
    if (!isValidUrl(url)) { showToast("error", "Please enter a valid URL"); return; }
    onSuccess({ url, preview: url });
  }

  function resetForm() {
    form.setQuestionText(""); form.setExplanation(""); form.setCorrectAnswer("A");
    form.setQuestionImage(null); form.setTextOptions(["", "", "", ""]);
    form.setOptionImages([null, null, null, null]); form.setSubTopic("");
    if (questionImgRef.current) questionImgRef.current.value = "";
    optionImgRefs.forEach((r) => { if (r.current) r.current.value = ""; });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.topic.trim()) { showToast("error", "Topic is required"); return; }
    if (!form.questionText.trim()) { showToast("error", "Question text is required"); return; }
    let options: string[];
    if (form.mode === "standard") {
      if (form.textOptions.some((o) => !o.trim())) { showToast("error", "All 4 text options are required"); return; }
      options = form.textOptions.map((o) => o.trim());
    } else {
      if (form.optionImages.some((o) => !o)) { showToast("error", "All 4 option images are required"); return; }
      options = form.optionImages.map((o) => o!.url);
    }
    const payload = {
      subject: form.subject, grade: form.grade, difficulty: form.difficulty,
      topic: form.topic.trim(), subTopic: form.subTopic.trim() || undefined,
      questionText: form.questionText.trim(),
      imageUrl: form.questionImage?.url ?? null,
      options, correctAnswer: form.correctAnswer, explanation: form.explanation.trim(),
    };
    setSubmitting(true);
    try {
      const res = await fetch(`${API_URL}/api/admin/add-question`, {
        method: "POST", headers: { "Content-Type": "application/json", "Authorization": `Bearer ${await getToken()}` },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) { showToast("error", data.error ?? "Failed to add question"); return; }
      onAdded({ subject: form.subject, grade: form.grade, topic: form.topic.trim(), questionText: form.questionText.trim() });
      resetForm();
    } catch { showToast("error", "Network error"); }
    finally { setSubmitting(false); }
  }

  return (
    <div className="space-y-5 pb-10">
      {lastAdded && (
        <div className="flex items-center justify-between gap-3 bg-emerald-900/40 border border-emerald-700/50 rounded-xl px-4 py-3">
          <div className="flex items-center gap-2 text-emerald-300 text-sm min-w-0">
            <CheckCircle size={16} className="shrink-0" />
            <span className="truncate">Added: <span className="font-semibold">{lastAdded.questionText.slice(0, 60)}{lastAdded.questionText.length > 60 ? "…" : ""}</span></span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button type="button"
              onClick={() => goToBrowse({ subject: lastAdded.subject, grade: lastAdded.grade, topic: lastAdded.topic, search: "", difficulty: "", hasImage: false })}
              className="flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-200 font-semibold whitespace-nowrap">
              Browse similar <ArrowRight size={13} />
            </button>
            <button type="button" onClick={onDismissAdded} className="text-slate-500 hover:text-slate-300">
              <X size={15} />
            </button>
          </div>
        </div>
      )}

      <div className="bg-slate-800 rounded-2xl p-5">
        <p className="label mb-3">Question Type</p>
        <div className="flex gap-3">
          <ModeButton active={form.mode === "standard"} onClick={() => form.setMode("standard")}
            icon={<Type size={16} />} label="Text answers" sub="4 text answer options. Question can optionally include an image." />
          <ModeButton active={form.mode === "image-options"} onClick={() => form.setMode("image-options")}
            icon={<ImageIcon size={16} />} label="Image answers" sub="4 image answer options. Question can optionally include an image too." />
        </div>
      </div>

      <div className="bg-slate-800 rounded-2xl p-5 grid grid-cols-2 md:grid-cols-3 gap-4">
        <div>
          <label className="label">Subject</label>
          <select value={form.subject} onChange={(e) => form.setSubject(e.target.value)} className="select">
            {SUBJECTS.map((s) => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Grade</label>
          <select value={form.grade} onChange={(e) => form.setGrade(Number(e.target.value))} className="select">
            {GRADES.map((g) => <option key={g} value={g}>Grade {g}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Difficulty</label>
          <select value={form.difficulty} onChange={(e) => form.setDifficulty(e.target.value)} className="select">
            {DIFFICULTIES.map((d) => <option key={d}>{d}</option>)}
          </select>
        </div>
        <div className="col-span-2">
          <label className="label">Topic <span className="text-red-400">*</span></label>
          <input value={form.topic} onChange={(e) => form.setTopic(e.target.value)}
            placeholder="e.g. Animals, Shapes, Geometry" className="input" required />
        </div>
        <div>
          <label className="label">SubTopic <span className="text-slate-500">(opt.)</span></label>
          <input value={form.subTopic} onChange={(e) => form.setSubTopic(e.target.value)}
            placeholder="e.g. Wild Animals" className="input" />
        </div>
      </div>

      <div className="bg-slate-800 rounded-2xl p-5 space-y-4">
        <div>
          <label className="label">Question Text <span className="text-red-400">*</span></label>
          <textarea value={form.questionText} onChange={(e) => form.setQuestionText(e.target.value)} rows={3}
            placeholder={form.mode === "image-options" ? "e.g. Which of the following is an apple?" : "Type your question here..."}
            className="input resize-none" required />
        </div>
        {/* Question image — available for both text-answer and image-answer modes */}
        <div>
          <label className="label">Question Image <span className="text-slate-500">(optional)</span></label>
          {form.questionImage
            ? <ImagePreview img={form.questionImage} onRemove={() => { form.setQuestionImage(null); if (questionImgRef.current) questionImgRef.current.value = ""; }} />
            : <ImageInput slotKey="question" inputRef={questionImgRef} uploading={!!uploading["question"]}
                onFile={(f) => onFileChosen(f, "question", form.setQuestionImage)}
                onUrl={(url) => onUrlConfirmed(url, form.setQuestionImage)} />
          }
        </div>
      </div>

      <div className="bg-slate-800 rounded-2xl p-5">
        <p className="label mb-3">Answer Options <span className="text-red-400">*</span></p>
        {form.mode === "standard" ? (
          <div className="space-y-3">
            {ANSWER_LABELS.map((lbl, i) => (
              <div key={lbl} className="flex items-center gap-3">
                <AnswerCircle letter={lbl} active={form.correctAnswer === lbl} onClick={() => form.setCorrectAnswer(lbl)} />
                <input value={form.textOptions[i]}
                  onChange={(e) => { const n = [...form.textOptions]; n[i] = e.target.value; form.setTextOptions(n); }}
                  placeholder={`Option ${lbl}`} className="input flex-1" />
              </div>
            ))}
            <p className="text-xs text-slate-400 mt-1">Click the letter circle to mark the correct answer.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {ANSWER_LABELS.map((lbl, i) => (
              <div key={lbl} className="space-y-2">
                <div className="flex items-center gap-2">
                  <AnswerCircle letter={lbl} active={form.correctAnswer === lbl} onClick={() => form.setCorrectAnswer(lbl)} small />
                  <span className="text-sm text-slate-300">Option {lbl}</span>
                </div>
                {form.optionImages[i]
                  ? <ImagePreview img={form.optionImages[i]!} compact
                      onRemove={() => { form.setOptionImages((prev) => { const n = [...prev]; n[i] = null; return n; }); if (optionImgRefs[i].current) optionImgRefs[i].current!.value = ""; }} />
                  : <ImageInput slotKey={`opt_${i}`} inputRef={optionImgRefs[i]} uploading={!!uploading[`opt_${i}`]} compact
                      onFile={(f) => onFileChosen(f, `opt_${i}`, (img) => form.setOptionImages((prev) => { const n = [...prev]; n[i] = img; return n; }))}
                      onUrl={(url) => onUrlConfirmed(url, (img) => form.setOptionImages((prev) => { const n = [...prev]; n[i] = img; return n; }))} />
                }
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-slate-800 rounded-2xl p-5">
        <label className="label">Explanation <span className="text-slate-500">(optional but recommended)</span></label>
        <textarea value={form.explanation} onChange={(e) => form.setExplanation(e.target.value)}
          rows={2} placeholder="Why is this the correct answer?" className="input resize-none" />
      </div>

      <form onSubmit={handleSubmit}>
        <div className="flex gap-3">
          <button type="submit" disabled={submitting} onClick={handleSubmit as never}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed
                       text-white font-semibold py-3 rounded-xl transition flex items-center justify-center gap-2">
            {submitting
              ? <><span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" />Saving...</>
              : "Add Question"}
          </button>
          <button type="button" onClick={resetForm}
            className="px-5 py-3 rounded-xl border border-slate-600 text-slate-300 hover:bg-slate-700 transition flex items-center gap-2">
            <RotateCcw size={14} /> Clear
          </button>
        </div>
      </form>
    </div>
  );
}

// ─── Browse & Manage Panel ────────────────────────────────────────────────────
function BrowsePanel({ showToast, filters, setFilters, triggerSearch, onDeleted, onEdit, pendingUpdate, onUpdateConsumed }: {

  showToast: (t: Toast["type"], m: string) => void;
  filters: { subject: string; grade: number | ""; difficulty: string; topic: string; search: string; hasImage: boolean };
  setFilters: React.Dispatch<React.SetStateAction<typeof filters>>;
  triggerSearch: number;
  onDeleted: () => void;
  onEdit: (q: BankQuestion) => void;
  pendingUpdate: BankQuestion | null;
  onUpdateConsumed: () => void;
}) {
  const { getToken } = useAuth();
  const [results, setResults]           = useState<BankQuestion[]>([]);
  const [total, setTotal]               = useState(0);
  const [page, setPage]                 = useState(1);
  const [loading, setLoading]           = useState(false);
  const [loadingMore, setLoadingMore]   = useState(false);
  const [revealedIds, setRevealedIds]   = useState<Set<string>>(new Set());
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [deleting, setDeleting]         = useState<string | null>(null);
  const [jumpInput, setJumpInput]       = useState("");
  const sentinelRef                     = useRef<HTMLDivElement>(null);
  const PAGE_SIZE                       = 50;
  const totalPages                      = Math.ceil(total / PAGE_SIZE);
  const hasMore                         = results.length > 0 && results.length < total;

  // ── In-place patch after edit — no list reset, no scroll jump ──────────────
  useEffect(() => {
    if (!pendingUpdate) return;
    setResults((prev) =>
      prev.map((q) => q.questionBankId === pendingUpdate.questionBankId ? pendingUpdate : q)
    );
    onUpdateConsumed();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingUpdate]);

  // ── Fetch (append=false resets list; append=true infinite-loads) ───────────
  const search = useCallback(async (p = 1, append = false) => {
    if (append) setLoadingMore(true); else setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.subject)   params.set("subject",    filters.subject);
      if (filters.grade)     params.set("grade",      String(filters.grade));
      if (filters.difficulty) params.set("difficulty", filters.difficulty);
      if (filters.topic)     params.set("topic",      filters.topic);
      if (filters.search)    params.set("search",     filters.search);
      if (filters.hasImage)  params.set("hasImage",   "true");
      params.set("page",     String(p));
      params.set("pageSize", String(PAGE_SIZE));

      const res  = await fetch(`${API_URL}/api/admin/questions?${params}`,
        { headers: { "Authorization": `Bearer ${await getToken()}` } });
      if (!res.ok) { showToast("error", "Search failed"); return; }
      const data = await res.json();

      if (append) {
        setResults((prev) => [...prev, ...data.items]);
      } else {
        setResults(data.items);
        setRevealedIds(new Set());
        setDeleteConfirm(null);
      }
      setTotal(data.total);
      setPage(p);
    } catch { showToast("error", "Network error"); }
    finally { setLoading(false); setLoadingMore(false); }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // Triggered by filter-change / goToBrowse
  useEffect(() => { if (triggerSearch > 0) search(1, false); }, [triggerSearch, search]);

  // ── Infinite-scroll sentinel ───────────────────────────────────────────────
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel || !hasMore || loading || loadingMore) return;
    const observer = new IntersectionObserver(
      (entries) => { if (entries[0].isIntersecting) search(page + 1, true); },
      { rootMargin: "400px" }
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, loading, loadingMore, page, search]);

  function clearFilters() {
    setFilters({ subject: "", grade: "", difficulty: "", topic: "", search: "", hasImage: false });
  }

  async function deleteQuestion(id: string) {
    setDeleting(id);
    try {
      const res = await fetch(`${API_URL}/api/admin/questions/${id}`,
        { method: "DELETE", headers: { "Authorization": `Bearer ${await getToken()}` } });
      if (!res.ok) { const e = await res.json().catch(() => ({})); showToast("error", e.error ?? "Delete failed"); return; }
      showToast("success", "Question deleted.");
      setResults((prev) => prev.filter((q) => q.questionBankId !== id));
      setTotal((t) => t - 1);
      setDeleteConfirm(null);
      onDeleted();
    } catch { showToast("error", "Network error"); }
    finally { setDeleting(null); }
  }

  function handleJump(e: React.FormEvent) {
    e.preventDefault();
    const p = parseInt(jumpInput, 10);
    if (isNaN(p) || p < 1 || p > totalPages) {
      showToast("error", `Enter a page between 1 and ${totalPages}`);
      return;
    }
    search(p, false);
    setJumpInput("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  const hasActiveFilters = filters.subject || filters.grade || filters.difficulty || filters.topic || filters.search || filters.hasImage;

  return (
    <div className="space-y-4 pb-10">

      {/* ── Sticky filter bar ─────────────────────────────────────────────── */}
      <div className="sticky top-0 z-10 -mx-4 px-4 pt-2 pb-3 bg-slate-900">
        <div className="bg-slate-800 rounded-2xl p-4 space-y-3 shadow-xl shadow-slate-900/80 ring-1 ring-slate-700/50">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <div>
              <label className="label">Subject</label>
              <select value={filters.subject} onChange={(e) => setFilters((f) => ({ ...f, subject: e.target.value }))} className="select">
                <option value="">All subjects</option>
                {SUBJECTS.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Grade</label>
              <select value={filters.grade} onChange={(e) => setFilters((f) => ({ ...f, grade: e.target.value ? Number(e.target.value) : "" }))} className="select">
                <option value="">All grades</option>
                {GRADES.map((g) => <option key={g} value={g}>Grade {g}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Difficulty</label>
              <select value={filters.difficulty} onChange={(e) => setFilters((f) => ({ ...f, difficulty: e.target.value }))} className="select">
                <option value="">All levels</option>
                {DIFFICULTIES.map((d) => <option key={d}>{d}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Topic</label>
              <input value={filters.topic} onChange={(e) => setFilters((f) => ({ ...f, topic: e.target.value }))}
                onKeyDown={(e) => e.key === "Enter" && search(1)} placeholder="e.g. Animals" className="input" />
            </div>
            <div>
              <label className="label">Question text search</label>
              <input value={filters.search} onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
                onKeyDown={(e) => e.key === "Enter" && search(1)} placeholder="Search question text..." className="input" />
            </div>
          </div>
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input type="checkbox" checked={filters.hasImage} onChange={(e) => setFilters((f) => ({ ...f, hasImage: e.target.checked }))}
                className="w-4 h-4 accent-indigo-500" />
              <span className="text-sm text-slate-300">Image questions only</span>
            </label>
            <div className="flex gap-2 items-center">
              {hasActiveFilters && (
                <button type="button" onClick={clearFilters}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs text-slate-400 hover:text-slate-200 border border-slate-600 transition">
                  <RotateCcw size={12} /> Clear
                </button>
              )}
              <button type="button" onClick={() => search(1)} disabled={loading}
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white font-semibold px-5 py-2 rounded-xl transition text-sm">
                {loading
                  ? <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  : <><Search size={14} /> Search</>}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ── Results summary + jump-to-page ───────────────────────────────── */}
      {results.length > 0 && (
        <div className="flex items-center justify-between gap-3 text-xs text-slate-400 px-1 flex-wrap">
          <span>
            Showing <span className="text-slate-200 font-semibold">{results.length.toLocaleString()}</span> of{" "}
            <span className="text-slate-200 font-semibold">{total.toLocaleString()}</span> question{total !== 1 ? "s" : ""}
            {hasMore && <span className="text-indigo-400 ml-1">· scroll to load more</span>}
          </span>
          {totalPages > 1 && (
            <form onSubmit={handleJump} className="flex items-center gap-2">
              <span className="hidden sm:inline">Jump to page</span>
              <input
                value={jumpInput}
                onChange={(e) => setJumpInput(e.target.value)}
                placeholder={`1–${totalPages}`}
                className="w-16 bg-slate-700 text-white text-xs rounded-lg px-2 py-1.5 border border-slate-600 outline-none focus:border-indigo-500 text-center"
              />
              <button type="submit"
                className="px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-indigo-400 hover:text-indigo-200 font-semibold text-xs transition border border-slate-600">
                Go
              </button>
            </form>
          )}
        </div>
      )}

      {/* ── Question cards ────────────────────────────────────────────────── */}
      {results.map((q) => {
        const hasImgOpts      = q.options.some(isImgUrl);
        const revealed        = revealedIds.has(q.questionBankId);
        const confirmingDelete = deleteConfirm === q.questionBankId;
        const isDeletingThis  = deleting === q.questionBankId;

        return (
          <div key={q.questionBankId} className="bg-slate-800 rounded-2xl p-5 space-y-3">
            {/* Header row */}
            <div className="flex items-start justify-between gap-2">
              <div className="flex flex-wrap gap-1.5">
                <Chip color="indigo">{q.subject}</Chip>
                <Chip>Grade {q.grade}</Chip>
                <Chip>{q.difficulty}</Chip>
                <Chip dim>{q.topic}{q.subTopic ? ` · ${q.subTopic}` : ""}</Chip>
              </div>
              <div className="shrink-0 flex items-center gap-1">
                {!confirmingDelete && (
                  <button type="button" onClick={() => onEdit(q)}
                    className="flex items-center gap-1 text-xs text-slate-400 hover:text-indigo-400 transition px-2 py-1 rounded-lg hover:bg-indigo-900/20">
                    <Pencil size={13} /> Edit
                  </button>
                )}
                {!confirmingDelete ? (
                  <button type="button" onClick={() => setDeleteConfirm(q.questionBankId)}
                    className="flex items-center gap-1 text-xs text-slate-500 hover:text-red-400 transition px-2 py-1 rounded-lg hover:bg-red-900/20">
                    <Trash2 size={13} /> Delete
                  </button>
                ) : (
                  <div className="flex items-center gap-2 bg-red-900/30 border border-red-700/40 rounded-xl px-3 py-1.5">
                    <span className="text-xs text-red-300">Sure?</span>
                    <button type="button" onClick={() => deleteQuestion(q.questionBankId)} disabled={isDeletingThis}
                      className="text-xs font-bold text-red-400 hover:text-red-200 disabled:opacity-50">
                      {isDeletingThis ? "…" : "Yes"}
                    </button>
                    <button type="button" onClick={() => setDeleteConfirm(null)}
                      className="text-xs text-slate-400 hover:text-slate-200">Cancel</button>
                  </div>
                )}
              </div>
            </div>

            <p className="text-white font-medium leading-relaxed">{q.questionText}</p>

            {q.imageUrl && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={q.imageUrl} alt="Question" className="max-h-48 rounded-xl object-contain bg-slate-700 p-2" />
            )}

            <div className={`grid gap-2 ${hasImgOpts ? "grid-cols-2" : "grid-cols-1"}`}>
              {q.options.map((opt, i) => {
                const lbl      = ANSWER_LABELS[i];
                const isCorrect = q.correctAnswer === lbl;
                let style      = "border-slate-600 bg-slate-700/40";
                if (revealed) {
                  style = isCorrect
                    ? "border-emerald-500 bg-emerald-900/40"
                    : "border-slate-700 bg-slate-800/60 opacity-40";
                }
                return (
                  <div key={lbl} className={`rounded-xl border-2 p-2.5 transition ${style}`}>
                    {hasImgOpts && isImgUrl(opt) ? (
                      <div className="flex flex-col items-center gap-1.5">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={opt} alt={`Option ${lbl}`} className="w-full max-h-28 object-contain rounded-lg" />
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${revealed && isCorrect ? "bg-emerald-500 text-white" : "bg-slate-600 text-slate-300"}`}>
                          {lbl}{revealed && isCorrect ? " ✓" : ""}
                        </span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <span className={`w-6 h-6 shrink-0 flex items-center justify-center rounded-full text-xs font-bold
                          ${revealed && isCorrect ? "bg-emerald-500 text-white" : "bg-slate-600 text-slate-300"}`}>
                          {lbl}
                        </span>
                        <span className="text-sm text-slate-200">{opt}</span>
                        {revealed && isCorrect && <CheckCircle size={14} className="ml-auto text-emerald-400 shrink-0" />}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {!revealed ? (
              <button type="button"
                onClick={() => setRevealedIds((s) => new Set([...s, q.questionBankId]))}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-200 underline underline-offset-2 transition">
                Reveal answer →
              </button>
            ) : (() => {
              // Look up the actual option value for the correct letter so we can render image options
              const correctIdx   = ANSWER_LABELS.indexOf(q.correctAnswer as AnswerLabel);
              const correctVal   = correctIdx >= 0 ? q.options[correctIdx] : null;
              const correctIsImg = correctVal ? isImgUrl(correctVal) : false;
              // Only show explanation if it exists AND is not a duplicate of the correct-answer image
              const explanationIsImg   = q.explanation ? isImgUrl(q.explanation) : false;
              const isDuplicateExpl    = explanationIsImg && q.explanation === correctVal;
              const showExplanation    = !!q.explanation && !isDuplicateExpl;
              return (
                <div className="rounded-xl bg-emerald-900/25 border border-emerald-700/30 px-4 py-3 space-y-2">
                  {/* Correct answer letter */}
                  <p className="text-xs font-bold text-emerald-400">✓ Correct answer: {q.correctAnswer}</p>
                  {/* Render the correct option value as an image if it's an image URL */}
                  {correctIsImg && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={correctVal!} alt={`Correct answer ${q.correctAnswer}`}
                      className="max-h-28 rounded-lg object-contain bg-slate-800/60 p-1 border border-emerald-700/40" />
                  )}
                  {/* Explanation — skip if it duplicates the correct-answer image already shown above */}
                  {showExplanation && (
                    explanationIsImg ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={q.explanation} alt="Explanation diagram"
                        className="max-h-36 rounded-lg object-contain bg-slate-800/60 p-1 border border-slate-700" />
                    ) : (
                      <p className="text-xs text-slate-300 leading-relaxed">{q.explanation}</p>
                    )
                  )}
                </div>
              );
            })()}
          </div>
        );
      })}

      {/* ── Infinite scroll sentinel ──────────────────────────────────────── */}
      <div ref={sentinelRef} className="h-2" />

      {/* Loading-more spinner */}
      {loadingMore && (
        <div className="flex items-center justify-center gap-2 py-6 text-slate-400 text-sm">
          <span className="animate-spin w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full" />
          Loading more questions…
        </div>
      )}

      {/* All-loaded footer */}
      {!hasMore && results.length > 0 && !loading && !loadingMore && (
        <div className="flex items-center justify-center gap-3 py-4 text-xs text-slate-500">
          <span>All {total.toLocaleString()} questions loaded</span>
          <span>·</span>
          <button type="button"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="text-indigo-400 hover:text-indigo-200 font-semibold transition">
            ↑ Back to top
          </button>
        </div>
      )}

      {results.length === 0 && !loading && (
        <div className="text-center text-slate-500 py-16 text-sm">
          <Search size={32} className="mx-auto mb-3 opacity-30" />
          Use the filters above and hit Search to browse questions.
        </div>
      )}
    </div>
  );
}

// ─── Shared UI components ─────────────────────────────────────────────────────
function Chip({ children, color, dim }: { children: React.ReactNode; color?: "indigo"; dim?: boolean }) {
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium
      ${color === "indigo" ? "bg-indigo-900/50 text-indigo-300" : dim ? "bg-slate-700 text-slate-400" : "bg-slate-700 text-slate-300"}`}>
      {children}
    </span>
  );
}

function ModeButton({ active, onClick, icon, label, sub }: {
  active: boolean; onClick: () => void; icon: React.ReactNode; label: string; sub: string;
}) {
  return (
    <button type="button" onClick={onClick}
      className={`flex-1 rounded-xl p-4 text-left transition border-2
        ${active ? "border-indigo-500 bg-indigo-500/10" : "border-slate-700 hover:border-slate-500"}`}>
      <div className={`flex items-center gap-2 font-semibold mb-1 ${active ? "text-indigo-400" : "text-slate-300"}`}>
        {icon} {label}
      </div>
      <p className="text-xs text-slate-400">{sub}</p>
    </button>
  );
}

function AnswerCircle({ letter, active, onClick, small = false }: {
  letter: string; active: boolean; onClick: () => void; small?: boolean;
}) {
  return (
    <button type="button" onClick={onClick}
      className={`${small ? "w-7 h-7 text-xs" : "w-8 h-8 text-sm"} rounded-full font-bold flex-shrink-0 transition border-2
        ${active ? "bg-emerald-500 border-emerald-500 text-white" : "border-slate-600 text-slate-400 hover:border-emerald-400"}`}>
      {letter}
    </button>
  );
}

function ImagePreview({ img, onRemove, compact = false }: { img: StoredImage; onRemove: () => void; compact?: boolean }) {
  return (
    <div className="relative inline-block max-w-full">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={img.preview} alt="preview"
        className={`rounded-xl object-contain bg-slate-700 p-2 ${compact ? "h-28 w-full" : "h-36"}`} />
      <button type="button" onClick={onRemove}
        className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 rounded-full p-0.5">
        <X size={14} />
      </button>
      <p className="text-xs text-slate-400 mt-1 truncate max-w-xs" title={img.url}>{img.url}</p>
    </div>
  );
}

function ImageInput({ slotKey, inputRef, uploading, onFile, onUrl, compact = false }: {
  slotKey: string; inputRef: React.RefObject<HTMLInputElement>; uploading: boolean;
  onFile: (f: File) => void; onUrl: (url: string) => void; compact?: boolean;
}) {
  const [tab, setTab] = useState<"upload" | "url">("upload");
  const [urlValue, setUrlValue] = useState("");
  return (
    <div className="border-2 border-dashed border-slate-600 rounded-xl overflow-hidden">
      <div className="flex border-b border-slate-700">
        <button type="button" onClick={() => setTab("upload")}
          className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 text-xs font-medium transition
            ${tab === "upload" ? "bg-slate-700 text-indigo-400" : "text-slate-400 hover:text-slate-200"}`}>
          <Upload size={12} /> Upload
        </button>
        <button type="button" onClick={() => setTab("url")}
          className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 text-xs font-medium transition
            ${tab === "url" ? "bg-slate-700 text-indigo-400" : "text-slate-400 hover:text-slate-200"}`}>
          <Link size={12} /> Paste URL
        </button>
      </div>
      {tab === "upload" && (
        <div onClick={() => !uploading && inputRef.current?.click()}
          className={`flex flex-col items-center justify-center cursor-pointer text-slate-400 hover:text-indigo-400 transition ${compact ? "py-4" : "py-7"}`}>
          {uploading
            ? <span className="animate-spin w-5 h-5 border-2 border-current border-t-transparent rounded-full" />
            : <><Upload size={compact ? 18 : 22} className="mb-1" />
               <p className={compact ? "text-xs" : "text-sm"}>{compact ? "Click to upload" : "Click or drag an image here"}</p>
               {!compact && <p className="text-xs text-slate-500 mt-0.5">JPG, PNG, GIF, WebP, SVG · max 10 MB</p>}</>
          }
          <input ref={inputRef} type="file" accept="image/*" className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }} />
        </div>
      )}
      {tab === "url" && (
        <div className="p-3 space-y-2">
          <p className="text-xs text-slate-400">Paste any public image URL (R2, S3, etc.)</p>
          <div className="flex gap-2">
            <input value={urlValue} onChange={(e) => setUrlValue(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), urlValue.trim() && (onUrl(urlValue.trim()), setUrlValue("")))}
              placeholder="https://pub-xxxx.r2.dev/questions/..." className="input flex-1 text-xs py-2" />
            <button type="button" onClick={() => { if (urlValue.trim()) { onUrl(urlValue.trim()); setUrlValue(""); } }}
              className="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs rounded-lg transition shrink-0">
              Use
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
