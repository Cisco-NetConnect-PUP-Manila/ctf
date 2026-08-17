import Marquee from "./components/Marquee";
import Link from "next/link";
import FaqAccordion from "./components/FaqAccordion";
import TimelineWave from "./components/TimelineWave";
import Window from "./components/Window";
import Reveal from "./components/Reveal";
import {
  acts,
  aiExamples,
  allowedResources,
  competition,
  faqs,
  mechanics,
  rankingCriteria,
  recommendedTools,
  rules,
  sponsors,
  timeline,
} from "./data";

export default function Home() {
  const totalCases = acts.reduce((sum, act) => sum + act.cases, 0);
  const totalScore = acts.reduce(
    (sum, act) => sum + Number(act.points.replace(/,/g, "")),
    0
  );

  return (
    <>
      <main id="top">
        <section className="hero">
          <div className="shell hero__grid">
            <div>
              <div className="hero__channel">
                <span className="live" />
                {competition.status} - Cyber Incident Response CTF
              </div>
              <h1>
                Packet
                <br />
                Capture
                <br />
                <span className="glitch" data-text="Beneath">
                  Beneath
                </span>
              </h1>
              <p className="hero__lead">{competition.hero}</p>
              <div className="btn-row hero__actions">
                <div className="hero__auth-actions">
                  <Link className="btn btn--primary btn--terminal" href="/register">
                    Register team
                  </Link>
                  <Link className="btn btn--ghost btn--terminal hero__sign-in" href="/login">
                    Sign in
                  </Link>
                </div>
                <a href="#rules" className="btn btn--ghost btn--terminal">
                  Read official rules
                </a>
              </div>
            </div>

            <div className="hero__side">
              <div className="dialog" role="alert">
                <div className="dialog__hatch" aria-hidden="true" />
                <div className="dialog__title">INCOMING TRANSMISSION</div>
                <div className="dialog__body">
                  You are looking at the network. Someone built something beneath it.
                </div>
                <div className="dialog__actions">
                  <a href="#about" className="btn">
                    Open brief
                  </a>
                  <a href="#faq" className="btn">
                    FAQ
                  </a>
                </div>
              </div>

              <Window title="STATUS.LCD" meta="public-brief // standby" icon="[]">
                <div className="lcd">
                  <div className="lcd__row">
                    <span className="lcd__k">&gt; EVENT</span>
                    <span className="lcd__v">Packet Capture</span>
                  </div>
                  <div className="lcd__row">
                    <span className="lcd__k">&gt; REGISTRATION</span>
                    <span className="lcd__v amber">Opening Soon</span>
                  </div>
                  <div className="lcd__row">
                    <span className="lcd__k">&gt; ACTS</span>
                    <span className="lcd__v">4 Sequential</span>
                  </div>
                  <div className="lcd__row">
                    <span className="lcd__k">&gt; PUBLIC CASES</span>
                    <span className="lcd__v">{totalCases}</span>
                  </div>
                  <div className="lcd__row">
                    <span className="lcd__k">&gt; FINAL LAYER</span>
                    <span className="lcd__v alert">Locked</span>
                  </div>
                  <div className="progress">
                    <i />
                  </div>
                </div>
              </Window>
            </div>
          </div>
        </section>

        <Marquee />

        <section id="about" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(01) Incident Brief</span>
                <h2>About Packet Capture</h2>
              </div>
              <span className="section-index">01 / 08</span>
            </Reveal>

            <Reveal className="about about__grid">
              <Window title="brief.log" meta="cleared" className="brief-window">
                <div>
                  <p>{competition.description}</p>
                  <p>{competition.about}</p>
                  <p>{competition.story}</p>
                </div>
              </Window>

              <div className="stats">
                <div className="stat">
                  <b>4</b>
                  <span>Sequential Acts</span>
                </div>
                <div className="stat">
                  <b>{totalCases}</b>
                  <span>Public Cases</span>
                </div>
                <div className="stat">
                  <b>{totalScore.toLocaleString()}</b>
                  <span>Investigation Score</span>
                </div>
                <div className="stat">
                  <b>1</b>
                  <span>Final Investigation</span>
                </div>
              </div>
            </Reveal>
          </div>
        </section>

        <section id="overview" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(02) Competition Overview</span>
                <h2>Race Smart. Score Higher.</h2>
              </div>
              <span className="section-index">02 / 08</span>
            </Reveal>
            <Reveal>
              <p className="sec__lead">
                Score leads the ranking. Time, Intel penalties, and Final
                Investigation timing break ties. Teams should solve accurately,
                manage time, and decide carefully when to request hints.
              </p>
            </Reveal>

            <div className="mechanics__grid">
              {mechanics.map((item, i) => (
                <Reveal className="mechanic-card" key={item.title} delay={i * 50}>
                  <div className="rule__n">{String(i + 1).padStart(2, "0")}</div>
                  <h3>{item.title}</h3>
                  <p>{item.body}</p>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        <section id="acts" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(03) Four Acts</span>
                <h2>The Investigation</h2>
              </div>
              <span className="section-index">03 / 08</span>
            </Reveal>
            <Reveal>
              <p className="sec__lead">
                Challenge names and point totals are public. Correct flags,
                final answers, and solution fragments remain{" "}
                <span className="classified">classified</span>.
              </p>
            </Reveal>

            <div className="acts__grid">
              {acts.map((act, i) => (
                <Reveal className="act" key={act.id} delay={i * 60}>
                  <Window
                    title={`${act.num} - ${act.track}`}
                    meta={`status: ${act.status} // ${act.cases} cases`}
                    icon="[]"
                  >
                    <div className="act__num">{act.track.toUpperCase()}</div>
                    <div className="act__title">{act.title}</div>
                    <div className="act__disc">&quot;{act.title}&quot;</div>
                    <p className="act__desc">{act.desc}</p>

                    <div className="act__figs">
                      <div className="act__fig">
                        <b>{act.cases}</b>
                        <span>Cases</span>
                      </div>
                      <div className="act__fig">
                        <b>{act.points}</b>
                        <span>Points</span>
                      </div>
                      <div className="act__fig">
                        <span
                          className="tag tag--live"
                          style={{ border: "none", padding: 0 }}
                        >
                          {act.status}
                        </span>
                        <span>Status</span>
                      </div>
                    </div>

                    <div className="cases">
                      <div className="cases__label">Public case names</div>
                      <div className="cases__list">
                        {act.caseNames.map((c) => (
                          <span className="case-chip" key={c}>
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="act__unlock">{act.unlock}</div>
                  </Window>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        <section id="scoring" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(04) Investigation Score</span>
                <h2>Ranking Priority</h2>
              </div>
              <span className="section-index">04 / 08</span>
            </Reveal>

            <Reveal className="brief-grid">
              <Window title="score.rules" meta="official scope">
                <div>
                  <p>
                    Teams are ranked primarily by total Investigation Score.
                    The competition rewards accuracy first, then efficiency when
                    teams are tied.
                  </p>
                  <ol className="ranking-list">
                    {rankingCriteria.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ol>
                </div>
              </Window>

              <Window title="flag.intel" meta="submission policy">
                <div>
                  <p>
                    Official flag format:
                    <span className="flag-format">{competition.format}</span>
                  </p>
                  <p>
                    Flags are case-sensitive. Incorrect submissions award no
                    points. Intel Requests may reveal hints at the cost of
                    Investigation Score.
                  </p>
                </div>
              </Window>
            </Reveal>
          </div>
        </section>

        <section id="rules" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(05) Rules of Engagement</span>
                <h2>Official Rules</h2>
              </div>
              <span className="section-index">05 / 08</span>
            </Reveal>
            <Reveal>
              <p className="sec__lead">
                By registering, participants agree to follow the rules and any
                decisions made by the organizing committee.
              </p>
            </Reveal>

            <div className="rules__grid">
              {rules.map((rule, i) => (
                <Reveal className="rule" key={rule.title} delay={i * 45}>
                  <div className="rule__n">
                    {String(i + 1).padStart(2, "0")}
                  </div>
                  <h3>{rule.title}</h3>
                  <p>{rule.body}</p>
                </Reveal>
              ))}
            </div>

            <Reveal className="resources-grid">
              <Window title="allowed.resources" meta="ethical use only">
                <ul className="terminal-list">
                  {allowedResources.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </Window>
              <Window title="ai.examples" meta="permitted">
                <ul className="terminal-list">
                  {aiExamples.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </Window>
              <Window title="recommended.tools" meta="prepare before event">
                <ul className="terminal-list">
                  {recommendedTools.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </Window>
            </Reveal>
          </div>
        </section>

        <section id="faq" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(06) FAQ</span>
                <h2>FAQ</h2>
              </div>
              <span className="section-index">06 / 08</span>
            </Reveal>

            <Reveal>
              <FaqAccordion items={faqs} />
            </Reveal>
          </div>
        </section>

        <section id="timeline" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(07) Operation Timeline</span>
                <h2>Event Timeline</h2>
              </div>
              <span className="section-index">07 / 08</span>
            </Reveal>

            <Reveal>
              <p className="notice-line">
                Dates are pending organizer confirmation. No final schedule has
                been invented in this public build.
              </p>
            </Reveal>

            <Reveal>
              <Window title="TIMELINE.LOG" meta="dates pending // organizer confirmation" icon="[]">
                <TimelineWave items={timeline} />
              </Window>
            </Reveal>
          </div>
        </section>

        <section id="sponsors" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(08) Sponsors &amp; Partners</span>
                <h2>Sponsors &amp; Partners</h2>
              </div>
              <span className="section-index">08 / 08</span>
            </Reveal>

            <Reveal>
              <Window title="partners.db" meta="pending">
                {sponsors.length > 0 ? (
                  <div className="sponsors__grid">
                    {sponsors.map((sponsor) => (
                      <a
                        className="sponsor"
                        href={sponsor.link || "#sponsors"}
                        key={sponsor.name}
                      >
                        {sponsor.name}
                        <small>{sponsor.tier}</small>
                      </a>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    Sponsor and partner details are not finalized yet.
                  </div>
                )}
              </Window>
            </Reveal>
          </div>
        </section>

        <section id="register" className="register">
          <div className="shell">
            <Reveal>
              <span className="eyebrow">REGISTER.EXE - Pending Launch</span>
              <h2>Join The Response</h2>
              <p>
                The network is only the surface. Assemble your team, study the
                rules, prepare your tools, and wait for the official
                registration window.
              </p>
              <div className="btn-row">
                <Link className="btn btn--primary" href="/register">
                  Register team
                </Link>
                <Link className="btn" href="/login">
                  Team login
                </Link>
              </div>
            </Reveal>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="shell">
          <div className="footer__grid">
            <div>
              <div className="footer__logo">PACKET CAPTURE</div>
              <p className="footer__copy">
                Beneath the Network. A story-driven cyber incident response CTF.
              </p>
            </div>
            <div>
              <h4>Navigate</h4>
              <ul>
                <li>
                  <a href="#about">About</a>
                </li>
                <li>
                  <a href="#acts">Four Acts</a>
                </li>
                <li>
                  <a href="#rules">Rules</a>
                </li>
                <li>
                  <a href="#faq">FAQ</a>
                </li>
                <li>
                  <a href="#sponsors">Sponsors</a>
                </li>
              </ul>
            </div>
            <div>
              <h4>Status</h4>
              <ul>
                <li>Registration <span className="footer__soon">(opening soon)</span></li>
                <li>Timeline <span className="footer__soon">(TBA)</span></li>
                <li>Partners <span className="footer__soon">(pending)</span></li>
              </ul>
            </div>
            <div>
              <h4>Contact</h4>
              <ul>
                <li>
                  <a href={`mailto:${competition.contact}`}>
                    {competition.contact}
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="footer__base">
            <span>2026 Packet Capture CTF - Beneath the Network</span>
            <span>{"// CHANNEL CLOSED"}</span>
          </div>
        </div>
      </footer>
    </>
  );
}
