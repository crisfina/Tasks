export type HouseholdRole = 'owner' | 'manager' | 'member';

export interface Household {
  id: number;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface HouseholdCreate {
  name: string;
}

export interface HouseholdMember {
  household_id: number;
  user_id: number;
  role: HouseholdRole;
  joined_at: string;
}

export interface HouseholdInvitationCreate {
  role?: HouseholdRole;
}

export interface HouseholdInvitationCreated {
  id: number;
  household_id: number;
  created_by_user_id: number;
  accepted_by_user_id: number | null;
  role: HouseholdRole;
  expires_at: string;
  accepted_at: string | null;
  revoked_at: string | null;
  created_at: string;
  code: string;
}

export interface HouseholdInvitationAccept {
  code: string;
}