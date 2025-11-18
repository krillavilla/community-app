/**
 * API Service for Garden Platform
 * 
 * Handles all HTTP requests to backend with Auth0 token integration.
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Store token setter function (will be set by Auth0Provider wrapper)
let getAccessToken = null;

export const setTokenGetter = (getter) => {
  getAccessToken = getter;
};

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    if (getAccessToken) {
      try {
        const token = await getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (error) {
        console.error('Error getting access token:', error);
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // TODO: Trigger re-authentication
      console.error('Unauthorized - redirecting to login');
    }
    return Promise.reject(error);
  }
);

// User API
export const userApi = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data) => api.put('/users/me', data),
  getUser: (userId) => api.get(`/users/${userId}`),
};

// Garden API
export const gardenApi = {
  getGarden: () => api.get('/garden'),
  createHabit: (data) => api.post('/garden/habits', data),
  getHabit: (habitId) => api.get(`/garden/habits/${habitId}`),
  updateHabit: (habitId, data) => api.put(`/garden/habits/${habitId}`, data),
  deleteHabit: (habitId) => api.delete(`/garden/habits/${habitId}`),
  logHabit: (habitId, data) => api.post(`/garden/habits/${habitId}/logs`, data),
};

// TODO: Add APIs for other features
// - Flourish Feed
// - The Orchard
// - Daily Nourishment
// - Share the Sunlight
// - Team Up
// - Anonymous Support
// - Trust System
// - Fellowship Groups

export default api;
