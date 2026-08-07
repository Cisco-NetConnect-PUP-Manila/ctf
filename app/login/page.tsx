import LoginForm from "../components/auth/LoginForm";
import Reveal from "../components/Reveal";
import Window from "../components/Window";

export default function LoginPage() {
  return (
    <main className="auth-page">
      <div className="shell auth-page__shell">
        <Reveal className="auth-page__intro">
          <span className="eyebrow">TEAM ACCESS.EXE</span>
          <h1>Resume the investigation</h1>
          <p>
            Sign in with the shared team account to enter the competition platform.
          </p>
        </Reveal>

        <Reveal>
          <Window title="SESSION.LOGIN" meta="secure team channel">
            <LoginForm />
          </Window>
        </Reveal>
      </div>
    </main>
  );
}

