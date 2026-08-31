export interface Room {
  id: number;
  household_id: number;
  name: string;
  color: string;
  display_order: number | null;
  is_active: boolean;
}

export interface RoomCreate {
  name: string;
  color?: string;
  display_order?: number | null;
}

export interface RoomUpdate {
  name?: string;
  color?: string;
  display_order?: number | null;
}