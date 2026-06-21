import { LegalPageLayout } from "@/components/LegalPageLayout";

export const metadata = {
  title: { absolute: "Cookie Policy · OlympiadReady" },
  description: "How OlympiadReady uses cookies and similar tracking technologies.",
};

export default function CookiesPage() {
  return (
    <LegalPageLayout title="Cookie Policy" lastUpdated="19 May 2026">
      <p>
        This Cookie Policy explains how OlympiadReady (operated by Nyxen Solutions) uses cookies and
        similar technologies when you visit our platform.
      </p>

      <h2>1. What Are Cookies?</h2>
      <p>
        Cookies are small text files stored on your device by your browser when you visit a website. They
        help us recognise you, remember your preferences, and understand how you use our Platform.
      </p>

      <h2>2. Cookies We Use</h2>

      <h3>Essential / Strictly Necessary Cookies</h3>
      <p>
        These cookies are required for OlympiadReady to function. You cannot opt out of them.
      </p>
      <ul>
        <li>
          <strong>__clerk_*</strong> — Authentication session cookies set by Clerk. Required to keep you
          signed in and protect your account.
        </li>
        <li>
          <strong>__session</strong> — Session management cookie used to maintain your active session.
        </li>
      </ul>

      <h3>Functional Cookies</h3>
      <p>
        These enhance your experience but are not strictly required.
      </p>
      <ul>
        <li>
          <strong>Preferences cookies</strong> — Remember your selected olympiad, grade, and subject
          preferences so you don&apos;t have to re-select them each visit.
        </li>
      </ul>

      <h3>Analytics Cookies</h3>
      <p>
        We may use privacy-respecting analytics tools to understand how the Platform is used. These
        cookies collect anonymised aggregate data (page views, session duration, feature usage) and
        do not identify you personally.
      </p>

      <h2>3. Third-Party Cookies</h2>
      <p>
        Some third-party services we use may set their own cookies:
      </p>
      <ul>
        <li>
          <strong>Clerk</strong> — Authentication provider. See{" "}
          <a href="https://clerk.com/privacy" target="_blank" rel="noopener noreferrer">Clerk&apos;s Privacy Policy</a>.
        </li>
        <li>
          <strong>Razorpay</strong> — Payment gateway. Razorpay may set cookies during checkout. See{" "}
          <a href="https://razorpay.com/privacy/" target="_blank" rel="noopener noreferrer">Razorpay&apos;s Privacy Policy</a>.
        </li>
      </ul>

      <h2>4. Managing Cookies</h2>
      <p>
        You can control cookies through your browser settings. Most browsers allow you to:
      </p>
      <ul>
        <li>View what cookies are stored and delete them.</li>
        <li>Block third-party cookies.</li>
        <li>Block cookies from specific websites.</li>
        <li>Block all cookies (note: this will break sign-in functionality).</li>
      </ul>
      <p>
        For guidance on managing cookies, visit your browser&apos;s help pages (Chrome, Firefox, Safari, Edge).
      </p>

      <h2>5. Cookie Duration</h2>
      <ul>
        <li><strong>Session cookies</strong> — Deleted when you close your browser.</li>
        <li><strong>Persistent cookies</strong> — Stored for a fixed period (typically 30–90 days) or until manually deleted.</li>
      </ul>

      <h2>6. Changes to This Policy</h2>
      <p>
        We may update this Cookie Policy as we add or change features. Material changes will be
        communicated via an in-app notice or email.
      </p>

      <h2>7. Contact</h2>
      <p>
        Questions about our cookie use? Email us at{" "}
        <a href="mailto:nyxencloud@gmail.com">nyxencloud@gmail.com</a>.
      </p>
    </LegalPageLayout>
  );
}
