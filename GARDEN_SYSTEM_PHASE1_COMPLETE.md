# Garden System Phase 1: COMPLETE ✅

## What Was Built

### 1. Database Models (8 tables created)
All models include lifecycle mechanics, growth tracking, and Garden metaphor properties:

- **Seed** (`backend/app/models/seed.py`)
  - Posts/videos with lifecycle states: PLANTED → SPROUTING → BLOOMING → WILTING → COMPOSTING
  - Growth metrics: water (views), nutrients (comment quality), sunlight (shares)
  - Privacy fences: public, friends, close_friends, orchard, private
  - Lifespan management: extends with upvotes (+6hrs), expires after toxicity or time

- **Vine** (`backend/app/models/vine.py`)
  - Users with garden health metrics
  - Growth stages: seedling → vine → mature → ancient
  - Soil health (reputation): 0-2 scale affecting content reach
  - Root strength (connection quality): 0-1 scale
  - Activity tracking: watering (last active), stats (seeds planted, soil given)

- **Soil** (`backend/app/models/soil.py`)
  - Comments as nutrients with voting
  - Nutrient score = nitrogen (upvotes) - toxins (downvotes)
  - Lifecycle: added_at → decays_at → composted_at
  - Auto-deletion at 5+ toxins

- **Nutrient** (`backend/app/models/nutrient.py`)
  - Individual votes on soil (nitrogen/toxin)
  - One vote per vine per soil (unique constraint)
  - Vote changing supported (nitrogen ↔ toxin)

- **Fence** (`backend/app/models/fence.py`)
  - Privacy circles for content visibility
  - Defines who can see seeds at each privacy level
  - Types: public, friends, close_friends, orchard, private

- **Root** (`backend/app/models/root.py`)
  - Direct messages between vines
  - Optional expiration (decays_at)
  - Compostable (archived)

- **PollinationEvent** (`backend/app/models/pollination_event.py`)
  - Discovery tracking for seeds
  - Pathways: wild_garden (FYP), rows (following), pollination (ML), search
  - Similarity scores for ML-driven recommendations

- **ClimateReading** (`backend/app/models/climate_reading.py`)
  - Community health snapshots
  - Metrics: toxicity_level, growth_rate, drought_risk, pest_incidents, temperature
  - Health scoring and intervention detection

### 2. Database Migration
- **003_garden_system_core.py** - Creates all 8 tables with proper indexes
- ENUMs: seed_state, garden_type, fence_type, vine_growth, nutrient_type
- Foreign keys with CASCADE deletes
- Indexes optimized for feed queries

### 3. Core Services (Garden System Engine)

- **LifecycleEngine** (`backend/app/garden/lifecycle.py`)
  - Manages seed state transitions
  - Constants: SPROUTING_DELAY (1hr), BLOOM_THRESHOLD (10), DEFAULT_LIFESPAN (7 days)
  - Methods:
    - `process_lifecycle_transitions()` - Main cron entry point
    - `apply_nutrient_to_seed()` - Applies vote effects (lifespan extension/toxicity)
    - `water_seed()` - Records view
    - `shine_sunlight()` - Records share

- **SoilService** (`backend/app/garden/soil_service.py`)
  - Comment and voting management
  - Methods:
    - `add_soil()` - Create comment
    - `add_nitrogen()` - Upvote (extends seed lifespan +6hrs)
    - `add_toxin()` - Downvote (5+ triggers composting)
    - `remove_vote()` - Undo vote
    - `get_soil_for_seed()` - Get comments for seed

- **GardenFeedService** (`backend/app/garden/feeds.py`)
  - Feed builders for all garden types
  - Methods:
    - `get_wild_garden()` - FYP algorithm (growth score + freshness)
    - `get_garden_rows()` - Following feed (chronological)
    - `get_greenhouse()` - Own seeds (private)
    - `get_seed_by_id()` - Single seed with privacy check
    - `search_seeds()` - Text search

### 4. Configuration Fixes
- Fixed missing `os` import in `backend/app/core/config.py`
- Moved R2 and Mux config into Settings class (proper Pydantic fields)
- All config now properly validated

## Database Schema

```
users (existing)
  ├── vines (1:1) - garden health metrics
  │
seeds (posts/videos)
  ├── state: ENUM(planted, sprouting, blooming, wilting, composting)
  ├── growth: water_level, nutrient_score, sunlight_hours
  ├── privacy: privacy_fence ENUM(public, friends, close_friends, orchard, private)
  ├── lifecycle: planted_at, sprouts_at, wilts_at, composted_at
  └── ML: pollination_vector (float[])
  
soil (comments)
  ├── nutrient_score = nitrogen_count - toxin_count
  ├── lifecycle: added_at, decays_at, composted_at
  └── foreign keys: seed_id, vine_id

nutrients (votes)
  ├── type: ENUM(nitrogen, toxin)
  ├── unique constraint: (soil_id, vine_id)
  └── foreign keys: soil_id, vine_id

fences (privacy circles)
  ├── fence_type: ENUM(public, friends, close_friends, orchard, private)
  ├── unique constraint: (vine_id, fence_type, member_vine_id)
  └── foreign keys: vine_id, member_vine_id

roots (DMs)
  ├── message, decays_at, is_read, composted
  └── foreign keys: from_vine_id, to_vine_id

pollination_events (discovery tracking)
  ├── pathway: 'wild_garden' | 'rows' | 'pollination' | 'search'
  ├── similarity_score (for ML recommendations)
  └── foreign keys: seed_id, vine_id

climate_readings (community health)
  ├── toxicity_level, growth_rate, drought_risk, pest_incidents, temperature
  └── computed: health_score, is_healthy, needs_intervention
```

## Key Mechanics Implemented

### Lifecycle State Machine
```
PLANTED (video processing)
  ↓ after 1 hour
SPROUTING (gaining traction)
  ↓ growth_score >= 10
BLOOMING (active engagement)
  ↓ approaching wilts_at (24hrs before)
WILTING (declining)
  ↓ past wilts_at OR 5+ toxins
COMPOSTING (archived)
```

### Nutrient System
- **Nitrogen (upvote)**: +6 hours lifespan per vote, max 30 days total
- **Toxin (downvote)**: 5+ toxins = immediate composting
- Affects seed: lifespan, visibility, composting
- Affects commenter vine: soil_health (+0.01 for upvoted, -0.1 for toxic)

### Feed Algorithms
- **Wild Garden**: Growth score ranking with freshness boost, avoids duplicates (24hr window)
- **Garden Rows**: Chronological from connections, respects privacy fences
- **Greenhouse**: User's own seeds, all states except composting

### Privacy System
- **Public**: Anyone can see
- **Friends**: Connections in fence
- **Close Friends**: Inner circle (separate fence type)
- **Orchard**: Specific community
- **Private**: Only creator

## Files Created

```
backend/
├── app/
│   ├── models/
│   │   ├── seed.py                   (Seed, SeedState, GardenType, FenceType)
│   │   ├── vine.py                   (Vine, VineGrowth)
│   │   ├── soil.py                   (Soil)
│   │   ├── nutrient.py               (Nutrient, NutrientType)
│   │   ├── fence.py                  (Fence)
│   │   ├── root.py                   (Root)
│   │   ├── pollination_event.py      (PollinationEvent)
│   │   ├── climate_reading.py        (ClimateReading)
│   │   └── __init__.py               (updated exports)
│   └── garden/
│       ├── __init__.py               (package exports)
│       ├── lifecycle.py              (LifecycleEngine)
│       ├── soil_service.py           (SoilService)
│       └── feeds.py                  (GardenFeedService)
└── alembic/
    └── versions/
        └── 003_garden_system_core.py (migration)
```

## What's Next (Phase 2)

### API Endpoints (Need to Create)
- `POST /api/v1/seeds` - Plant seed (create post)
- `GET /api/v1/seeds/{id}` - Get seed by ID
- `GET /api/v1/gardens/wild` - Wild Garden feed
- `GET /api/v1/gardens/rows` - Garden Rows feed
- `GET /api/v1/gardens/greenhouse` - Greenhouse feed
- `POST /api/v1/seeds/{id}/soil` - Add soil (comment)
- `POST /api/v1/soil/{id}/nitrogen` - Upvote
- `POST /api/v1/soil/{id}/toxin` - Downvote
- `DELETE /api/v1/soil/{id}/vote` - Remove vote
- `POST /api/v1/seeds/{id}/water` - Record view
- `POST /api/v1/seeds/{id}/sunlight` - Record share
- `GET /api/v1/vines/me` - Get vine profile
- `POST /api/v1/fences` - Add to fence
- `GET /api/v1/climate` - Get climate readings

### Workers (Need to Create)
- `lifecycle_worker.py` - Cron job: runs `LifecycleEngine.process_lifecycle_transitions()` every 5 minutes
- `climate_worker.py` - Cron job: records ClimateReading snapshots every hour
- `compost_worker.py` - Cron job: archives composted seeds to cold storage daily

### ML Service Integration (Phase 3)
- Pollination model: content-based similarity (embeddings)
- Soil health model: reputation scoring from vote patterns
- Climate model: anomaly detection for toxicity spikes
- Compost learning: extract embeddings from expired content for training

### Frontend Components (Phase 4)
- Feed components: WildGarden, GardenRows, Greenhouse
- Seed card: growth meter, lifecycle indicator, water/nutrient/sunlight display
- Soil panel: comments with nitrogen/toxin voting
- Vine profile: growth stage, soil health, root strength displays
- Climate dashboard: community health metrics (Guardians only)

## Migration Status
✅ Database migration applied successfully
✅ All 8 tables created with indexes
✅ ENUMs created: seed_state, garden_type, fence_type, vine_growth, nutrient_type

## Testing Commands

```bash
# Run migration
docker compose run --rm backend alembic upgrade head

# Check tables exist
docker compose run --rm backend python -c "from app.models import *; print('All models imported')"

# Test lifecycle engine
docker compose run --rm backend python -c "from app.garden import LifecycleEngine; print('Lifecycle engine imported')"
```

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  WildGarden │ GardenRows │ Greenhouse │ SeedCard        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                  Backend API (FastAPI)                   │
│  Seeds API │ Gardens API │ Soil API │ Vines API         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                  Garden System Services                  │
│  LifecycleEngine │ SoilService │ GardenFeedService      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                   Database (PostgreSQL)                  │
│  seeds │ vines │ soil │ nutrients │ fences │ roots      │
│  pollination_events │ climate_readings                   │
└─────────────────────────────────────────────────────────┘
         │
┌────────┴──────────┐
│   Workers (Cron)   │
│  Lifecycle │ Climate│
│  Compost           │
└────────────────────┘
```

---

**Status**: Phase 1 Complete
**Token Usage**: 71k/200k (129k remaining)
**Next**: Create API endpoints or continue with workers?
