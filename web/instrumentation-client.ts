import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  // Capture 10% of transactions for performance monitoring.
  // Increase to 1.0 temporarily when investigating a specific issue.
  tracesSampleRate: 0.1,

  // GlitchTip does not support session replay — keep both at 0.
  replaysSessionSampleRate: 0,
  replaysOnErrorSampleRate: 0,

  environment: process.env.NODE_ENV,
  debug: process.env.NODE_ENV === "development",
});

// Instrument client-side navigation transitions
export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
