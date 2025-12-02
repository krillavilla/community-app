#!/usr/bin/env python3
"""
Lifecycle Worker - Transitions seeds through lifecycle states.

Runs every 5 minutes via cron to:
- Transition PLANTED → SPROUTING (after 1 hour)
- Transition SPROUTING → BLOOMING (growth_score >= 10)
- Transition BLOOMING → WILTING (24hrs before expiration)
- Transition WILTING → COMPOSTING (past expiration)

Usage:
    python -m app.workers.lifecycle_worker
    
Cron:
    */5 * * * * cd /app && python -m app.workers.lifecycle_worker >> /var/log/lifecycle.log 2>&1
"""
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_lifecycle_transitions():
    """Run lifecycle transitions for all seeds using B2 lifecycle engine."""
    from app.core.database import SessionLocal
    from app.models.seed import Seed, LifecycleStage
    
    logger.info("=== Lifecycle Worker Started (B2 Engine) ===")
    start_time = datetime.utcnow()
    
    db = SessionLocal()
    try:
        # Get all non-composted seeds
        active_seeds = db.query(Seed).filter(
            Seed.lifecycle_stage != 'compost'
        ).all()
        
        logger.info(f"Processing {len(active_seeds)} active seeds...")
        
        transitions = {"sprout": 0, "vine": 0, "fruit": 0, "compost": 0}
        
        for seed in active_seeds:
            # Update engagement score
            seed.engagement_score = seed.calculate_engagement_score()
            
            # Check for expiry
            if seed.expiry_date and datetime.utcnow() > seed.expiry_date:
                seed.lifecycle_stage = LifecycleStage.COMPOST
                transitions["compost"] += 1
                logger.info(f"🍂 Composted seed {seed.id}")
                continue
            
            # Check for stage transition
            new_stage = seed.update_lifecycle_stage()
            
            if new_stage != seed.lifecycle_stage:
                old = seed.lifecycle_stage.value
                seed.lifecycle_stage = new_stage
                seed.lifecycle_updated_at = datetime.utcnow()
                transitions[new_stage.value] = transitions.get(new_stage.value, 0) + 1
                logger.info(f"{seed.lifecycle_emoji} Seed {seed.id}: {old} → {new_stage.value}")
        
        # Commit all changes
        db.commit()
        
        # Log results
        logger.info(f"Sprouted: {transitions.get('sprout', 0)} seeds")
        logger.info(f"Vined: {transitions.get('vine', 0)} seeds")
        logger.info(f"Fruited: {transitions.get('fruit', 0)} seeds")
        logger.info(f"Composted: {transitions['compost']} seeds")
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"✅ Lifecycle transitions completed in {duration:.2f}s")
        logger.info("=== Lifecycle Worker Finished ===")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Fatal error in lifecycle worker: {e}", exc_info=True)
        db.rollback()
        return 1
        
    finally:
        db.close()


if __name__ == "__main__":
    exit_code = run_lifecycle_transitions()
    sys.exit(exit_code)
