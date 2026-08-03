from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import html


OUT_DIR = Path(__file__).resolve().parent
DOCX_PATH = OUT_DIR / "Packet-Capture-Developer-Handoff.docx"
GDOC_MD_PATH = OUT_DIR / "packet-capture-developer-handoff-google-docs.md"
FORM_MD_PATH = OUT_DIR / "packet-capture-dev-completion-form.md"


def esc(value: str) -> str:
    return html.escape(value, quote=False)


def run(text: str, bold: bool = False, size: int | None = None, color: str | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if size:
        props.append(f'<w:sz w:val="{size * 2}"/>')
        props.append(f'<w:szCs w:val="{size * 2}"/>')
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f"<w:r>{rpr}<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>"


def para(
    text: str = "",
    style: str | None = None,
    bold: bool = False,
    size: int | None = None,
    color: str | None = None,
    before: int | None = None,
    after: int | None = None,
    num_id: int | None = None,
    level: int = 0,
) -> str:
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if before is not None or after is not None:
        attrs = []
        if before is not None:
            attrs.append(f'w:before="{before}"')
        if after is not None:
            attrs.append(f'w:after="{after}"')
        ppr.append(f"<w:spacing {' '.join(attrs)} w:line=\"276\" w:lineRule=\"auto\"/>")
    if num_id is not None:
        ppr.append(
            f"<w:numPr><w:ilvl w:val=\"{level}\"/><w:numId w:val=\"{num_id}\"/></w:numPr>"
        )
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    return f"<w:p>{ppr_xml}{run(text, bold=bold, size=size, color=color)}</w:p>"


def h1(text: str) -> str:
    return para(text, style="Heading1", size=20, before=320, after=120)


def h2(text: str) -> str:
    return para(text, style="Heading2", size=16, before=280, after=120)


def h3(text: str) -> str:
    return para(text, style="Heading3", size=14, color="434343", before=220, after=80)


def bullet(text: str, level: int = 0) -> str:
    return para(text, num_id=1, level=level, after=80)


def number(text: str, level: int = 0) -> str:
    return para(text, num_id=2, level=level, after=80)


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def table(headers: list[str], rows: list[list[str]], widths: list[int]) -> str:
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    body = [
        '<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/>'
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="DADCE0"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="DADCE0"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="DADCE0"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="DADCE0"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="DADCE0"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="DADCE0"/>'
        '</w:tblBorders>'
        '<w:tblCellMar><w:top w:w="100" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="100" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar>'
        "</w:tblPr>",
        f"<w:tblGrid>{grid}</w:tblGrid>",
    ]

    def row(cells: list[str], header: bool = False) -> str:
        tcs = []
        for idx, cell in enumerate(cells):
            fill = '<w:shd w:fill="F8F9FA"/>' if header else ""
            cell_para = para(cell, bold=header, after=0)
            tcs.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{widths[idx]}" w:type="dxa"/>{fill}</w:tcPr>{cell_para}</w:tc>'
            )
        return f"<w:tr>{''.join(tcs)}</w:tr>"

    body.append(row(headers, header=True))
    body.extend(row(r) for r in rows)
    body.append("</w:tbl>")
    return "".join(body)


def document_xml() -> str:
    parts: list[str] = []
    parts.append(para("Packet Capture Developer Handoff", size=26, after=60))
    parts.append(
        para(
            "Google Docs-ready guide for the remaining work on Packet Capture: Beneath the Network",
            size=11,
            color="555555",
            after=160,
        )
    )
    parts.append(
        para(
            "Status: Frontend-only Next.js implementation. Public content is aligned with the CTF Guidelines and Storyline docs. Backend, auth, database, scoring, and admin operations are still missing.",
            bold=True,
            after=160,
        )
    )

    parts.append(h1("1. Current State"))
    for item in [
        "Framework: Next.js App Router",
        "Main public site route: /",
        "Competition platform shell: /platform",
        "Admin panel shell: /admin",
        "Shared public content source: app/data.ts",
        "Main styles and font rules: app/globals.css",
        "Public assets: public/fonts and public/images",
        "Implementation type: static frontend only, with no API, database, or authentication",
    ]:
        parts.append(bullet(item))

    parts.append(h1("2. What Already Exists"))
    for item in [
        "Public event intro, About, Overview, Four Acts, Rules, Scoring, FAQ, Timeline, Sponsors and Partners, and Footer sections",
        "Route-aware navigation for Main, Competition Platform, and Admin",
        "Frontend shell for participant modules",
        "Frontend shell for organizer/admin modules",
        "Centralized event content in app/data.ts",
        "Public-safe flag format display: PacketCapture{FLAG_NAME}",
    ]:
        parts.append(bullet(item))

    parts.append(h1("3. Critical Content Rule"))
    parts.append(
        para(
            "Do not expose real flags, final investigation answers, hidden keys, solution fragments, or final phrases in frontend code, static files, comments, public JSON, or generated HTML.",
            bold=True,
            after=120,
        )
    )
    parts.append(
        para(
            "Keep secret challenge material only in backend-controlled storage or organizer-only files outside the public frontend bundle."
        )
    )

    parts.append(h1("4. Gap Matrix"))
    parts.append(
        table(
            ["Area", "Current State", "Still Needed", "Priority"],
            [
                ["Backend/API", "None", "Auth, registration, challenge APIs, submissions, scoring, admin operations", "Critical"],
                ["Database", "None", "Users, teams, challenges, flags, submissions, solves, logs, settings", "Critical"],
                ["Auth", "None", "Participant/team/admin login, role access, sessions, password reset", "Critical"],
                ["Registration", "Opening soon copy only", "Registration form, team validation, approval flow, state controls", "High"],
                ["Platform", "Frontend shell", "Dashboard, challenges, progress, evidence board, leaderboard, announcements", "Critical"],
                ["Admin", "Frontend shell", "Challenge/team/leaderboard/announcement/submission/platform management", "Critical"],
                ["Scoring", "Static copy only", "Backend score engine, hint penalties, tie-breakers, audit trail", "Critical"],
                ["Timeline/contact", "TBA placeholders", "Organizer-confirmed dates and official channel", "High"],
                ["Sponsors", "Empty placeholder", "Sponsor names, tiers, logos, links", "Medium"],
                ["Testing", "Build only", "Unit, integration, E2E, role access, scoring tests", "High"],
            ],
            [1700, 2200, 4060, 1400],
        )
    )

    parts.append(h1("5. Backend and Database Requirements"))
    parts.append(h2("API Areas"))
    for item in [
        "Authentication and session management",
        "Registration and team management",
        "Challenge loading and access control",
        "Flag submission and validation",
        "Score calculation and ranking",
        "Act unlock logic",
        "Intel Request and hint penalties",
        "Leaderboard data",
        "Announcements",
        "Admin operations",
        "Submission logs and audit logs",
        "Platform settings",
    ]:
        parts.append(bullet(item))

    parts.append(h2("Minimum Data Entities"))
    for item in [
        "users, teams, team_members, registrations",
        "acts, challenges, challenge_files, flags",
        "submissions, solves, act_unlocks",
        "intel_requests, story_fragments, evidence_items",
        "announcements, penalties, leaderboard_snapshots",
        "audit_logs, platform_settings",
    ]:
        parts.append(bullet(item))

    parts.append(h1("6. Competition Platform Requirements"))
    parts.append(
        para("The /platform route should become the registered participant area after backend/auth exists.")
    )
    for item in [
        "Dashboard with team score, rank, current Act, solved count, progress, activity, and announcements",
        "Storyline view for Prologue, four Acts, and locked Final Investigation",
        "Challenge workspace grouped by Act with mission brief, objectives, files, hints, and flag submission",
        "Progress page showing unlock status, remaining points, completed challenges, fragments, and penalties",
        "Investigation Board for story fragments, evidence, recovered files, keys, and notes",
        "Leaderboard using Investigation Score first, then official tie-breakers",
        "Announcements, Team Profile, Settings, and Logout",
    ]:
        parts.append(bullet(item))

    parts.append(h1("7. Admin Panel Requirements"))
    parts.append(
        para("The /admin route should become a restricted organizer-only area. All permissions must be enforced on the server.")
    )
    for item in [
        "Admin dashboard with event health, activity, standings, solves, and platform status",
        "Challenge management for challenge CRUD, files, flags, story fragments, Intel Requests, and point values",
        "Team management for viewing teams, edits, password resets, progress resets, penalties, and disqualification",
        "Leaderboard management for overrides, deductions, bonus points, and freeze mode",
        "Announcement management for creating, editing, scheduling, and archiving announcements",
        "Submission logs for login history, flag attempts, Intel usage, unlock events, and score changes",
        "Platform settings for event status, registration state, access controls, and scoring settings",
    ]:
        parts.append(bullet(item))

    parts.append(h1("8. Security Requirements"))
    for item in [
        "Validate flags and calculate scores only on the backend",
        "Store flags securely, preferably hashed or protected by server-only validation",
        "Rate-limit login and flag submission",
        "Use server-side authorization for participant and admin access",
        "Add CSRF protection if using cookie-based sessions",
        "Validate all inputs and escape all outputs",
        "Keep secrets out of frontend bundles, public files, source maps, and client-side data",
        "Record audit logs for admin actions and score-affecting events",
    ]:
        parts.append(bullet(item))

    parts.append(h1("9. Organizer Details Still Needed"))
    for item in [
        "Exact registration open date",
        "Exact registration close date",
        "Competition start date",
        "Final submission deadline",
        "Awarding/closing date",
        "Official contact channel",
        "Team size requirements",
        "Registration URL or form",
        "Sponsor and partner names/logos",
        "Final production platform URL",
    ]:
        parts.append(bullet(item))

    parts.append(h1("10. Recommended Build Order"))
    steps = [
        "Add README and .env.example.",
        "Choose backend and database stack.",
        "Implement auth and role-based access.",
        "Build registration and team model.",
        "Build challenge schema and admin challenge management.",
        "Build flag submission and scoring.",
        "Build Act unlock and Intel Request logic.",
        "Connect participant platform pages to real API data.",
        "Build leaderboard.",
        "Build announcement system.",
        "Build audit logs and admin controls.",
        "Add tests and security hardening.",
        "Replace TBA event details with organizer-approved values.",
        "Deploy staging, run QA, then deploy production.",
    ]
    for item in steps:
        parts.append(number(item))

    parts.append(h1("11. Launch Readiness Checklist"))
    for item in [
        "Official dates are confirmed.",
        "Official contact channel is confirmed.",
        "Registration form is live.",
        "Authentication is implemented.",
        "Participant platform is protected.",
        "Admin panel is protected.",
        "Challenges are stored outside the public frontend.",
        "Real flags and final answers are not exposed.",
        "Score logic is backend-controlled.",
        "Intel penalties are backend-controlled.",
        "Leaderboard is live and tested.",
        "Submission logs are available to organizers.",
        "Rate limiting is enabled.",
        "Admin audit logs are enabled.",
        "Full participant flow is tested.",
        "Full admin flow is tested.",
        "Production deployment is verified.",
    ]:
        parts.append(bullet("[ ] " + item))

    body = "".join(parts)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}"
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'
        "</w:body></w:document>"
    )


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr></w:rPrDefault>
    <w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr><w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="400" w:after="120"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="40"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="360" w:after="120"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="320" w:after="80"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="434343"/><w:sz w:val="28"/></w:rPr></w:style>
</w:styles>"""


def numbering_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="1">
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>
  <w:abstractNum w:abstractNumId="2">
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl>
  </w:abstractNum>
  <w:num w:numId="2"><w:abstractNumId w:val="2"/></w:num>
</w:numbering>"""


def build_docx() -> None:
    files = {
        "[Content_Types].xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>""",
        "_rels/.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""",
        "word/_rels/document.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>""",
        "word/document.xml": document_xml(),
        "word/styles.xml": styles_xml(),
        "word/numbering.xml": numbering_xml(),
    }
    with ZipFile(DOCX_PATH, "w", ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)


def build_google_docs_md() -> None:
    GDOC_MD_PATH.write_text(
        """# Packet Capture Developer Handoff

Google Docs-ready guide for the remaining work on **Packet Capture: Beneath the Network**.

**Status:** Frontend-only Next.js implementation. Public content is aligned with the CTF Guidelines and Storyline docs. Backend, auth, database, scoring, and admin operations are still missing.

## Current State

- Framework: Next.js App Router
- Main public site route: `/`
- Competition platform shell: `/platform`
- Admin panel shell: `/admin`
- Shared public content source: `app/data.ts`
- Main styles and font rules: `app/globals.css`
- Public assets: `public/fonts`, `public/images`
- Implementation type: static frontend only, with no API, database, or authentication

## What Already Exists

- Public event intro, About, Overview, Four Acts, Rules, Scoring, FAQ, Timeline, Sponsors and Partners, and Footer sections
- Route-aware navigation for Main, Competition Platform, and Admin
- Frontend shell for participant modules
- Frontend shell for organizer/admin modules
- Centralized event content in `app/data.ts`
- Public-safe flag format display: `PacketCapture{FLAG_NAME}`

## Critical Content Rule

Do not expose real flags, final investigation answers, hidden keys, solution fragments, or final phrases in frontend code, static files, comments, public JSON, or generated HTML.

Keep secret challenge material only in backend-controlled storage or organizer-only files outside the public frontend bundle.

## Gap Matrix

| Area | Current State | Still Needed | Priority |
|---|---|---|---|
| Backend/API | None | Auth, registration, challenge APIs, submissions, scoring, admin operations | Critical |
| Database | None | Users, teams, challenges, flags, submissions, solves, logs, settings | Critical |
| Auth | None | Participant/team/admin login, role access, sessions, password reset | Critical |
| Registration | Opening soon copy only | Registration form, team validation, approval flow, state controls | High |
| Platform | Frontend shell | Dashboard, challenges, progress, evidence board, leaderboard, announcements | Critical |
| Admin | Frontend shell | Challenge/team/leaderboard/announcement/submission/platform management | Critical |
| Scoring | Static copy only | Backend score engine, hint penalties, tie-breakers, audit trail | Critical |
| Timeline/contact | TBA placeholders | Organizer-confirmed dates and official channel | High |
| Sponsors | Empty placeholder | Sponsor names, tiers, logos, links | Medium |
| Testing | Build only | Unit, integration, E2E, role access, scoring tests | High |

## Backend and Database Requirements

### API Areas

- Authentication and session management
- Registration and team management
- Challenge loading and access control
- Flag submission and validation
- Score calculation and ranking
- Act unlock logic
- Intel Request and hint penalties
- Leaderboard data
- Announcements
- Admin operations
- Submission logs and audit logs
- Platform settings

### Minimum Data Entities

- `users`, `teams`, `team_members`, `registrations`
- `acts`, `challenges`, `challenge_files`, `flags`
- `submissions`, `solves`, `act_unlocks`
- `intel_requests`, `story_fragments`, `evidence_items`
- `announcements`, `penalties`, `leaderboard_snapshots`
- `audit_logs`, `platform_settings`

## Competition Platform Requirements

The `/platform` route should become the registered participant area after backend/auth exists.

- Dashboard with team score, rank, current Act, solved count, progress, activity, and announcements
- Storyline view for Prologue, four Acts, and locked Final Investigation
- Challenge workspace grouped by Act with mission brief, objectives, files, hints, and flag submission
- Progress page showing unlock status, remaining points, completed challenges, fragments, and penalties
- Investigation Board for story fragments, evidence, recovered files, keys, and notes
- Leaderboard using Investigation Score first, then official tie-breakers
- Announcements, Team Profile, Settings, and Logout

## Admin Panel Requirements

The `/admin` route should become a restricted organizer-only area. All permissions must be enforced on the server.

- Admin dashboard with event health, activity, standings, solves, and platform status
- Challenge management for challenge CRUD, files, flags, story fragments, Intel Requests, and point values
- Team management for viewing teams, edits, password resets, progress resets, penalties, and disqualification
- Leaderboard management for overrides, deductions, bonus points, and freeze mode
- Announcement management for creating, editing, scheduling, and archiving announcements
- Submission logs for login history, flag attempts, Intel usage, unlock events, and score changes
- Platform settings for event status, registration state, access controls, and scoring settings

## Security Requirements

- Validate flags and calculate scores only on the backend
- Store flags securely, preferably hashed or protected by server-only validation
- Rate-limit login and flag submission
- Use server-side authorization for participant and admin access
- Add CSRF protection if using cookie-based sessions
- Validate all inputs and escape all outputs
- Keep secrets out of frontend bundles, public files, source maps, and client-side data
- Record audit logs for admin actions and score-affecting events

## Organizer Details Still Needed

- Exact registration open date
- Exact registration close date
- Competition start date
- Final submission deadline
- Awarding/closing date
- Official contact channel
- Team size requirements
- Registration URL or form
- Sponsor and partner names/logos
- Final production platform URL

## Recommended Build Order

1. Add README and `.env.example`.
2. Choose backend and database stack.
3. Implement auth and role-based access.
4. Build registration and team model.
5. Build challenge schema and admin challenge management.
6. Build flag submission and scoring.
7. Build Act unlock and Intel Request logic.
8. Connect participant platform pages to real API data.
9. Build leaderboard.
10. Build announcement system.
11. Build audit logs and admin controls.
12. Add tests and security hardening.
13. Replace TBA event details with organizer-approved values.
14. Deploy staging, run QA, then deploy production.

## Launch Readiness Checklist

- [ ] Official dates are confirmed.
- [ ] Official contact channel is confirmed.
- [ ] Registration form is live.
- [ ] Authentication is implemented.
- [ ] Participant platform is protected.
- [ ] Admin panel is protected.
- [ ] Challenges are stored outside the public frontend.
- [ ] Real flags and final answers are not exposed.
- [ ] Score logic is backend-controlled.
- [ ] Intel penalties are backend-controlled.
- [ ] Leaderboard is live and tested.
- [ ] Submission logs are available to organizers.
- [ ] Rate limiting is enabled.
- [ ] Admin audit logs are enabled.
- [ ] Full participant flow is tested.
- [ ] Full admin flow is tested.
- [ ] Production deployment is verified.
""",
        encoding="utf-8",
    )


def build_form_md() -> None:
    FORM_MD_PATH.write_text(
        """# Google Forms Format: Packet Capture Development Completion Checklist

Use this as a Google Forms structure if the team wants to collect dev status, ownership, blockers, and launch readiness.

## Form Title

Packet Capture Development Completion Checklist

## Form Description

This form tracks the remaining work for Packet Capture: Beneath the Network. The current site is frontend-only. Backend, authentication, database, scoring, admin operations, security hardening, and launch details still need implementation before production.

## Section 1: Developer Information

1. Developer/team name  
   Question type: Short answer  
   Required: Yes

2. Assigned area  
   Question type: Multiple choice  
   Required: Yes  
   Options:
   - Backend/API
   - Database
   - Authentication
   - Registration
   - Competition Platform
   - Admin Panel
   - Scoring/Leaderboard
   - Security
   - Testing/QA
   - Deployment

3. Current status  
   Question type: Multiple choice  
   Required: Yes  
   Options:
   - Not started
   - In progress
   - Blocked
   - Ready for review
   - Done

## Section 2: Backend/API

4. Which API areas are implemented?  
   Question type: Checkboxes  
   Options:
   - Authentication
   - Registration
   - Team management
   - Challenge loading
   - Flag submission
   - Score calculation
   - Act unlock logic
   - Intel Request penalties
   - Leaderboard
   - Announcements
   - Admin operations
   - Submission/audit logs
   - Platform settings

5. Backend notes/blockers  
   Question type: Paragraph

## Section 3: Database

6. Which data models are implemented?  
   Question type: Checkboxes  
   Options:
   - users
   - teams
   - team_members
   - registrations
   - acts
   - challenges
   - challenge_files
   - flags
   - submissions
   - solves
   - act_unlocks
   - intel_requests
   - story_fragments
   - evidence_items
   - announcements
   - penalties
   - leaderboard_snapshots
   - audit_logs
   - platform_settings

7. Are real flags protected outside the frontend bundle?  
   Question type: Multiple choice  
   Required: Yes  
   Options:
   - Yes
   - No
   - Not applicable yet

## Section 4: Competition Platform

8. Which participant modules are functional?  
   Question type: Checkboxes  
   Options:
   - Dashboard
   - Storyline
   - Challenges
   - Progress
   - Investigation Board
   - Leaderboard
   - Announcements
   - Team Profile
   - Settings
   - Logout

9. Can teams submit flags through backend validation?  
   Question type: Multiple choice  
   Options:
   - Yes
   - No
   - In progress

10. Can Acts unlock based on Investigation Score?  
    Question type: Multiple choice  
    Options:
    - Yes
    - No
    - In progress

## Section 5: Admin Panel

11. Which admin modules are functional?  
    Question type: Checkboxes  
    Options:
    - Admin dashboard
    - Challenge management
    - Team management
    - Leaderboard management
    - Announcement management
    - Submission logs
    - Platform settings

12. Are admin actions protected by server-side role checks?  
    Question type: Multiple choice  
    Options:
    - Yes
    - No
    - In progress

13. Are admin actions recorded in audit logs?  
    Question type: Multiple choice  
    Options:
    - Yes
    - No
    - In progress

## Section 6: Launch Details

14. Which organizer details are already confirmed?  
    Question type: Checkboxes  
    Options:
    - Registration open date
    - Registration close date
    - Competition start date
    - Final submission deadline
    - Awarding/closing date
    - Official contact channel
    - Team size requirements
    - Registration URL/form
    - Sponsor/partner names
    - Production platform URL

15. Remaining launch blockers  
    Question type: Paragraph

## Section 7: Final Readiness

16. Final readiness check  
    Question type: Checkboxes  
    Options:
    - Auth implemented
    - Participant platform protected
    - Admin panel protected
    - Real flags not exposed
    - Score logic backend-controlled
    - Intel penalties backend-controlled
    - Leaderboard tested
    - Submission logs available
    - Rate limiting enabled
    - Admin audit logs enabled
    - Participant flow tested
    - Admin flow tested
    - Production deployment verified

17. Overall readiness rating  
    Question type: Linear scale  
    Scale: 1 to 10  
    Label 1: Not ready  
    Label 10: Launch ready
""",
        encoding="utf-8",
    )


def main() -> None:
    build_docx()
    build_google_docs_md()
    build_form_md()
    print(DOCX_PATH)
    print(GDOC_MD_PATH)
    print(FORM_MD_PATH)


if __name__ == "__main__":
    main()
