export const siteUrl = "https://packetcapture.xyz";
export const siteName = "Packet Capture";
export const siteTitle = "Packet Capture | Beneath the Network CTF";
export const siteDescription =
  "Packet Capture is a story-driven cybersecurity CTF where teams investigate a connected incident through OSINT, web security, digital forensics, and networking challenges.";
export const socialImage = `${siteUrl}/images/packet-capture-social.webp`;

export const homeStructuredData = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": `${siteUrl}/#website`,
      url: siteUrl,
      name: siteName,
      alternateName: "Packet Capture: Beneath the Network",
      description: siteDescription,
      inLanguage: "en-PH",
    },
    {
      "@type": "WebPage",
      "@id": `${siteUrl}/#webpage`,
      url: siteUrl,
      name: siteTitle,
      description: siteDescription,
      isPartOf: { "@id": `${siteUrl}/#website` },
      about: {
        "@type": "Thing",
        name: "Cybersecurity Capture-the-Flag competition",
      },
      inLanguage: "en-PH",
    },
  ],
};

export function stringifyJsonLd(value: unknown) {
  return JSON.stringify(value).replace(/</g, "\\u003c");
}
