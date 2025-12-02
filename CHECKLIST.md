# ✅ Garden Platform - Week 1 Checklist

## 📋 Quick Execution Steps

### Phase 1: Deploy Code (15 mins)
- [ ] Run `./scripts/week1_deploy.sh` from project root
- [ ] Verify no errors in output
- [ ] Check all services are up: `docker compose ps`

### Phase 2: Test Onboarding (5 mins)
- [ ] Go to http://localhost
- [ ] Click "Begin Your Journey"
- [ ] Complete Welcome screen
- [ ] Complete Choose Path (select Personal/Emotional)
- [ ] Complete Create Profile (enter name)
- [ ] Complete Plant First Seed (choose a habit)
- [ ] See completion screen

### Phase 3: Test Backend (5 mins)
- [ ] Login at http://localhost
- [ ] Open browser DevTools (F12)
- [ ] Go to Application → Local Storage → Copy Auth0 token
- [ ] Test GDPR export:
  ```bash
  TOKEN="your_token"
  curl http://localhost:8000/api/v1/gdpr/export -H "Authorization: Bearer $TOKEN"
  ```
- [ ] Should return JSON with your data

### Phase 4: Sign Up for Services (10 mins)
- [ ] Create Cloudflare R2 account
- [ ] Create R2 bucket: `garden-videos-prod`
- [ ] Get R2 credentials (Access Key, Secret Key, Endpoint URL)
- [ ] Create Mux account
- [ ] Get Mux credentials (Token ID, Token Secret)
- [ ] Add all credentials to `backend/.env`
- [ ] Run `docker compose restart backend`

---

## 🎉 Week 1 Complete!

When all boxes are checked, you have:
- ✅ Working onboarding flow
- ✅ GDPR compliance
- ✅ Age verification
- ✅ Database schema for videos
- ✅ External services ready

**Next**: Build video features (Week 2-3)

---

## 🆘 Problems?

### Deployment failed?
→ Check `EXECUTE_NOW.md` Troubleshooting section

### Can't access http://localhost?
→ Run `docker compose logs frontend`

### Migration errors?
→ Run `docker compose logs backend`

### Need help?
→ Read `docs/WEEK_1_FOUNDATION_GUIDE.md`

---

**Start here**: `./scripts/week1_deploy.sh` 🚀
