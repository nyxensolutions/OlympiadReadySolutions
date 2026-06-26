import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Contact Us",
  description:
    "Get in touch with OlympiadReady — for questions, feedback, school partnerships, or support. We'd love to hear from you.",
  alternates: { canonical: "/contact" }
};

export default function ContactLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
