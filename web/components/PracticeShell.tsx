"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import type { PreviewRequest } from "@/lib/types";
import { GeneratorFlow } from "@/components/GeneratorFlow";
import { OlympiadSelector, OLYMPIAD_DATA, type OlympiadId } from "@/components/OlympiadSelector";
import { OnboardingModal, type OnboardingData } from "@/components/OnboardingModal";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";
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
  const { getToken, isSignedIn } = useAuth();
  const [olympiad, setOlympiad] = useState<OlympiadId>("open");
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [autoStart, setAutoStart] = useState(initialConfig?.mistakesOnly ?? false);
  const [onboardingConfig, setOnboardingConfig] = useState<Partial<PreviewRequest> | undefined>(undefined);

  useEffect(() => {
    if (typeof window !== "undefined") {
      if (!localStorage.getItem("hasCompletedOnboarding")) {
        setShowOnboarding(true);
      }

      // If we arrived via a deep link (e.g. ?mistakes=true), clear the URL so
      // refreshing the page doesn't trap the user in an auto-start loop.
      if (window.location.search) {
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }, []);

  const olympiadInfo = OLYMPIAD_DATA.find((o) => o.id === olympiad)!;
  const { Left, Right } = SKETCH_PAIRS[olympiad] ?? DEFAULT_SKETCHES;
  const rot = ROTATE[olympiad] ?? DEFAULT_ROTATE;

  // Pre-fill the subject field when a specific olympiad is selected
  const subjectOverride: Partial<PreviewRequest> | undefined =
    onboardingConfig ||
    (olympiadInfo.subject
      ? { ...(initialConfig ?? {}), subject: olympiadInfo.subject }
      : initialConfig);

  const handleOnboardingComplete = async (data: OnboardingData) => {
    localStorage.setItem("hasCompletedOnboarding", "true");
    localStorage.setItem("onboardingGrade", String(data.grade));
    localStorage.setItem("onboardingSubject", data.subject);
    setOlympiad(data.olympiadId);
    setOnboardingConfig({
      grade: data.grade,
      subject: data.subject,
      difficulty: "Foundation",
      count: 10,
    });
    setAutoStart(true);
    setShowOnboarding(false);

    if (data.schoolInviteCode && isSignedIn) {
      try {
        const token = await getToken();
        const res = await fetch(`${API_URL}/api/schools/join`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ inviteCode: data.schoolInviteCode }),
        });
        if (res.ok) {
          const school = await res.json();
          localStorage.setItem("schoolInfo", JSON.stringify({ name: school.name, logoUrl: school.logoUrl }));
          // Reload to let AppHeader and subscription status pick up school membership
          window.location.reload();
        }
      } catch {
        // Non-fatal
      }
    }
  };

  return (
    <div className="relative w-full">
      {showOnboarding && <OnboardingModal onComplete={handleOnboardingComplete} />}
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

      <OlympiadSelector 
        selected={olympiad} 
        onSelect={(id) => {
          setOlympiad(id);
          setAutoStart(false);
        }} 
      />

      <GeneratorFlow key={olympiad} initialConfig={subjectOverride} autoStart={autoStart} olympiadId={olympiad} />
    </div>
  );
}
