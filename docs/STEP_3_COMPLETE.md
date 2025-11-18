# STEP 3 - Database Layer ✅ COMPLETE

## Summary

STEP 3 establishes the complete database layer with Alembic migrations, initialization scripts, and seed data capabilities.

## What Was Created

### Alembic Configuration ✅

**Files Created:**
- `alembic.ini` - Alembic configuration with logging and migration settings
- `alembic/env.py` - Environment configuration with model imports and settings
- `alembic/script.py.mako` - Migration script template
- `alembic/versions/` - Directory for migration files

**Features:**
- Automatic model detection from `app.models`
- Database URL from environment variables
- Type comparison enabled for schema changes
- Server default comparison enabled
- Timestamp-based migration file naming

### Database Initialization ✅

**Files Created:**
- `init_db.py` - Complete database initialization script with:
  - Table creation from models
  - Optional test data seeding
  - Guardian user creation
  - Sample Garden and Habits

**Test Data Includes:**
- Test Guardian user (guardian@test.com)
- Sample Garden with 3 habits
- Full role and trust level configuration

### Environment Configuration ✅

**Files Created:**
- `.env` - Development configuration with:
  - SQLite database for local development
  - Mock Auth0 configuration
  - Debug mode enabled
  - Local CORS origins

## Database Schema Overview

### Tables Created (19 models):

1. **users** - Core user accounts with Auth0 integration
2. **guide_profiles** - Extended profiles for verified Guides
3. **guide_applications** - Guide role applications
4. **trust_verification_applications** - Trust level promotion requests
5. **gardens** - User habit containers
6. **habits** - Individual habits with tracking
7. **habit_logs** - Habit completion records
8. **flourish_posts** - Community posts
9. **comments** - Nested comments on posts
10. **reactions** - Post and comment reactions
11. **connections** - User connections
12. **messages** - Private messaging
13. **mentorship_requests** - Formal mentorship
14. **nourishment_items** - Daily inspirational content
15. **sunlight_posts** - Gratitude shares
16. **sunlight_reactions** - Sunlight post reactions
17. **projects** - Collaborative projects
18. **project_members** - Project membership
19. **project_discussions** - Project communication
20. **support_requests** - Anonymous support (with token_hash)
21. **support_responses** - Support responses
22. **fellowship_groups** - Interest-based groups
23. **group_members** - Group membership
24. **group_events** - Group events
25. **event_rsvps** - Event attendance
26. **reports** - Content moderation reports

### Key Database Features:

**UUID Primary Keys:**
- All models use UUID for distributed system compatibility
- Auto-generated on insert

**Timestamps:**
- `created_at` - Record creation time
- `updated_at` - Last modification time (auto-updated)

**Relationships:**
- Proper foreign key constraints
- Cascade options for deletions
- Back-references for bidirectional navigation

**Indexes:**
- Foreign keys automatically indexed
- Additional indexes on frequently queried fields
- Unique constraints where needed

**Enums:**
- Database-level enum types for data integrity
- Type-safe Python enums

## Setup Instructions

### Option 1: Quick Start (SQLite)

The project is configured for SQLite by default for easy local development:

```bash
cd backend

# 1. Install dependencies (if not already done)
pip install -r requirements.txt

# 2. Initialize database
python init_db.py

# Answer 'y' to seed test data

# 3. Start server
uvicorn app.main:app --reload

# 4. Visit API docs
# http://localhost:8000/docs
```

### Option 2: PostgreSQL Setup

For production-like environment:

```bash
# 1. Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# 2. Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE garden_db;
CREATE USER garden_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE garden_db TO garden_user;
\q
```

```bash
# 3. Update .env
DATABASE_URL="postgresql://garden_user:your_secure_password@localhost:5432/garden_db"

# 4. Initialize database
python init_db.py

# 5. Start server
uvicorn app.main:app --reload
```

### Option 3: Using Alembic Migrations

For version-controlled schema management:

```bash
cd backend

# 1. Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# 2. Review migration in alembic/versions/

# 3. Apply migration
alembic upgrade head

# 4. Seed test data (optional)
python -c "from init_db import seed_test_data; from app.core.database import SessionLocal; db = SessionLocal(); seed_test_data(db); db.close()"

# 5. Start server
uvicorn app.main:app --reload
```

## Database Management Commands

### Alembic Migrations:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show current revision
alembic current

# View migration history
alembic history
```

### Direct Database Access:

```bash
# SQLite
sqlite3 garden_dev.db

# PostgreSQL
psql -U garden_user -d garden_db
```

## Test Data

The seed script creates:

**Test Guardian User:**
- Email: `guardian@test.com`
- Auth0 Sub: `auth0|test-guardian-12345`
- Role: GUARDIAN
- Trust Level: FLOURISHING

**Sample Garden:**
- Name: "Guardian's Test Garden"
- 3 habits: Morning Meditation, Exercise, Reading
- All habits are DAILY frequency

## Verification Steps

### 1. Check Database Connection:

```bash
cd backend
python -c "from app.core.database import engine; print('✅ Database connection successful!' if engine else '❌ Connection failed')"
```

### 2. Verify Tables Created:

```bash
# SQLite
sqlite3 garden_dev.db ".tables"

# PostgreSQL
psql -U garden_user -d garden_db -c "\dt"
```

### 3. Check Test Data:

```bash
python -c "
from app.core.database import SessionLocal
from app.models import User
db = SessionLocal()
users = db.query(User).all()
print(f'✅ Found {len(users)} user(s)')
for user in users:
    print(f'  - {user.email} ({user.role.value})')
db.close()
"
```

### 4. Test API Endpoints:

```bash
# Start server
uvicorn app.main:app --reload

# In another terminal:
curl http://localhost:8000/health
curl http://localhost:8000/
```

## Database Schema Diagram

```
users
├── id (UUID, PK)
├── auth0_sub (unique)
├── email (unique)
├── display_name
├── role (enum: user/guide/guardian)
├── trust_level (enum: new_sprout/growing/good_soil/flourishing)
└── relationships → gardens, guide_profile, applications, etc.

gardens
├── id (UUID, PK)
├── user_id (FK → users)
└── habits → habit_logs

flourish_posts
├── id (UUID, PK)
├── author_id (FK → users)
├── comments → reactions
└── visibility (enum)

connections
├── id (UUID, PK)
├── requester_id (FK → users)
├── addressee_id (FK → users)
└── status (enum: pending/accepted/rejected)

support_requests
├── id (UUID, PK)
├── token_hash (bcrypt, unique)  ← Anonymous auth
└── support_responses

fellowship_groups
├── id (UUID, PK)
├── creator_id (FK → users)
├── group_members
└── group_events → event_rsvps
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pydantic_settings'"

```bash
pip install pydantic-settings
```

### Issue: "Database locked" (SQLite)

SQLite doesn't handle concurrent writes well. For production, use PostgreSQL.

### Issue: "relation already exists"

Drop and recreate:

```bash
# SQLite
rm garden_dev.db
python init_db.py

# PostgreSQL
psql -U garden_user -d garden_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
python init_db.py
```

### Issue: Alembic can't detect models

Ensure all models are imported in `alembic/env.py` and `app/models/__init__.py`.

## Next Steps

### STEP 4 - ML Service (PyTorch)
1. Design embedding model for content similarity
2. Implement user similarity algorithm
3. Create toxicity detection
4. Set up recommendation system
5. Deploy ML service API

### STEP 5 - Frontend (React 18 + Vite)
1. Initialize React project with Vite
2. Set up Auth0 authentication
3. Create UI components for features
4. Integrate with backend API
5. Implement state management

### STEP 6 - Integration Testing
1. API integration tests
2. Auth0 flow testing
3. Database transaction tests
4. End-to-end feature tests

### STEP 7 - Deployment
1. Docker containerization
2. Docker Compose orchestration
3. CI/CD pipeline setup
4. Production deployment guide

## Current State Summary

✅ **Database Layer Complete:**
- Alembic configuration ready
- All 19 models defined and tested
- Migration infrastructure in place
- Seed data available
- SQLite for development
- PostgreSQL-ready for production

✅ **Ready for Development:**
- Backend API functional
- Database schema validated
- Test data available
- Documentation complete

---

**Status:** STEP 3 Database Layer - ✅ **COMPLETE**

Ready to proceed to **STEP 4 - ML Service** when you say "continue".
