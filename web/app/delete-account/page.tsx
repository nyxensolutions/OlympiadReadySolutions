import { LegalPageLayout } from "@/components/LegalPageLayout";

export const metadata = {
  title: { absolute: "Delete Your Account · OlympiadReady" },
  description:
    "How to request deletion of your OlympiadReady account and data, what is deleted, and what is retained.",
};

export default function DeleteAccountPage() {
  return (
    <LegalPageLayout title="Delete Your Account" lastUpdated="13 October 2026">
      <p>
        This page explains how to delete your account for <strong>Olympiad Ready</strong> (the OlympiadReady
        website and the Olympiad Ready app on Google Play and the App Store), operated by{" "}
        <strong>NyxenCloud Solutions Private Limited</strong>.
      </p>

      <h2>How to request deletion</h2>
      <ol>
        <li>
          Send an email to{" "}
          <a href="mailto:support@olympiadready.com?subject=Delete%20my%20account">support@olympiadready.com</a>{" "}
          from the email address you use to sign in.
        </li>
        <li>
          Use the subject <strong>&quot;Delete my account&quot;</strong>. If you signed in with Google, mention that
          too.
        </li>
        <li>
          We will confirm your request and delete your account within <strong>30 days</strong>. You will receive
          an email when the deletion is complete.
        </li>
      </ol>
      <p>
        A parent or guardian can request deletion of a child&apos;s account in the same way, from the email
        address registered on that account.
      </p>

      <h2>What we delete</h2>
      <ul>
        <li>Your account and sign-in details (name, email address, profile information).</li>
        <li>Your class, subject preferences and onboarding answers.</li>
        <li>Practice papers, test answers, results, scores, topic mastery and badges.</li>
        <li>Your AI Tutor conversations.</li>
        <li>Notification settings and the device token used to send you notifications.</li>
      </ul>

      <h2>What we keep, and for how long</h2>
      <ul>
        <li>
          <strong>Payment records</strong> (order ID, payment ID, amount, plan and date) are kept for up to{" "}
          <strong>8 years</strong>, as required by Indian tax and accounting laws. Your card and bank details are
          never stored by us; they are handled by Razorpay.
        </li>
        <li>
          Backups are overwritten in the normal course of operation and are fully cleared within{" "}
          <strong>90 days</strong> of deletion.
        </li>
      </ul>

      <h2 id="delete-data">Deleting only some of your data</h2>
      <p>
        If you want to keep your account but remove specific data, such as your test history or AI Tutor
        conversations, email{" "}
        <a href="mailto:support@olympiadready.com">support@olympiadready.com</a> and tell us what you would like
        removed.
      </p>

      <p>
        For more about how we handle your data, see our <a href="/privacy">Privacy Policy</a>.
      </p>
    </LegalPageLayout>
  );
}
