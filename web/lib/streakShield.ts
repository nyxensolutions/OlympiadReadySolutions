/**
 * Streak Shield — client-side store using localStorage.
 * Free users get 0 shields, Pro users get 2 per calendar month.
 * Shield data is reset automatically on the first access of a new month.
 */

const KEY = "or_streak_shields";

type ShieldStore = {
  shields: number;
  usedDates: string[];   // ISO date strings (YYYY-MM-DD) that shields protected
  resetMonth: string;    // "YYYY-MM" — resets when month changes
};

function thisMonth(): string {
  return new Date().toISOString().slice(0, 7);
}

function load(tier: "Free" | "Pro"): ShieldStore {
  const maxShields = tier === "Pro" ? 2 : 0;
  const month = thisMonth();
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const stored: ShieldStore = JSON.parse(raw);
      if (stored.resetMonth === month) return stored;
    }
  } catch {
    // ignore
  }
  // New month or nothing stored — reset
  return { shields: maxShields, usedDates: [], resetMonth: month };
}

function save(store: ShieldStore) {
  try {
    localStorage.setItem(KEY, JSON.stringify(store));
  } catch {
    // ignore
  }
}

export function getShieldState(tier: "Free" | "Pro"): ShieldStore {
  return load(tier);
}

export function useShield(tier: "Free" | "Pro"): boolean {
  const store = load(tier);
  if (store.shields <= 0) return false;
  const yesterday = new Date(Date.now() - 86_400_000).toISOString().split("T")[0];
  if (store.usedDates.includes(yesterday)) return false; // already shielded
  const updated: ShieldStore = {
    ...store,
    shields: store.shields - 1,
    usedDates: [...store.usedDates, yesterday],
  };
  save(updated);
  return true;
}

export function getShieldedDates(tier: "Free" | "Pro"): string[] {
  return load(tier).usedDates;
}
