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

type SketchFC = React.FC<{ className?: string }>;

const SKETCH_PAIRS: Partial<Record<OlympiadId, { Left: SketchFC; Right: SketchFC }>> = {
  open:              { Left: PencilSketch,   Right: LightbulbSketch },
  hbcse:             { Left: PiSketch,       Right: CompassSketch   },
  sof_imo:           { Left: PiSketch,       Right: CompassSketch   },
  sof_nso:           { Left: AtomSketch,     Right: FlaskSketch     },
  sof_ieo:           { Left: PencilSketch,   Right: LightbulbSketch },
  sof_nco:           { Left: LaptopSketch,   Right: AIChipSketch    },
  silverzone_math:   { Left: PiSketch,       Right: LaptopSketch    },
  silverzone_science:{ Left: TestTubeSketch, Right: FlaskSketch     },
  silverzone_english:{ Left: PencilSketch,   Right: LightbulbSketch },
  silverzone_computer:{ Left: LaptopSketch,  Right: AIChipSketch    },
  unified_nstse:     { Left: AtomSketch,     Right: CompassSketch   },
  unified_uieo:      { Left: PencilSketch,   Right: LightbulbSketch },
  math_olympiad:     { Left: PiSketch,       Right: CompassSketch   },
  science_olympiad:  { Left: FlaskSketch,    Right: AtomSketch      },
  computer_olympiad: { Left: LaptopSketch,   Right: AIChipSketch    },
  english_olympiad:  { Left: PencilSketch,   Right: LightbulbSketch },
};

const ROTATE: Partial<Record<OlympiadId, { left: string; right: string }>> = {
  open:    { left: "rotate(-8deg)",  right: "rotate(6deg)"  },
  hbcse:   { left: "rotate(-5deg)",  right: "rotate(8deg)"  },
  sof_imo: { left: "rotate(-5deg)",  right: "rotate(8deg)"  },
  sof_nso: { left: "rotate(-10deg)", right: "rotate(5deg)"  },
};

const DEFAULT_SKETCHES = { Left: PencilSketch, Right: LightbulbSketch };
const DEFAULT_ROTATE   = { left: "rotate(-8deg)", right: "rotate(6deg)" };

export function PracticeShell({
  initialConfig,
}: {
  initialConfig?: Partial<PreviewRequest>;
}) {
  const [olympiad, setOlympiad] = useState<OlympiadId>("open");
  const olympiadInfo = OLYMPIAD_DATA.find((o) => o.id === olympiad)!;
  const { Left, Right } = SKETCH_PAIRS[olympiad] ?? DEFAULT_SKETCHES;
  const rot = ROTATE[olympiad] ?? DEFAULT_ROTATE;

  // Pre-fill the subject field when a specific olympiad is selected
  const subjectOverride: Partial<PreviewRequest> | undefined =
    olympiadInfo.subject
      ? { ...(initialConfig ?? {}), subject: olympiadInfo.subject }
      : initialConfig;

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

      <GeneratorFlow initialConfig={subjectOverride} />
    </div>
  );
}
