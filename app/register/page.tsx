import RegistrationForm from "../components/auth/RegistrationForm";
import Reveal from "../components/Reveal";
import Window from "../components/Window";

export default function RegisterPage() {
  return (
    <main className="auth-page auth-page--register">
      <div className="shell auth-page__shell">
        <Reveal className="auth-page__intro">
          <span className="eyebrow">TEAM REGISTRATION.EXE</span>
          <h1 className="auth-title">
            Assemble
            <br />
            The Response
            <br />
            <span className="glitch" data-text="Team">
              Team
            </span>
          </h1>
          <p>
            Create one shared account for your group. The team login email must belong to the listed team leader.
          </p>
        </Reveal>

        <Reveal>
          <Window title="REGISTRATION.FORM" meta="4–5 members // one shared account">
            <RegistrationForm />
          </Window>
        </Reveal>
      </div>
    </main>
  );
}
