import Link from "next/link";
import Reveal from "../components/Reveal";
import Window from "../components/Window";

export default function RegisterPage() {
  return (
    <main className="auth-page auth-page--register">
      <div className="shell auth-page__shell auth-page__shell--single">
        <Reveal className="auth-page__intro">
          <span className="eyebrow">REGISTRATION.EXE // EXTERNAL CHANNEL</span>
          <h1 className="auth-title">
            Registration
            <br />
            <span className="glitch" data-text="External">
              External
            </span>
          </h1>
          <p>
            Participant registration is handled through the official registration
            portal. This site is for confirmed participant access only.
          </p>
          <p className="auth-intro-link">
            Already have credentials? <Link href="/login">Open participant access</Link>.
          </p>
        </Reveal>

        <Reveal>
          <Window title="REGISTRATION.ROUTE" meta="external organizer channel">
            <div className="registration-state registration-state--closed">
              <h2>Registration is handled elsewhere.</h2>
              <p>
                Solo participants and teams receive their access credentials through
                the official registration process. Organizer approval is required
                before challenge access opens.
              </p>
              <div className="registration-state__actions">
                <Link className="btn btn--primary" href="/login">
                  Sign in
                </Link>
                <Link className="btn" href="/#rules">
                  Read official rules
                </Link>
              </div>
            </div>
          </Window>
        </Reveal>
      </div>
    </main>
  );
}
