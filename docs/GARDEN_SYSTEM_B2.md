# Garden System B2 - Prototype Options

This document outlines three core features that embody the Garden metaphor. Each can be built as a standalone prototype.

---

## Overview: The Garden Philosophy

The Garden System (B2) transforms social interaction into a living ecosystem where:
- **Posts = Seeds** that grow through natural lifecycles
- **Engagement = Nutrients** that sustain growth
- **Users = Vines** contributing to a shared garden
- **Communities = Orchards** with their own climate
- **Discovery = Pollination** via semantic connections

---

## Prototype Option C1: Lifecycle Engine ⭐ RECOMMENDED FIRST

### Concept
Every post follows a natural lifecycle: **Seed → Sprout → Vine → Fruit → Compost**

### Lifecycle Stages

| Stage | Icon | Trigger | Duration | Visibility |
|-------|------|---------|----------|------------|
| 🌱 **Seed** | Initial | Post created | 0-24h | Limited (close friends) |
| 🌿 **Sprout** | 5+ engagements | Post gaining traction | 1-7 days | Moderate (friends) |
| 🍇 **Vine** | 20+ engagements | High resonance | 7-30 days | High (public) |
| 🍂 **Fruit** | Peak influence | Mature content | 30-90 days | Archive mode |
| 💀 **Compost** | Natural decay | Expired | Permanent | Hidden, ML learns from it |

### Technical Components

**Database Changes:**
- Add `lifecycle_stage` enum field to posts
- Add `lifecycle_updated_at` timestamp
- Add `engagement_score` integer (calculated from likes, comments, shares)
- Add `expiry_date` timestamp

**Background Worker:**
- Cron job runs every hour
- Checks engagement scores
- Transitions posts to next stage
- Archives composted content

**API Endpoints:**
- `GET /api/v1/seeds/{id}/lifecycle` - Get current stage
- `POST /api/v1/seeds/{id}/water` - Manual engagement boost
- `GET /api/v1/garden/growth` - User's lifecycle dashboard

**Frontend:**
- Visual lifecycle indicator on each post
- Growth meter showing progress to next stage
- Notifications when seeds sprout or vine

### Learning Outcomes
- Event-driven architecture
- Background job scheduling
- State machines
- Time-based transitions

---

## Prototype Option C2: Soil Health System

### Concept
Each user has a **soil health score** representing their garden's quality. Positive interactions nourish the soil; negative behavior depletes it.

### Soil Health Metrics

**Score Range:** 0-100

**Nutrients (Positive):**
- Thoughtful comments: +2
- Helpful responses: +3
- Content that inspires: +5
- Mentorship interactions: +8

**Toxins (Negative):**
- Spam: -5
- Harassment: -10
- Misinformation: -8
- Excessive negativity: -3

### Effects of Soil Health

| Soil Score | Garden Status | Post Lifespan | Visibility |
|------------|---------------|---------------|------------|
| 80-100 | Rich soil | +50% longer | Boosted discovery |
| 60-79 | Healthy soil | Normal | Standard |
| 40-59 | Depleted soil | -25% shorter | Reduced reach |
| 0-39 | Toxic soil | -50% shorter | Severely limited |

### Technical Components

**Database Changes:**
- Add `soil_health` score to user profiles
- Add `soil_nutrients` table tracking interactions
- Add `toxicity_events` table for negative patterns

**Background Analysis:**
- ML toxicity detection (using existing transformers)
- Sentiment analysis on interactions
- Pattern detection for spam/abuse

**API Endpoints:**
- `GET /api/v1/users/{id}/soil-health` - View soil composition
- `GET /api/v1/garden/nutrients` - Recent interactions
- `POST /api/v1/moderation/toxicity-report` - Manual report

**Frontend:**
- Soil health dashboard with visual meter
- Nutrient/toxin breakdown chart
- Tips for improving soil quality

### Learning Outcomes
- User reputation systems
- Behavioral scoring
- ML integration for content analysis
- Organic moderation

---

## Prototype Option C3: Pollination System

### Concept
Content discovery via **semantic similarity**. Posts "pollinate" each other based on meaning, not just hashtags or follows.

### How Pollination Works

1. **Embedding Generation:**
   - ML model creates vector embeddings for each post
   - Captures semantic meaning beyond keywords

2. **Pollination Paths:**
   - Vector similarity search finds related content
   - Users discover posts that resonate with their interests
   - Cross-garden connections form naturally

3. **Discovery Feed:**
   - Not algorithmic ranking
   - Organic exploration based on shared themes
   - Visual pollination trails showing connections

### Technical Components

**ML Service:**
- Sentence transformer model (MiniLM or SBERT)
- Vector database (FAISS or Milvus)
- Embedding generation pipeline
- Similarity search API

**Database Changes:**
- Store embedding vectors in vector DB
- Track pollination relationships
- Log discovery patterns

**API Endpoints:**
- `POST /api/v1/seeds/{id}/pollinate` - Generate related seeds
- `GET /api/v1/discovery/pollination-feed` - Discovery feed
- `GET /api/v1/seeds/{id}/pollination-paths` - Show connections

**Frontend:**
- "Pollinate" button on posts
- Visual pollination trail (connected nodes)
- Discovery feed with explanation of connections
- Animated pollen particles (subtle effect)

### Learning Outcomes
- Vector embeddings and semantic search
- ML model integration
- Vector database usage
- Graph visualization

---

## Implementation Roadmap

### Phase 1: Lifecycle Engine (Week 1-2)
Build C1 to establish core Garden metaphor and prove the concept works.

### Phase 2: Soil Health (Week 3-4)
Add C2 to enable organic moderation and user reputation.

### Phase 3: Pollination (Week 5-8)
Integrate C3 for unique discovery mechanism. Requires ML infrastructure.

---

## Success Metrics

**For C1 (Lifecycle):**
- Users understand lifecycle stages
- Engagement increases in sprout/vine stages
- Natural expiry feels organic, not jarring

**For C2 (Soil Health):**
- Toxic behavior decreases
- Users value their soil score
- High-quality gardens emerge

**For C3 (Pollination):**
- Discovery rate improves
- Users find unexpected connections
- Pollination feels magical, not algorithmic

---

## Technical Stack Requirements

| Feature | Requirements |
|---------|-------------|
| C1: Lifecycle | Python worker, Postgres, Redis, Celery/APScheduler |
| C2: Soil Health | ML toxicity model, sentiment analysis, scoring engine |
| C3: Pollination | Vector DB (FAISS), sentence transformers, graph rendering |

---

## Next Steps

1. ✅ **Start with C1** (Lifecycle Engine) - simplest, most impactful
2. Validate the Garden metaphor resonates with users
3. Build C2 and C3 incrementally
4. Eventually merge all three into unified Garden ecosystem

---

*Document created: 2025-11-25*  
*Status: C1 (Lifecycle Engine) - IN PROGRESS*
