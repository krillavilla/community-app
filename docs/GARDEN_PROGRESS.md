# 🌱 Garden System - Build Progress

## Phase 1, Part 1: Database & Models

### ✅ Completed

1. **Database Migration** (`backend/alembic/versions/002_garden_system_core.py`)
   - Created 8 new tables: seeds, vines, soil, nutrients, fences, roots, pollination_events, climate_readings
   - Added 5 ENUM types for lifecycle states
   - Complex file - I wrote this for you

2. **Build Guide #1** (`docs/guides/BUILD_01_seed_model.md`)
   - Step-by-step instructions to create Seed model
   - Beginner-friendly with explanations
   - YOU will build this (20 mins)

### 📋 Next Steps (In Order)

1. **Follow BUILD_01_seed_model.md** to create `backend/app/models/seed.py`
2. **Create Vine model** (user) - Guide coming next
3. **Create Soil model** (comments) - Guide coming
4. **Run migration**: `docker compose run --rm backend alembic upgrade head`
5. **Test models work**

---

## What You Have So Far

```
community-app/
├── backend/
│   ├── alembic/versions/
│   │   ├── 001_video_gdpr.py          ✅ (existing)
│   │   └── 002_garden_system_core.py  ✅ NEW
│   └── app/models/
│       ├── seed.py                     ⏳ YOU BUILD THIS
│       ├── vine.py                     ⏳ COMING NEXT
│       └── soil.py                     ⏳ COMING
└── docs/
    ├── GARDEN_ARCHITECTURE.md          ✅ (high-level design)
    ├── GARDEN_PROGRESS.md              ✅ (this file)
    └── guides/
        └── BUILD_01_seed_model.md      ✅ (your guide)
```

---

## Garden System Glossary

| Garden Term | Technical | What It Is |
|-------------|-----------|------------|
| Seed | Post/Video | User-created content with lifecycle |
| Vine | User | Person using the app |
| Soil | Comment | Feedback on a seed |
| Nutrients | Votes | Upvotes (nitrogen) or downvotes (toxins) |
| Water Level | Engagement | Likes, shares, views |
| Sunlight | Views | How many people saw it |
| Wild Garden | For You Page | Discovery feed |
| Garden Rows | Following Feed | People you follow |
| Greenhouse | Private Feed | Your private content |
| Fence | Privacy Circle | Who can see your seeds |
| Pollination | Discovery | ML-based recommendations |
| Compost | Archived Data | Old content used for ML training |
| Climate | Community Health | Overall mood/safety metrics |

---

## Lifecycle States

### Seed States
```
PLANTED → SPROUTING → BLOOMING → WILTING → COMPOSTING
```

- **Planted**: Just created, no engagement yet (age < 1hr)
- **Sprouting**: First likes/views coming in
- **Blooming**: Peak engagement happening
- **Wilting**: Decaying, approaching expiration
- **Composting**: Archived, used for ML embeddings

### Vine Growth Stages
```
SEEDLING → VINE → MATURE → ANCIENT
```

- **Seedling**: New user (< 7 days)
- **Vine**: Active user (7-30 days)
- **Mature**: Established user (30-90 days)
- **Ancient**: Long-time member (90+ days)

---

## Time Estimate

### Phase 1 (Database & Models): ~3-4 hours
- ✅ Migration (done by me)
- ⏳ Seed model (you: 20 mins)
- ⏳ Vine model (you: 20 mins)
- ⏳ Soil model (you: 15 mins)
- ⏳ Run migration (you: 5 mins)
- ⏳ Test (you: 10 mins)

### Phase 2 (Lifecycle Engine): ~2-3 hours
- State machine logic (me: complex)
- Worker setup (guide for you)

### Phase 3 (API Endpoints): ~2-3 hours
- Seed creation endpoint (guide)
- Garden feeds (guide)
- Soil/nutrients (guide)

### Phase 4 (Frontend): ~4-5 hours
- Seed player (guide)
- Garden views (guide)
- Soil panel (guide)

---

## Token Usage

Current: ~156k / 200k (44k remaining)
Minimum: 60k

We're good! Still plenty of room.

---

## Questions?

If you're confused about anything:
1. Check the glossary above
2. Read `GARDEN_ARCHITECTURE.md` for big picture
3. Ask me!

---

**Start with BUILD_01_seed_model.md when ready!**
