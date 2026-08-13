import Link from "next/link";
import LoginForm from "../../components/auth/LoginForm";
import Reveal from "../../components/Reveal";
import Window from "../../components/Window";

export default function AdminLoginPage() {
  return (
    <main className="auth-page auth-page--admin">
      <div className="shell auth-page__shell">
        <Reveal className="auth-page__intro">
          <span className="eyebrow">ADMIN ACCESS.SYS</span>
          <h1 className="auth-title">
            Organizer
            <br />
            Control
            <br />
            <span className="glitch" data-text="Console">
              Console
            </span>
          </h1>
          <p>Restricted login for challenge makers and competition organizers.</p>
          <p className="auth-switch">
            Participant? <Link href="/participant/login">Open team login</Link>
          </p>
        </Reveal>

        <Reveal>
          <Window title="ADMIN.LOGIN" meta="organizer channel" tone="alert">
            <LoginForm portal="admin" />
          </Window>
        </Reveal>
      </div>
    </main>
  );
}
