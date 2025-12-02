# 🚀 Garden MVP - User Testing Deployment Guide

**Status**: Ready for real user testing  
**Philosophy**: Simple, stable, Garden-metaphor-only  
**Timeline**: Deploy in < 30 minutes

---

## 📋 What's Included in This MVP

### ✅ Core Features (Working Now)
- **Auth0 Login/Signup** - Users can create accounts
- **Post Creation** - Upload videos (stored in R2) or text posts
- **Chronological Feed** - Simple feed showing recent posts
- **Likes** - "Watering" posts (symbolic Garden metaphor)
- **Comments** - "Soil" with upvote/downvote
- **Follow/Unfollow** - Build connections
- **Profile Pages** - View user stats and posts
- **24-Hour Expiration** - Posts disappear after 24 hours
- **7-Day Comment Expiration** - Comments expire after 7 days
- **Privacy** - Public or friends-only posts

### ❌ NOT Included (Phase 2+)
- ❌ ML recommendations / For You Page algorithm
- ❌ Complex lifecycle states (sprouting, blooming, wilting)
- ❌ Reputation systems
- ❌ Multiple feed types
- ❌ Advanced privacy circles
- ❌ Climate tracking
- ❌ Mux video encoding (using direct MP4 for now)

---

## 🛠️ Setup Steps

### Step 1: Run Database Migration

```bash
# Stop services if running
docker compose down

# Run new migration
docker compose run --rm backend alembic upgrade head

# Restart services
docker compose up -d
```

**What this does**: Creates simplified MVP tables (posts, comments, likes, follows), removes complex Garden System tables.

---

### Step 2: Configure R2 Storage (Optional)

For video uploads, you need Cloudflare R2 storage. **If you skip this, videos will be stored locally (dev mode).**

#### Sign up for Cloudflare R2
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to R2 → Create bucket → Name: `garden-videos`
3. Get API credentials:
   - Go to R2 → Manage R2 API Tokens
   - Create API token with read/write access
   - Copy Access Key ID and Secret Access Key

#### Add R2 credentials to `.env`
```bash
# Add to backend/.env
R2_ACCESS_KEY_ID=your_access_key_here
R2_SECRET_ACCESS_KEY=your_secret_key_here
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET_NAME=garden-videos
```

#### Restart backend
```bash
docker compose restart backend
```

---

### Step 3: Set Up Nightly Expiration Worker

This worker runs nightly to soft-delete expired posts and comments.

#### Option A: Docker Cron (Recommended)

Create `docker-compose.worker.yml`:
```yaml
version: '3.8'

services:
  expiration-worker:
    build: ./backend
    container_name: garden_expiration_worker
    environment:
      DATABASE_URL: postgresql://garden:garden@postgres:5432/garden_db
    command: python -m app.workers.expiration_worker
    networks:
      - garden_network
    depends_on:
      - postgres

networks:
  garden_network:
    external: true
```

Add cron job on host machine:
```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 3am)
0 3 * * * cd /home/krillavilla/Documents/community-app && docker compose -f docker-compose.worker.yml run --rm expiration-worker >> /tmp/garden-expiration.log 2>&1
```

#### Option B: Manual Testing

Run worker manually to test:
```bash
docker compose run --rm backend python -m app.workers.expiration_worker
```

---

### Step 4: Test the MVP API

#### Check health
```bash
curl http://localhost:8000/health
```

#### Test MVP endpoints (requires Auth0 token)
```bash
# Get auth token from frontend or Auth0
TOKEN="your_auth0_token_here"

# Get feed
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/mvp/feed

# Create post
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -F "caption=My first Garden post!" \
  -F "is_public=true" \
  http://localhost:8000/api/v1/mvp/posts

# Like a post
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/mvp/posts/{post_id}/like
```

#### API Documentation
Visit http://localhost:8000/docs to see all MVP endpoints.

---

## 📱 Frontend Updates Needed

Your frontend needs to call the new MVP API endpoints. Update these files:

### 1. Create MVP API Service

Create `frontend/src/services/mvpAPI.js`:
```javascript
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
```

### 2. Update Feed Component

Simplify `frontend/src/components/feed/SwipeableFeed.jsx` or create `SimpleFeed.jsx`:
```jsx
import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { mvpAPI } from '../../services/mvpAPI';

export default function SimpleFeed() {
  const { getAccessTokenSilently } = useAuth0();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFeed();
  }, []);

  const loadFeed = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await mvpAPI.getFeed(token);
      setPosts(response.data.posts);
    } catch (error) {
      console.error('Error loading feed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (postId) => {
    try {
      const token = await getAccessTokenSilently();
      await mvpAPI.likePost(token, postId);
      // Refresh feed to show updated like count
      loadFeed();
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  if (loading) return <div>Loading feed...</div>;

  return (
    <div className="feed-container">
      {posts.map(post => (
        <div key={post.id} className="post-card">
          <div className="post-header">
            <span>{post.author_name}</span>
            <span className="time-remaining">{post.hours_remaining.toFixed(1)}h left</span>
          </div>
          
          {post.video_url && (
            <video controls src={post.video_url} className="post-video" />
          )}
          
          <p className="post-caption">{post.caption}</p>
          
          <div className="post-actions">
            <button 
              onClick={() => handleLike(post.id)}
              className={post.is_liked ? 'liked' : ''}
            >
              💧 {post.like_count}
            </button>
            <button>💬 {post.comment_count}</button>
            <button>👁️ {post.view_count}</button>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## 🧪 Testing with Real Users

### Pre-Launch Checklist
- [ ] Database migration completed
- [ ] R2 storage configured (or dev mode enabled)
- [ ] Nightly worker scheduled
- [ ] Frontend updated to use MVP API
- [ ] Auth0 configured and tested
- [ ] Tested post creation
- [ ] Tested feed loading
- [ ] Tested likes, comments, follows
- [ ] Verified 24hr expiration works

### Invite Test Users
1. Share your app URL (e.g., http://your-domain.com or localhost for local testing)
2. Users sign up via Auth0
3. Encourage users to:
   - Create posts (text or video)
   - Like and comment on posts
   - Follow other users
   - Check back after 24 hours to see posts expire

### Monitoring
```bash
# Watch backend logs
docker compose logs -f backend

# Check expiration worker logs
tail -f /tmp/garden-expiration.log

# View database stats
docker compose exec postgres psql -U garden -d garden_db -c "
SELECT 
  (SELECT COUNT(*) FROM posts WHERE soft_deleted = false) as active_posts,
  (SELECT COUNT(*) FROM comments WHERE soft_deleted = false) as active_comments,
  (SELECT COUNT(*) FROM users) as total_users,
  (SELECT COUNT(*) FROM follows) as total_follows;
"
```

---

## 🐛 Troubleshooting

### Issue: Posts not expiring
**Solution**: Check expiration worker is running
```bash
# Run manually to test
docker compose run --rm backend python -m app.workers.expiration_worker

# Check cron job
crontab -l
```

### Issue: Video uploads failing
**Solution**: Check R2 configuration
```bash
# Test R2 connection
docker compose exec backend python -c "
from app.services.r2_storage import R2StorageService
storage = R2StorageService()
print(f'R2 enabled: {storage.enabled}')
"
```

### Issue: Feed not loading
**Solution**: Check Auth0 token
- Verify token is being sent in Authorization header
- Check token hasn't expired
- Verify API audience matches Auth0 config

---

## 📊 What to Collect from Users

### Qualitative Feedback
- Is the onboarding clear?
- Do you understand the 24-hour expiration?
- Does the feed load fast enough?
- Is video upload intuitive?
- Any bugs or confusing behavior?

### Quantitative Metrics
- Daily active users
- Posts created per day
- Average likes per post
- Comments per post
- User retention (Day 1, Day 7)

### Questions to Answer
1. **Do users post more than once?** (validates engagement)
2. **Do users return after 24 hours?** (validates ephemeral model)
3. **Are comments helpful or toxic?** (validates soil metaphor)
4. **Do users follow each other?** (validates social aspect)

---

## 🎯 Next Steps After Testing

Based on user feedback, prioritize:

### Phase 2: If Users Love It
- Add video encoding (Mux)
- Improve video player
- Add notifications
- Build mobile app

### Phase 3: If Users Want Discovery
- Simple algorithm (engagement-based)
- Hashtag search
- Trending posts
- Suggested users to follow

### Phase 4: Bring Back Garden System (Selectively)
- Lifecycle states (if users want gamification)
- Reputation systems (if you need moderation)
- ML recommendations (if organic discovery isn't enough)
- Multiple feeds (if chronological isn't sufficient)

---

## 💡 Remember

**The Goal**: Validate that users want:
1. Ephemeral video sharing (24hr posts)
2. Lightweight social features (likes, comments, follows)
3. Simple chronological feed

**NOT**: To test complex lifecycle engines, ML algorithms, or advanced features.

**Ship this MVP → Collect real feedback → Iterate based on what users actually want.**

---

## 🚀 Ready to Deploy?

```bash
# 1. Migrate database
docker compose run --rm backend alembic upgrade head

# 2. Restart services
docker compose restart

# 3. Test endpoints
curl http://localhost:8000/docs

# 4. Invite test users!
```

**Good luck! 🌱**
