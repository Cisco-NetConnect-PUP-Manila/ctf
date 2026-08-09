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

