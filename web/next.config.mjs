import { withSentryConfig } from "@sentry/nextjs";

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
};

export default withSentryConfig(nextConfig, {
  // Suppress noisy build-time Sentry output
  silent: true,

  // GlitchTip does not have a source-map upload API — disable entirely
  // so builds never need SENTRY_AUTH_TOKEN
  sourcemaps: {
    disable: true,
  },

  // Use the new webpack config keys instead of deprecated shorthand flags
  webpack: {
    automaticVercelMonitors: false,
    treeshake: {
      removeDebugLogging: true,
    },
  },
});
