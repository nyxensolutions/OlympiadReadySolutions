"use client";

import { useState } from "react";
import type { PreviewRequest } from "@/lib/types";
import { GeneratorFlow } from "@/components/GeneratorFlow";
import { OlympiadSelector, OLYMPIAD_DATA, type OlympiadId } from "@/components/OlympiadSelector";
import {
  AtomSketch,
  AIChipSketch,
  CompassSketch,
  FlaskSketch,
  LaptopSketch,
  LightbulbSketch,
  PencilSketch,
  PiSketch,
  TestTubeSketch,
} from "@/components/DecorativeSketches";

// Each olympiad shows a distinct sketch pair in the left/right gutters
const SKETCH_PAIRS: Record<OlympiadId, { Left: React.FC<{ className?: string }>; Right: React.FC<{ className?: string }> }> = {
  open:  { Left: PencilSketch,  Right: LightbulbSketch },
  imo:   { Left: PiSketch,      Right: CompassSketch },
  nso:   { Left: AtomSketch,    Right: FlaskSketch },
  ieo:   { Left: PencilSketch,  Right: LightbulbSketch },
  ntse:  { Left: TestTubeSketch,Right: AIChipSketch },
  ioqm:  { Left: PiSketch,      Right: LaptopSketch },
};

const ROTATE: Record<OlympiadId, { left: string; right: string }> = {
  open:  { left: "rotate(-8deg)",  right: "rotate(6deg)"   },
  imo:   { left: "rotate(-5deg)",  right: "rotate(8deg)"   },
  nso:   { left: "rotate(-10deg)", right: "rotate(5deg)"   },
  ieo:   { left: "rotate(-6deg)",  right: "rotate(10deg)"  },
  ntse:  { left: "rotate(-12deg)", right: "rotate(4deg)"   },
  ioqm:  { left: "rotate(-7deg)",  right: "rotate(-5deg)"  },
};

export function PracticeShell({
  initialConfig,
}: {
  initialConfig?: Partial<PreviewRequest>;
}) {
  const [olympiad, setOlympiad] = useState<OlympiadId>("open");
  const olympiadInfo = OLYMPIAD_DATA.find((o) => o.id === olympiad)!;
  const { Left, Right } = SKETCH_PAIRS[olympiad];
  const rot = ROTATE[olympiad];

  return (
    <div className="relative w-full">
      {/* Left gutter sketch */}
      <div
        className="pointer-events-none absolute -left-10 top-20 hidden opacity-40 xl:block"
        style={{ transform: rot.left }}
      >
        <Left className="text-slate-300" />
      </div>

      {/* Right gutter sketch */}
      <div
        className="pointer-events-none absolute -right-8 top-36 hidden opacity-40 xl:block"
        style={{ transform: rot.right }}
      >
        <Right className="text-slate-300" />
      </div>

      {/* Second pair of sketches lower down */}
      <div
        className="pointer-events-none absolute -left-8 top-[420px] hidden opacity-25 xl:block"
        style={{ transform: "rotate(10deg)" }}
      >
        <Right className="text-slate-300" />
      </div>
      <div
        className="pointer-events-none absolute -right-10 top-[520px] hidden opacity-25 xl:block"
        style={{ transform: "rotate(-8deg)" }}
      >
        <Left className="text-slate-300" />
      </div>

      {/* Olympiad selector */}
      <OlympiadSelector selected={olympiad} onSelect={setOlympiad} />

      {/* Context pill when a specific olympiad is chosen */}
      {olympiad !== "open" && (
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-500 shadow-sm">
          <span className="font-semibold text-slate-700">
            {olympiadInfo.icon} Preparing for {olympiadInfo.name}
          </span>
          <span className="text-slate-400">·</span>
          <span>{olympiadInfo.fullName ?? olympiadInfo.name}</span>
          <span className="text-slate-400">·</span>
          <span className="text-brand-600 font-medium">AI-generated questions</span>
        </div>
      )}

      <GeneratorFlow initialConfig={initialConfig} />
    </div>
  );
}
