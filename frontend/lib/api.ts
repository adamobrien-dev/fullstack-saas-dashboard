import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Important: sends cookies automatically
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth API calls
export const authApi = {
  register: async (email: string, name: string, password: string) => {
    const response = await api.post('/auth/register', { email, name, password });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  refreshToken: async () => {
    const response = await api.post('/auth/refresh');
    return response.data;
  },

  requestPasswordReset: async (email: string) => {
    const trimmedEmail = email.trim();
    const response = await api.post('/auth/password-reset-request', { email: trimmedEmail });
    return response.data;
  },

  resetPassword: async (token: string, newPassword: string) => {
    const response = await api.post('/auth/password-reset', {
      token,
      new_password: newPassword,
    });
    return response.data;
  },

  updateProfile: async (name?: string, email?: string) => {
    const payload: any = {};
    if (name !== undefined) payload.name = name;
    if (email !== undefined) payload.email = email;
    const response = await api.patch('/auth/profile', payload);
    return response.data;
  },

  uploadAvatar: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/auth/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  changePassword: async (currentPassword: string, newPassword: string) => {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

// Organization API calls
export const orgApi = {
  create: async (name: string) => {
    const response = await api.post('/orgs', { name });
    return response.data;
  },

  listMine: async () => {
    const response = await api.get('/orgs/mine');
    return response.data;
  },

  invite: async (orgId: number, email: string, role: string) => {
    const response = await api.post(`/orgs/${orgId}/invite`, { email, role });
    return response.data;
  },

  listPendingInvitations: async () => {
    const response = await api.get('/orgs/invitations/pending');
    return response.data;
  },

  acceptInvite: async (token: string) => {
    const response = await api.post('/orgs/accept', { token });
    return response.data;
  },

  listMembers: async (orgId: number) => {
    const response = await api.get(`/orgs/${orgId}/members`);
    return response.data;
  },

  updateMemberRole: async (orgId: number, userId: number, role: string) => {
    const response = await api.patch(`/orgs/${orgId}/members/${userId}`, { role });
    return response.data;
  },

  removeMember: async (orgId: number, userId: number) => {
    const response = await api.delete(`/orgs/${orgId}/members/${userId}`);
    return response.data;
  },
};

// Analytics API calls
export const analyticsApi = {
  getDashboard: async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  },

  getUserStats: async () => {
    const response = await api.get('/analytics/users/stats');
    return response.data;
  },

  getUserGrowth: async (days: number = 30) => {
    const response = await api.get(`/analytics/users/growth?days=${days}`);
    return response.data;
  },

  getActivityStats: async () => {
    const response = await api.get('/analytics/activities/stats');
    return response.data;
  },

  getActivityTimeline: async (days: number = 30, period: 'day' | 'week' | 'month' = 'day') => {
    const response = await api.get(`/analytics/activities/timeline?days=${days}&period=${period}`);
    return response.data;
  },

  getOrganizationStats: async () => {
    const response = await api.get('/analytics/organizations/stats');
    return response.data;
  },
};

// Activity Log API calls
export const activityApi = {
  /**
   * Get activity logs with filtering and pagination.
   * Users can only see their own logs or logs from organizations they belong to.
   */
  getLogs: async (filters?: {
    page?: number;
    page_size?: number;
    user_id?: number;
    action?: string;
    resource_type?: string;
    organization_id?: number;
  }) => {
    const params = new URLSearchParams();
    if (filters) {
      if (filters.page !== undefined) params.append('page', filters.page.toString());
      if (filters.page_size !== undefined) params.append('page_size', filters.page_size.toString());
      if (filters.user_id !== undefined) params.append('user_id', filters.user_id.toString());
      if (filters.action) params.append('action', filters.action);
      if (filters.resource_type) params.append('resource_type', filters.resource_type);
      if (filters.organization_id !== undefined) params.append('organization_id', filters.organization_id.toString());
    }
    const response = await api.get(`/activity/logs?${params.toString()}`);
    return response.data;
  },

  /**
   * Get activity logs for the current user only.
   */
  getMyLogs: async (page?: number, page_size?: number, action?: string) => {
    const params = new URLSearchParams();
    if (page !== undefined) params.append('page', page.toString());
    if (page_size !== undefined) params.append('page_size', page_size.toString());
    if (action) params.append('action', action);
    const response = await api.get(`/activity/logs/me?${params.toString()}`);
    return response.data;
  },

  /**
   * Get activity logs for a specific organization.
   * Requires membership in the organization.
   */
  getOrgLogs: async (
    orgId: number,
    filters?: {
      page?: number;
      page_size?: number;
      user_id?: number;
      action?: string;
    }
  ) => {
    const params = new URLSearchParams();
    if (filters) {
      if (filters.page !== undefined) params.append('page', filters.page.toString());
      if (filters.page_size !== undefined) params.append('page_size', filters.page_size.toString());
      if (filters.user_id !== undefined) params.append('user_id', filters.user_id.toString());
      if (filters.action) params.append('action', filters.action);
    }
    const response = await api.get(`/activity/logs/org/${orgId}?${params.toString()}`);
    return response.data;
  },

  /**
   * Get a specific activity log by ID.
   * User must have access to it (own log or member of organization).
   */
  getLog: async (logId: number) => {
    const response = await api.get(`/activity/logs/${logId}`);
    return response.data;
  },
};

