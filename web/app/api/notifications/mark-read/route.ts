import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5080";

export async function POST(req: NextRequest) {
  const auth = req.headers.get("Authorization");
  if (!auth) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const res = await fetch(`${API_URL}/api/notifications/mark-read`, {
    method: "POST",
    headers: { Authorization: auth },
  });

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
