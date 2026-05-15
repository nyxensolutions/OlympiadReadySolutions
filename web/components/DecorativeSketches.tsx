// Stroke-only SVG sketches used as decorative background elements.
// All are aria-hidden and pointer-events-none — purely cosmetic.

type P = { className?: string };

export function FlaskSketch({ className }: P) {
  return (
    <svg width="56" height="82" viewBox="0 0 56 82" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <line x1="16" y1="6" x2="40" y2="6" strokeWidth="2.5" />
      <line x1="19" y1="6" x2="19" y2="26" />
      <line x1="37" y1="6" x2="37" y2="26" />
      <line x1="19" y1="26" x2="4"  y2="68" />
      <line x1="37" y1="26" x2="52" y2="68" />
      <line x1="4"  y1="68" x2="52" y2="68" />
      <path d="M8 54 Q16 50 24 54 Q32 58 44 54" />
      <circle cx="14" cy="61" r="2" />
      <circle cx="25" cy="58" r="1.5" />
      <circle cx="36" cy="62" r="2" />
    </svg>
  );
}

export function AtomSketch({ className }: P) {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <circle cx="32" cy="32" r="5" />
      <ellipse cx="32" cy="32" rx="28" ry="10" />
      <ellipse cx="32" cy="32" rx="28" ry="10" transform="rotate(60 32 32)" />
      <ellipse cx="32" cy="32" rx="28" ry="10" transform="rotate(120 32 32)" />
      <circle cx="60" cy="32" r="3" fill="currentColor" stroke="none" />
      <circle cx="18" cy="9"  r="3" fill="currentColor" stroke="none" />
      <circle cx="18" cy="55" r="3" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function LaptopSketch({ className }: P) {
  return (
    <svg width="74" height="54" viewBox="0 0 74 54" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <rect x="6"  y="2"  width="62" height="38" rx="3" />
      <rect x="10" y="6"  width="54" height="30" rx="1" />
      <line x1="16" y1="14" x2="46" y2="14" strokeDasharray="2 3" />
      <line x1="16" y1="20" x2="56" y2="20" strokeDasharray="2 3" />
      <line x1="16" y1="26" x2="38" y2="26" strokeDasharray="2 3" />
      <line x1="4"  y1="40" x2="70" y2="40" />
      <path d="M2 40 L0 52 L74 52 L72 40 Z" />
      <rect x="29" y="44" width="16" height="5" rx="1.5" />
    </svg>
  );
}

export function AIChipSketch({ className }: P) {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <rect x="14" y="14" width="36" height="36" rx="3" />
      <line x1="24" y1="14" x2="24" y2="50" />
      <line x1="32" y1="14" x2="32" y2="50" />
      <line x1="40" y1="14" x2="40" y2="50" />
      <line x1="14" y1="24" x2="50" y2="24" />
      <line x1="14" y1="32" x2="50" y2="32" />
      <line x1="14" y1="40" x2="50" y2="40" />
      {/* pins left */}
      <line x1="14" y1="20" x2="6"  y2="20" />
      <line x1="14" y1="28" x2="6"  y2="28" />
      <line x1="14" y1="36" x2="6"  y2="36" />
      <line x1="14" y1="44" x2="6"  y2="44" />
      {/* pins right */}
      <line x1="50" y1="20" x2="58" y2="20" />
      <line x1="50" y1="28" x2="58" y2="28" />
      <line x1="50" y1="36" x2="58" y2="36" />
      <line x1="50" y1="44" x2="58" y2="44" />
      {/* pins top */}
      <line x1="22" y1="14" x2="22" y2="6" />
      <line x1="30" y1="14" x2="30" y2="6" />
      <line x1="38" y1="14" x2="38" y2="6" />
      <line x1="46" y1="14" x2="46" y2="6" />
      {/* pins bottom */}
      <line x1="22" y1="50" x2="22" y2="58" />
      <line x1="30" y1="50" x2="30" y2="58" />
      <line x1="38" y1="50" x2="38" y2="58" />
      <line x1="46" y1="50" x2="46" y2="58" />
    </svg>
  );
}

export function CompassSketch({ className }: P) {
  return (
    <svg width="52" height="80" viewBox="0 0 52 80" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <circle cx="26" cy="12" r="5" />
      <line x1="26" y1="17" x2="8"  y2="68" />
      <line x1="26" y1="17" x2="44" y2="68" />
      <line x1="14" y1="42" x2="38" y2="42" />
      <circle cx="8"  cy="68" r="2" fill="currentColor" stroke="none" />
      <path  d="M40 64 L44 68 L40 72 L38 68 Z" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function PiSketch({ className }: P) {
  return (
    <svg width="60" height="70" viewBox="0 0 60 70" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <line x1="8"  y1="18" x2="52" y2="18" strokeWidth="2" />
      <line x1="18" y1="18" x2="18" y2="60" />
      <path d="M38 18 L40 52 C40 60 46 64 52 64" />
      <circle cx="52" cy="10" r="4" />
      <line x1="50" y1="10" x2="54" y2="10" />
      <line x1="52" y1="8"  x2="52" y2="12" />
    </svg>
  );
}

export function TestTubeSketch({ className }: P) {
  return (
    <svg width="34" height="80" viewBox="0 0 34 80" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <line x1="10" y1="4"  x2="10" y2="60" />
      <line x1="24" y1="4"  x2="24" y2="60" />
      <path d="M10 60 Q17 74 24 60" />
      <line x1="6"  y1="4"  x2="28" y2="4" />
      <path d="M10 50 Q17 46 24 50" />
      <circle cx="15" cy="60" r="2" />
      <circle cx="21" cy="56" r="1.5" />
      <line x1="10" y1="25" x2="14" y2="25" />
      <line x1="10" y1="35" x2="14" y2="35" />
      <line x1="10" y1="45" x2="14" y2="45" />
    </svg>
  );
}

export function PencilSketch({ className }: P) {
  return (
    <svg width="44" height="120" viewBox="0 0 44 120" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <rect x="12" y="4"  width="20" height="9"  rx="2" />
      <line x1="12" y1="13" x2="32" y2="13" />
      <rect x="12" y="16" width="20" height="64" />
      <line x1="14" y1="28" x2="30" y2="28" strokeDasharray="2 3" />
      <line x1="14" y1="40" x2="30" y2="40" strokeDasharray="2 3" />
      <line x1="14" y1="52" x2="30" y2="52" strokeDasharray="2 3" />
      <path d="M12 80 L22 108 L32 80 Z" />
      <line x1="12" y1="80" x2="32" y2="80" />
      <circle cx="22" cy="108" r="1.5" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function LightbulbSketch({ className }: P) {
  return (
    <svg width="56" height="100" viewBox="0 0 56 100" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true">
      <line x1="28" y1="4"  x2="28" y2="10" />
      <line x1="12" y1="8"  x2="16" y2="13" />
      <line x1="44" y1="8"  x2="40" y2="13" />
      <line x1="4"  y1="24" x2="10" y2="24" />
      <line x1="52" y1="24" x2="46" y2="24" />
      <path d="M28 15 C17 15 10 23 10 33 C10 42 15 49 21 53 L21 64 L35 64 L35 53 C41 49 46 42 46 33 C46 23 39 15 28 15 Z" />
      <path d="M20 28 C22 23 25 20 28 20" strokeOpacity="0.4" />
      <line x1="21" y1="68" x2="35" y2="68" />
      <line x1="23" y1="72" x2="33" y2="72" />
      <path d="M26 76 Q28 80 30 76" />
    </svg>
  );
}
