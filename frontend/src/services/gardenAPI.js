/**
 * Garden API Service
 * 
 * Handles all Garden System API calls.
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const gardenAPI = {
  // Feeds
  getFeed: async (feedType, skip = 0, limit = 20) => {
    const endpoints = {
      wild: '/gardens/wild',
      rows: '/gardens/rows',
      greenhouse: '/gardens/greenhouse'
    };
    const { data } = await api.get(endpoints[feedType], { params: { skip, limit } });
    return data;
  },
  
  // Seeds
  getSeed: async (seedId) => {
    const { data } = await api.get(`/seeds/${seedId}`);
    return data;
  },
  
  plantSeed: async (videoFile, content, privacyFence = 'public') => {
    const formData = new FormData();
    formData.append('file', videoFile);
    formData.append('content', content);
    formData.append('privacy_fence', privacyFence);
    
    const { data } = await api.post('/seeds', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return data;
  },
  
  waterSeed: async (seedId) => {
    const { data } = await api.post(`/seeds/${seedId}/water`);
    return data;
  },
  
  shineSunlight: async (seedId) => {
    const { data } = await api.post(`/seeds/${seedId}/sunlight`);
    return data;
  },
  
  // Soil (comments)
  getSoilForSeed: async (seedId, skip = 0, limit = 50) => {
    const { data } = await api.get(`/seeds/${seedId}/soil`, { params: { skip, limit } });
    return data;
  },
  
  addSoil: async (seedId, content) => {
    const { data } = await api.post(`/soil?seed_id=${seedId}`, { content });
    return data;
  },
  
  addNitrogen: async (soilId) => {
    const { data } = await api.post(`/soil/${soilId}/nitrogen`);
    return data;
  },
  
  addToxin: async (soilId) => {
    const { data } = await api.post(`/soil/${soilId}/toxin`);
    return data;
  },
  
  removeVote: async (soilId) => {
    const { data } = await api.delete(`/soil/${soilId}/vote`);
    return data;
  },
  
  // Vine
  getMyVine: async () => {
    const { data } = await api.get('/vines/me');
    return data;
  },
  
  getVine: async (vineId) => {
    const { data } = await api.get(`/vines/${vineId}`);
    return data;
  },
  
  // Search
  searchSeeds: async (query, skip = 0, limit = 20) => {
    const { data } = await api.get('/gardens/search', { params: { query, skip, limit } });
    return data;
  }
};
