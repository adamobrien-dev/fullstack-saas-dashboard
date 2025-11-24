export interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  avatar_url?: string | null;
}

export interface LoginResponse {
  message: string;
  user: User;
}

