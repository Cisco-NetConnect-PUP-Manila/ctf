import type { Metadata } from "next";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL
  ?? (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "http://localhost:3000");

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Capture The Flag",
    template: "%s | Capture The Flag",
  },
  applicationName: "Capture The Flag",
  description:
    "A narrative networking and security CTF where incident responders trace anomalies, preserve evidence, and uncover what lives beneath the network.",
  icons: {
    icon: [
      {
        url: "/assets/ctf.png",
        type: "image/png",
      },
    ],
    apple: [
      {
        url: "/assets/ctf.png",
        type: "image/png",
      },
    ],
  },
  openGraph: {
    title: "Capture The Flag",
    description:
      "A narrative networking and security CTF where incident responders trace anomalies, preserve evidence, and uncover what lives beneath the network.",
    images: ["/assets/ctf.png"],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Capture The Flag",
    description:
      "A narrative networking and security CTF where incident responders trace anomalies, preserve evidence, and uncover what lives beneath the network.",
    images: ["/assets/ctf.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
