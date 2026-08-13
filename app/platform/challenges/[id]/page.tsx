import Link from "next/link";
import ParticipantSessionGuard from "../../../components/auth/ParticipantSessionGuard";
import ParticipantChallengeDetail from "../../../components/challenges/ParticipantChallengeDetail";

export default async function ParticipantChallengePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <ParticipantSessionGuard>
      <main className="portal-page">
        <section className="sec challenge-detail-page">
          <div className="shell">
            <ParticipantChallengeDetail challengeId={id} />
          </div>
        </section>
        <footer className="footer footer--portal">
          <div className="shell">
            <div className="footer__base">
              <span>Secured Challenge Channel</span>
              <Link href="/platform">Return to platform</Link>
            </div>
          </div>
        </footer>
      </main>
    </ParticipantSessionGuard>
  );
}
