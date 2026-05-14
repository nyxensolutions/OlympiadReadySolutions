"use client";

import { AiCalloutSection } from "./landing/AiCalloutSection";
import { CTASection } from "./landing/CTASection";
import { FeaturesSection } from "./landing/FeaturesSection";
import { HeroSection } from "./landing/HeroSection";
import { HowItWorksSection } from "./landing/HowItWorksSection";
import { LandingFooter } from "./landing/LandingFooter";
import { SocialProofSection } from "./landing/SocialProofSection";
import { SubjectCoverageSection } from "./landing/SubjectCoverageSection";
import { TestimonialsSection } from "./landing/TestimonialsSection";

export function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      <HeroSection />
      <SocialProofSection />
      <FeaturesSection />
      <HowItWorksSection />
      <TestimonialsSection />
      <AiCalloutSection />
      <SubjectCoverageSection />
      <CTASection />
      <LandingFooter />
    </div>
  );
}
