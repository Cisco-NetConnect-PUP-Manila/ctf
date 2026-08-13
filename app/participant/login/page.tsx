import Link from "next/link";
import LoginForm from "../../components/auth/LoginForm";
import Reveal from "../../components/Reveal";
import Window from "../../components/Window";

export default function ParticipantLoginPage() {
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
          <p>Sign in with the shared team account after organizer approval.</p>
          <p className="auth-switch">
            Organizer? <Link href="/admin/login">Open admin login</Link>
          </p>
        </Reveal>

        <Reveal>
          <Window title="TEAM.LOGIN" meta="participant channel">
            <LoginForm portal="participant" />
          </Window>
        </Reveal>
      </div>
    </main>
  );
}
