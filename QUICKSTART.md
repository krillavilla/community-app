# 🚀 Garden Platform - Quick Start Guide

Get the Garden Platform running in under 5 minutes!

---

## ⚡ Prerequisites

- **Docker** & **Docker Compose** installed
- **Auth0 account** (free tier works)
- **Git** installed

---

## 📦 Installation

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd community-app
```

### 2. Configure Auth0

#### Create Auth0 Application
1. Go to [auth0.com](https://auth0.com) → Applications
2. Create new **Single Page Application**
3. Note: `Domain` and `Client ID`

#### Configure Settings
- **Allowed Callback URLs**: `http://localhost:5173, http://localhost`
- **Allowed Logout URLs**: `http://localhost:5173, http://localhost`
- **Allowed Web Origins**: `http://localhost:5173, http://localhost`

#### Create Auth0 API
1. Go to Applications → APIs
2. Create new API
3. **Identifier**: `https://api.garden-platform.com`
4. **Signing Algorithm**: RS256

### 3. Environment Variables

#### Backend (.env)
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```bash
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/garden_db
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=https://api.garden-platform.com
ML_SERVICE_URL=http://ml-service:8001
ML_API_KEY=dev-secret-key-change-in-production
DEBUG=true
LOG_LEVEL=debug
```

#### Frontend (.env)
```bash
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id-here
VITE_AUTH0_AUDIENCE=https://api.garden-platform.com
VITE_AUTH0_REDIRECT_URI=http://localhost:5173
```

### 4. Start Services
```bash
docker compose up -d
```

**Wait ~30 seconds** for ML models to download on first run.

### 5. Initialize Database
```bash
docker compose exec backend python init_db.py
```

---

## 🎯 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost | Main application |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **ML Service** | http://localhost:8001 | ML endpoints |
| **ML Docs** | http://localhost:8001/docs | ML API docs |

---

## 🧪 Verify Installation

### Test Backend
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Test ML Service
```bash
curl http://localhost:8001/health
# Expected: {"status":"healthy","model_loaded":true}
```

### Test Frontend
Open http://localhost in browser → Should see landing page

---

## 👤 First Login

1. Go to http://localhost
2. Click "Log In"
3. Auth0 Universal Login appears
4. Sign up or log in
5. Redirected to Dashboard

**Note**: First user is created automatically with `user` role.

---

## 🛠️ Common Commands

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f ml-service
docker compose logs -f frontend
```

### Restart Services
```bash
docker compose restart
```

### Stop Services
```bash
docker compose down
```

### Rebuild After Code Changes
```bash
docker compose up --build -d
```

### Run Database Migrations
```bash
docker compose exec backend alembic upgrade head
```

### Access Database
```bash
docker compose exec postgres psql -U postgres garden_db
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Common fixes:
# 1. Database not ready - wait 10 seconds, then restart
docker compose restart backend

# 2. Missing environment variables
cat backend/.env  # Verify all vars are set
```

### ML Service slow to start
```bash
# First run downloads ~90MB model - be patient
docker compose logs ml-service

# Should see: "Model loaded successfully"
```

### Frontend shows Auth0 errors
- Verify `frontend/.env` has correct Auth0 credentials
- Check Auth0 dashboard → Application → Settings
- Ensure callback URLs include `http://localhost:5173`

### Port conflicts
```bash
# If port 80, 8000, or 8001 is in use:
# Edit docker compose.yml and change port mappings
# Example: "8080:80" instead of "80:80"
```

---

## 📚 Next Steps

### Explore API Documentation
Visit http://localhost:8000/docs to see all available endpoints

### Run Tests
```bash
# Backend tests
cd backend
pytest --cov=app

# Frontend tests (when implemented)
cd frontend
npm test
```

### Development Mode (without Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### ML Service
```bash
cd ml-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8001 --reload
```

---

## 🎓 Learn More

- **Full Documentation**: `docs/PROJECT_COMPLETE.md`
- **Backend Details**: `docs/STEP_2_COMPLETE.md`
- **ML Service**: `docs/STEP_4_COMPLETE.md`
- **Frontend**: `docs/STEP_5_COMPLETE.md`
- **Deployment**: `docs/STEP_7_COMPLETE.md`

---

## 💡 Pro Tips

### 1. Create Guardian User (for support)
```bash
# In database
docker compose exec postgres psql -U postgres garden_db
UPDATE users SET role = 'guardian' WHERE email = 'your@email.com';
```

### 2. Add Test Data
```bash
# Run init_db.py multiple times for more seed data
docker compose exec backend python init_db.py
```

### 3. Monitor ML Service Performance
```bash
# Check ML service logs for processing times
docker compose logs ml-service | grep "Processing time"
```

### 4. Hot Reload in Development
- **Backend**: Already enabled with `--reload`
- **Frontend**: Vite dev server auto-reloads
- **Docker**: Mount volumes for hot reload (see `docker compose.override.yml`)

---

## 🆘 Get Help

### Check Status
```bash
docker compose ps
```

### Full Reset
```bash
# WARNING: Deletes all data!
docker compose down -v
docker compose up -d
docker compose exec backend python init_db.py
```

### Report Issues
- Check logs first: `docker compose logs`
- Review documentation: `docs/`
- Common issues: See Troubleshooting section above

---

## 🎉 You're Ready!

The Garden Platform is now running locally. Start exploring:

1. ✅ Create your first Garden
2. ✅ Add some Habits
3. ✅ Log habit completions
4. ✅ Explore the API at `/docs`
5. ✅ Check out ML recommendations

**Happy Growing!** 🌱
