# Garden Platform - Backend API

Growth-oriented community platform backend built with FastAPI, SQLAlchemy, and Auth0.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python init_db.py

# 3. Start development server
uvicorn app.main:app --reload

# 4. Visit API documentation
# http://localhost:8000/docs
```

## Features

- ✅ **Auth0 JWT Authentication** - Secure RS256 token validation
- ✅ **10 Core Features** - Habits, social feed, mentorship, support groups, and more
- ✅ **19 Data Models** - Complete schema with relationships
- ✅ **RBAC** - Role-based access control (User/Guide/Guardian)
- ✅ **Trust System** - 4-level progression (New Sprout → Flourishing)
- ✅ **Anonymous Support** - Bcrypt token hashing for privacy
- ✅ **SQLite/PostgreSQL** - Flexible database options
- ✅ **Alembic Migrations** - Version-controlled schema management

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Alembic configuration
├── app/
│   ├── api/
│   │   ├── deps/        # Dependency injection (auth, db)
│   │   └── v1/          # API route modules
│   ├── core/            # Core configuration
│   │   ├── config.py    # Settings
│   │   ├── security.py  # Auth0 JWT validation
│   │   └── database.py  # SQLAlchemy setup
│   ├── models/          # SQLAlchemy models (19 models)
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic & ML client
│   └── main.py          # FastAPI application
├── init_db.py           # Database initialization
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── README.md            # This file
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL="sqlite:///./garden_dev.db"  # or PostgreSQL

# Auth0
AUTH0_DOMAIN="your-tenant.us.auth0.com"
AUTH0_API_AUDIENCE="https://api.your-app.com"

# ML Service
ML_SERVICE_URL="http://localhost:8001"
ML_API_KEY="your-ml-api-key"
```

## API Endpoints

### Authentication & Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update profile
- `GET /api/v1/users/{user_id}` - Get user public profile

### My Garden (Habit Tracking)
- `GET /api/v1/garden` - Get user's garden
- `POST /api/v1/garden/habits` - Create habit
- `PUT /api/v1/garden/habits/{id}` - Update habit
- `POST /api/v1/garden/habits/{id}/logs` - Log completion

### Health Checks
- `GET /` - Root health check
- `GET /health` - Detailed health status

**TODO:** Additional route modules for Flourish, Orchard, Nourishment, Sunlight, TeamUp, Support, Trust, Fellowship, and Guardians features.

## Database Management

### Initialize Database

```bash
# Create tables and seed test data
python init_db.py
```

### Alembic Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## Development

### Start Development Server

```bash
uvicorn app.main:app --reload
```

API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Test Data

Default test Guardian user:
- Email: `guardian@test.com`
- Auth0 Sub: `auth0|test-guardian-12345`
- Role: GUARDIAN
- Trust Level: FLOURISHING

## Data Models

### Core Models
- **User** - Auth0-integrated user accounts
- **Garden** - Habit tracking container
- **Habit** - Individual habits with categories
- **HabitLog** - Completion tracking

### Social Features
- **FlourishPost** - Community posts with visibility control
- **Comment** - Nested comments
- **Reaction** - Post/comment reactions
- **Connection** - User connections
- **Message** - Private messaging

### Mentorship
- **GuideProfile** - Verified Guide profiles
- **GuideApplication** - Guide role applications
- **MentorshipRequest** - Formal mentorship requests

### Community
- **FellowshipGroup** - Interest-based groups
- **GroupEvent** - Group events with RSVP
- **Project** - Collaborative projects
- **SupportRequest** - Anonymous support (token-based auth)

### Content
- **NourishmentItem** - Daily inspirational content
- **SunlightPost** - Gratitude shares
- **Report** - Content moderation

## Authentication

Uses Auth0 JWT (RS256) with JWKS caching:

1. Client obtains access token from Auth0
2. Client sends token in Authorization header: `Bearer <token>`
3. API validates token signature and claims
4. User is created on first login (get-or-create pattern)
5. Subsequent requests use existing user

## Trust Levels

Progressive trust system:
- **New Sprout** (default) - New users
- **Growing** - Active participation
- **Good Soil** - Consistent contributions (required for Guide applications)
- **Flourishing** - Exemplary community members

## RBAC

Three roles with escalating permissions:
- **User** - Standard access
- **Guide** - Mentorship features (requires Good Soil + Guardian approval)
- **Guardian** - Moderation and administration

## Deployment

See `../STEP_3_COMPLETE.md` for:
- PostgreSQL setup
- Production configuration
- Docker deployment (coming in STEP 7)

## Documentation

- **STEP_2_COMPLETE.md** - Backend architecture
- **STEP_3_COMPLETE.md** - Database setup
- **API Docs** - http://localhost:8000/docs

## License

[Your License Here]

## Support

For issues or questions, see project documentation or contact the development team.
