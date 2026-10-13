import { LegalPageLayout } from "@/components/LegalPageLayout";

export const metadata = {
  title: { absolute: "Privacy Policy · OlympiadReady" },
  description: "How OlympiadReady collects, uses, and protects your personal information.",
};

export default function PrivacyPage() {
  return (
    <LegalPageLayout title="Privacy Policy" lastUpdated="13 October 2026">
      <h2>1. Who We Are</h2>
      <p>
        OlympiadReady (the website at olympiadready.com and the Olympiad Ready mobile app) is operated by{" "}
        <strong>NyxenCloud Solutions Private Limited</strong>, a company registered in India. We provide an
        AI-powered Olympiad preparation platform for school students. You can contact us at{" "}
        <a href="mailto:support@olympiadready.com">support@olympiadready.com</a>.
      </p>

      <h2>2. What Information We Collect</h2>
      <h3>Information you provide</h3>
      <ul>
        <li>
          <strong>Account data:</strong> Your name, email address and password, or your name, email address and
          profile photo if you sign in with Google. Sign-in is handled by Clerk.
        </li>
        <li>
          <strong>Study preferences:</strong> Your class/grade and the subjects you choose.
        </li>
        <li>
          <strong>Payment data:</strong> When you buy a plan, payments are processed by Razorpay. Razorpay
          collects your payment details (card, UPI or net banking) and may ask for your phone number at checkout.
          We receive only the order ID, payment ID, amount and plan. We do <em>not</em> store your card numbers or
          bank details.
        </li>
        <li>
          <strong>AI Tutor questions:</strong> When you ask the AI Tutor a question, your question and the
          current conversation are sent to our AI provider (OpenAI) to generate a reply. We do not store your AI
          Tutor conversations on our servers; we only count how many chats you have used.
        </li>
      </ul>
      <h3>Information collected automatically</h3>
      <ul>
        <li>
          <strong>Usage data:</strong> Practice papers you generate, your answers, test results, scores, topic
          mastery and badges.
        </li>
        <li>
          <strong>Device data (mobile app):</strong> A push notification token, so we can send you reminders and
          updates. You can turn notifications off in the app or in your phone settings.
        </li>
        <li>
          <strong>Log data (website):</strong> Browser type, IP address and pages visited, used for security and
          for privacy-friendly visit statistics (Umami, which does not use tracking cookies).
        </li>
        <li>
          <strong>Cookies (website):</strong> Sign-in and session cookies. See our{" "}
          <a href="/cookies">Cookie Policy</a>.
        </li>
      </ul>
      <p>
        The mobile app does not use advertising, ad identifiers, location, contacts or third-party analytics.
      </p>

      <h2>3. How We Use Your Information</h2>
      <ul>
        <li>To provide and improve the OlympiadReady service.</li>
        <li>To personalise your practice and track your topic mastery.</li>
        <li>To process payments and give access to paid plans and PDF downloads.</li>
        <li>To answer your AI Tutor questions.</li>
        <li>To send service messages and reminders by email and push notification.</li>
        <li>To keep the service secure and comply with legal obligations.</li>
      </ul>

      <h2>4. Who We Share Data With</h2>
      <p>
        We do <strong>not</strong> sell your personal data and we do not show ads. We use these service providers,
        who process data only to provide their service to us:
      </p>
      <ul>
        <li><strong>Clerk</strong>: sign-in and account management.</li>
        <li><strong>Razorpay</strong>: payment processing, under Razorpay&apos;s own Privacy Policy.</li>
        <li>
          <strong>OpenAI</strong>: generating practice questions (only the subject, class, topic and difficulty
          are sent) and answering AI Tutor questions (the text of your questions is sent; your name and email are
          not).
        </li>
        <li><strong>Microsoft Azure</strong>: hosting of our servers and database.</li>
        <li><strong>Brevo</strong>: sending service emails.</li>
        <li><strong>Expo and Google Firebase Cloud Messaging</strong>: delivering push notifications.</li>
        <li><strong>Umami</strong>: privacy-friendly website visit statistics.</li>
        <li><strong>Law enforcement</strong>: only when required by applicable Indian law.</li>
      </ul>

      <h2>5. Data Retention</h2>
      <p>
        We keep your account data for as long as your account is active. Practice results and mastery data are
        kept to power your dashboard until you delete your account. Payment records are kept for up to 8 years
        as required by Indian tax and accounting laws.
      </p>

      <h2>6. Deleting Your Account and Data</h2>
      <p>
        You can ask us to delete your account and data, or only some of your data, at any time. See{" "}
        <a href="/delete-account">Delete Your Account</a> for the steps, what is deleted and what is kept.
      </p>

      <h2>7. Your Rights</h2>
      <p>You have the right to:</p>
      <ul>
        <li>Access the personal data we hold about you.</li>
        <li>Request correction of inaccurate data.</li>
        <li>Request deletion of your account and associated data.</li>
        <li>Withdraw consent and object to processing for marketing purposes.</li>
      </ul>
      <p>
        To exercise these rights, contact us at{" "}
        <a href="mailto:support@olympiadready.com">support@olympiadready.com</a>.
      </p>

      <h2>8. Security</h2>
      <p>
        We use industry-standard security measures, including HTTPS encryption for all data in transit, secure
        credential storage through Clerk, and signature verification for all Razorpay payments.
      </p>

      <h2>9. Children&apos;s Privacy</h2>
      <p>
        OlympiadReady is designed for school students from Class 1 to 12, including children under 13. A parent
        or guardian should create the account for a child, or supervise and consent to their use of the service.
        We collect only the information needed to run the service, as described above. We do not show ads, do not
        use advertising identifiers, and do not sell or share children&apos;s data for advertising. A parent or
        guardian can review or delete their child&apos;s data at any time by contacting{" "}
        <a href="mailto:support@olympiadready.com">support@olympiadready.com</a>.
      </p>

      <h2>10. Changes to This Policy</h2>
      <p>
        We may update this policy from time to time. Material changes will be communicated by email or an in-app
        notice. Continued use of OlympiadReady after changes means you accept the updated policy.
      </p>

      <h2>11. Contact</h2>
      <p>
        Questions? Contact NyxenCloud Solutions Private Limited at{" "}
        <a href="mailto:support@olympiadready.com">support@olympiadready.com</a>.
      </p>
    </LegalPageLayout>
  );
}
