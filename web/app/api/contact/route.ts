import { NextRequest, NextResponse } from "next/server";

const BREVO_API_KEY = process.env.BREVO_API_KEY ?? "";
const TO_EMAIL      = "nyxencloud@gmail.com";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, email, message, type, schoolName, city, studentCount } = body;

    if (!name || !email || !message) {
      return NextResponse.json({ error: "Name, email and message are required." }, { status: 400 });
    }

    const isSchool  = type === "school";
    const subject   = isSchool
      ? `School Inquiry from ${schoolName || name} — OlympiadReady`
      : `Contact Form — ${name} — OlympiadReady`;

    const schoolDetails = isSchool
      ? `<tr><td style="padding:4px 0;color:#64748b;font-size:13px;">School Name</td><td style="padding:4px 0 4px 16px;font-size:13px;font-weight:600;">${schoolName || "—"}</td></tr>
         <tr><td style="padding:4px 0;color:#64748b;font-size:13px;">City</td><td style="padding:4px 0 4px 16px;font-size:13px;font-weight:600;">${city || "—"}</td></tr>
         <tr><td style="padding:4px 0;color:#64748b;font-size:13px;">Est. Students</td><td style="padding:4px 0 4px 16px;font-size:13px;font-weight:600;">${studentCount || "—"}</td></tr>`
      : "";

    const htmlContent = `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
        <div style="background:#2563eb;padding:20px 24px;">
          <h2 style="color:#fff;margin:0;font-size:18px;">${isSchool ? "🏫 School / Institution Inquiry" : "📬 Contact Form Submission"}</h2>
          <p style="color:#bfdbfe;margin:4px 0 0;font-size:13px;">OlympiadReady</p>
        </div>
        <div style="padding:24px;">
          <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:4px 0;color:#64748b;font-size:13px;">Name</td><td style="padding:4px 0 4px 16px;font-size:13px;font-weight:600;">${name}</td></tr>
            <tr><td style="padding:4px 0;color:#64748b;font-size:13px;">Email</td><td style="padding:4px 0 4px 16px;font-size:13px;"><a href="mailto:${email}" style="color:#2563eb;">${email}</a></td></tr>
            ${schoolDetails}
          </table>
          <div style="margin-top:16px;padding:16px;background:#f8fafc;border-radius:8px;border-left:3px solid #2563eb;">
            <p style="margin:0;font-size:13px;color:#374151;white-space:pre-wrap;">${message}</p>
          </div>
        </div>
        <div style="padding:12px 24px;background:#f8fafc;border-top:1px solid #e2e8f0;">
          <p style="margin:0;font-size:11px;color:#94a3b8;">Sent via OlympiadReady contact form · Reply directly to ${email}</p>
        </div>
      </div>`;

    const res = await fetch("https://api.brevo.com/v3/smtp/email", {
      method: "POST",
      headers: {
        "api-key":     BREVO_API_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sender:      { name: "OlympiadReady Contact", email: "nyxencloud@gmail.com" },
        to:          [{ email: TO_EMAIL, name: "OlympiadReady" }],
        replyTo:     { email, name },
        subject,
        htmlContent,
      }),
    });

    if (!res.ok) {
      const err = await res.text();
      console.error("Brevo error:", err);
      return NextResponse.json({ error: "Failed to send message. Please email us directly." }, { status: 502 });
    }

    return NextResponse.json({ success: true });
  } catch (e) {
    console.error("Contact route error:", e);
    return NextResponse.json({ error: "Server error." }, { status: 500 });
  }
}
