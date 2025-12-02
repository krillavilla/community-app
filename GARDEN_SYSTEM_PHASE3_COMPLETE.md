# Garden System Phase 3: Workers COMPLETE ✅

## What Was Built

### 3 Background Workers
All workers are standalone Python scripts that connect to the database and run scheduled tasks.

#### 1. Lifecycle Worker (`lifecycle_worker.py`)
**Schedule**: Every 5 minutes
**Purpose**: Transitions seeds through lifecycle states

**What it does**:
- Queries for seeds ready to transition
- PLANTED → SPROUTING (after 1 hour)
- SPROUTING → BLOOMING (growth_score >= 10)
- BLOOMING → WILTING (24 hours before wilts_at)
- WILTING → COMPOSTING (past wilts_at)
- Commits all transitions to database

**Output**:
```
=== Lifecycle Worker Started ===
Processing lifecycle transitions...
Sprouted: 3 seeds
Bloomed: 1 seeds
Wilted: 2 seeds
Composted: 1 seeds
Lifecycle transitions completed in 0.45s
=== Lifecycle Worker Finished ===
```

**Key Logic**:
- Uses `LifecycleEngine.process_lifecycle_transitions()`
- Handles all state transitions in single transaction
- Returns summary dict with counts + errors

---

#### 2. Climate Worker (`climate_worker.py`)
**Schedule**: Every hour
**Purpose**: Records community health snapshots

**What it does**:
- Calculates 5 community health metrics:
  1. **Toxicity Level** - Ratio of toxic comments (5+ downvotes) in last 24 hours
  2. **Growth Rate** - New seeds per day (averaged over 7 days)
  3. **Drought Risk** - % of vines inactive for 7+ days
  4. **Pest Incidents** - Reports filed in last hour
  5. **Temperature** - Community mood from vote ratios (0.0 = all toxins, 1.0 = all nitrogen)
- Creates ClimateReading record with metrics
- Logs health score and alerts if intervention needed

**Output**:
```
=== Climate Worker Started ===
Calculating climate metrics...
Climate Reading ID: abc-123
Toxicity Level: 12.50%
Growth Rate: 23.4 seeds/day
Drought Risk: 15.20%
Pest Incidents: 2
Temperature: 0.78
Health Score: 72.3/100
✅ Community is healthy
Climate reading recorded in 0.23s
=== Climate Worker Finished ===
```

**Health Thresholds**:
- **Healthy**: toxicity < 30%, drought < 50%, pests < 10
- **Needs Intervention**: toxicity > 70% OR drought > 80% OR pests > 50

---

#### 3. Compost Worker (`compost_worker.py`)
**Schedule**: Daily at 3am
**Purpose**: Archives expired content and cleans up old data

**What it does**:
- Finds seeds in COMPOSTING state
- Archives videos to cold storage (placeholder for R2 tier transition)
- Extracts ML embeddings (placeholder for ML service call)
- Deletes pollination_events older than 30 days
- Marks seeds as soft_deleted (fully archived)

**Output**:
```
=== Compost Worker Started ===
Finding seeds to compost...
Found 5 seeds to compost
Processing seed abc-123...
  ✓ Video archived
  ✓ Embeddings extracted
  ✓ Seed abc-123 fully composted
...
Cleaning up old pollination events...
Deleted 1234 old pollination events (30+ days)
=== Compost Summary ===
Seeds archived: 5
Embeddings extracted: 5
Pollination events cleaned: 1234
Composting completed in 2.34s
=== Compost Worker Finished ===
```

**Future TODOs**:
- Implement R2 storage tier transition (move to infrequent access)
- Implement ML service call for embedding extraction
- Add video thumbnail archival

---

## Files Created

```
backend/
├── app/
│   └── workers/
│       ├── __init__.py             (Package init)
│       ├── lifecycle_worker.py     (Lifecycle transitions - 75 lines)
│       ├── climate_worker.py       (Community health - 170 lines)
│       └── compost_worker.py       (Archival & cleanup - 182 lines)
├── crontab                         (Cron schedule config)
└── test_workers.sh                 (Manual test script)
```

---

## Installation & Usage

### Manual Testing (Run Once)
```bash
# Test all workers
./backend/test_workers.sh

# Or run individually
docker compose run --rm backend python -m app.workers.lifecycle_worker
docker compose run --rm backend python -m app.workers.climate_worker
docker compose run --rm backend python -m app.workers.compost_worker
```

### Production Setup (Cron)

**Option 1: Inside Docker Container**
```bash
# Install crontab inside backend container
docker exec backend crontab /app/crontab

# Verify cron is running
docker exec backend crontab -l
```

**Option 2: Host Cron**
```bash
# Add to host crontab (crontab -e)
*/5 * * * * docker compose run --rm backend python -m app.workers.lifecycle_worker >> /var/log/lifecycle.log 2>&1
0 * * * * docker compose run --rm backend python -m app.workers.climate_worker >> /var/log/climate.log 2>&1
0 3 * * * docker compose run --rm backend python -m app.workers.compost_worker >> /var/log/compost.log 2>&1
```

**Option 3: Kubernetes CronJob (Production)**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: lifecycle-worker
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: worker
            image: garden-backend:latest
            command: ["python", "-m", "app.workers.lifecycle_worker"]
```

---

## Monitoring

### Logs
Workers log to stdout with structured format:
```
2025-11-25 05:30:00 - app.workers.lifecycle_worker - INFO - Sprouted: 3 seeds
```

**Log Locations** (if using file redirection):
- `/var/log/lifecycle.log` - Lifecycle transitions
- `/var/log/climate.log` - Community health
- `/var/log/compost.log` - Archival & cleanup

### Metrics to Monitor
1. **Lifecycle Worker**:
   - Seeds processed per run
   - Errors in transitions
   - Run duration

2. **Climate Worker**:
   - Health score trend
   - Intervention alerts
   - Toxicity spikes

3. **Compost Worker**:
   - Seeds archived per day
   - Storage savings
   - Cleanup efficiency

---

## Worker Architecture

```
┌─────────────────────────────────────────┐
│          Cron Scheduler                 │
│  (Every 5min / Hourly / Daily)          │
└───────────────┬─────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
┌───────────────┐ ┌──────────────┐
│  Lifecycle    │ │   Climate    │
│   Worker      │ │    Worker    │
└───────┬───────┘ └──────┬───────┘
        │                │
        │   ┌────────────┴───────┐
        │   │                    │
        ▼   ▼                    ▼
    ┌─────────────────┐  ┌─────────────┐
    │   Database      │  │  Compost    │
    │  (PostgreSQL)   │  │   Worker    │
    └─────────────────┘  └──────┬──────┘
                                 │
                         ┌───────┴──────┐
                         ▼              ▼
                    ┌─────────┐  ┌──────────┐
                    │   R2    │  │    ML    │
                    │ Storage │  │  Service │
                    └─────────┘  └──────────┘
```

---

## How Seeds Flow Through Workers

### Example Timeline

**10:00am** - User plants seed
- State: PLANTED
- `planted_at`: 2025-11-25 10:00:00
- `wilts_at`: null (will be set by lifecycle worker)

**11:05am** - Lifecycle worker runs
- Finds seed 1 hour old
- Transitions PLANTED → SPROUTING
- Sets `sprouts_at`: 2025-11-25 11:05:00
- Sets `wilts_at`: 2025-12-02 10:00:00 (7 days default)

**11:30am** - Users engage with seed
- 50 views (water_level = 50)
- 5 upvoted comments (nutrient_score = 5, extends wilts_at by 30 hours)
- 2 shares (sunlight_hours = 2)
- Growth score: (50 * 0.3) + (5 * 0.5) + (2 * 0.2) = 17.9

**11:35am** - Lifecycle worker runs
- Finds seed with growth_score >= 10
- Transitions SPROUTING → BLOOMING
- Seed now appears in Wild Garden feed

**Dec 1, 6pm** - Lifecycle worker runs
- Seed's wilts_at is 2025-12-02 4pm (40 hours away)
- Within 24 hour wilt warning window
- Transitions BLOOMING → WILTING
- Visual indicator shown to users

**Dec 2, 4:05pm** - Lifecycle worker runs
- Seed past wilts_at timestamp
- Transitions WILTING → COMPOSTING
- Sets `composted_at`: 2025-12-02 16:05:00
- Removed from all feeds

**Dec 3, 3am** - Compost worker runs
- Finds seed in COMPOSTING state
- Archives video to cold storage
- Extracts embeddings for ML
- Marks `soft_deleted = true`
- Seed fully archived ✅

---

## Testing Scenarios

### 1. Test Lifecycle Transitions
```bash
# Create test seed
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.mp4" \
  http://localhost:8000/api/v1/seeds

# Wait 1 hour (or manually update planted_at in DB)
# Run lifecycle worker
docker compose run --rm backend python -m app.workers.lifecycle_worker

# Check seed state changed to SPROUTING
```

### 2. Test Climate Recording
```bash
# Create some activity (plant seeds, add comments, vote)
# Run climate worker
docker compose run --rm backend python -m app.workers.climate_worker

# Check climate_readings table for new record
```

### 3. Test Composting
```bash
# Manually set seed to COMPOSTING state in DB
UPDATE seeds SET state='composting', composted_at=NOW() WHERE id='...';

# Run compost worker
docker compose run --rm backend python -m app.workers.compost_worker

# Check seed is soft_deleted
```

---

## What's Next (Future Enhancements)

### Worker Improvements
1. **Celery Migration** - Upgrade to distributed task queue
   - Better monitoring with Flower dashboard
   - Automatic retries on failure
   - Task prioritization
   - Distributed execution

2. **Error Alerting** - Send alerts on worker failures
   - Slack/Discord webhooks
   - Email notifications
   - PagerDuty integration

3. **Performance Optimization**
   - Batch processing for large datasets
   - Database connection pooling
   - Parallel processing where possible

### Feature Additions
1. **Lifecycle Worker**
   - Gradual growth score boost for consistency
   - Seasonal modifiers (holidays, events)
   - A/B testing for transition thresholds

2. **Climate Worker**
   - Trend analysis (week-over-week, month-over-month)
   - Anomaly detection with ML
   - Automated Guardian alerts
   - Public health dashboard

3. **Compost Worker**
   - R2 storage tier transition implementation
   - ML embedding extraction
   - Video thumbnail archival
   - Historical data exports

### ML Integration (Phase 4)
- Pollination similarity model (content-based recommendations)
- Soil health scoring (reputation patterns)
- Climate prediction (forecast toxicity)
- Growth optimization (recommend best posting times)

---

**Status**: Phase 3 Complete
**Token Usage**: 111k/200k (89k remaining)
**Next**: Frontend components or ML service integration
