# Garden - Personal Growth & Community Platform

A full-stack web application for personal growth tracking, community support, and AI-powered mentorship matching. Built with React, FastAPI, PostgreSQL, PyTorch, and Auth0.

## Architecture

```
Garden Platform
├── Frontend (React + Vite + Auth0)
├── Backend (FastAPI + PostgreSQL)
├── ML Service (PyTorch + scikit-learn)
└── Database (PostgreSQL 16)
```

## Features

### 🌱 My Garden
Track daily habits and personal growth goals with visual progress indicators.

### ✨ My Flourish
Community feed for sharing experiences, celebrating wins, and supporting others.

### 🌳 The Orchard
AI-powered matching to connect with mentors and peers on similar growth journeys.

### ☀️ Daily Nourishment
Receive daily inspirational quotes, prompts, and reflections curated by community guardians.

### 🌟 Share the Sunlight
Celebrate victories and positive moments with the community.

### 👥 Team Up
Collaborate on growth projects with others in the community.

## Tech Stack

**Frontend:**
- React 18 with Vite
- Auth0 React SDK (Universal Login)
- TailwindCSS
- Axios
- React Router v6
- Lucide React Icons

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy (ORM)
- Alembic (Migrations)
- PostgreSQL 16
- Auth0 JWT Validation (RS256)
- Pydantic v2

**ML Service:**
- PyTorch
- scikit-learn
- FastAPI
- Cosine similarity matching
- KMeans clustering

**Infrastructure:**
- Docker & Docker Compose
- Nginx (Production)
- PostgreSQL 16

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Auth0 account
- Make (optional, for shortcuts)

### 1. Clone & Setup

```bash
git clone <repository>
cd community-app
cp .env.example .env
```

### 2. Configure Auth0

Create an Auth0 application:

1. **Create API:**
   - Go to Auth0 Dashboard → APIs
   - Create API with identifier: `https://community.api`
   - Enable RS256 signing algorithm

2. **Create Application:**
   - Type: Single Page Application
   - Allowed Callback URLs: `http://localhost:3000, http://localhost`
   - Allowed Logout URLs: `http://localhost:3000, http://localhost`
   - Allowed Web Origins: `http://localhost:3000, http://localhost`

3. **Update .env:**
```env
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_API_AUDIENCE=https://community.api
ML_API_KEY=your-secure-key-here
```

4. **Update frontend/.env:**
```env
VITE_AUTH0_DOMAIN=your-tenant.us.auth0.com
VITE_AUTH0_CLIENT_ID=your-spa-client-id
VITE_AUTH0_AUDIENCE=https://community.api
VITE_API_URL=http://localhost:8000
```

### 3. Build & Run

```bash
# Using Make
make build
make up

# Or using Docker Compose directly
docker-compose build
docker-compose up -d
```

### 4. Initialize Database

```bash
# Run migrations
make migrate

# Seed initial data
make seed
```

### 5. Access Application

- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ML Service:** http://localhost:8001
- **ML Docs:** http://localhost:8001/docs

## Development

### Frontend Development

```bash
cd frontend
npm install
npm run dev  # Starts on port 3000
```

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### ML Service Development

```bash
cd ml
pip install -r requirements.txt

# Train clustering model
python training/train_clustering.py

# Start service
uvicorn service.main:app --port 8001 --reload
```

## Database Management

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
make migrate

# Seed data
make seed

# Database shell
make db-shell

# Reset database (CAUTION: Deletes all data)
docker-compose exec backend python reset_db.py
```

## API Documentation

### Authentication
All protected endpoints require `Authorization: Bearer <token>` header with Auth0 JWT.

### Key Endpoints

**Auth:**
- `GET /api/v1/auth/me` - Get current user

**Garden (Habits):**
- `GET /api/v1/garden/habits` - List habits
- `POST /api/v1/garden/habits` - Create habit
- `POST /api/v1/garden/habits/{id}/log` - Log completion

**Flourish (Posts):**
- `GET /api/v1/flourish/posts` - List posts
- `POST /api/v1/flourish/posts` - Create post
- `POST /api/v1/flourish/posts/{id}/react` - React to post

**Orchard (Connections):**
- `GET /api/v1/orchard/match` - Get ML-powered matches
- `POST /api/v1/orchard/connections` - Request connection
- `GET /api/v1/orchard/connections/{id}/messages` - Get messages

Full API documentation: http://localhost:8000/docs

## ML Service API

**Feature Extraction:**
```bash
POST /features/extract
{
  "user_id": "user_123",
  "habits": [{"name": "meditation", "category": "mindfulness", "frequency": "daily"}]
}
```

**Similarity Matching:**
```bash
POST /similarity
{
  "query_user": {...},
  "candidate_users": [...],
  "top_k": 10
}
```

**Clustering:**
```bash
POST /cluster/train
{
  "user_features": [...],
  "n_clusters": 8
}
```

## Make Commands

```bash
make help         # Show all commands
make build        # Build all images
make up           # Start services
make down         # Stop services
make logs         # View logs
make restart      # Restart all services
make migrate      # Run migrations
make seed         # Seed database
make clean        # Remove everything
make db-shell     # PostgreSQL shell
make backend-shell # Backend container shell
```

## Production Deployment

### Using Docker Compose

```bash
# Build and start production services
make prod-up

# Or manually
docker-compose -f docker-compose.prod.yml up -d --build
```

### Environment Variables (Production)

Create `.env` file with:
```env
POSTGRES_USER=garden_prod
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=garden_prod_db
AUTH0_DOMAIN=<your-domain>
AUTH0_API_AUDIENCE=https://community.api
ML_API_KEY=<strong-api-key>
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong ML_API_KEY
- [ ] Configure Auth0 production application
- [ ] Enable HTTPS (add SSL certificates to nginx)
- [ ] Restrict database access
- [ ] Enable CORS only for production domains
- [ ] Review and restrict Auth0 permissions
- [ ] Set up database backups
- [ ] Configure logging and monitoring

## Project Structure

```
community-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   └── schemas/        # Pydantic schemas
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Route pages
│   │   └── services/      # API client
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── ml/                     # ML service
│   ├── service/           # FastAPI ML API
│   ├── training/          # Training scripts
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml      # Development
├── docker-compose.prod.yml # Production
├── Makefile
└── README.md
```

## Testing

### Backend Tests
```bash
docker-compose exec backend pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Troubleshooting

### Database Connection Issues
```bash
# Check if postgres is healthy
docker-compose ps

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Auth0 Token Issues
- Verify AUTH0_DOMAIN and AUTH0_API_AUDIENCE match in backend and frontend
- Check Auth0 application settings allow your callback URLs
- Ensure API uses RS256 algorithm

### ML Service Issues
```bash
# Check ML service logs
docker-compose logs ml-service

# Retrain model
docker-compose exec ml-service python training/train_clustering.py
```

## License

MIT License

## Support

For issues and questions:
- Open an issue on GitHub
- Check documentation in component README files
- Review API docs at http://localhost:8000/docs
