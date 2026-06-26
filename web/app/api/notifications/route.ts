import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

export async function GET(req: NextRequest) {
  const auth = req.headers.get("Authorization");
  if (!auth) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  try {
    const res = await fetch(`${API_URL}/api/notifications`, {
      headers: { Authorization: auth },
    });

    const contentType = res.headers.get("content-type") ?? "";
    if (!contentType.includes("application/json")) {
      // Backend returned plain text (e.g. startup exception) — return empty list rather than crashing
      return NextResponse.json([], { status: 200 });
    }

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json([], { status: 200 });
  }
}
