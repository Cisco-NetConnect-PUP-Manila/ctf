import LoginForm from "../components/auth/LoginForm";
import Reveal from "../components/Reveal";
import Window from "../components/Window";

export default function LoginPage() {
  return (
    <main className="auth-page">
      <div className="shell auth-page__shell">
        <Reveal className="auth-page__intro">
          <span className="eyebrow">SECURE ACCESS.EXE</span>
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
            Teams and organizers use the same secure account entry point. Your
            authenticated role determines which workspace opens.
          </p>
        </Reveal>

        <Reveal>
          <Window title="ACCOUNT.LOGIN" meta="role-aware channel">
            <LoginForm portal="auto" />
          </Window>
        </Reveal>
      </div>
    </main>
  );
}
