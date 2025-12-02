# C1: Lifecycle Engine - Implementation Guide

This guide walks you through building the Lifecycle Engine prototype step-by-step.

---

## Phase 1: Database Schema Updates

### Step 1.1: Create Alembic Migration

```bash
cd backend
alembic revision -m "add_lifecycle_fields_to_seed"
```

### Step 1.2: Edit the Migration File

Open `backend/alembic/versions/[timestamp]_add_lifecycle_fields_to_seed.py`:

```python
"""add lifecycle fields to seed

Revision ID: [auto-generated]
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Lifecycle stage enum
lifecycle_stage = postgresql.ENUM(
    'seed', 'sprout', 'vine', 'fruit', 'compost',
    name='lifecycle_stage'
)

def upgrade():
    # Create enum type
    lifecycle_stage.create(op.get_bind(), checkfirst=True)
    
    # Add lifecycle columns to seed table
    op.add_column('seed', sa.Column(
        'lifecycle_stage',
        lifecycle_stage,
        nullable=False,
        server_default='seed'
    ))
    op.add_column('seed', sa.Column(
        'lifecycle_updated_at',
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text('NOW()')
    ))
    op.add_column('seed', sa.Column(
        'engagement_score',
        sa.Integer(),
        nullable=False,
        server_default='0'
    ))
    op.add_column('seed', sa.Column(
        'expiry_date',
        sa.DateTime(timezone=True),
        nullable=True
    ))
    
    # Create index for background worker queries
    op.create_index(
        'idx_seed_lifecycle_stage',
        'seed',
        ['lifecycle_stage', 'lifecycle_updated_at']
    )

def downgrade():
    op.drop_index('idx_seed_lifecycle_stage', 'seed')
    op.drop_column('seed', 'expiry_date')
    op.drop_column('seed', 'engagement_score')
    op.drop_column('seed', 'lifecycle_updated_at')
    op.drop_column('seed', 'lifecycle_stage')
    lifecycle_stage.drop(op.get_bind(), checkfirst=True)
```

### Step 1.3: Run Migration

```bash
# Inside Docker container
docker compose exec backend alembic upgrade head
```

---

## Phase 2: Update Seed Model

### Step 2.1: Edit `backend/app/models/seed.py`

Add these imports and fields:

```python
from datetime import datetime, timedelta
from sqlalchemy import Enum
import enum

# Define lifecycle enum
class LifecycleStage(str, enum.Enum):
    SEED = "seed"
    SPROUT = "sprout"
    VINE = "vine"
    FRUIT = "fruit"
    COMPOST = "compost"

# Inside the Seed model class, add:
class Seed(Base):
    # ... existing fields ...
    
    # Lifecycle fields
    lifecycle_stage = Column(
        Enum(LifecycleStage),
        nullable=False,
        default=LifecycleStage.SEED
    )
    lifecycle_updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    engagement_score = Column(Integer, default=0)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    @property
    def lifecycle_emoji(self):
        """Return emoji for current lifecycle stage"""
        emoji_map = {
            LifecycleStage.SEED: "🌱",
            LifecycleStage.SPROUT: "🌿",
            LifecycleStage.VINE: "🍇",
            LifecycleStage.FRUIT: "🍂",
            LifecycleStage.COMPOST: "💀"
        }
        return emoji_map.get(self.lifecycle_stage, "🌱")
    
    def calculate_engagement_score(self):
        """Calculate engagement from interactions"""
        # water_level = views, sunlight_hours = shares
        score = (self.water_level or 0) + (self.sunlight_hours or 0) * 5
        return score
    
    def update_lifecycle_stage(self):
        """Determine if seed should transition to next stage"""
        score = self.calculate_engagement_score()
        age_hours = (datetime.utcnow() - self.planted_at).total_seconds() / 3600
        
        # Transition rules
        if score >= 20 and age_hours >= 24:
            return LifecycleStage.VINE
        elif score >= 5 and age_hours >= 1:
            return LifecycleStage.SPROUT
        elif age_hours >= 720:  # 30 days
            return LifecycleStage.FRUIT
        
        return self.lifecycle_stage
```

---

## Phase 3: Create Lifecycle Worker

### Step 3.1: Create Worker Script

Create `backend/app/workers/lifecycle_worker.py`:

```python
"""
Lifecycle Worker - Transitions seeds through growth stages
Runs as background job every hour
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.seed import Seed, LifecycleStage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transition_seed_lifecycle(db: Session):
    """
    Check all active seeds and transition them through lifecycle stages
    """
    # Get all seeds that aren't composted yet
    active_seeds = db.query(Seed).filter(
        Seed.lifecycle_stage != LifecycleStage.COMPOST
    ).all()
    
    transitions = 0
    composted = 0
    
    for seed in active_seeds:
        # Update engagement score
        seed.engagement_score = seed.calculate_engagement_score()
        
        # Calculate new stage
        new_stage = seed.update_lifecycle_stage()
        
        # Check if should be composted (expired)
        if seed.expiry_date and datetime.utcnow() > seed.expiry_date:
            seed.lifecycle_stage = LifecycleStage.COMPOST
            composted += 1
            logger.info(f"🍂 Composted seed {seed.id}")
        
        # Transition to new stage if changed
        elif new_stage != seed.lifecycle_stage:
            old_stage = seed.lifecycle_stage
            seed.lifecycle_stage = new_stage
            seed.lifecycle_updated_at = datetime.utcnow()
            transitions += 1
            logger.info(
                f"🌱→{seed.lifecycle_emoji} Seed {seed.id}: "
                f"{old_stage} → {new_stage}"
            )
    
    db.commit()
    logger.info(
        f"✅ Lifecycle check complete: "
        f"{transitions} transitions, {composted} composted"
    )

def run_lifecycle_worker():
    """Main worker entry point"""
    logger.info("🌿 Starting lifecycle worker...")
    db = SessionLocal()
    try:
        transition_seed_lifecycle(db)
    except Exception as e:
        logger.error(f"❌ Lifecycle worker error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_lifecycle_worker()
```

### Step 3.2: Create Cron Job

Create `backend/app/workers/lifecycle_cron.py`:

```python
"""
Simple cron scheduler for lifecycle worker
Runs every hour
"""
import time
import schedule
from lifecycle_worker import run_lifecycle_worker

# Schedule worker to run every hour
schedule.every(1).hours.do(run_lifecycle_worker)

print("🌱 Lifecycle worker scheduler started")
print("Running every 1 hour...")

# Run immediately on start
run_lifecycle_worker()

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

### Step 3.3: Add Dependencies

Add to `backend/requirements.txt`:

```
schedule==1.2.0
```

---

## Phase 4: Create API Endpoints

### Step 4.1: Create Lifecycle Schemas

Create `backend/app/schemas/lifecycle.py`:

```python
from pydantic import BaseModel
from datetime import datetime
from app.models.seed import LifecycleStage

class LifecycleResponse(BaseModel):
    stage: LifecycleStage
    emoji: str
    updated_at: datetime
    engagement_score: int
    progress_to_next: float  # 0-100%

class GrowthDashboard(BaseModel):
    total_seeds: int
    seeds_by_stage: dict
    recent_transitions: list
```

### Step 4.2: Create Lifecycle Endpoints

Create `backend/app/api/v1/endpoints/lifecycle.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user
from app.models.seed import Seed, LifecycleStage
from app.models.vine import Vine
from app.schemas.lifecycle import LifecycleResponse, GrowthDashboard

router = APIRouter()

@router.get("/seeds/{seed_id}/lifecycle", response_model=LifecycleResponse)
def get_seed_lifecycle(
    seed_id: str,
    db: Session = Depends(get_db)
):
    """Get lifecycle info for a seed"""
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    if not seed:
        raise HTTPException(404, "Seed not found")
    
    # Calculate progress to next stage
    score = seed.engagement_score
    progress = min((score / 20) * 100, 100)  # 20 = vine threshold
    
    return LifecycleResponse(
        stage=seed.lifecycle_stage,
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
    """
    'Water' a seed - increment engagement
    (This is like a 'like' in traditional social media)
    """
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    if not seed:
        raise HTTPException(404, "Seed not found")
    
    # Increment water level (views/likes)
    seed.water_level = (seed.water_level or 0) + 1
    seed.engagement_score = seed.calculate_engagement_score()
    
    db.commit()
    
    return {"message": "💧 Seed watered!", "new_score": seed.engagement_score}

@router.get("/garden/growth", response_model=GrowthDashboard)
def get_growth_dashboard(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's garden growth statistics"""
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        return GrowthDashboard(
            total_seeds=0,
            seeds_by_stage={},
            recent_transitions=[]
        )
    
    seeds = db.query(Seed).filter(Seed.vine_id == vine.id).all()
    
    # Count by stage
    stage_counts = {}
    for stage in LifecycleStage:
        count = sum(1 for s in seeds if s.lifecycle_stage == stage)
        stage_counts[stage.value] = count
    
    return GrowthDashboard(
        total_seeds=len(seeds),
        seeds_by_stage=stage_counts,
        recent_transitions=[]  # TODO: Add transition log table
    )
```

### Step 4.3: Register Routes

Add to `backend/app/api/v1/api.py`:

```python
from app.api.v1.endpoints import lifecycle

api_router.include_router(
    lifecycle.router,
    prefix="/lifecycle",
    tags=["lifecycle"]
)
```

---

## Phase 5: Frontend Components

### Step 5.1: Create Lifecycle Badge Component

Create `frontend/src/components/garden/LifecycleBadge.jsx`:

```jsx
/**
 * Visual indicator showing seed's current lifecycle stage
 */
export default function LifecycleBadge({ stage, progress }) {
  const stageConfig = {
    seed: { emoji: '🌱', label: 'Seed', color: 'bg-green-100 text-green-800' },
    sprout: { emoji: '🌿', label: 'Sprout', color: 'bg-green-200 text-green-900' },
    vine: { emoji: '🍇', label: 'Vine', color: 'bg-purple-100 text-purple-800' },
    fruit: { emoji: '🍂', label: 'Fruit', color: 'bg-amber-100 text-amber-800' },
    compost: { emoji: '💀', label: 'Composted', color: 'bg-gray-100 text-gray-600' },
  };

  const config = stageConfig[stage] || stageConfig.seed;

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

### Step 5.2: Update SeedCard Component

Edit `frontend/src/components/garden/SeedCard.jsx`:

```jsx
import LifecycleBadge from './LifecycleBadge';
import { useState, useEffect } from 'react';

export default function SeedCard({ seed }) {
  const [lifecycle, setLifecycle] = useState(null);

  useEffect(() => {
    // Fetch lifecycle data
    fetch(`/api/v1/lifecycle/seeds/${seed.id}/lifecycle`)
      .then(res => res.json())
      .then(data => setLifecycle(data));
  }, [seed.id]);

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-3">
      {/* Lifecycle badge at top */}
      {lifecycle && (
        <LifecycleBadge
          stage={lifecycle.stage}
          progress={lifecycle.progress_to_next}
        />
      )}
      
      {/* Rest of seed content */}
      <p>{seed.content}</p>
      
      {/* Water button */}
      <button
        onClick={() => waterSeed(seed.id)}
        className="px-4 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600"
      >
        💧 Water
      </button>
    </div>
  );
}

function waterSeed(seedId) {
  fetch(`/api/v1/lifecycle/seeds/${seedId}/water`, { method: 'POST' })
    .then(res => res.json())
    .then(data => alert(data.message));
}
```

---

## Testing Your Implementation

### 1. Run Migration
```bash
docker compose exec backend alembic upgrade head
```

### 2. Start Lifecycle Worker
```bash
docker compose exec backend python -m app.workers.lifecycle_cron
```

### 3. Test Lifecycle Transitions

```python
# Create a test seed via API
# Water it multiple times
# Wait for worker to run
# Check if it transitioned to "sprout"
```

### 4. View Growth Dashboard
Navigate to `/garden/growth` to see all your seeds by stage.

---

## Next Steps

1. ✅ Deploy and test lifecycle transitions
2. Add notifications when seeds transition stages
3. Build admin dashboard to monitor lifecycle health
4. Integrate lifecycle with feed algorithm (boost vines, hide composted)

---

*Last updated: 2025-11-25*
