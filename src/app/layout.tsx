import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Packet Capture: Beneath the Network",
  description:
    "A narrative networking and security CTF where incident responders trace anomalies, preserve evidence, and uncover what lives beneath the network.",
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
