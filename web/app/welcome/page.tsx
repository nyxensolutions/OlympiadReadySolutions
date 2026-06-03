"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function WelcomePage() {
  const router = useRouter();

  useEffect(() => {
    // Fire Google Ads conversion event
    if (typeof window !== "undefined" && typeof (window as any).gtag === "function") {
      (window as any).gtag('event', 'conversion', {
        'send_to': 'AW-18206317015/sUnNCNPqjbgcENezuelD'
      });
    }

    // Redirect to the main practice dashboard after firing
    const timeout = setTimeout(() => {
      router.push("/");
    }, 700);

    return () => clearTimeout(timeout);
  }, [router]);

  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center gap-5 text-center bg-slate-50 px-4">
      <Loader2 className="h-10 w-10 animate-spin text-brand-500" />
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Welcome to OlympiadReady!</h1>
        <p className="mt-2 text-slate-500">Preparing your personalized dashboard...</p>
      </div>
    </div>
  );
}
