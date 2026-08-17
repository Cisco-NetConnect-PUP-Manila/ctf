import Link from "next/link";
import Reveal from "../components/Reveal";
import Window from "../components/Window";
import ParticipantSessionGuard from "../components/auth/ParticipantSessionGuard";
import ParticipantAccountControls from "../components/auth/ParticipantAccountControls";
import AnnouncementsFeed from "../components/announcements/AnnouncementsFeed";
import ParticipantDashboardSnapshot from "../components/challenges/ParticipantDashboardSnapshot";
import ParticipantChallengeList from "../components/challenges/ParticipantChallengeList";
import ParticipantPlatformStatusGate from "../components/challenges/ParticipantPlatformStatusGate";
import ParticipantLeaderboard from "../components/leaderboard/ParticipantLeaderboard";

export default function CompetitionPlatformPage() {
  return (
    <ParticipantSessionGuard>
      <main className="portal-page portal-page--platform" id="platform-top">
      <section className="portal-hero" id="dashboard">
        <div className="shell portal-hero__grid">
          <Reveal className="platform-hero-copy">
            <span className="eyebrow">TEAM PORTAL.EXE</span>
            <h1>
              Competition
              <br />
              <span className="glitch" data-text="Platform">
                Platform
              </span>
            </h1>
            <p>
              Participant workspace for approved teams. Open available
              challenges, download evidence files, submit flags, and track
              current progress.
            </p>
            <div className="platform-brief-grid" aria-label="Participant workflow">
              <div>
                <span>01</span>
                <b>Review updates</b>
                <small>Check organizer transmissions before starting a solve.</small>
              </div>
              <div>
                <span>02</span>
                <b>Open unlocked Acts</b>
                <small>Use only challenges your team has access to.</small>
              </div>
              <div>
                <span>03</span>
                <b>Submit recovered flags</b>
                <small>Correct solves update your score and progression.</small>
              </div>
            </div>
            <div className="portal-actions platform-hero-actions">
              <Link className="btn" href="#announcements-feed">
                Read announcements
              </Link>
              <Link className="btn btn--primary" href="#challenges">
                Open challenges
              </Link>
            </div>
          </Reveal>

          <Reveal>
            <Window title="team.snapshot" meta="backend live">
              <div className="platform-snapshot-panel">
                <ParticipantDashboardSnapshot />
              </div>
              <div className="platform-session-panel">
                <ParticipantAccountControls />
                <Link className="btn" href="/">
                  Back to public site
                </Link>
              </div>
            </Window>
          </Reveal>
        </div>
      </section>

      <ParticipantPlatformStatusGate>
        <section className="sec" id="announcements-feed">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(02) Announcements</span>
                <h2>Event Transmissions</h2>
              </div>
              <span className="section-index">02 / 04</span>
            </Reveal>

            <Reveal>
              <AnnouncementsFeed />
            </Reveal>
          </div>
        </section>

        <section className="sec" id="leaderboard">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(03) Leaderboard</span>
                <h2>Investigation Standings</h2>
              </div>
              <span className="section-index">03 / 04</span>
            </Reveal>

            <Reveal>
              <ParticipantLeaderboard />
            </Reveal>
          </div>
        </section>

      {/* Temporarily hidden: static storyline/modules/status sections were making the
          participant page read like documentation instead of a working CTF portal.
      <section className="sec" id="storyline">
        <div className="shell">
          <Reveal className="sec__head">
            <div>
              <span className="eyebrow">(03) Storyline</span>
              <h2>Act Progression</h2>
            </div>
            <span className="section-index">03 / 06</span>
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
              <span className="eyebrow">(04) Participant Modules</span>
              <h2>Platform Modules</h2>
            </div>
            <span className="section-index">04 / 06</span>
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
                <span className="eyebrow">(04) Challenge Workspace</span>
                <h2>Challenge Directory</h2>
              </div>
              <span className="section-index">04 / 04</span>
            </Reveal>

            <Reveal>
              <ParticipantChallengeList />
            </Reveal>
          </div>
        </section>
      </ParticipantPlatformStatusGate>

      {/* Temporarily hidden: redundant backend status banner.
      <section className="register" id="portal-status">
        <div className="shell">
          <Reveal>
            <span className="eyebrow">PORTAL STATUS</span>
            <h2>Backend Connected</h2>
            <p>
              Participant login, approval gating, challenge access, file
              downloads, flag submissions, scoring, and Act progression now
              read from the backend.
            </p>
          </Reveal>
        </div>
      </section>
      */}

      {/* Temporarily hidden: footer repeated the same links/status text as the page.
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
                  <Link href="/platform#dashboard">Dashboard</Link>
                </li>
                <li>
                  <Link href="/platform#storyline">Storyline</Link>
                </li>
                <li>
                  <Link href="/platform#modules">Modules</Link>
                </li>
                <li>
                  <Link href="/platform#challenges">Challenges</Link>
                </li>
              </ul>
            </div>
            <div>
              <h4>Access</h4>
              <ul>
                <li>Login <span className="footer__soon">(live)</span></li>
                <li>Scoring <span className="footer__soon">(live)</span></li>
                <li>Flags <span className="footer__soon">(server-side)</span></li>
              </ul>
            </div>
            <div>
              <h4>Switch</h4>
              <ul>
                <li>
                  <Link href="/">Main Site</Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="footer__base">
            <span>Competition Platform - backend-connected team workspace</span>
            <span>{"// TEAM CHANNEL"}</span>
          </div>
        </div>
      </footer>
      */}
      </main>
    </ParticipantSessionGuard>
  );
}
