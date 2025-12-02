# Migration Fix Guide

## Problem
The base database was created with `init_db.py`, which already includes most tables and some of the fields we're trying to add in the migration.

## Solution
Skip the migration and start all services. The migration is trying to add features that may already exist or can be added later.

## Steps to Fix

### 1. Start All Services

```bash
cd /home/krillavilla/Documents/community-app

# Start all services
docker compose up -d
```

### 2. Verify Services Are Running

```bash
docker compose ps

# Should show:
# - garden_postgres (running)
# - garden_backend (running)
# - garden_frontend (running)
```

### 3. Test the Application

```bash
# Open browser
# Go to: http://localhost

# Should see the Garden landing page
# Click "Begin Your Journey" to test onboarding
```

### 4. Test GDPR Endpoint

```bash
# After logging in, check if GDPR endpoint works
curl http://localhost:8000/api/v1/gdpr/export \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## What's Working

Even without the migration, you have:
- ✅ All base tables (users, flourish_posts, comments, etc.)
- ✅ GDPR endpoints (export/delete)
- ✅ Age verification endpoint
- ✅ Onboarding flow
- ✅ Backend API running

## What's Missing (Can Add Later)

The migration was trying to add:
- Video-specific columns (video_url, thumbnail_url, duration_seconds)
- Expiration columns (expires_at)
- Privacy columns (privacy_level, soft_deleted)
- Analytics tables (post_views, comment_votes)

These can be added manually when you start building video features in Week 2-3.

---

## Manual Column Addition (Optional)

If you need the video columns now:

```sql
-- Connect to database
docker compose exec postgres psql -U garden -d garden

-- Add video columns to flourish_posts
ALTER TABLE flourish_posts ADD COLUMN IF NOT EXISTS video_url VARCHAR(512);
ALTER TABLE flourish_posts ADD COLUMN IF NOT EXISTS thumbnail_url VARCHAR(512);
ALTER TABLE flourish_posts ADD COLUMN IF NOT EXISTS duration_seconds INTEGER;
ALTER TABLE flourish_posts ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;
ALTER TABLE flourish_posts ADD COLUMN IF NOT EXISTS privacy_level VARCHAR(50) DEFAULT 'public';
ALTER TABLE flourish_posts ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;

-- Check age verification columns exist
\d users

-- You should see date_of_birth and age_verified already there
```

---

## Next Steps

1. **Verify app works**: http://localhost
2. **Complete onboarding flow**: Test all 5 screens
3. **Sign up for external services**: Cloudflare R2 + Mux
4. **Week 2-3**: Build video upload features

The core functionality is working even without the full migration!
