export type Act = {
  id: string;
  num: string;
  track: string;
  title: string;
  desc: string;
  cases: number;
  points: string;
  status: string;
  unlock: string;
  caseNames: string[];
};

export type RuleSection = {
  title: string;
  body: string;
};

export type FaqItem = {
  q: string;
  a: string;
};

export type Sponsor = {
  name: string;
  tier: string;
  link?: string;
};

export type SponsorLogo = {
  src: string;
  name: string;
};

export type SponsorGroup = {
  id: string;
  title: string;
  code: string;
  logos: SponsorLogo[];
};

export type RecommendedTool = {
  name: string;
  href: string;
};

export type PortalModule = {
  title: string;
  body: string;
  details: string[];
  status: string;
};

export const competition = {
  name: "Packet Capture: Beneath the Network",
  phrase: "Race Smart. Score Higher.",
  status: "Participant access only",
  format: "PacketCapture{FLAG_NAME}",
  contact: "learncyberph@gmail.com",
  description:
    "A story-driven Capture-the-Flag competition for solo participants and teams, bridging networking fundamentals and cybersecurity through immersive, hands-on technical challenges.",
  hero:
    "Participants become a Cyber Incident Response Team tracing anomalies across a seemingly ordinary network. Every solved challenge uncovers another fragment of the larger investigation beneath the network.",
  about:
    "Packet Capture places participants inside an evolving cyber incident instead of a disconnected list of challenges. Solo participants and teams move from intelligence gathering and attack-vector discovery to digital evidence recovery and network restoration.",
  story:
    "Organizations connected to the same digital infrastructure begin reporting identical anomalies: account lockouts, altered internal websites, missing files, and unexplained traffic. There is no ransom demand, only a transmission from somewhere below the surface.",
};

export const acts: Act[] = [
  {
    id: "act-1",
    num: "ACT I",
    track: "Open-Source Intelligence",
    title: "The Signal",
    desc: "Participants investigate public traces, forgotten repositories, archived sites, metadata, leaked documents, and scattered digital identities.",
    cases: 8,
    points: "800",
    status: "Sequential",
    unlock: "Reach the required Investigation Score to unlock Act II.",
    caseNames: [
      "Hidden Profile",
      "Forgotten Repository",
      "Metadata Never Lies",
      "Ghost Domain",
      "Digital Footprints",
      "Mirror Identity",
      "Silent Observer",
      "The Last Breadcrumb",
    ],
  },
  {
    id: "act-2",
    num: "ACT II",
    track: "Web Penetration Testing",
    title: "The Breach",
    desc: "The trail leads to abandoned web applications, hidden portals, confidential documents, source code, authentication tokens, and encrypted archives.",
    cases: 8,
    points: "1,125",
    status: "Locked by score",
    unlock: "Reach the required Investigation Score to unlock Act III.",
    caseNames: [
      "Login Failure",
      "Employee Records",
      "Hidden Admin",
      "Poisoned Search",
      "Echo Chamber",
      "Backdoor Upload",
      "Session Drift",
      "Final Console",
    ],
  },
  {
    id: "act-3",
    num: "ACT III",
    track: "Digital Forensics",
    title: "The Echo",
    desc: "Hard drives, memory dumps, packet captures, deleted files, and system logs begin contradicting the official timeline of the incident.",
    cases: 8,
    points: "1,125",
    status: "Locked by score",
    unlock: "Reach the required Investigation Score to unlock Act IV.",
    caseNames: [
      "Deleted Doesn't Mean Gone",
      "Hidden Within",
      "USB Secrets",
      "Memory Echoes",
      "Timeline Reconstruction",
      "Registry Secrets",
      "Last Packet",
      "Buried Evidence",
    ],
  },
  {
    id: "act-4",
    num: "ACT IV",
    track: "Cisco Packet Tracer and Networking",
    title: "Beneath the Network",
    desc: "Teams restore connectivity, rebuild routing paths, secure devices, remove malicious configurations, and recover hidden network evidence.",
    cases: 5,
    points: "1,000",
    status: "Locked by score",
    unlock: "Complete progression requirements to unlock the Final Investigation.",
    caseNames: [
      "Broken Topology",
      "VLAN Maze",
      "Routing Blackout",
      "Compromised Edge",
      "Final Backbone",
    ],
  },
];

export const rankingCriteria = [
  "Highest total Investigation Score",
  "Fastest overall completion time",
  "Lowest accumulated Intel Request penalties",
  "Earliest successful Final Investigation submission, when applicable",
];

export const mechanics = [
  {
    title: "Investigation Score",
    body: "Every challenge has a predefined score based on difficulty. Rankings are primarily score-based, so solving accurately matters more than simply rushing.",
  },
  {
    title: "Progression",
    body: "Teams do not need to solve every challenge inside an Act. The next Act unlocks after the required minimum Investigation Score is reached.",
  },
  {
    title: "Intel Requests",
    body: "Selected Medium, Hard, and Expert challenges may include hints. Requesting Intel deducts points, making hints a strategic decision.",
  },
  {
    title: "Final Investigation",
    body: "The final stage is not a normal challenge list. Qualified teams reconstruct the complete investigation using recovered fragments, keys, files, evidence, and artifacts.",
  },
];

export const rules: RuleSection[] = [
  {
    title: "General Rules",
    body: "Participants may compete solo or as a team and must demonstrate professionalism, ethical conduct, and compliance with organizer decisions throughout the event.",
  },
  {
    title: "Competition Format",
    body: "The competition is divided into four sequential Acts: The Signal, The Breach, The Echo, and Beneath the Network.",
  },
  {
    title: "Scoring System",
    body: "Each challenge awards Investigation Score based on difficulty. The objective is to accumulate the highest possible score across all Acts.",
  },
  {
    title: "Progression System",
    body: "Entries unlock the next Act by reaching the required minimum Investigation Score. Previously unlocked challenges remain available until the competition ends.",
  },
  {
    title: "Flag Submission",
    body: "Flags are case-sensitive and must follow the official PacketCapture format exactly. Incorrect submissions award no points.",
  },
  {
    title: "Intel Requests",
    body: "Optional hints may deduct points from the entry's Investigation Score. Participants should weigh each request carefully.",
  },
  {
    title: "Allowed Resources",
    body: "AI tools, search engines, official documentation, technical articles, educational resources, personal notes, and approved software may be used ethically within scope.",
  },
  {
    title: "Prohibited Actions",
    body: "No flag sharing, account access against other teams, platform exploitation outside intended challenges, denial-of-service attacks, out-of-scope attacks, automated flag submission, outside assistance, cheating, plagiarism, or unsportsmanlike conduct.",
  },
  {
    title: "Violations",
    body: "Violations may result in warnings, point deductions, challenge invalidation, or immediate disqualification.",
  },
  {
    title: "Final Investigation",
    body: "Completing the four Acts may unlock one final terminal-style reconstruction challenge for qualified entries, based on the evidence collected throughout the event.",
  },
];

export const allowedResources = [
  "Artificial Intelligence tools",
  "Search engines",
  "Official documentation",
  "Technical articles",
  "Educational resources",
  "Personal notes",
  "Approved software and analysis tools",
];

export const aiExamples = [
  "ChatGPT",
  "Microsoft Copilot",
  "Google Gemini",
  "Claude",
  "Perplexity",
  "GitHub Copilot",
  "Similar technologies",
];

export const recommendedTools: RecommendedTool[] = [
  { name: "Cisco Packet Tracer", href: "https://www.netacad.com/courses/getting-started-cisco-packet-tracer/1000" },
  { name: "Wireshark", href: "https://www.wireshark.org/download.html" },
  { name: "Burp Suite Community Edition", href: "https://portswigger.net/burp/communitydownload" },
  { name: "Nmap", href: "https://nmap.org/download.html" },
  { name: "CyberChef", href: "https://gchq.github.io/CyberChef/" },
  { name: "Python", href: "https://www.python.org/downloads/" },
  { name: "Firefox (modern web browser)", href: "https://www.mozilla.org/en-US/firefox/new/" },
];

export const faqs: FaqItem[] = [
  {
    q: "Who can participate?",
    a: "The competition is open to students, professionals, and individuals interested in networking and cybersecurity.",
  },
  {
    q: "How are solo and team entries handled?",
    a: "Solo participants use their own approved participant record. Teams use one approved group record and follow the roster requirements specified by the organizers.",
  },
  {
    q: "Can we use Artificial Intelligence?",
    a: "Yes. AI tools such as ChatGPT, Microsoft Copilot, Google Gemini, Claude, Perplexity, GitHub Copilot, and similar technologies are allowed when used ethically and within scope.",
  },
  {
    q: "Can we use Google and online documentation?",
    a: "Yes. Public documentation, technical articles, official manuals, and educational resources are permitted.",
  },
  {
    q: "Can we skip challenges?",
    a: "Yes. Teams only need to earn the minimum Investigation Score required to unlock the next Act.",
  },
  {
    q: "Can we return to previous Acts?",
    a: "Yes. Previously unlocked challenges remain available until the competition concludes.",
  },
  {
    q: "What happens if we submit the wrong flag?",
    a: "Incorrect submissions do not award points.",
  },
  {
    q: "What happens if we use a hint?",
    a: "Using an Intel Request deducts points from your Investigation Score.",
  },
  {
    q: "Is the competition based on speed?",
    a: "Partially. Investigation Score is the primary ranking factor, while completion time and other criteria break ties.",
  },
  {
    q: "What software should we prepare?",
    a: "Prepare tools such as Cisco Packet Tracer, Wireshark, Burp Suite Community Edition, Nmap, CyberChef, Python, a modern browser, and other common cybersecurity utilities.",
  },
];

export const timeline = [
  {
    date: "OCT 03",
    title: "Registration Opens",
    body: "Teams can begin registering for the competition.",
  },
  {
    date: "OCT 10",
    title: "Registration Closes",
    body: "The registration period ends before the event begins.",
  },
  {
    date: "OCT 10",
    title: "Webinar",
    body: "Join the event webinar to prepare for the CTF.",
  },
  {
    date: "OCT 18",
    title: "CTF Starts",
    body: "The competition begins and teams take on the challenges.",
  },
  {
    date: "OCT 18",
    title: "CTF End / Awarding",
    body: "The event concludes with the awarding ceremony.",
  },
];

export const sponsors: Sponsor[] = [];

export const sponsorGroups: SponsorGroup[] = [
  {
    id: "challenge-partners",
    title: "Challenge Partners",
    code: "CHALLENGE.PARTNERS",
    logos: [
      {
        src: "/images/challenges/Copy of A1SBERG Logo 2025-2026 w_ Background.png",
        name: "A1SBERG",
      },
      { src: "/images/challenges/synx_logo.png", name: "SYNX" },
    ],
  },
  {
    id: "co-organizers",
    title: "Co-Organizers",
    code: "CO.ORGANIZERS",
    logos: [
      { src: "/images/co-organizer/CNCP Logo.png", name: "CNCP" },
      { src: "/images/co-organizer/Cyber PH logo.png", name: "CyberPH" },
      { src: "/images/co-organizer/ICPEP SE Logo.png", name: "ICpEP.SE" },
      { src: "/images/co-organizer/MQ CyberSec Club.webp", name: "MQ CyberSec Club" },
      { src: "/images/co-organizer/WORKFLOW PH - TRANSPARENT (1).png", name: "Workflow PH" },
    ],
  },
  {
    id: "partners",
    title: "Partners",
    code: "PARTNERS.NET",
    logos: [
      {
        src: "/images/partners/Amazon Web Services Student Builder Group - Spade.png",
        name: "AWS Student Builder Group - SPADE",
      },
      {
        src: "/images/partners/AWS Student Builder Group - Colegio de Muntinlupa .png",
        name: "AWS Student Builder Group - Colegio de Muntinlupa",
      },
      {
        src: "/images/partners/Information Security Organization (ISO) - DLSU.jpg",
        name: "Information Security Organization - DLSU",
      },
      {
        src: "/images/partners/PCU-Interactive Society of Computer Engineering Students.PNG",
        name: "PCU Interactive Society of Computer Engineering Students",
      },
    ],
  },
  {
    id: "sponsors",
    title: "Sponsors",
    code: "SPONSORS.DAT",
    logos: [
      { src: "/images/sponsors/appkademiya_logo.png", name: "Appkademiya" },
      { src: "/images/sponsors/HCDG-LOGO.png", name: "HCDG" },
      { src: "/images/sponsors/Prosple_Logo.png", name: "Prosple" },
      { src: "/images/sponsors/Tutorials-Dojo-Logo-Circle.png", name: "Tutorials Dojo" },
    ],
  },
];

export const competitionModules: PortalModule[] = [
  {
    title: "Dashboard",
    body: "The team's command center for score, rank, current Act, challenge progress, recent activity, announcements, and quick navigation.",
    status: "Snapshot live",
    details: [
      "Team name",
      "Current Investigation Score",
      "Current rank",
      "Current Act",
      "Challenges solved",
      "Progress overview",
      "Recent activity",
      "Latest announcements",
    ],
  },
  {
    title: "Storyline",
    body: "Narrative progression for the Prologue, four Acts, and locked Final Investigation.",
    status: "Frontend shell",
    details: [
      "Prologue",
      "Act I - The Signal",
      "Act II - The Breach",
      "Act III - The Echo",
      "Act IV - Beneath the Network",
      "Final Investigation",
    ],
  },
  {
    title: "Challenges",
    body: "Backend-driven published challenge directory organized by Act with team-specific access states.",
    status: "Directory live",
    details: [
      "Challenge title",
      "Category",
      "Difficulty",
      "Investigation Score",
      "Mission brief",
      "Story context",
      "Objectives",
      "Locked or unlocked state",
    ],
  },
  {
    title: "Progress",
    body: "A live view of unlock progress, remaining points, completed work, unfinished challenges, story fragments, and Intel penalties.",
    status: "Partially live",
    details: [
      "Current score",
      "Overall progress",
      "Current Act",
      "Completed challenges",
      "Remaining challenges",
      "Story fragments collected",
      "Hint penalties",
      "Unlock progress",
    ],
  },
  {
    title: "Investigation Board",
    body: "Digital evidence repository used throughout the competition and especially during the Final Investigation.",
    status: "Frontend shell",
    details: [
      "Story fragments",
      "Investigation keys",
      "Digital evidence",
      "Challenge completion history",
      "Recovered files",
      "Investigation notes",
    ],
  },
  {
    title: "Leaderboard",
    body: "Competition rankings using Investigation Score first, then time, Intel penalties, and Final Investigation timing.",
    status: "Backend required",
    details: [
      "Team rank",
      "Team name",
      "Investigation Score",
      "Challenges solved",
      "Current Act",
      "Completion time",
      "Hint penalties",
    ],
  },
  {
    title: "Announcements",
    body: "Official communication channel for event updates, schedule changes, challenge notices, and platform maintenance.",
    status: "Live feed",
    details: [
      "Event updates",
      "Schedule changes",
      "Challenge notifications",
      "Maintenance notices",
      "Important announcements",
    ],
  },
  {
    title: "Team Profile",
    body: "Team information and competition statistics for registered participants.",
    status: "Session live",
    details: [
      "Team name",
      "Team members",
      "Institution",
      "Registration details",
      "Competition statistics",
    ],
  },
  {
    title: "Settings",
    body: "Participant preferences and account controls once authentication exists.",
    status: "Backend required",
    details: [
      "Change password",
      "Notification preferences",
      "Theme selection",
      "Audio preferences",
    ],
  },
];

export const adminModules: PortalModule[] = [
  {
    title: "Admin Dashboard",
    body: "Organizer overview of competition health, participant activity, live standings, and platform status.",
    status: "Restricted",
    details: [
      "Total registered teams",
      "Active participants",
      "Live leaderboard",
      "Total challenge solves",
      "Recent activity",
      "Platform status",
    ],
  },
  {
    title: "Challenge Management",
    body: "Organizer tools for creating, editing, publishing, and configuring challenges.",
    status: "Live console",
    details: [
      "Create challenges",
      "Edit challenges",
      "Delete challenges",
      "Publish or unpublish challenges",
      "Configure flags",
      "Configure story fragments",
      "Configure point values",
    ],
  },
  {
    title: "Team Management",
    body: "Administrative control for participant accounts and competition eligibility.",
    status: "Approval live",
    details: [
      "View teams",
      "Edit team information",
      "Reset team password",
      "Reset team progress",
      "Apply penalties",
      "Disqualify teams",
    ],
  },
  {
    title: "Leaderboard Management",
    body: "Monitoring and controlled organizer overrides for ranking-related operations.",
    status: "Backend required",
    details: [
      "View live rankings",
      "Award bonus points",
      "Apply score deductions",
      "Override scores",
      "Freeze leaderboard",
    ],
  },
  {
    title: "Announcement Management",
    body: "Organizer publishing tools for participant-facing announcements.",
    status: "Live console",
    details: [
      "Create announcements",
      "Edit announcements",
      "Publish announcements",
      "Delete announcements",
    ],
  },
  {
    title: "Submission Logs",
    body: "Audit trail for authentication, submissions, Intel Request usage, unlock events, and score changes.",
    status: "Monitor live",
    details: [
      "Flag submission attempts",
      "Correct and incorrect attempts",
      "Rapid solve signals",
      "Shared metadata signals",
      "Challenge completion",
      "Unlock events",
      "Score changes",
    ],
  },
  {
    title: "Platform Settings",
    body: "Protected configuration area for competition-wide platform controls.",
    status: "Restricted",
    details: [
      "Event status",
      "Registration state",
      "Score rules",
      "Access controls",
      "System settings",
    ],
  },
];

export const marqueeItems = [
  "[01] ACT I / THE SIGNAL",
  "[02] ACT II / THE BREACH",
  "[03] ACT III / THE ECHO",
  "[04] ACT IV / BENEATH THE NETWORK",
  "[05] RACE SMART / SCORE HIGHER",
  "[06] INTEL REQUESTS / COST SCORE",
  "[07] FINAL INVESTIGATION / LOCKED",
];
