export interface ActivityLog {
  id: number;
  user_id: number | null;
  action: string;
  resource_type: string | null;
  resource_id: number | null;
  organization_id: number | null;
  details: Record<string, any> | null;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string; // ISO datetime string
  user_name?: string | null;
  organization_name?: string | null;
}

export interface ActivityLogList {
  logs: ActivityLog[];
  total: number;
  page: number;
  page_size: number;
}

export interface ActivityLogFilters {
  page?: number;
  page_size?: number;
  user_id?: number;
  action?: string;
  resource_type?: string;
  organization_id?: number;
}

