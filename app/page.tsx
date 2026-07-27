// import BootSequence from "./components/BootSequence"; // disabled: replaced by IntroExperience (fake landing -> glitch -> welcome)
import Marquee from "./components/Marquee";
import TimelineWave from "./components/TimelineWave";
import Window from "./components/Window";
import Reveal from "./components/Reveal";
import { acts, rules, timeline, sponsors } from "./data";

export default function Home() {
  return (
    <>
      {/* <BootSequence /> */}

      <main id="top">
        {/* ===================== HERO ===================== */}
        <section className="hero">
          <div className="shell hero__grid">
            <div>
              <div className="hero__channel">
                <span className="live" />
                Channel Open — Cyber Incident Response Team
              </div>
              <h1>
                Beneath
                <br />
                The{" "}
                <span className="glitch" data-text="Network">
                  Network
                </span>
              </h1>
              <p className="hero__lead">
                A seemingly ordinary infrastructure is broadcasting impossible
                anomalies. Join the response team, trace the evidence, and
                preserve every key you recover.
              </p>
              <div className="btn-row">
                <a href="#register" className="btn btn--primary">
                  &raquo; Begin Investigation
                </a>
                <a href="#about" className="btn btn--ghost">
                  Read the brief
                </a>
              </div>
            </div>

            <div className="hero__side">
              <div className="dialog" role="alert">
                <div className="dialog__hatch" aria-hidden="true" />
                <div className="dialog__title">! WARNING !</div>
                <div className="dialog__body">
                  ACCESS DENIED: INVALID TEMPORAL AURA
                  <br />
                  Unsanctioned signal on subnet 10.29.0.0/16 — response team required.
                </div>
                <div className="dialog__actions">
                  <a href="#register" className="btn">Respond</a>
                  <a href="#about" className="btn">Details</a>
                </div>
              </div>

              <Window title="STATUS.LCD" meta="rt-monitor // intrusion active" icon="▣" tone="alert">
                <div className="lcd">
                  <div className="lcd__row">
                    <span className="lcd__k">&gt; SYSTEM</span>
                    <span className="lcd__v">ONLINE</span>
                  </div>
                  <div className="lcd__row">
                    <span className="lcd__k">&gt; INTRUSION</span>
                    <span className="lcd__v alert">DETECTED</span>
                  </div>
                  <div className="lcd__row">
                    <span className="lcd__k">&gt; EVIDENCE</span>
                    <span className="lcd__v">0 / 29</span>
                  </div>
                  <div className="lcd__row">
                    <span className="lcd__k">&gt; ACTS UNLOCKED</span>
                    <span className="lcd__v">1 / 4</span>
                  </div>
                  <div className="lcd__row">
                    <span className="lcd__k">&gt; TEAM STATUS</span>
                    <span className="lcd__v amber">STANDBY</span>
                  </div>
                  <div className="progress">
                    <i />
                  </div>
                </div>
              </Window>
            </div>
          </div>
        </section>

        <div className="shell">
          <div className="hazard">
            <span>// FOR ALL TIMELINES // AUTHORIZED RESPONDERS ONLY // PRESERVE EVERY KEY //</span>
          </div>
        </div>

        <Marquee />

        {/* ===================== ABOUT ===================== */}
        <section id="about" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(01) Incident Brief</span>
                <h2>ABOUT.TXT</h2>
              </div>
              <span className="section-index">01 / 05</span>
            </Reveal>

            <Reveal className="about about__grid">
              <Window title="brief.log" meta="cleared">
                <div>
                  <p>
                    Every network has two realities: the trusted surface everyone
                    sees, and the hidden layer where abandoned systems, corrupted
                    logs, and <strong>impossible traffic</strong> tell the real
                    story.
                  </p>
                  <p>
                    Your response team will follow that trail across four acts —
                    from open-source traces to the network&apos;s buried
                    infrastructure — preserving every artifact until the final
                    transmission.
                  </p>
                </div>
              </Window>

              <div className="stats">
                <div className="stat">
                  <b>4</b>
                  <span>Narrative Acts</span>
                </div>
                <div className="stat">
                  <b>29</b>
                  <span>Public Cases</span>
                </div>
                <div className="stat">
                  <b>4,050</b>
                  <span>Total Points</span>
                </div>
                <div className="stat">
                  <b>1</b>
                  <span>Final Layer</span>
                </div>
              </div>
            </Reveal>
          </div>
        </section>

        {/* ===================== ACTS ===================== */}
        <section id="acts" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(02) Four Acts</span>
                <h2>The Investigation</h2>
              </div>
              <span className="section-index">02 / 05</span>
            </Reveal>
            <Reveal>
              <p className="sec__lead">
                Challenge names, point totals, and unlock thresholds are public.
                Flags and solution fragments stay{" "}
                <span className="classified">classified</span>.
              </p>
            </Reveal>

            <div className="acts__grid">
              {acts.map((act, i) => (
                <Reveal className="act" key={act.id} delay={i * 60}>
                  <Window
                    title={`${act.num} — ${act.track}`}
                    meta={`status: ${act.status} // ${act.cases} cases`}
                    icon="▤"
                  >
                    <div className="act__num">{act.track.toUpperCase()}</div>
                    <div className="act__title">{act.title}</div>
                    <div className="act__disc">&ldquo;{act.title}&rdquo;</div>
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

        {/* ===================== RULES ===================== */}
        <section id="rules" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(03) Rules of Engagement</span>
                <h2>Preserve the Evidence</h2>
              </div>
              <span className="section-index">03 / 05</span>
            </Reveal>
            <Reveal>
              <p className="sec__lead">
                This is an incident response operation, not a free-for-all.
                Follow the trail, respect the scope, and keep every recovered
                artifact until the final transmission tells you otherwise.
              </p>
            </Reveal>

            <div className="rules__grid">
              {rules.map((rule, i) => (
                <Reveal className="rule" key={rule.title} delay={i * 60}>
                  <div className="rule__n">
                    {String(i + 1).padStart(2, "0")}
                  </div>
                  <h3>{rule.title}</h3>
                  <p>{rule.body}</p>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* ===================== TIMELINE ===================== */}
        <section id="timeline" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(04) Operation Timeline</span>
                <h2>Event Timeline</h2>
              </div>
              <span className="section-index">04 / 05</span>
            </Reveal>

            <Reveal>
              <Window title="TIMELINE.LOG" meta="operation-2026 // 5 events" icon="◷">
                <TimelineWave items={timeline} />
              </Window>
            </Reveal>
          </div>
        </section>

        {/* ===================== SPONSORS ===================== */}
        <section id="sponsors" className="sec">
          <div className="shell">
            <Reveal className="sec__head">
              <div>
                <span className="eyebrow">(05) Backed By</span>
                <h2>Partners &amp; Sponsors</h2>
              </div>
              <span className="section-index">05 / 05</span>
            </Reveal>

            <Reveal>
              <div className="sponsors__grid">
                {sponsors.map((s) => (
                  <div className="sponsor" key={s}>
                    {s}
                    <small>PLACEHOLDER</small>
                  </div>
                ))}
                <div className="sponsor" style={{ color: "var(--w95-title)" }}>
                  + YOU?
                  <small>SLOT OPEN</small>
                </div>
              </div>
            </Reveal>

            <Reveal>
              <Window title="PARTNER_WITH_US.EXE" meta="run">
                <div className="partner">
                  <div>
                    <h3>Become a Partner</h3>
                    <p>
                      Put your brand in front of the region&apos;s sharpest
                      security talent. Let&apos;s build something together.
                    </p>
                  </div>
                  <a
                    href="mailto:sponsors@packetcapture.ctf"
                    className="btn btn--primary"
                  >
                    Get in Touch →
                  </a>
                </div>
              </Window>
            </Reveal>
          </div>
        </section>

        {/* ===================== REGISTER ===================== */}
        <section id="register" className="register">
          <div className="shell">
            <Reveal>
              <span className="eyebrow">REGISTER.EXE — Final Transmission</span>
              <h2>Join the Response?</h2>
              <p>
                The network is only the surface. Register your team, preserve
                every artifact, and wait for the final transmission.
              </p>
              <div className="reg-status">REGISTRATION OPENING SOON</div>
            </Reveal>
          </div>
        </section>
      </main>

      {/* ===================== FOOTER ===================== */}
      <footer className="footer">
        <div className="shell">
          <div className="footer__grid">
            <div>
              <div className="footer__logo">PACKET CAPTURE</div>
              <p
                style={{
                  color: "var(--ink-dim)",
                  fontSize: "0.95rem",
                  marginTop: "10px",
                  maxWidth: "36ch",
                  lineHeight: 1.5,
                }}
              >
                Beneath the Network. A cyber incident response CTF operation.
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
                  <a href="#timeline">Timeline</a>
                </li>
              </ul>
            </div>
            <div>
              <h4>Connect</h4>
              <ul>
                <li>
                  Discord <span className="footer__soon">(soon)</span>
                </li>
                <li>
                  Twitter / X <span className="footer__soon">(soon)</span>
                </li>
                <li>
                  GitHub <span className="footer__soon">(soon)</span>
                </li>
              </ul>
            </div>
            <div>
              <h4>Contact</h4>
              <ul>
                <li>
                  <a href="mailto:hello@packetcapture.ctf">
                    hello@packetcapture.ctf
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="footer__base">
            <span>© 2026 Packet Capture CTF — Beneath the Network</span>
            <span>// CHANNEL CLOSED</span>
          </div>
        </div>
      </footer>
    </>
  );
}
