import axios from 'axios';
const API_BASE = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
// Auth header helper
const authHeader = (token) => ({ Authorization: `Bearer ${token}` });
export const mvpAPI = {
  // Feed
  getFeed: (token, skip = 0, limit = 20) =>
    axios.get(`${API_BASE}/mvp/feed?skip=${skip}&limit=${limit}`, {
      headers: authHeader(token)
    }),
  // Posts
  createPost: (token, caption, isPublic, videoFile) => {
    const formData = new FormData();
    formData.append('caption', caption);
    formData.append('is_public', isPublic);
    if (videoFile) formData.append('video_file', videoFile);

    return axios.post(`${API_BASE}/mvp/posts`, formData, {
      headers: { ...authHeader(token), 'Content-Type': 'multipart/form-data' }
    });
  },
  likePost: (token, postId) =>
    axios.post(`${API_BASE}/mvp/posts/${postId}/like`, {}, {
      headers: authHeader(token)
    }),
  trackView: (token, postId) =>
    axios.post(`${API_BASE}/mvp/posts/${postId}/view`, {}, {
      headers: authHeader(token)
    }),
  // Comments
  getComments: (token, postId) =>
    axios.get(`${API_BASE}/mvp/posts/${postId}/comments`, {
      headers: authHeader(token)
    }),
  addComment: (token, postId, content) => {
    const formData = new FormData();
    formData.append('content', content);
    return axios.post(`${API_BASE}/mvp/posts/${postId}/comments`, formData, {
      headers: authHeader(token)
    });
  },
  voteComment: (token, commentId, voteType) => {
    const formData = new FormData();
    formData.append('vote_type', voteType); // 'up', 'down', or 'remove'
    return axios.post(`${API_BASE}/mvp/comments/${commentId}/vote`, formData, {
      headers: authHeader(token)
    });
  },
  // Users
  followUser: (token, userId) =>
    axios.post(`${API_BASE}/mvp/users/${userId}/follow`, {}, {
      headers: authHeader(token)
    }),
  getProfile: (token, userId) =>
    axios.get(`${API_BASE}/mvp/users/${userId}/profile`, {
      headers: authHeader(token)
    }),
  getUserPosts: (token, userId, skip = 0, limit = 20) =>
    axios.get(`${API_BASE}/mvp/users/${userId}/posts?skip=${skip}&limit=${limit}`, {
      headers: authHeader(token)
    })
};
