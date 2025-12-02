# 🌱 Build Guide #1: Seed Model (Post/Video)

**Time**: 20 minutes  
**Difficulty**: Beginner  
**What you'll learn**: SQLAlchemy models, ENUMs, relationships

---

## What is a Seed?

In the Garden System, a **Seed** is a post/video. It has a **lifecycle**:
- **Planted** → just created
- **Sprouting** → getting first engagement
- **Blooming** → peak engagement
- **Wilting** → decaying/expiring
- **Composting** → archived (becomes ML training data)

---

## Step 1: Create the file

```bash
cd /home/krillavilla/Documents/community-app/backend
touch app/models/seed.py
```

---

## Step 2: Import dependencies

Open `app/models/seed.py` and add:

```python
"""
Seed Model - Represents a post/video in the Garden System
A seed goes through lifecycle states: planted → sprouting → blooming → wilting → composting
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
```

**What this does**:
- `uuid`: Generates unique IDs for seeds
- `datetime`: Tracks when seed was planted, when it wilts, etc.
- `sqlalchemy`: Database ORM (Object-Relational Mapping) - lets us work with database as Python objects
- `enum`: Creates fixed choices (like seed states)

---

## Step 3: Define lifecycle states

Add after imports:

```python
class SeedState(str, enum.Enum):
    """Lifecycle states a seed can be in"""
    PLANTED = "planted"       # Just created, no engagement yet
    SPROUTING = "sprouting"   # First views/likes happening
    BLOOMING = "blooming"     # Peak engagement
    WILTING = "wilting"       # Decaying, losing engagement
    COMPOSTING = "composting" # Archived, used for ML training


class GardenType(str, enum.Enum):
    """Which garden feed the seed appears in"""
    WILD = "wild"             # For You Page (discovery)
    ROWS = "rows"             # Following feed
    GREENHOUSE = "greenhouse" # Private feed


class FenceType(str, enum.Enum):
    """Privacy level (who can see this seed)"""
    PUBLIC = "public"                # Everyone
    FRIENDS = "friends"              # Approved friends
    CLOSE_FRIENDS = "close_friends"  # Inner circle
    ORCHARD = "orchard"              # Mentors only
    PRIVATE = "private"              # Only you
```

**What this does**:
- Creates dropdown-like choices for seed properties
- Makes code safer (can't typo "bloo ming" instead of "blooming")

---

## Step 4: Create the Seed model class

Add:

```python
class Seed(Base):
    """
    A Seed represents a post/video in the Garden System.
    It has lifecycle states and grows based on engagement.
    """
    __tablename__ = "seeds"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Creator (vine_id links to users table)
    vine_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Content
    content = Column(Text, nullable=True)  # Caption
    video_url = Column(String(512), nullable=True)
    thumbnail_url = Column(String(512), nullable=True)
    mux_asset_id = Column(String(255), nullable=True)
    mux_playback_id = Column(String(255), nullable=True)
    
    # Lifecycle state
    state = Column(Enum(SeedState), nullable=False, default=SeedState.PLANTED)
    planted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sprouts_at = Column(DateTime, nullable=True)  # When first engagement happened
    wilts_at = Column(DateTime, nullable=True)    # When it will expire
    composted_at = Column(DateTime, nullable=True)
    
    # Growth metrics (how well the seed is doing)
    water_level = Column(Integer, nullable=False, default=0)      # Engagement score
    nutrient_score = Column(Integer, nullable=False, default=0)   # Comment quality
    sunlight_hours = Column(Integer, nullable=False, default=0)   # View count
    
    # Garden location
    garden_type = Column(Enum(GardenType), nullable=False, default=GardenType.WILD)
    privacy_fence = Column(Enum(FenceType), nullable=False, default=FenceType.PUBLIC)
    
    # Soil quality at planting time (creator's reputation)
    soil_health = Column(Float, nullable=False, default=1.0)
    
    # ML embedding for discovery (pollination)
    pollination_vector = Column(ARRAY(Float), nullable=True)
    
    # Soft delete (mark as deleted but keep in database)
    soft_deleted = Column(Boolean, nullable=False, default=False)
    
    # Relationships (will add later)
    # soil = relationship("Soil", back_populates="seed")  # Comments
    # pollination_events = relationship("PollinationEvent", back_populates="seed")
```

**What this does**:
- Defines database columns for a seed
- Each row in the `seeds` table = one video/post
- `nullable=False` means required, `nullable=True` means optional
- `default=` sets initial value when seed is created

---

## Step 5: Add helper methods

Add these inside the `Seed` class (after the relationships section):

```python
    @property
    def age_hours(self) -> float:
        """How many hours since seed was planted"""
        if not self.planted_at:
            return 0
        return (datetime.utcnow() - self.planted_at).total_seconds() / 3600
    
    @property
    def time_until_wilts(self) -> str:
        """Human-readable time until expiration"""
        if not self.wilts_at:
            return "Unknown"
        
        delta = self.wilts_at - datetime.utcnow()
        
        if delta.total_seconds() < 0:
            return "Wilted"
        
        hours = delta.total_seconds() / 3600
        if hours < 1:
            return f"{int(delta.total_seconds() / 60)} minutes"
        elif hours < 24:
            return f"{int(hours)} hours"
        else:
            return f"{int(hours / 24)} days"
    
    @property
    def is_alive(self) -> bool:
        """Check if seed is still active (not wilted/composted)"""
        return self.state in [SeedState.PLANTED, SeedState.SPROUTING, SeedState.BLOOMING]
    
    def __repr__(self):
        return f"<Seed {self.id} state={self.state.value} water={self.water_level}>"
```

**What this does**:
- `@property` creates computed values (calculated, not stored in database)
- `age_hours` calculates how old the seed is
- `time_until_wilts` shows expiration countdown
- `is_alive` checks if seed is active

---

## Step 6: Test your model

Create a test file:

```bash
touch tests/test_seed_model.py
```

Add:

```python
from app.models.seed import Seed, SeedState
from datetime import datetime, timedelta

def test_seed_creation():
    seed = Seed()
    seed.content = "My first seed!"
    seed.water_level = 10
    
    assert seed.state == SeedState.PLANTED
    assert seed.is_alive == True
    assert seed.garden_type.value == "wild"
    
    print("✅ Seed model works!")

if __name__ == "__main__":
    test_seed_creation()
```

---

## Step 7: Run migration

```bash
cd /home/krillavilla/Documents/community-app
docker compose run --rm backend alembic upgrade head
```

This creates the `seeds` table in your database!

---

## ✅ Done!

You've created the **Seed model**. Next, you'll create the **Vine model** (users).

**What you learned**:
- SQLAlchemy ORM basics
- Database columns and types
- ENUMs for fixed choices
- Computed properties with `@property`
- Foreign keys for relationships
