/** @type {import('next').NextConfig} */
const backendUrl = (
  process.env.BACKEND_INTERNAL_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  ""
).replace(/\/$/, "");

const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  async rewrites() {
    if (!backendUrl) return [];

    return {
      beforeFiles: [
        {
          source: "/api/backend/:path*",
          destination: `${backendUrl}/:path*`,
        },
      ],
    };
  },
};

module.exports = nextConfig;
