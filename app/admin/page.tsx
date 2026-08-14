import Link from "next/link";
import Reveal from "../components/Reveal";
import Window from "../components/Window";
import AdminSessionGuard from "../components/auth/AdminSessionGuard";
import AdminAccountControls from "../components/auth/AdminAccountControls";
import AdminOverviewSnapshot from "../components/admin/AdminOverviewSnapshot";
import AdminSubmissionMonitor from "../components/admin/AdminSubmissionMonitor";
import AdminTeamManager from "../components/admin/AdminTeamManager";
import AnnouncementsManager from "../components/announcements/AnnouncementsManager";
import AdminChallengeManager from "../components/challenges/AdminChallengeManager";

export default function AdminPanelPage() {
  return (
    <AdminSessionGuard>
      <main className="portal-page portal-page--admin" id="admin-top">
      <section className="portal-hero">
        <div className="shell portal-hero__grid">
          <Reveal>
            <span className="eyebrow">ADMIN CONSOLE.SYS</span>
            <h1>Administrative Panel</h1>
            <p>
              Organizer workspace for challenge publishing, team approvals,
              announcements, and submission monitoring.
            </p>
            <div className="portal-actions">
              <AdminAccountControls />
              <Link className="btn btn--primary" href="/">
                Back to public site
              </Link>
            </div>
          </Reveal>

          {/* Temporarily hidden: static access explainer. The working admin tools below
              make the authenticated state clear without extra copy. */}
        </div>
      </section>

      <section className="sec" id="overview">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(01) Admin Overview</span>
              <h2>Control Room</h2>
            </div>
            <span className="section-index">01 / 05</span>
          </Reveal>

          <Reveal className="portal-dashboard">
            <Window title="platform.status" meta="backend live">
              <AdminOverviewSnapshot />
            </Window>

            {/* Temporarily hidden: audit checklist repeated the submission monitor below. */}
          </Reveal>
        </div>
      </section>

      {/* Temporarily hidden: module cards are mostly planning/documentation text.
      <section className="sec" id="modules">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(02) Organizer Modules</span>
              <h2>Admin Modules</h2>
            </div>
            <span className="section-index">02 / 06</span>
          </Reveal>

          <div className="module-grid module-grid--admin">
            {adminModules.map((module, i) => (
              <Reveal className="module-card" key={module.title} delay={i * 35}>
                <div className="module-card__top">
                  <h3>{module.title}</h3>
                  <span>{module.status}</span>
                </div>
                <p>{module.body}</p>
                <ul className="module-list">
                  {module.details.map((detail) => (
                    <li key={detail}>{detail}</li>
                  ))}
                </ul>
                {moduleActions[module.title] && (
                  <Link className="btn btn--primary module-card__action" href={moduleActions[module.title].href}>
                    {moduleActions[module.title].label}
                  </Link>
                )}
              </Reveal>
            ))}
          </div>
        </div>
      </section>
      */}

      <section className="sec" id="challenges">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(03) Challenge Management</span>
              <h2>Challenge Control Console</h2>
            </div>
            <span className="section-index">02 / 05</span>
          </Reveal>

          <Reveal>
            <Window title="challenge.console" meta="backend-enforced admin CRUD">
              <AdminChallengeManager />
            </Window>
          </Reveal>
        </div>
      </section>

      <section className="sec" id="teams">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(04) Team Management</span>
              <h2>Registration Approval Queue</h2>
            </div>
            <span className="section-index">03 / 05</span>
          </Reveal>

          <Reveal>
            <Window title="team.approval" meta="admin approve / reject / disable">
              <AdminTeamManager />
            </Window>
          </Reveal>
        </div>
      </section>

      <section className="sec" id="announcements">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(05) Announcements</span>
              <h2>Publish Event Updates</h2>
            </div>
            <span className="section-index">04 / 05</span>
          </Reveal>

          <Reveal>
            <Window title="announcement.console" meta="admin publish / archive">
              <AnnouncementsManager />
            </Window>
          </Reveal>
        </div>
      </section>

      {/* Temporarily hidden: backend authority notes are useful docs, but noisy in the
          production admin surface.
      <section className="sec" id="authority">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(06) Safety Boundary</span>
              <h2>Backend Authority</h2>
            </div>
            <span className="section-index">06 / 07</span>
          </Reveal>

          <Reveal className="brief-grid">
            <Window title="frontend.can.display" meta="safe scope">
              <ul className="terminal-list">
                <li>Tables, forms, filters, empty states, and previews</li>
                <li>Locked states before organizer login</li>
                <li>Confirmation dialogs for risky actions</li>
                <li>Audit views once API data exists</li>
              </ul>
            </Window>
            <Window title="backend.must.control" meta="authoritative scope">
              <ul className="terminal-list">
                <li>Admin role validation</li>
                <li>Flag and final-answer storage</li>
                <li>Score calculation and overrides</li>
                <li>Penalties, disqualification, and unlock events</li>
              </ul>
            </Window>
          </Reveal>
        </div>
      </section>
      */}

      <section className="sec" id="submissions">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
            <span className="eyebrow">(05) Submission Monitor</span>
              <h2>Anti-Sharing Signals</h2>
            </div>
            <span className="section-index">05 / 05</span>
          </Reveal>

          <Reveal>
            <Window title="submission.monitor" meta="attempts / solves / suspicious signals">
              <AdminSubmissionMonitor />
            </Window>
          </Reveal>
        </div>
      </section>

      {/* Temporarily hidden: redundant status banner.
      <section className="register" id="admin-status">
        <div className="shell">
          <Reveal>
            <span className="eyebrow">ADMIN STATUS</span>
            <h2>Restricted Shell Ready</h2>
            <p>
              This route contains the documented administrative surface without
              pretending real organizer actions are available before backend
              integration.
            </p>
          </Reveal>
        </div>
      </section>
      */}

      {/* Temporarily hidden: footer repeated page navigation and added visual noise.
      <footer className="footer footer--portal">
        <div className="shell">
          <div className="footer__grid">
            <div>
              <div className="footer__logo">ADMINISTRATIVE PANEL</div>
              <p className="footer__copy">
                Organizer-side shell for challenge management, teams,
                leaderboard controls, announcements, logs, and settings.
              </p>
            </div>
            <div>
              <h4>Admin</h4>
              <ul>
                <li>
                  <Link href="/admin#overview">Overview</Link>
                </li>
                <li>
                  <Link href="/admin#modules">Modules</Link>
                </li>
                <li>
                  <Link href="/admin#challenges">Challenges</Link>
                </li>
                <li>
                  <Link href="/admin#teams">Teams</Link>
                </li>
                <li>
                  <Link href="/admin#submissions">Submissions</Link>
                </li>
                <li>
                  <Link href="/admin#authority">Authority</Link>
                </li>
                <li>
                  <Link href="/admin#admin-status">Status</Link>
                </li>
              </ul>
            </div>
            <div>
              <h4>Protected</h4>
              <ul>
                <li>Roles <span className="footer__soon">(live)</span></li>
                <li>Overrides <span className="footer__soon">(backend)</span></li>
                <li>Submission Monitor <span className="footer__soon">(live)</span></li>
              </ul>
            </div>
            <div>
              <h4>Switch</h4>
              <ul>
                <li>
                  <Link href="/">Main Site</Link>
                </li>
                <li>
                  <Link href="/platform">Competition Platform</Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="footer__base">
            <span>Administrative Panel - backend-connected control room</span>
            <span>{"// ADMIN CHANNEL"}</span>
          </div>
        </div>
      </footer>
      */}
    </main>
    </AdminSessionGuard>
  );
}
