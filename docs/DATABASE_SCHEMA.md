# Database Schema Design

**Purpose**: Production database schema for Community App  
**Scope**: PostgreSQL schema, Alembic migrations, SQLAlchemy models  
**Status**: Production-Ready  
**Last Updated**: 2025-11-17

---

## Table of Contents

1. [Entity Relationship Diagram](#entity-relationship-diagram)
2. [Table Definitions](#table-definitions)
3. [Indexes and Constraints](#indexes-and-constraints)
4. [Sample SQL](#sample-sql)
5. [SQLAlchemy Models](#sqlalchemy-models)
6. [Alembic Migration Strategy](#alembic-migration-strategy)
7. [Design Rationale](#design-rationale)

---

## Entity Relationship Diagram

### Users and Related Domain

```
┌───────────────┐      1 ── 1      ┌──────────────────────┐
│ users         │──────────────────▶│ user_profiles        │
│ auth0_sub* PK │                   │ user_id (PK=FK)      │
│ email         │                   │ display_name         │
│ created_at    │                   │ bio                  │
└───────┬───────┘                   │ journaling_frequency │
        │1                          │ updated_at           │
        │                           └──────────┬───────────┘
        │1 ─── n                             1 │
        │                                      │
        │                                     n│ ─── m
┌───────▼────────┐       n ─── m     ┌────────▼──────────┐
│ stories        │◀─────────────────▶│ tags              │
│ id (PK)        │         ▲         │ id (PK)           │
│ user_id (FK)   │         │         │ name (unique)     │
│ title          │   ┌─────┴────────┐│ created_at        │
│ content        │   │ user_tags    │└───────────────────┘
│ visibility     │   │ (user_id,    │
│ created_at     │   │  tag_id) PK  │
│ updated_at     │   └──────────────┘
└────────────────┘
        │1
        │
┌───────▼────────┐
│ habits         │
│ id (PK)        │
│ user_id (FK)   │
│ name           │
│ frequency      │
│ meta (JSONB)   │
│ created_at     │
└────────────────┘
```

### Matching and Features

```
┌──────────────────────┐      ┌───────────────────────┐
│ user_features        │      │ match_results         │
│ user_id (PK=FK)      │      │ id (PK)               │
│ vector (JSONB)       │      │ user_id (FK)          │
│ version              │      │ target_user_id (FK)   │
│ updated_at           │      │ score                 │
└──────────────────────┘      │ created_at            │
                              └───────────────────────┘
```

### Gardens Metaphor

```
┌──────────────────┐
│ gardens          │
│ id (PK)          │
│ user_id (FK)     │ (one primary garden per user, enforce unique)
│ name             │
│ theme            │
│ created_at       │
└──────────────────┘
```

---

## Table Definitions

### users

Core user authentication table. Primary key is Auth0 `sub` claim.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `auth0_sub` | VARCHAR(64) | PRIMARY KEY | Auth0 subject identifier (e.g., "auth0\|abc123") |
| `email` | CITEXT | UNIQUE NOT NULL | User email (case-insensitive) |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | Account creation timestamp |

**Indexes**:
- PRIMARY KEY on `auth0_sub`
- UNIQUE INDEX on `email`

**Reasoning**:
- `auth0_sub` as PK eliminates need for local user ID mapping
- `CITEXT` for case-insensitive email comparison
- Minimal columns (profile data in separate table)

---

### user_profiles

Extended user profile information (1-to-1 with users).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | VARCHAR(64) | PRIMARY KEY, FOREIGN KEY → users(auth0_sub) ON DELETE CASCADE | References auth0_sub |
| `display_name` | VARCHAR(80) | NULL | Public display name |
| `bio` | TEXT | NULL | User bio/description |
| `journaling_frequency` | INTEGER | CHECK (journaling_frequency >= 0) | Frequency metric (0-7 for weekly) |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() | Last profile update |

**Indexes**:
- PRIMARY KEY on `user_id`

**Reasoning**:
- 1-to-1 relationship keeps auth table lean
- `account_age_days` computed application-side (created_at → days)
- Supports future expansion without altering users table

---

### tags

Global tag taxonomy for categorizing stories and user interests.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Auto-incrementing tag ID |
| `name` | VARCHAR(64) | UNIQUE NOT NULL | Tag name (e.g., "growth", "meditation") |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | Tag creation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `name`

**Reasoning**:
- Shared tag vocabulary prevents duplication
- Can be seeded with common tags
- Future: add `category`, `popularity_score`

---

### user_tags

Many-to-many junction table between users and tags.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | VARCHAR(64) | FOREIGN KEY → users(auth0_sub) ON DELETE CASCADE | User reference |
| `tag_id` | BIGINT | FOREIGN KEY → tags(id) ON DELETE CASCADE | Tag reference |

**Indexes**:
- PRIMARY KEY on `(user_id, tag_id)` (composite)
- INDEX on `tag_id` (for reverse lookups)

**Reasoning**:
- Supports efficient tag-based matching
- Cascade delete ensures cleanup
- Index on tag_id enables "find users with tag X" queries

---

### stories

User-generated stories with visibility controls.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Auto-incrementing story ID |
| `user_id` | VARCHAR(64) | FOREIGN KEY → users(auth0_sub) ON DELETE CASCADE | Story author |
| `title` | VARCHAR(140) | NOT NULL | Story title (Twitter-length) |
| `content` | TEXT | NOT NULL | Story content (Markdown-friendly) |
| `visibility` | VARCHAR(16) | DEFAULT 'private', CHECK (visibility IN ('private','public','friends')) | Access control |
| `tags_cached` | VARCHAR[] | NULL | Denormalized tag names for search |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | Story creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() | Last edit timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `(user_id, created_at DESC)` (user's stories chronological)
- INDEX on `visibility` (filter public stories)

**Reasoning**:
- `tags_cached` denormalization improves search performance
- Visibility enum supports future "friends" feature
- 140-char title encourages conciseness

---

### habits

User habits for tracking and matching.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Auto-incrementing habit ID |
| `user_id` | VARCHAR(64) | FOREIGN KEY → users(auth0_sub) ON DELETE CASCADE | Habit owner |
| `name` | VARCHAR(80) | NOT NULL | Habit name (e.g., "Meditate daily") |
| `frequency` | VARCHAR(24) | CHECK (frequency IN ('daily','weekly','monthly','custom')) | Recurrence pattern |
| `meta` | JSONB | DEFAULT '{}'::jsonb | Extensible metadata (e.g., {"minutes": 10}) |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | Habit creation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `(user_id, name)` (prevent duplicate habit names per user)

**Reasoning**:
- `meta` JSONB allows flexible storage without schema changes
- UNIQUE constraint prevents accidental duplicates
- Frequency enum supports common patterns

---

### gardens

User's virtual garden (one per user for MVP).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Auto-incrementing garden ID |
| `user_id` | VARCHAR(64) | FOREIGN KEY → users(auth0_sub) ON DELETE CASCADE, UNIQUE | Garden owner |
| `name` | VARCHAR(80) | NOT NULL | Garden name (e.g., "My Growth Garden") |
| `theme` | VARCHAR(40) | NULL | Visual theme (e.g., "vineyard", "zen") |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | Garden creation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `user_id` (one garden per user)

**Reasoning**:
- UNIQUE on user_id enforces "my garden" metaphor for MVP
- Future: remove unique constraint for multiple gardens
- Theme supports frontend customization

---

### user_features

ML feature vectors for matching (JSONB for MVP, pgvector later).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | VARCHAR(64) | PRIMARY KEY, FOREIGN KEY → users(auth0_sub) ON DELETE CASCADE | User reference |
| `vector` | JSONB | NOT NULL | Feature vector as JSON array [0.1, 0.5, ...] |
| `version` | INTEGER | DEFAULT 1 | Schema version for migrations |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() | Last feature recalculation |

**Indexes**:
- PRIMARY KEY on `user_id`
- INDEX on `updated_at` (find stale features)

**Reasoning**:
- JSONB vector for simplicity (Phase 1)
- Future: migrate to pgvector extension for efficient similarity search
- Version field supports feature schema evolution

---

### match_results

Cached matching results for performance.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Auto-incrementing result ID |
| `user_id` | VARCHAR(64) | FOREIGN KEY → users(auth0_sub) ON DELETE CASCADE | Requesting user |
| `target_user_id` | VARCHAR(64) | FOREIGN KEY → users(auth0_sub) ON DELETE CASCADE | Matched user |
| `score` | DOUBLE PRECISION | NOT NULL | Similarity score (0.0-1.0) |
| `created_at` | TIMESTAMPTZ | DEFAULT now() | Match calculation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `(user_id, target_user_id, created_at)` (dedupe per batch)
- INDEX on `(user_id, score DESC)` (top matches query)

**Reasoning**:
- Caching reduces ML service load
- Composite unique index prevents duplicate entries per run
- Score index enables efficient "top N matches" queries

---

## Indexes and Constraints

### Primary Keys
All tables have single-column PKs except:
- `user_tags`: Composite PK `(user_id, tag_id)`

### Foreign Keys
All FKs use `ON DELETE CASCADE` for automatic cleanup:
- `user_profiles.user_id` → `users.auth0_sub`
- `user_tags.user_id` → `users.auth0_sub`
- `user_tags.tag_id` → `tags.id`
- `stories.user_id` → `users.auth0_sub`
- `habits.user_id` → `users.auth0_sub`
- `gardens.user_id` → `users.auth0_sub`
- `user_features.user_id` → `users.auth0_sub`
- `match_results.user_id` → `users.auth0_sub`
- `match_results.target_user_id` → `users.auth0_sub`

### Unique Constraints
- `users.email`
- `tags.name`
- `habits(user_id, name)` (composite)
- `gardens.user_id`
- `match_results(user_id, target_user_id, created_at)` (composite)

### Check Constraints
- `user_profiles.journaling_frequency >= 0`
- `stories.visibility IN ('private','public','friends')`
- `habits.frequency IN ('daily','weekly','monthly','custom')`

### Performance Indexes
- `stories(user_id, created_at DESC)` - User's stories chronological
- `stories.visibility` - Filter public stories
- `user_tags.tag_id` - Reverse tag lookups
- `match_results(user_id, score DESC)` - Top matches
- `user_features.updated_at` - Find stale features

---

## Sample SQL

### Create Users and Profiles

```sql
-- Enable citext extension for case-insensitive text
CREATE EXTENSION IF NOT EXISTS citext;

-- Users table
CREATE TABLE users (
  auth0_sub VARCHAR(64) PRIMARY KEY,
  email CITEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_users_email ON users(email);

-- User profiles table
CREATE TABLE user_profiles (
  user_id VARCHAR(64) PRIMARY KEY REFERENCES users(auth0_sub) ON DELETE CASCADE,
  display_name VARCHAR(80),
  bio TEXT,
  journaling_frequency INTEGER CHECK (journaling_frequency >= 0),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### Create Tags and User Tags

```sql
-- Tags table
CREATE TABLE tags (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(64) UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- User tags junction table
CREATE TABLE user_tags (
  user_id VARCHAR(64) REFERENCES users(auth0_sub) ON DELETE CASCADE,
  tag_id BIGINT REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, tag_id)
);

CREATE INDEX idx_user_tags_tag_id ON user_tags(tag_id);
```

### Create Stories

```sql
CREATE TABLE stories (
  id BIGSERIAL PRIMARY KEY,
  user_id VARCHAR(64) REFERENCES users(auth0_sub) ON DELETE CASCADE,
  title VARCHAR(140) NOT NULL,
  content TEXT NOT NULL,
  visibility VARCHAR(16) DEFAULT 'private' CHECK (visibility IN ('private','public','friends')),
  tags_cached VARCHAR[],
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_stories_user_created ON stories(user_id, created_at DESC);
CREATE INDEX idx_stories_visibility ON stories(visibility);
```

### Create Habits

```sql
CREATE TABLE habits (
  id BIGSERIAL PRIMARY KEY,
  user_id VARCHAR(64) REFERENCES users(auth0_sub) ON DELETE CASCADE,
  name VARCHAR(80) NOT NULL,
  frequency VARCHAR(24) CHECK (frequency IN ('daily','weekly','monthly','custom')),
  meta JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (user_id, name)
);
```

### Create Gardens

```sql
CREATE TABLE gardens (
  id BIGSERIAL PRIMARY KEY,
  user_id VARCHAR(64) UNIQUE REFERENCES users(auth0_sub) ON DELETE CASCADE,
  name VARCHAR(80) NOT NULL,
  theme VARCHAR(40),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### Create ML Tables

```sql
-- User features
CREATE TABLE user_features (
  user_id VARCHAR(64) PRIMARY KEY REFERENCES users(auth0_sub) ON DELETE CASCADE,
  vector JSONB NOT NULL,
  version INTEGER DEFAULT 1,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_user_features_updated ON user_features(updated_at);

-- Match results
CREATE TABLE match_results (
  id BIGSERIAL PRIMARY KEY,
  user_id VARCHAR(64) REFERENCES users(auth0_sub) ON DELETE CASCADE,
  target_user_id VARCHAR(64) REFERENCES users(auth0_sub) ON DELETE CASCADE,
  score DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (user_id, target_user_id, created_at)
);

CREATE INDEX idx_match_results_user_score ON match_results(user_id, score DESC);
```

---

## SQLAlchemy Models

### User Model (`backend/app/models/user.py`)

```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    auth0_sub = Column(String(64), primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    garden = relationship("Garden", back_populates="user", uselist=False, cascade="all, delete-orphan")
    features = relationship("UserFeature", back_populates="user", uselist=False, cascade="all, delete-orphan")
```

### UserProfile Model (`backend/app/models/user_profile.py`)

```python
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    user_id = Column(String(64), ForeignKey("users.auth0_sub", ondelete="CASCADE"), primary_key=True)
    display_name = Column(String(80))
    bio = Column(Text)
    journaling_frequency = Column(Integer, CheckConstraint("journaling_frequency >= 0"))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")
```

### Additional Models (Stubs)

```python
# backend/app/models/tag.py
class Tag(Base):
    __tablename__ = "tags"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# backend/app/models/story.py
class Story(Base):
    __tablename__ = "stories"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String(64), ForeignKey("users.auth0_sub", ondelete="CASCADE"))
    title = Column(String(140), nullable=False)
    content = Column(Text, nullable=False)
    visibility = Column(String(16), default="private")
    # ... (see sample SQL for full schema)
```

---

## Alembic Migration Strategy

### Phase 1: Initialize Alembic

```bash
cd backend
alembic init app/db/migrations
```

**Configure `alembic.ini`**:
```ini
sqlalchemy.url = postgresql+psycopg://community:community@localhost:5432/community
```

**Configure `app/db/migrations/env.py`**:
```python
from app.db.base import Base
from app.models.user import User
from app.models.user_profile import UserProfile
# Import all models

target_metadata = Base.metadata
```

### Phase 2: Create Migrations

**First Migration** (users + profiles):
```bash
alembic revision -m "init users and profiles"
# Edit versions/*.py to create users, user_profiles tables
alembic upgrade head
```

**Second Migration** (content tables):
```bash
alembic revision -m "add stories habits gardens"
# Add tags, user_tags, stories, habits, gardens tables
alembic upgrade head
```

**Third Migration** (ML tables):
```bash
alembic revision -m "add ml features and results"
# Add user_features, match_results tables
alembic upgrade head
```

### Migration Best Practices

- Use SQLAlchemy 2.0 typed declarative mappings
- Include both `upgrade()` and `downgrade()` functions
- Test migrations in dev before prod
- Backup database before running migrations
- Use `alembic stamp head` for existing databases

---

## Design Rationale

### Why Auth0 Sub as Primary Key?

**Pros**:
- No local user ID mapping complexity
- Direct JWT sub → database lookup
- Simplifies auth flow
- Auth0 sub is immutable

**Cons**:
- VARCHAR(64) slightly larger than INTEGER
- Foreign keys are strings

**Decision**: Benefits outweigh costs for MVP. Can migrate later if needed.

### Why JSONB for Vectors?

**Pros**:
- Simple to implement (no extensions)
- Flexible schema
- PostgreSQL JSONB is performant

**Cons**:
- Not optimized for vector operations
- No built-in similarity search

**Decision**: Use JSONB for MVP, migrate to pgvector in Phase 5.

### Why Denormalize tags_cached?

**Pros**:
- Faster full-text search
- Avoid JOIN on stories queries
- PostgreSQL array types are efficient

**Cons**:
- Data duplication
- Must keep in sync

**Decision**: Denormalize for read performance. Update via trigger or application logic.

### Why UNIQUE Constraint on gardens.user_id?

**Pros**:
- Enforces "my garden" metaphor for MVP
- Simpler UX (one garden)
- Easier to reason about

**Cons**:
- Limits future extensibility

**Decision**: Use UNIQUE for MVP, remove constraint when multiple gardens feature ships.

---

## Acceptance Criteria

✅ ERD covers all MVP entities and relationships  
✅ All tables have primary keys defined  
✅ Foreign keys use ON DELETE CASCADE  
✅ Check constraints validate enum-like columns  
✅ Indexes support common query patterns  
✅ Sample SQL provided for all tables  
✅ SQLAlchemy models align with schema  
✅ Alembic migration strategy documented  
✅ Design rationale explains key decisions  

---

## Next Steps

1. **Create `backend/app/db/base.py`** with SQLAlchemy Base
2. **Create `backend/app/db/session.py`** with engine and SessionLocal
3. **Initialize Alembic** with `alembic init`
4. **Create first migration** for users + profiles
5. **Run `alembic upgrade head`** to create tables
6. **Seed tags** (optional) with common values
7. **Test CRUD operations** via psql or pgAdmin

---

**Document Status**: ✅ Complete  
**Implementation Status**: Models created, migrations pending  
**Dependencies**: PostgreSQL 14+, SQLAlchemy 2.0+, Alembic 1.12+
