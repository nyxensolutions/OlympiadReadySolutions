"use client";

import { useEffect, useRef } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth, useClerk, SignedIn, SignedOut } from "@clerk/nextjs";
import { Loader2 } from "lucide-react";

/**
 * Wrap any internal/protected page with <AuthGate> to require sign-in.
 *
 * Behaviour:
 *  - While Clerk is still loading, shows a lightweight spinner.
 *  - If the visitor is signed out, the page content is NOT rendered.
 *    Instead we immediately open Clerk's sign-in / sign-up popup.
 *  - If the visitor dismisses (cancels) the popup while still signed out,
 *    they are redirected to the landing page ("/").
 *  - Once signed in, the protected children render normally.
 */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const { isLoaded, isSignedIn } = useAuth();
  const { openSignIn } = useClerk();
  const router = useRouter();
  const pathname = usePathname();
  const opened = useRef(false);

  useEffect(() => {
    if (!isLoaded || isSignedIn) {
      opened.current = false;
      return;
    }

    // Signed out: open the Clerk modal once and keep visitor off the page.
    opened.current = true;
    const redirectUrl = pathname || "/";
    openSignIn({
      fallbackRedirectUrl: redirectUrl,
      signUpFallbackRedirectUrl: "/welcome",
    });

    // Detect cancellation: Clerk portals its modal into the DOM. When the
    // modal element disappears and the visitor is still signed out, we treat
    // that as a cancel and send them back to the landing page.
    let settled = false;
    const interval = window.setInterval(() => {
      if (!opened.current) return;
      const modalOpen = document.querySelector(
        ".cl-modalBackdrop, .cl-modal, [class*='cl-modal']"
      );
      if (!modalOpen && !settled) {
        // Give Clerk a tick to flip auth state after a successful sign-in.
        settled = true;
        window.setTimeout(() => {
          if (!isSignedIn) router.push("/");
        }, 400);
      }
    }, 300);

    return () => window.clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded, isSignedIn, pathname]);

  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut>
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-center">
          <Loader2 className="h-6 w-6 animate-spin text-brand-500" />
          <p className="text-sm text-slate-500">
            Please sign in to continue…
          </p>
        </div>
      </SignedOut>
    </>
  );
}
