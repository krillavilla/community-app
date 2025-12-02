# Garden System Phase 2: API Endpoints COMPLETE ✅

## What Was Built

### Pydantic Schemas (`backend/app/schemas/garden.py`)
All request/response models for Garden System API:

- **SeedCreate** - Request to plant seed
- **SeedResponse** - Full seed details with computed fields
- **SeedSummary** - Minimal seed info for feeds
- **VineResponse** - Vine profile with health metrics
- **SoilCreate** - Request to add soil (comment)
- **SoilResponse** - Soil details with nutrient info
- **FeedResponse** - Feed wrapper with pagination
- **WaterResponse** - Watering confirmation
- **SunlightResponse** - Sunlight confirmation
- **VoteResponse** - Vote confirmation with updated scores
- **SearchRequest** - Search parameters
- **ClimateReadingResponse** - Community health snapshot

### API Endpoints

#### Seeds API (`/api/v1/seeds`)
**File**: `backend/app/api/v1/endpoints/seeds.py`

- `POST /seeds` - Plant seed (upload video + create post)
  - Validates file type and size (max 100MB)
  - Uploads to R2 storage
  - Sends to Mux for encoding
  - Creates Seed record in database
  - Auto-creates Vine if user doesn't have one
  - Updates vine stats

- `GET /seeds/{id}` - Get seed by ID with privacy check
  - Respects fence privacy rules
  - Returns 404 if access denied
  - Includes computed fields (growth_score, time_until_wilt)

- `POST /seeds/{id}/water` - Record view
  - Increments water_level
  - Waters vine (updates last_watered_at)

- `POST /seeds/{id}/sunlight` - Record share
  - Increments sunlight_hours
  - Adds sunlight to vine

- `GET /seeds/{id}/soil` - Get comments for seed
  - Paginated (skip/limit)
  - Ordered by nutrient_score DESC, then added_at DESC
  - Includes computed fields (is_toxic, is_nourishing)

#### Gardens API (`/api/v1/gardens`)
**File**: `backend/app/api/v1/endpoints/gardens.py`

- `GET /gardens/wild` - Wild Garden feed (For You Page)
  - Algorithm-driven: growth score + freshness
  - Avoids duplicates (24hr window via pollination_events)
  - Only blooming + public seeds
  - Tracks pollination events
  - Paginated

- `GET /gardens/rows` - Garden Rows feed (Following)
  - Chronological from connections
  - Respects privacy fences (public, friends)
  - Tracks pollination events
  - Paginated

- `GET /gardens/greenhouse` - Greenhouse feed (Private)
  - User's own seeds
  - All states except composting
  - Chronological
  - Paginated

- `GET /gardens/search` - Search seeds
  - Simple text search on content
  - Only public, blooming/sprouting seeds
  - Tracks pollination events as 'search' pathway
  - Paginated

#### Soil API (`/api/v1/soil`)
**File**: `backend/app/api/v1/endpoints/soil.py`

- `POST /soil?seed_id={id}` - Add soil (comment)
  - Creates Soil record
  - Updates vine stats (soil_given counter)

- `POST /soil/{id}/nitrogen` - Upvote comment
  - Creates/updates Nutrient record
  - Extends parent seed lifespan (+6 hours per upvote)
  - Updates commenter vine soil_health (+0.01)
  - Supports vote changing (toxin → nitrogen)

- `POST /soil/{id}/toxin` - Downvote comment
  - Creates/updates Nutrient record
  - If 5+ toxins: marks soil soft_deleted, composts parent seed
  - Updates commenter vine soil_health (-0.1 if toxic)
  - Supports vote changing (nitrogen → toxin)

- `DELETE /soil/{id}/vote` - Remove vote
  - Deletes Nutrient record
  - Reverts vote effects on Soil

#### Vines API (`/api/v1/vines`)
**File**: `backend/app/api/v1/endpoints/vines.py`

- `GET /vines/me` - Get current user's vine
  - Auto-creates vine if doesn't exist
  - Updates growth_stage based on days_since_planted
  - Returns computed fields (days_since_planted, needs_water, reputation_score)

- `GET /vines/{id}` - Get vine by ID
  - Returns public vine profile
  - Includes computed fields

### Route Registration
All routes registered in `backend/app/main.py`:

```python
# Garden System routes
app.include_router(seeds.router, prefix="/api/v1/seeds", tags=["seeds"])
app.include_router(gardens.router, prefix="/api/v1/gardens", tags=["gardens"])
app.include_router(soil.router, prefix="/api/v1/soil", tags=["soil"])
app.include_router(vines.router, prefix="/api/v1/vines", tags=["vines"])
```

## API Summary

### Planting & Viewing Seeds
```bash
# Plant seed (upload video)
POST /api/v1/seeds
Content-Type: multipart/form-data
Body: file (video), content (caption), privacy_fence

# Get seed
GET /api/v1/seeds/{id}

# Record view
POST /api/v1/seeds/{id}/water

# Record share
POST /api/v1/seeds/{id}/sunlight
```

### Feeds
```bash
# Wild Garden (FYP)
GET /api/v1/gardens/wild?skip=0&limit=20

# Garden Rows (Following)
GET /api/v1/gardens/rows?skip=0&limit=20

# Greenhouse (Private)
GET /api/v1/gardens/greenhouse?skip=0&limit=20

# Search
GET /api/v1/gardens/search?query=meditation&skip=0&limit=20
```

### Comments & Voting
```bash
# Add comment
POST /api/v1/soil?seed_id={seed_id}
Body: {"content": "Great video!"}

# Get comments for seed
GET /api/v1/seeds/{id}/soil?skip=0&limit=50

# Upvote (add nitrogen)
POST /api/v1/soil/{id}/nitrogen

# Downvote (add toxin)
POST /api/v1/soil/{id}/toxin

# Remove vote
DELETE /api/v1/soil/{id}/vote
```

### Vine Profile
```bash
# Get my vine
GET /api/v1/vines/me

# Get vine by ID
GET /api/v1/vines/{id}
```

## Key Features Implemented

### Auto-Vine Creation
- Vines auto-created when:
  - User first plants seed
  - User first accesses feeds
  - User calls GET /vines/me

### Privacy System
- `get_seed_by_id()` respects fence privacy
- Feed builders filter by privacy:
  - Wild Garden: public only
  - Garden Rows: public + friends
  - Greenhouse: own seeds only

### Pollination Tracking
- All feed views tracked via PollinationEvent:
  - `wild_garden` - FYP views
  - `rows` - Following views
  - `search` - Search results
  - `pollination` - ML recommendations (Phase 3)

### Nutrient Mechanics
- Upvote (nitrogen): +6 hours lifespan to seed, +0.01 soil_health to commenter
- Downvote (toxin): If 5+ toxins → delete comment + compost seed, -0.1 soil_health to commenter
- Vote changing: Can flip nitrogen ↔ toxin

### Computed Fields
Seeds:
- `growth_score` - Weighted sum of water/nutrients/sunlight
- `time_until_wilt` - Human-readable hours remaining

Vines:
- `days_since_planted` - Account age
- `needs_water` - Inactive 7+ days
- `reputation_score` - Combined soil_health + root_strength (0-100 scale)

Soil:
- `is_toxic` - 5+ downvotes
- `is_nourishing` - Positive nutrient score

## Files Created

```
backend/
├── app/
│   ├── schemas/
│   │   └── garden.py               (Pydantic schemas - 194 lines)
│   └── api/
│       └── v1/
│           └── endpoints/
│               ├── seeds.py         (Seeds API - 216 lines)
│               ├── gardens.py       (Gardens API - 152 lines)
│               ├── soil.py          (Soil API - 154 lines)
│               └── vines.py         (Vines API - 73 lines)
```

## Testing

### Start Services
```bash
docker compose up -d
```

### Test Endpoints (requires Auth0 token)
```bash
# Get auth token
TOKEN="your_auth0_jwt_token"

# Get my vine
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/vines/me

# Get Wild Garden feed
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/gardens/wild?limit=10

# Plant seed (would need multipart/form-data with video file)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@video.mp4" \
  -F "content=Check out my progress!" \
  -F "privacy_fence=public" \
  http://localhost:8000/api/v1/seeds
```

### Check API Docs
Visit http://localhost:8000/docs for interactive Swagger documentation

## What's Next (Phase 3)

### Workers (Cron Jobs)
1. **Lifecycle Worker** - Runs every 5 minutes
   - Calls `LifecycleEngine.process_lifecycle_transitions()`
   - Transitions seeds through states
   - Archives composted seeds

2. **Climate Worker** - Runs every hour
   - Records ClimateReading snapshots
   - Calculates community health metrics
   - Detects anomalies

3. **Compost Worker** - Runs daily
   - Archives composted seeds to cold storage
   - Extracts embeddings for ML training
   - Cleans up pollination_events older than 30 days

### ML Service Integration
- Pollination similarity model (content-based recommendations)
- Soil health scoring (reputation from vote patterns)
- Climate anomaly detection (toxicity spikes)
- Compost learning (embeddings from expired content)

### Frontend (Phase 4)
- Feed components (WildGarden, GardenRows, Greenhouse)
- Seed card with growth visualization
- Soil panel with voting UI
- Vine profile dashboard
- Climate health displays

---

**Status**: Phase 2 Complete
**Token Usage**: 95k/200k (105k remaining)
**Next**: Create worker scripts for lifecycle management
