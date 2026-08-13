import ParticipantSessionGuard from "../../components/auth/ParticipantSessionGuard";
import ParticipantPendingNotice from "../../components/auth/ParticipantPendingNotice";

export default function ParticipantPendingPage() {
  return (
    <ParticipantSessionGuard allowPending>
      <ParticipantPendingNotice />
    </ParticipantSessionGuard>
  );
}
