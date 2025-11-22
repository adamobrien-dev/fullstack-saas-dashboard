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
};

