import type { NextConfig } from "next";

// Default for local `npm run dev`. Docker Compose sets BACKEND_URL=http://backend:8000.
const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Hide the dev-only corner menu (route info, Turbopack, preferences).
  devIndicators: false,
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  async rewrites() {
    // Proxy all calls from the client to the FastAPI backend through `/api/*`.
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;

