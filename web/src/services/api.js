import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => {
    // Convert to URLSearchParams for OAuth2 password flow
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    return api.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  },
  getProfile: () => api.get('/auth/me'),
};

// Analysis API
export const analysisAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/analysis/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getResult: (id) => api.get(`/analysis/results/${id}`),
  getHistory: () => api.get('/analysis/history'),
  deleteAnalysis: (id) => api.delete(`/analysis/results/${id}`),
};

export default api;