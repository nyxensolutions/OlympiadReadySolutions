import { LegalPageLayout } from "@/components/LegalPageLayout";

export const metadata = {
  title: { absolute: "Privacy Policy · OlympiadReady" },
  description: "How OlympiadReady collects, uses, and protects your personal information.",
};

export default function PrivacyPage() {
  return (
    <LegalPageLayout title="Privacy Policy" lastUpdated="19 May 2026">
      <h2>1. Who We Are</h2>
      <p>
        OlympiadReady is operated by <strong>Nyxen Solutions</strong>, a technology company based in India.
        We provide an AI-powered Olympiad preparation platform for school students. Our registered contact
        email is <a href="mailto:nyxencloud@gmail.com">nyxencloud@gmail.com</a>.
      </p>

      <h2>2. What Information We Collect</h2>
      <h3>Information you provide</h3>
      <ul>
        <li><strong>Account data:</strong> Name, email address, and any profile information provided during sign-up via Clerk.</li>
        <li><strong>Payment data:</strong> For paid purchases, we collect the Razorpay order ID and payment ID. We do <em>not</em> store your card numbers or bank details — these are handled entirely by Razorpay.</li>
      </ul>
      <h3>Information collected automatically</h3>
      <ul>
        <li><strong>Usage data:</strong> Practice papers generated, test results, topic mastery scores, and interaction timestamps.</li>
        <li><strong>Device &amp; log data:</strong> Browser type, IP address, and pages visited — collected for security and analytics.</li>
        <li><strong>Cookies:</strong> Authentication tokens and session cookies. See our <a href="/cookies">Cookie Policy</a>.</li>
      </ul>

      <h2>3. How We Use Your Information</h2>
      <ul>
        <li>To provide and improve the OlympiadReady service.</li>
        <li>To personalise your practice experience and track topic mastery.</li>
        <li>To process payments and grant access to Pro features or PDF downloads.</li>
        <li>To send important service communications (e.g., subscription renewal reminders).</li>
        <li>To comply with legal obligations.</li>
      </ul>

      <h2>4. Data Sharing</h2>
      <p>We do <strong>not</strong> sell your personal data. We share data only with:</p>
      <ul>
        <li><strong>Clerk</strong> — authentication and identity management.</li>
        <li><strong>Razorpay</strong> — payment processing (governed by Razorpay's own Privacy Policy).</li>
        <li><strong>Anthropic (Claude API)</strong> — AI question generation. Only subject/grade/difficulty metadata is sent; no personal data.</li>
        <li><strong>Law enforcement</strong> — when required by applicable Indian law.</li>
      </ul>

      <h2>5. Data Retention</h2>
      <p>
        We retain your account data for as long as your account is active. Practice results and mastery
        data are retained indefinitely to power your personalised dashboard. You may request deletion at
        any time by emailing <a href="mailto:nyxencloud@gmail.com">nyxencloud@gmail.com</a>.
      </p>

      <h2>6. Your Rights</h2>
      <p>You have the right to:</p>
      <ul>
        <li>Access the personal data we hold about you.</li>
        <li>Request correction of inaccurate data.</li>
        <li>Request deletion of your account and associated data.</li>
        <li>Object to processing for marketing purposes.</li>
      </ul>
      <p>To exercise these rights, contact us at <a href="mailto:nyxencloud@gmail.com">nyxencloud@gmail.com</a>.</p>

      <h2>7. Security</h2>
      <p>
        We use industry-standard security measures including HTTPS encryption, secure credential storage
        via Clerk, and HMAC-SHA256 signature verification for all Razorpay payments.
      </p>

      <h2>8. Children&apos;s Privacy</h2>
      <p>
        OlympiadReady is designed for school students. Users under 13 must use the platform under
        parental supervision. We do not knowingly collect data from children under 13 without parental
        consent.
      </p>

      <h2>9. Changes to This Policy</h2>
      <p>
        We may update this policy from time to time. Material changes will be communicated via email or
        an in-app notice. Continued use of OlympiadReady after changes constitutes acceptance.
      </p>

      <h2>10. Contact</h2>
      <p>
        Questions? Contact us at <a href="mailto:nyxencloud@gmail.com">nyxencloud@gmail.com</a> or
        WhatsApp <a href="https://wa.me/919953699143">+91 99536 99143</a>.
      </p>
    </LegalPageLayout>
  );
}
