import LoginForm from "../components/auth/LoginForm";
import Reveal from "../components/Reveal";
import Window from "../components/Window";

export default function LoginPage() {
  return (
    <main className="auth-page">
      <div className="shell auth-page__shell">
        <Reveal className="auth-page__intro">
          <span className="eyebrow">TEAM ACCESS.EXE</span>
          <h1 className="auth-title">
            Access
            <br />
            The
            <br />
            <span className="glitch" data-text="Platform">
              Platform
            </span>
          </h1>
          <p>
            Use your approved team account to enter the competition, or register
            your team if this is your first time joining.
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
