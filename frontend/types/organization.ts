export interface Organization {
  id: number;
  name: string;
  created_at: string;
}

export interface Member {
  id: number;
  user_id: number;
  org_id: number;
  role: string;
  created_at: string;
  user_email: string;
  user_name: string;
}

export interface Invitation {
  id: number;
  org_id: number;
  email: string;
  role: string;
  token: string;
  status: string;
  expires_at: string | null;
  created_at: string;
}

export interface InviteRequest {
  email: string;
  role: 'owner' | 'admin' | 'member';
}

export interface UpdateMemberRoleRequest {
  role: 'owner' | 'admin' | 'member';
}

