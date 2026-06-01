import type { Metadata } from "next";
import SpellBeeClient from "./SpellBeeClient";

export const metadata: Metadata = {
  title: "Spell Bee Practice — Online Spelling Bee Trainer for Kids",
  description:
    "Practise for the Spell Bee with an AI-powered voice trainer for Classes 1–12. Hear words, spell them aloud, and build vocabulary with curated word lists and instant feedback.",
  keywords: [
    "spell bee practice",
    "spelling bee online",
    "spell bee words",
    "spelling practice for kids",
    "english spelling bee preparation",
    "vocabulary builder"
  ],
  alternates: { canonical: "/spell-bee" },
  openGraph: {
    title: "Spell Bee Practice — Online Spelling Bee Trainer | OlympiadReady",
    description:
      "AI voice-powered Spell Bee trainer for Classes 1–12. Hear words, spell them, and build vocabulary with instant feedback.",
    url: "https://olympiadready.com/spell-bee",
    type: "website"
  }
};

export default function Page() {
  return <SpellBeeClient />;
}
