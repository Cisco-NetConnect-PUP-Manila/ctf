export type TeamMemberInput = {
  full_name: string;
  email: string;
};

export type RegisterInput = {
  group_name: string;
  email: string;
  password: string;
  members: TeamMemberInput[];
};

export type LoginInput = {
  email: string;
  password: string;
};

export type Account = {
  id: string;
  email: string;
  role: string;
  status: string;
};

export type TeamMember = TeamMemberInput & {
  id: string;
  is_leader: boolean;
};

export type Team = {
  id: string;
  group_name: string;
  status: string;
  members: TeamMember[];
};

export type AdminTeamMember = TeamMember;

export type AdminTeam = {
  id: string;
  group_name: string;
  status: string;
  email: string;
  member_count: number;
  members: AdminTeamMember[];
  approved_at: string | null;
  rejected_at: string | null;
  rejection_reason: string | null;
  created_at: string;
};

export type CurrentAccount = {
  account: Account;
  team: Team | null;
};

export type FieldErrors = Record<string, string>;

// Shared pagination envelope, mirrors backend app/schemas/common.py Page.
export type Page<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
};

export type AnnouncementStatus = "draft" | "published" | "archived";

// Participant-facing shape (matches backend AnnouncementResponse exactly).
export type Announcement = {
  id: string;
  title: string;
  body: string;
  published_at: string | null;
};

// Full admin shape (matches backend AnnouncementAdminResponse).
export type AdminAnnouncement = Announcement & {
  status: AnnouncementStatus;
  created_by_account_id: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type AnnouncementInput = {
  title: string;
  body: string;
};

export type ParticipantAct = {
  id: string;
  act_number: number;
  slug: string;
  title: string;
  description: string | null;
  unlocked: boolean;
  total_points: number;
  earned_points: number;
  required_points: number;
};

export type ParticipantChallenge = {
  id: string;
  act_id: string;
  act_number: number;
  title: string;
  slug: string;
  category: string | null;
  difficulty: string | null;
  points: number;
  mission_brief: string;
  story_context: string | null;
  objectives: string[];
  locked: boolean;
  solved: boolean;
  awarded_points: number | null;
  team_fragment: string | null;
};

export type ActChallengeGroup = {
  act: ParticipantAct;
  challenges: ParticipantChallenge[];
};

export type ParticipantChallengeList = {
  acts: ActChallengeGroup[];
  current_act: number;
  current_score: number;
};

export type AdminAct = {
  id: string;
  act_number: number;
  slug: string;
  title: string;
  description: string | null;
  unlock_threshold_points: number | null;
  unlock_threshold_percent: number;
  sort_order: number;
  is_active: boolean;
};

export type ChallengeLookup = {
  id: string;
  name: string;
  slug: string;
  sort_order: number;
  is_active: boolean;
};

export type ChallengeStatus = "draft" | "ready_for_review" | "published" | "archived";

export type ChallengeFile = {
  id: string;
  challenge_id: string;
  display_name: string;
  original_filename: string;
  extension: string;
  content_type: string | null;
  size_bytes: number;
  is_active: boolean;
};

export type AdminChallenge = {
  id: string;
  act_id: string;
  act_number: number;
  title: string;
  slug: string;
  mission_brief: string;
  story_context: string | null;
  objectives: string[];
  points: number;
  status: ChallengeStatus;
  is_visible: boolean;
  story_fragment: string | null;
  sort_order: number;
  category: ChallengeLookup | null;
  difficulty: ChallengeLookup | null;
  active_flag_count: number;
  active_file_count: number;
};

export type AdminChallengeInput = {
  act_id: string;
  title: string;
  slug: string;
  mission_brief: string;
  story_context: string | null;
  objectives: string[];
  points: number;
  category_id: string | null;
  difficulty_id: string | null;
  story_fragment: string | null;
  sort_order: number;
  is_visible: boolean;
};

export type ChallengeFlag = {
  id: string;
  challenge_id: string;
  label: string | null;
  validator_type: string;
  is_active: boolean;
};

export type UnlockedAct = {
  id: string;
  act_number: number;
  slug: string;
  title: string;
};

export type FlagSubmissionResult = {
  correct: boolean;
  awarded_points: number;
  current_score: number;
  solved: boolean;
  message: string;
  next_act_unlocked: UnlockedAct | null;
  team_fragment: string | null;
};

export type AdminSubmissionMonitorRow = {
  challenge_id: string;
  challenge_title: string;
  team_id: string;
  team_name: string;
  solved_at: string | null;
  correct_attempts: number;
  incorrect_attempts: number;
  first_attempt_at: string | null;
  last_attempt_at: string | null;
  first_correct_at: string | null;
  seconds_to_solve: number | null;
  shared_ip_hash_team_count: number;
  shared_user_agent_hash_team_count: number;
  rapid_solve: boolean;
  suspicious_notes: string[];
};

export type AdminSubmissionMonitorResponse = {
  rows: AdminSubmissionMonitorRow[];
};

export type CompetitionStatus = "upcoming" | "live" | "paused" | "ended";

export type PlatformSettings = {
  registration_open: boolean;
  submissions_open: boolean;
  competition_status: CompetitionStatus;
  leaderboard_visible: boolean;
};

export type PlatformSettingsUpdate = Partial<PlatformSettings>;

export type AdminLeaderboardRow = {
  rank: number;
  team_id: string;
  team_name: string;
  team_status: string;
  member_count: number;
  score: number;
  current_act: number;
  solves: number;
  attempts: number;
  incorrect_attempts: number;
  last_solve_at: string | null;
};

export type AdminLeaderboardResponse = {
  rows: AdminLeaderboardRow[];
};

