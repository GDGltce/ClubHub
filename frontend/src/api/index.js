import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const path = err.config?.url || '';
    const isAuthCall = path.includes('/auth/login') || path.includes('/auth/register') || path.includes('/auth/refresh');
    if (err.response?.status === 401 && !err.config._retry && !isAuthCall) {
      err.config._retry = true;
      try {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) throw new Error('No refresh token');
        const { data } = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refresh });
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        err.config.headers.Authorization = `Bearer ${data.access_token}`;
        return api(err.config);
      } catch {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(err);
  }
);

// ── Auth ───────────────────────────────────────────────────────
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login:    (data) => api.post('/auth/login', data),
  refresh:  (data) => api.post('/auth/refresh', data),
  me:       ()     => api.get('/auth/me'),
};

// ── Institutions ───────────────────────────────────────────────
export const institutionApi = {
  listColleges:     ()           => api.get('/institutions/colleges'),
  getCollege:       (id)         => api.get(`/institutions/colleges/${id}`),
  createCollege:    (data)       => api.post('/institutions/colleges', data),
  listDepartments:  (collegeId)  => api.get(`/institutions/colleges/${collegeId}/departments`),
};

// ── Clubs ──────────────────────────────────────────────────────
export const clubApi = {
  list:    (params) => api.get('/clubs', { params }),
  get:     (id)     => api.get(`/clubs/${id}`),
  create:  (data)   => api.post('/clubs', data),
  update:  (id, data) => api.patch(`/clubs/${id}`, data),
  approve: (id)     => api.patch(`/clubs/${id}/approve`),
};

// ── Memberships ────────────────────────────────────────────────
export const membershipApi = {
  submitJoinRequest: (data)       => api.post('/memberships/join-requests', data),
  getJoinRequests:   (clubId)     => api.get(`/memberships/join-requests/club/${clubId}`),
  reviewRequest:     (id, data)   => api.patch(`/memberships/join-requests/${id}/review`, data),
};

// ── Events ─────────────────────────────────────────────────────
export const eventApi = {
  list:         (params) => api.get('/events', { params }),
  get:          (id)     => api.get(`/events/${id}`),
  create:       (data)   => api.post('/events', data),
  update:       (id, data) => api.patch(`/events/${id}`, data),
  advanceStage: (id, data) => api.post(`/events/${id}/advance-stage`, data),
};

// ── Documents ──────────────────────────────────────────────────
export const documentApi = {
  upload:         (data)   => api.post('/documents', data),
  listByClub:     (clubId) => api.get(`/documents/club/${clubId}`),
  approve:        (id)     => api.patch(`/documents/${id}/approve`),
};

// ── Meetings ───────────────────────────────────────────────────
export const meetingApi = {
  listByClub:   (clubId)   => api.get(`/meetings/club/${clubId}`),
  create:       (data)     => api.post('/meetings', data),
  updateMinutes:(id, data) => api.patch(`/meetings/${id}/minutes`, data),
};

// ── Notifications ──────────────────────────────────────────────
export const notificationApi = {
  list:     ()   => api.get('/notifications'),
  markRead: (id) => api.patch(`/notifications/${id}/read`),
};

// ── Users (Admin) ──────────────────────────────────────────────
export const userApi = {
  list:   (params) => api.get('/users', { params }),
  get:    (id)     => api.get(`/users/${id}`),
  update: (id, data) => api.patch(`/users/${id}`, data),
};

export default api;
