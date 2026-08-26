export interface Category {
  id: number;
  name: string;
  icon: string;
  color: string;
  display_order: number | null;
  household_id: number | null;
  user_id: number | null;
  is_active: boolean;
}

export interface CategoryCreate {
  name: string;
  icon?: string;
  color?: string;
  display_order?: number | null;
}

export interface CategoryUpdate {
  name?: string;
  icon?: string;
  color?: string;
  display_order?: number | null;
}