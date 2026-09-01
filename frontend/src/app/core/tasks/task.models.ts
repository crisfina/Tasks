export type AssignmentMode =
  | 'none'
  | 'manual'
  | 'fixed'
  | 'alternating'
  | 'lowest_score'
  | 'random'
  | 'least_busy'
  | 'shortest_estimated_time';

export type Difficulty =
  | 'very_easy'
  | 'easy'
  | 'medium'
  | 'hard'
  | 'very_hard';

export type Priority =
  | 'very_low'
  | 'low'
  | 'medium'
  | 'high'
  | 'very_high';

export type Urgency =
  | 'very_low'
  | 'low'
  | 'medium'
  | 'high'
  | 'very_high';

export type Visibility = 'shared' | 'private' | 'hidden';

export type RepeatType =
  | 'daily'
  | 'weekly'
  | 'biweekly'
  | 'monthly'
  | 'semesterly'
  | 'twice_a_year'
  | 'yearly';

export interface Task {
  id: number;
  title: string;
  description: string | null;
  category_id: number | null;
  room_id: number | null;
  estimated_minutes: number | null;
  difficulty: Difficulty;
  priority: Priority;
  urgency: Urgency;
  repeat_type: RepeatType | null;
  repeat_interval: number | null;
  days_before_due: number | null;
  days_until_due: number | null;
  visibility: Visibility;
  household_id: number | null;
  assignment_mode: AssignmentMode | null;
  display_order: number | null;
  awards_points: boolean;
  created_by: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  category_id?: number | null;
  room_id?: number | null;
  estimated_minutes?: number | null;
  difficulty: Difficulty;
  priority: Priority;
  urgency: Urgency;
  repeat_type?: RepeatType | null;
  repeat_interval?: number | null;
  days_before_due?: number | null;
  days_until_due?: number | null;
  available_from?: string | null;
  visibility: Visibility;
  household_id?: number | null;
  assignment_mode?: AssignmentMode | null;
  display_order?: number | null;
  awards_points?: boolean;
  assigned_user_ids?: number[];
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  category_id?: number | null;
  room_id?: number | null;
  estimated_minutes?: number | null;
  difficulty?: Difficulty;
  priority?: Priority;
  urgency?: Urgency;
  repeat_type?: RepeatType | null;
  repeat_interval?: number | null;
  days_before_due?: number | null;
  days_until_due?: number | null;
  visibility?: Visibility;
  assignment_mode?: AssignmentMode | null;
  display_order?: number | null;
  awards_points?: boolean;
  assigned_user_ids?: number[];
}

export interface TaskOccurrence {
  id: number;
  task_id: number;
  assigned_user_id: number | null;
  available_from: string;
  due_date: string;
  notes: string | null;
  completed_at: string | null;
  completed_by_user_id: number | null;
  realized_minutes: number | null;
  awarded_points: number | null;
  created_at: string;
  updated_at: string;
}

export interface TaskOccurrenceCreate {
  assigned_user_id?: number | null;
  available_from: string;
  due_date: string;
  notes?: string | null;
}

export interface TaskOccurrenceUpdate {
  assigned_user_id?: number | null;
  available_from?: string;
  due_date?: string;
  notes?: string | null;
}

export interface TaskOccurrenceComplete {
  realized_minutes: number;
  notes?: string | null;
}