import { clerkMiddleware } from "@clerk/nextjs/server";

// Attach Clerk session to all non-static requests. Page-level gating happens
// inside components via <SignedIn>/<SignedOut>; the API itself enforces auth.
export default clerkMiddleware();

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)"
  ]
};
