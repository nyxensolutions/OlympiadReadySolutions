import { LegalPageLayout } from "@/components/LegalPageLayout";

export const metadata = {
  title: "Refund Policy · OlympiadReady",
  description: "OlympiadReady refund and cancellation policy for Pro subscriptions and PDF purchases.",
};

export default function RefundPage() {
  return (
    <LegalPageLayout title="Refund Policy" lastUpdated="19 May 2026">
      <p>
        This Refund Policy describes the conditions under which OlympiadReady (operated by Nyxen
        Solutions) offers refunds for paid purchases made through our platform.
      </p>

      <h2>1. Pro Subscription Refunds</h2>
      <p>
        We offer a <strong>7-day refund window</strong> for Pro subscription purchases. To qualify:
      </p>
      <ul>
        <li>The refund request must be made within 7 days of the original payment date.</li>
        <li>
          You must not have generated more than <strong>5 AI practice papers</strong> during the
          subscription period (indicating meaningful use of the Pro features).
        </li>
        <li>
          Refund requests must be submitted via email to{" "}
          <a href="mailto:nyxencloud@gmail.com">nyxencloud@gmail.com</a> with your registered email
          address and the Razorpay Order ID.
        </li>
      </ul>
      <p>
        Approved refunds will be processed within <strong>5–10 business days</strong> to the original
        payment method via Razorpay.
      </p>

      <h2>2. PDF Download Refunds</h2>
      <p>
        PDF practice paper purchases (₹29 per download, or less with bundle discounts) are <strong>generally non-refundable</strong>
        once the PDF has been successfully generated and delivered, as the digital content is
        immediately accessible.
      </p>
      <p>
        However, we will provide a full refund in the following exceptional circumstances:
      </p>
      <ul>
        <li>The PDF was not delivered due to a technical error on our end.</li>
        <li>The payment was processed but the PDF generation failed.</li>
        <li>A duplicate payment was charged for the same PDF.</li>
      </ul>

      <h2>3. Free Plan</h2>
      <p>
        The Free plan does not involve any payment and is therefore not subject to this Refund Policy.
      </p>

      <h2>4. How to Request a Refund</h2>
      <p>To request a refund, please email us at <a href="mailto:nyxencloud@gmail.com">nyxencloud@gmail.com</a> with:</p>
      <ul>
        <li>Subject line: <strong>Refund Request — OlympiadReady</strong></li>
        <li>Your registered email address.</li>
        <li>The Razorpay Order ID (visible in your purchases panel or email receipt).</li>
        <li>A brief description of the reason for the refund request.</li>
      </ul>
      <p>
        Our team will respond within 2 business days. You can also reach us on WhatsApp at{" "}
        <a href="https://wa.me/919953699143">+91 99536 99143</a> (Mon–Sat, 9 am–6 pm IST).
      </p>

      <h2>5. Chargebacks</h2>
      <p>
        We encourage you to contact us before initiating a chargeback with your bank. Filing a
        chargeback without first contacting us may result in account suspension while the dispute is
        investigated.
      </p>

      <h2>6. Changes to This Policy</h2>
      <p>
        We reserve the right to update this Refund Policy. Changes will be posted on this page with an
        updated date.
      </p>

      <h2>7. Contact</h2>
      <p>
        For refund-related queries, email{" "}
        <a href="mailto:nyxencloud@gmail.com">nyxencloud@gmail.com</a> or WhatsApp{" "}
        <a href="https://wa.me/919953699143">+91 99536 99143</a>.
      </p>
    </LegalPageLayout>
  );
}
