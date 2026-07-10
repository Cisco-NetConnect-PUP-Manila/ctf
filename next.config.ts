import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    unoptimized: false,
  },
  transpilePackages: ["three"],
};

export default nextConfig;
