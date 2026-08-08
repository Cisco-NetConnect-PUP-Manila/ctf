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

