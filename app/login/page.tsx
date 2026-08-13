import Link from "next/link";
import Reveal from "../components/Reveal";
import Window from "../components/Window";

export default function LoginPage() {
  return (
    <main className="auth-page">
      <div className="shell auth-page__shell">
        <Reveal className="auth-page__intro">
          <span className="eyebrow">TEAM ACCESS.EXE</span>
          <h1 className="auth-title">
            Resume
            <br />
            The
            <br />
            <span className="glitch" data-text="Investigation">
              Investigation
            </span>
          </h1>
          <p>
            Choose the correct access channel. Team login is the main participant
            path; organizer access is kept separate for admins.
          </p>
        </Reveal>

        <Reveal>
          <Window title="ACCESS.ROUTER" meta="select channel">
            <div className="login-router">
              <Link className="login-router__primary" href="/participant/login">
                <span className="eyebrow">PARTICIPANT CHANNEL</span>
                <strong>Team Login</strong>
                <small>Use the shared team email after organizer approval.</small>
              </Link>

              <div className="login-router__secondary">
                <span>Organizer access</span>
                <Link href="/admin/login">Admin login</Link>
              </div>
            </div>
          </Window>
        </Reveal>
      </div>
    </main>
  );
}
