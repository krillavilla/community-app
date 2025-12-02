#!/usr/bin/env python3
"""
Climate Worker - Records community health snapshots.

Runs every hour via cron to:
- Calculate toxicity_level (ratio of toxic comments)
- Calculate growth_rate (new seeds per day)
- Calculate drought_risk (inactive vines %)
- Count pest_incidents (reports filed in last hour)
- Calculate temperature (community mood from votes)
- Store ClimateReading in database

Usage:
    python -m app.workers.climate_worker
    
Cron:
    0 * * * * cd /app && python -m app.workers.climate_worker >> /var/log/climate.log 2>&1
"""
import sys
import logging
from datetime import datetime, timedelta
from sqlalchemy import func

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def calculate_climate_metrics(db):
    """
    Calculate community health metrics.
    
    Returns:
        dict: Climate metrics
    """
    from app.models.seed import Seed, SeedState
    from app.models.soil import Soil
    from app.models.vine import Vine
    from app.models.report import Report
    
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(days=1)
    seven_days_ago = now - timedelta(days=7)
    
    # 1. Toxicity Level (ratio of toxic comments in last 24 hours)
    total_soil = db.query(Soil).filter(
        Soil.added_at >= one_day_ago,
        Soil.soft_deleted == False
    ).count()
    
    toxic_soil = db.query(Soil).filter(
        Soil.added_at >= one_day_ago,
        Soil.toxin_count >= 5,
        Soil.soft_deleted == False
    ).count()
    
    toxicity_level = (toxic_soil / total_soil) if total_soil > 0 else 0.0
    
    # 2. Growth Rate (new seeds per day, averaged over 7 days)
    new_seeds = db.query(Seed).filter(
        Seed.planted_at >= seven_days_ago
    ).count()
    
    growth_rate = new_seeds / 7.0
    
    # 3. Drought Risk (% of vines inactive for 7+ days)
    total_vines = db.query(Vine).count()
    
    inactive_vines = db.query(Vine).filter(
        Vine.last_watered_at < seven_days_ago
    ).count()
    
    drought_risk = (inactive_vines / total_vines) if total_vines > 0 else 0.0
    
    # 4. Pest Incidents (reports filed in last hour)
    pest_incidents = db.query(Report).filter(
        Report.created_at >= one_hour_ago
    ).count()
    
    # 5. Temperature (community mood from vote ratios in last 24 hours)
    # Get total nitrogen vs toxin counts
    soil_with_votes = db.query(Soil).filter(
        Soil.added_at >= one_day_ago,
        Soil.soft_deleted == False
    ).all()
    
    total_nitrogen = sum(s.nitrogen_count for s in soil_with_votes)
    total_toxins = sum(s.toxin_count for s in soil_with_votes)
    total_votes = total_nitrogen + total_toxins
    
    if total_votes > 0:
        # Temperature: 0.0 (all toxins) to 1.0 (all nitrogen)
        temperature = total_nitrogen / total_votes
    else:
        temperature = 0.5  # Neutral if no votes
    
    return {
        'toxicity_level': toxicity_level,
        'growth_rate': growth_rate,
        'drought_risk': drought_risk,
        'pest_incidents': pest_incidents,
        'temperature': temperature
    }


def record_climate_reading():
    """Record community health snapshot."""
    from app.core.database import SessionLocal
    from app.models.climate_reading import ClimateReading
    
    logger.info("=== Climate Worker Started ===")
    start_time = datetime.utcnow()
    
    db = SessionLocal()
    try:
        # Calculate metrics
        logger.info("Calculating climate metrics...")
        metrics = calculate_climate_metrics(db)
        
        # Create climate reading
        reading = ClimateReading(
            measured_at=start_time,
            toxicity_level=metrics['toxicity_level'],
            growth_rate=metrics['growth_rate'],
            drought_risk=metrics['drought_risk'],
            pest_incidents=metrics['pest_incidents'],
            temperature=metrics['temperature']
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)
        
        # Log results
        logger.info(f"Climate Reading ID: {reading.id}")
        logger.info(f"Toxicity Level: {reading.toxicity_level:.2%}")
        logger.info(f"Growth Rate: {reading.growth_rate:.1f} seeds/day")
        logger.info(f"Drought Risk: {reading.drought_risk:.2%}")
        logger.info(f"Pest Incidents: {reading.pest_incidents}")
        logger.info(f"Temperature: {reading.temperature:.2f}")
        logger.info(f"Health Score: {reading.health_score:.1f}/100")
        
        if reading.needs_intervention:
            logger.warning("⚠️  COMMUNITY NEEDS INTERVENTION - High toxicity/drought/pests")
        elif reading.is_healthy:
            logger.info("✅ Community is healthy")
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Climate reading recorded in {duration:.2f}s")
        logger.info("=== Climate Worker Finished ===")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error in climate worker: {e}", exc_info=True)
        return 1
        
    finally:
        db.close()


if __name__ == "__main__":
    exit_code = record_climate_reading()
    sys.exit(exit_code)
