import Reveal from "../components/Reveal";
import Window from "../components/Window";
import ParticipantSessionGuard from "../components/auth/ParticipantSessionGuard";
import ParticipantAccountControls, {
  ParticipantTeamName,
} from "../components/auth/ParticipantAccountControls";
import {
  acts,
  competition,
  competitionModules,
  rankingCriteria,
} from "../data";

export default function CompetitionPlatformPage() {
  return (
    <ParticipantSessionGuard>
      <main className="portal-page" id="platform-top">
      <section className="portal-hero">
        <div className="shell portal-hero__grid">
          <Reveal>
            <span className="eyebrow">TEAM PORTAL.EXE</span>
            <h1>Competition Platform</h1>
            <p>
              Participant workspace for story progression, challenge access,
              Investigation Score tracking, recovered evidence, leaderboard
              position, announcements, and team profile.
            </p>
            <div className="portal-actions">
              <ParticipantAccountControls />
              <a className="btn btn--primary" href="/">
                Back to public site
              </a>
            </div>
          </Reveal>

          <Reveal>
            <Window title="ACCESS.STATE" meta="authenticated frontend shell">
              <div className="portal-lock">
                <b>Team channel authenticated.</b>
                <span>
                  Protected participant access is active. Score calculation,
                  unlock logic, Intel penalties, flag validation, and final-answer
                  verification remain controlled by backend services.
                </span>
              </div>
            </Window>
          </Reveal>
        </div>
      </section>

      <section className="sec" id="dashboard">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(01) Team Dashboard</span>
              <h2>Standby Snapshot</h2>
            </div>
            <span className="section-index">01 / 05</span>
          </Reveal>

          <Reveal className="portal-dashboard">
            <Window title="team.snapshot" meta="mock display only">
              <div className="metric-grid">
                <div className="metric">
                  <span>Team</span>
                  <ParticipantTeamName />
                </div>
                <div className="metric">
                  <span>Investigation Score</span>
                  <b>0</b>
                </div>
                <div className="metric">
                  <span>Current Rank</span>
                  <b>--</b>
                </div>
                <div className="metric">
                  <span>Current Act</span>
                  <b>Locked</b>
                </div>
              </div>
            </Window>

            <Window title="ranking.priority" meta="official order">
              <ol className="ranking-list">
                {rankingCriteria.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ol>
            </Window>
          </Reveal>
        </div>
      </section>

      <section className="sec" id="storyline">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(02) Storyline</span>
              <h2>Act Progression</h2>
            </div>
            <span className="section-index">02 / 05</span>
          </Reveal>

          <div className="portal-act-grid">
            {acts.map((act, i) => (
              <Reveal className="portal-card" key={act.id} delay={i * 50}>
                <span className="status-pill">{act.status}</span>
                <h3>
                  {act.num}: {act.title}
                </h3>
                <p>{act.track}</p>
                <p>{act.desc}</p>
                <div className="portal-card__meta">
                  {act.cases} cases / {act.points} pts
                </div>
              </Reveal>
            ))}
            <Reveal className="portal-card portal-card--locked">
              <span className="status-pill">Locked</span>
              <h3>Final Investigation</h3>
              <p>
                Reconstruct the complete investigation using recovered story
                fragments, investigation keys, digital evidence, files, and
                artifacts from all Acts.
              </p>
              <div className="portal-card__meta">Terminal interface pending</div>
            </Reveal>
          </div>
        </div>
      </section>

      <section className="sec" id="modules">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(03) Participant Modules</span>
              <h2>Platform Modules</h2>
            </div>
            <span className="section-index">03 / 05</span>
          </Reveal>

          <div className="module-grid">
            {competitionModules.map((module, i) => (
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
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="sec" id="challenges">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(04) Challenge Workspace</span>
              <h2>Submission Policy</h2>
            </div>
            <span className="section-index">04 / 05</span>
          </Reveal>

          <Reveal className="brief-grid">
            <Window title="challenge.fields" meta="required page content">
              <ul className="terminal-list">
                <li>Challenge title, category, difficulty, and score</li>
                <li>Mission brief, story context, description, and objectives</li>
                <li>Downloadable files where applicable</li>
                <li>Intel Requests with penalty confirmation</li>
                <li>Flag submission form with backend validation</li>
              </ul>
            </Window>
            <Window title="final.warning" meta="do not expose answers">
              <p>
                Correct flags and the final reconstructed phrase must never be
                shipped in frontend source. The UI can submit attempts, but the
                backend must decide whether they are correct.
              </p>
              <span className="flag-format">{competition.format}</span>
            </Window>
          </Reveal>
        </div>
      </section>

      <section className="register" id="portal-status">
        <div className="shell">
          <Reveal>
            <span className="eyebrow">PORTAL STATUS</span>
            <h2>Backend Required</h2>
            <p>
              This route now contains the documented participant platform
              surface. Live data, submissions, accounts, and scoring are ready
              for backend integration later.
            </p>
          </Reveal>
        </div>
      </section>

      <footer className="footer footer--portal">
        <div className="shell">
          <div className="footer__grid">
            <div>
              <div className="footer__logo">COMPETITION PLATFORM</div>
              <p className="footer__copy">
                Participant-side shell for teams, progress, challenges,
                evidence, leaderboard, and announcements.
              </p>
            </div>
            <div>
              <h4>Portal</h4>
              <ul>
                <li>
                  <a href="/platform#dashboard">Dashboard</a>
                </li>
                <li>
                  <a href="/platform#storyline">Storyline</a>
                </li>
                <li>
                  <a href="/platform#modules">Modules</a>
                </li>
                <li>
                  <a href="/platform#challenges">Challenges</a>
                </li>
              </ul>
            </div>
            <div>
              <h4>Access</h4>
              <ul>
                <li>Login <span className="footer__soon">(backend)</span></li>
                <li>Scoring <span className="footer__soon">(backend)</span></li>
                <li>Flags <span className="footer__soon">(server-side)</span></li>
              </ul>
            </div>
            <div>
              <h4>Switch</h4>
              <ul>
                <li>
                  <a href="/">Main Site</a>
                </li>
                <li>
                  <a href="/admin">Admin</a>
                </li>
              </ul>
            </div>
          </div>
          <div className="footer__base">
            <span>Competition Platform - frontend shell</span>
            <span>// TEAM CHANNEL</span>
          </div>
        </div>
      </footer>
      </main>
    </ParticipantSessionGuard>
  );
}
