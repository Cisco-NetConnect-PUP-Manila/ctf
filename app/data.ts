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

export const acts: Act[] = [
  {
    id: "act-1",
    num: "ACT I",
    track: "OSINT",
    title: "The Signal",
    desc: "Anonymous profiles, forgotten repositories, archived domains, and leaked traces point toward an organization operating in the shadows.",
    cases: 8,
    points: "800",
    status: "Live",
    unlock: "500 pts unlocks Act II",
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
    track: "Web Penetration",
    title: "The Breach",
    desc: "The trail leads to abandoned web applications, hidden portals, confidential documents, source code, and tokens that should not still exist.",
    cases: 8,
    points: "1,125",
    status: "Live",
    unlock: "700 pts unlocks Act III",
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
    desc: "Hard drives, memory dumps, packet captures, deleted files, and system logs begin contradicting the timeline of the incident.",
    cases: 8,
    points: "1,125",
    status: "Live",
    unlock: "700 pts unlocks Act IV",
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
    track: "Cisco Packet Tracer",
    title: "Beneath the Network",
    desc: "Connectivity must be restored, routing paths rebuilt, vulnerable devices secured, and hidden infrastructure recovered from the network itself.",
    cases: 5,
    points: "1,000",
    status: "Live",
    unlock: "700 pts + preserved fragments unlock the final layer",
    caseNames: [
      "Broken Topology",
      "VLAN Maze",
      "Routing Blackout",
      "Compromised Edge",
      "Final Backbone",
    ],
  },
];

export const rules = [
  {
    title: "Work Inside Scope",
    body: "Investigate only the systems, files, and infrastructure provided for the operation.",
  },
  {
    title: "Preserve Every Key",
    body: "Recovered keys and artifacts may matter later. Do not discard evidence just because it looks small.",
  },
  {
    title: "Unlock in Sequence",
    body: "Each act opens through its point threshold. The final layer requires Act IV progress and preserved fragments.",
  },
  {
    title: "Keep the Case Clean",
    body: "No flag sharing, team sabotage, or attacks against infrastructure outside the assigned environment.",
  },
];

export const timeline = [
  {
    date: "JUL 15",
    title: "Registration Opens",
    body: "Assemble your response team and reserve a slot before the operation begins.",
  },
  {
    date: "AUG 01",
    title: "Briefing Window",
    body: "Teams receive scope, rules of engagement, and the first incident brief.",
  },
  {
    date: "AUG 15",
    title: "Act I Opens",
    body: "The Signal goes live and the first public traces enter the case file.",
  },
  {
    date: "SEP 01",
    title: "Live Operation",
    body: "The Breach, The Echo, and the network restoration phases escalate the investigation.",
  },
  {
    date: "SEP 02",
    title: "Final Transmission",
    body: "Qualifying teams face the last layer after preserving the evidence they recovered.",
  },
];

export const sponsors = [
  "CyberGuard",
  "NetCore",
  "CloudSec",
  "CorpShield",
  "HackCom",
  "FlagPrize",
  "AllyNet",
];

export const marqueeItems = [
  "[01] ACT I / THE SIGNAL",
  "[02] ACT II / THE BREACH",
  "[03] ACT III / THE ECHO",
  "[04] ACT IV / BENEATH",
  "[05] PRESERVE / EVERY KEY",
  "[06] RECOVER / EVIDENCE",
  "[07] FINAL / TRANSMISSION",
];
