# 🚀 START HERE - MVP User Testing

**Goal**: Ship a working Garden MVP to real users in under 1 hour.

---

## ⚡ Quick Deploy (5 minutes)

```bash
# Run this one command to deploy everything:
./deploy_mvp.sh
```

**Done!** API is now running at http://localhost:8000

---

## ✅ What Just Happened

The deploy script:
1. ✅ Ran database migration (created MVP tables)
2. ✅ Started all services (backend, frontend, database)
3. ✅ Verified backend health

---

## 🎯 What's Working Now

### Backend (Complete ✅)
- Auth0 authentication
- POST /mvp/posts - Upload videos or text
- GET /mvp/feed - Chronological feed
- POST /mvp/posts/{id}/like - Like posts
- POST /mvp/posts/{id}/comments - Comment
- POST /mvp/comments/{id}/vote - Upvote/downvote
- POST /mvp/users/{id}/follow - Follow users
- GET /mvp/users/{id}/profile - User profiles
- Nightly expiration worker (posts: 24hrs, comments: 7 days)

### Frontend (Your Work 🔨)
Templates provided in `MVP_DEPLOYMENT_GUIDE.md`:
- MVP API service (complete code example)
- Simple feed component (copy-paste ready)
- Video upload pattern
- Profile page pattern

---

## 📋 Your Next Steps

### 1. Test the Backend API (2 minutes)
```bash
# Open API docs
open http://localhost:8000/docs

# Or test manually
curl http://localhost:8000/health
```

### 2. Update Frontend (30 minutes)
Follow the code examples in `MVP_DEPLOYMENT_GUIDE.md`:
- Create `frontend/src/services/mvpAPI.js` (full code provided)
- Update or create simple feed component (example provided)
- Update video upload to use `/mvp/posts`
- Add comment UI
- Test with Auth0 login

### 3. (Optional) Configure R2 Storage (10 minutes)
For video uploads:
```bash
# Add to backend/.env
R2_ACCESS_KEY_ID=your_key_here
R2_SECRET_ACCESS_KEY=your_secret_here
R2_ENDPOINT_URL=https://your-account.r2.cloudflarestorage.com
R2_BUCKET_NAME=garden-videos

# Restart backend
docker compose restart backend
```

**Without R2**: Videos save to `/tmp` (dev mode) - fine for testing!

### 4. Schedule Nightly Worker (5 minutes)
```bash
crontab -e

# Add this line (runs at 3am daily):
0 3 * * * cd /home/krillavilla/Documents/community-app && docker compose run --rm backend python -m app.workers.expiration_worker >> /tmp/garden-expiration.log 2>&1
```

### 5. Invite Test Users! (10 minutes)
1. Share your app URL
2. Users sign up via Auth0
3. They create posts, like, comment, follow
4. Check back in 24hrs to see posts expire

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **MVP_START_HERE.md** (this file) | Quick reference |
| **MVP_DEPLOYMENT_GUIDE.md** | Full deployment instructions + frontend code examples |
| **MVP_SUMMARY.md** | What was built, technical details |
| **deploy_mvp.sh** | One-command deployment script |

---

## 🎯 Garden Metaphor (Simplified)

For this MVP, the Garden System is **symbolic only**:

- 🌱 **Seeds** = Posts (expire in 24 hours)
- 💧 **Watering** = Likes (symbolic name only)
- 🌿 **Soil** = Comments (expire in 7 days)
- ⏰ **Expiration** = Fixed timeouts (no extensions yet)

**Phase 2+**: Add lifecycle states, reputation, ML recommendations, etc. (after user testing)

---

## ❓ FAQ

### Q: Do I need to configure R2 now?
**A**: No! Videos save locally in dev mode. Add R2 when ready for real users.

### Q: What about Mux video encoding?
**A**: Not in MVP. Direct MP4 upload only. Add Mux in Phase 2 if users want better video quality.

### Q: Where are the complex Garden System features?
**A**: Removed for MVP. Will add back selectively based on user feedback.

### Q: Can I still use the old Garden System code?
**A**: Yes! It's still in git history. The migration can be reversed.

### Q: How do I test the expiration worker?
**A**: Run manually:
```bash
docker compose run --rm backend python -m app.workers.expiration_worker
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Common fix: restart
docker compose restart backend
```

### Migration fails
```bash
# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d
docker compose run --rm backend alembic upgrade head
```

### Feed returns empty
- Check Auth0 token is valid
- Verify users have created posts
- Check database: `docker compose exec postgres psql -U garden -d garden_db -c "SELECT COUNT(*) FROM posts WHERE soft_deleted = false;"`

---

## 🎯 Success Criteria

Before inviting users, verify:
- [ ] Can sign up via Auth0
- [ ] Can create post (text or video)
- [ ] Feed loads with posts
- [ ] Can like a post
- [ ] Can comment on a post
- [ ] Can follow another user
- [ ] Can view user profile
- [ ] Posts expire after 24 hours (test by manually running worker)

---

## 🚀 Ready to Ship?

```bash
# 1. Deploy (if you haven't already)
./deploy_mvp.sh

# 2. Update frontend with MVP API
# See MVP_DEPLOYMENT_GUIDE.md for code templates

# 3. Test everything works

# 4. Invite 5-10 test users

# 5. Collect feedback (see MVP_DEPLOYMENT_GUIDE.md for questions to ask)

# 6. Iterate based on what users actually want!
```

---

**Good luck! 🌱**

Need help? Check `MVP_DEPLOYMENT_GUIDE.md` for detailed instructions and troubleshooting.
