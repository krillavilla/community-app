# 🚀 Execute Now - Complete Setup Guide

## ✅ What's Been Created

All code has been written for you! Here's what's ready:

### Backend Code ✅
- `/backend/app/services/gdpr_service.py` - GDPR data export/deletion
- `/backend/app/api/v1/endpoints/gdpr.py` - GDPR API endpoints
- `/backend/app/api/v1/users.py` - Age verification endpoint added
- `/backend/app/models/user.py` - Age & soft delete fields added
- `/backend/app/main.py` - GDPR routes registered
- `/backend/alembic/versions/001_add_video_and_gdpr_features.py` - Full migration

### Frontend Code ✅
- `/frontend/src/components/onboarding/CreateProfile.jsx` - Already exists
- `/frontend/src/components/onboarding/PlantFirstSeed.jsx` - Already exists
- `/frontend/src/components/onboarding/Complete.jsx` - Already exists
- `/frontend/src/App.jsx` - Routes already configured
- `/frontend/tailwind.config.js` - Already configured
- `/frontend/src/index.css` - Already configured

### Scripts ✅
- `/scripts/week1_deploy.sh` - Automated deployment

### Documentation ✅
- `/ONBOARDING_SETUP_GUIDE.md` - Frontend setup (root)
- `/docs/WEEK_1_FOUNDATION_GUIDE.md` - Backend setup
- `/docs/IMPLEMENTATION_ROADMAP.md` - Full roadmap

---

## 🎯 Quick Start (30 Minutes)

### Step 1: Deploy Frontend Onboarding (5 mins)

```bash
cd /home/krillavilla/Documents/community-app/frontend

# Rebuild frontend
docker compose down frontend
docker compose build --no-cache frontend
docker compose up -d frontend
```

**Test it:**
- Go to http://localhost
- Click "Begin Your Journey"
- Complete all 5 screens
- Should end at Dashboard

---

### Step 2: Deploy Backend Foundation (10 mins)

```bash
cd /home/krillavilla/Documents/community-app

# Make script executable
chmod +x scripts/week1_deploy.sh

# Run automated deployment
./scripts/week1_deploy.sh
```

**What this does:**
1. Rebuilds backend container
2. Runs database migration
3. Restarts all services
4. Tests health check

---

### Step 3: Verify Everything Works (5 mins)

#### Test 1: Check Migration

```bash
# Verify new tables exist
docker compose exec postgres psql -U garden_user -d garden_db -c "\dt"

# You should see: post_views, comment_votes, privacy_circles, direct_messages
```

#### Test 2: Test GDPR Export

```bash
# 1. Login at http://localhost
# 2. Get your Auth0 token from browser DevTools (Application → Local Storage)
# 3. Run:

TOKEN="YOUR_TOKEN_HERE"
curl -X GET http://localhost:8000/api/v1/gdpr/export \
  -H "Authorization: Bearer $TOKEN"

# Should return JSON with your user data
```

#### Test 3: Test Age Verification

```bash
curl -X POST http://localhost:8000/api/v1/users/me/verify-age \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date_of_birth": "1990-01-01"}'

# Should return: {"message": "Age verified successfully", "is_minor": false, "age_verified": true}
```

---

## 🎥 Next: Sign Up for External Services (10 mins)

### Cloudflare R2 (Video Storage)

1. Go to https://dash.cloudflare.com
2. Navigate to **R2 Object Storage**
3. Click **Create bucket** → Name it `garden-videos-prod`
4. Go to **R2 → Settings → API Tokens**
5. Click **Create API Token**
6. Copy these values:
   - Access Key ID
   - Secret Access Key
   - Endpoint URL (format: `https://[account-id].r2.cloudflarestorage.com`)

### Mux (Video Encoding)

1. Go to https://mux.com
2. Sign up for free account
3. Go to **Settings → Access Tokens**
4. Click **Generate new token**
5. Copy:
   - Token ID
   - Token Secret

### Update Environment Variables

Add to `/backend/.env`:

```bash
# Cloudflare R2
R2_ACCESS_KEY_ID=your_r2_access_key_here
R2_SECRET_ACCESS_KEY=your_r2_secret_key_here
R2_ENDPOINT_URL=https://your_account_id.r2.cloudflarestorage.com
R2_BUCKET_NAME=garden-videos-prod
R2_PUBLIC_URL=https://your_bucket.r2.dev

# Mux Video
MUX_TOKEN_ID=your_mux_token_id_here
MUX_TOKEN_SECRET=your_mux_token_secret_here
```

Then restart backend:

```bash
docker compose restart backend
```

---

## 📊 What You've Accomplished

### ✅ Week 1 Complete
- [x] Onboarding flow (5 screens, mobile-responsive)
- [x] Database schema updated (video, expiration, GDPR)
- [x] GDPR compliance (export & delete endpoints)
- [x] Age verification (13+ minimum, COPPA compliant)
- [x] User model updated (age, soft delete)
- [x] External services ready (R2, Mux accounts)

### 🎯 Ready for Week 2-3: Video Core

You now have:
- Working onboarding user flow ✅
- Legal compliance foundation ✅
- Database schema for videos ✅
- Storage accounts ready ✅

**Next**: Build video upload, player, and swipeable feed (see Week 2-3 guide)

---

## 🐛 Troubleshooting

### Frontend not loading?

```bash
# Check logs
docker compose logs frontend --tail=50

# Rebuild
docker compose down frontend
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Backend errors?

```bash
# Check logs
docker compose logs backend --tail=50

# Check if migration ran
docker compose exec backend alembic current

# Re-run migration
docker compose run --rm backend alembic upgrade head
```

### Database connection issues?

```bash
# Restart postgres
docker compose restart postgres

# Check if it's running
docker compose ps postgres
```

### Can't login?

Check Auth0 environment variables in:
- `frontend/.env` (VITE_AUTH0_DOMAIN, VITE_AUTH0_CLIENT_ID)
- `backend/.env` (AUTH0_DOMAIN, AUTH0_API_AUDIENCE)

---

## 📈 Cost Estimate (MVP Testing)

**For 100 test users, 1000 videos:**
- Cloudflare R2: ~$5-10/month
- Mux encoding: ~$10-15/month (1000 mins)
- Auth0: Free (up to 7,000 users)
- Hosting: $0 (existing Docker setup)

**Total: ~$15-25/month** during testing phase

---

## 🎉 Success Criteria

You've completed Week 1 if:
- ✅ Onboarding flow works end-to-end
- ✅ Database migration successful
- ✅ GDPR endpoints return data
- ✅ Age verification works
- ✅ R2 and Mux accounts created
- ✅ All services running without errors

---

## 📚 Documentation Reference

- **Architecture Plan**: See Warp notebook "Garden Social Video Platform"
- **Week 1 Details**: `docs/WEEK_1_FOUNDATION_GUIDE.md`
- **Week 2-3 Preview**: Video upload, player, swipeable feed
- **Full Roadmap**: `docs/IMPLEMENTATION_ROADMAP.md`

---

## 🚀 What's Next?

### Week 2-3: Video Core (coming soon)

You'll build:
1. Video upload endpoint (multipart upload to R2)
2. Mux transcoding integration
3. Video.js player component
4. Swiper.js swipeable feed
5. Basic feed algorithm (chronological)

This will take 16-24 hours over 2-3 weeks.

---

**Ready to launch?** Run `./scripts/week1_deploy.sh` and start testing! 🌱
