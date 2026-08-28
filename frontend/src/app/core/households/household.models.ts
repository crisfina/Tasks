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
  role: string;
  joined_at: string;
}