import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    // This folder is the app root (silences the "package-lock.json outside the repo" warning)
    root: __dirname,
    // Turns on Tailwind. Without this rule the app renders with no styles.
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
