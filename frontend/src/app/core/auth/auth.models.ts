export interface LoginRequest {
  identifier: string;
  password: string;
  remember_me: boolean;
}

export interface TokenRead {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  color?: string | null;
  avatar_url?: string | null;
}

export type UserRole = 'admin' | 'user';

export interface UserRead {
  id: number;
  username: string;
  email: string;
  color: string | null;
  avatar_url: string | null;
  is_active: boolean;
  role: UserRole;
  created_at: string;
  updated_at: string;
}