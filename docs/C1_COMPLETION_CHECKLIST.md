# C1 Lifecycle Engine - Completion Checklist

## ✅ COMPLETED

### 1. Database Migration
- ✅ Created `004_add_lifecycle_engine.py` migration
- ✅ Adds lifecycle_stage, lifecycle_updated_at, engagement_score, expiry_date

### 2. Seed Model Updates
- ✅ Added `LifecycleStage` enum (SEED, SPROUT, VINE, FRUIT, COMPOST)
- ✅ Added lifecycle fields to Seed model
- ✅ Created `lifecycle_emoji` property
- ✅ Created `calculate_engagement_score()` method  
- ✅ Created `update_lifecycle_stage()` method

### 3. Lifecycle Worker
- ✅ Updated `lifecycle_worker.py` to use B2 engine
- ✅ Worker transitions seeds through stages every run
- ✅ Worker composts expired seeds

---

## 🔨 TODO - Complete These Steps

### Step 1: Run Database Migration

```bash
# Start your containers
docker compose up -d

# Run the migration
docker compose exec backend alembic upgrade head

# Verify it worked
docker compose exec backend alembic current
```

Expected output: Should show revision `004_lifecycle`

---

### Step 2: Add Lifecycle API Endpoints

Create `backend/app/api/v1/endpoints/lifecycle.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user
from app.models.seed import Seed, LifecycleStage
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class LifecycleResponse(BaseModel):
    stage: str
    emoji: str
    updated_at: datetime
    engagement_score: int
    progress_to_next: float

@router.get("/seeds/{seed_id}/lifecycle")
def get_seed_lifecycle(seed_id: str, db: Session = Depends(get_db)):
    """Get lifecycle info for a seed"""
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    if not seed:
        raise HTTPException(404, "Seed not found")
    
    # Calculate progress (score needed for next stage)
    score = seed.engagement_score
    progress = min((score / 20) * 100, 100)  # 20 = vine threshold
    
    return LifecycleResponse(
        stage=seed.lifecycle_stage.value,
        emoji=seed.lifecycle_emoji,
        updated_at=seed.lifecycle_updated_at,
        engagement_score=score,
        progress_to_next=progress
    )

@router.post("/seeds/{seed_id}/water")
def water_seed(
    seed_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """'Water' a seed - add engagement"""
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    if not seed:
        raise HTTPException(404, "Seed not found")
    
    # Increment water level (views)
    seed.add_water(1)
    seed.engagement_score = seed.calculate_engagement_score()
    db.commit()
    
    return {"message": "💧 Seed watered!", "new_score": seed.engagement_score}
```

Then register it in `backend/app/api/v1/api.py`:

```python
from app.api.v1.endpoints import lifecycle

api_router.include_router(
    lifecycle.router,
    prefix="/lifecycle",
    tags=["lifecycle"]
)
```

---

### Step 3: Test the Worker

```bash
# Run the worker manually once
docker compose exec backend python -m app.workers.lifecycle_worker

# Should see output like:
# === Lifecycle Worker Started (B2 Engine) ===
# Processing X active seeds...
# ✅ Lifecycle transitions completed in 0.23s
```

---

### Step 4: Create Frontend Component

Create `frontend/src/components/garden/LifecycleBadge.jsx`:

```jsx
export default function LifecycleBadge({ stage, progress }) {
  const config = {
    seed: { emoji: '🌱', label: 'Seed', color: 'bg-green-100 text-green-800' },
    sprout: { emoji: '🌿', label: 'Sprout', color: 'bg-green-200 text-green-900' },
    vine: { emoji: '🍇', label: 'Vine', color: 'bg-purple-100 text-purple-800' },
    fruit: { emoji: '🍂', label: 'Fruit', color: 'bg-amber-100 text-amber-800' },
    compost: { emoji: '💀', label: 'Composted', color: 'bg-gray-100 text-gray-600' },
  }[stage] || { emoji: '🌱', label: 'Seed', color: 'bg-gray-100' };

  return (
    <div className="flex items-center gap-2">
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        {config.emoji} {config.label}
      </span>
      {progress > 0 && progress < 100 && (
        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
}
```

---

### Step 5: Update SeedCard to Show Lifecycle

Edit `frontend/src/components/garden/SeedCard.jsx`:

```jsx
import { useState, useEffect } from 'react';
import LifecycleBadge from './LifecycleBadge';

export default function SeedCard({ seed }) {
  const [lifecycle, setLifecycle] = useState(null);

  useEffect(() => {
    fetch(`/api/v1/lifecycle/seeds/${seed.id}/lifecycle`)
      .then(res => res.json())
      .then(data => setLifecycle(data))
      .catch(err => console.error('Lifecycle fetch failed:', err));
  }, [seed.id]);

  const waterSeed = async () => {
    const res = await fetch(`/api/v1/lifecycle/seeds/${seed.id}/water`, { 
      method: 'POST' 
    });
    const data = await res.json();
    alert(data.message);
    // Refresh lifecycle data
    const updated = await fetch(`/api/v1/lifecycle/seeds/${seed.id}/lifecycle`);
    setLifecycle(await updated.json());
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-3">
      {/* Lifecycle badge */}
      {lifecycle && (
        <LifecycleBadge 
          stage={lifecycle.stage} 
          progress={lifecycle.progress_to_next} 
        />
      )}
      
      {/* Seed content */}
      <p>{seed.content}</p>
      
      {/* Water button */}
      <button
        onClick={waterSeed}
        className="px-4 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600"
      >
        💧 Water
      </button>
    </div>
  );
}
```

---

### Step 6: Schedule Worker to Run Hourly

**Option A: Add to Docker Compose**

Add this to `docker-compose.yml`:

```yaml
  lifecycle-worker:
    build: ./backend
    container_name: garden_lifecycle_worker
    command: >
      sh -c "while true; do
        python -m app.workers.lifecycle_worker;
        sleep 3600;
      done"
    environment:
      DATABASE_URL: postgresql://garden:garden@postgres:5432/garden_db
    depends_on:
      - postgres
    networks:
      - garden_network
```

**Option B: Use System Cron (on host)**

```bash
# Edit crontab
crontab -e

# Add this line (runs every hour)
0 * * * * docker compose -f /path/to/community-app/docker-compose.yml exec backend python -m app.workers.lifecycle_worker >> /var/log/lifecycle.log 2>&1
```

---

## 🧪 Testing Checklist

1. **Test Migration**
   - [ ] Migration runs without errors
   - [ ] Database has new lifecycle columns

2. **Test API Endpoints**
   - [ ] `/api/v1/lifecycle/seeds/{id}/lifecycle` returns lifecycle data
   - [ ] `/api/v1/lifecycle/seeds/{id}/water` increments engagement

3. **Test Worker**
   - [ ] Worker runs without errors
   - [ ] Seeds transition from SEED → SPROUT when conditions met
   - [ ] Seeds transition from SPROUT → VINE when engagement high

4. **Test Frontend**
   - [ ] Lifecycle badge shows on seed cards
   - [ ] Progress bar displays correctly
   - [ ] Water button updates engagement score

---

## 🎯 Success Criteria

You'll know C1 is working when:
1. New seeds start as 🌱 SEED
2. After 1 hour + 5 engagements → 🌿 SPROUT
3. After 24 hours + 20 engagements → 🍇 VINE
4. After 30 days → 🍂 FRUIT
5. Expired seeds → 💀 COMPOST

---

## 📚 Next Steps After C1

Once C1 is working, you can:
1. Build **C2: Soil Health System** (user reputation)
2. Build **C3: Pollination System** (ML-powered discovery)
3. Integrate lifecycle into feed algorithm (boost vines, hide compost)
4. Add notifications when seeds transition stages

---

*Last updated: 2025-11-25*
*Status: Backend complete, Frontend + Testing remaining*
