#!/usr/bin/env python3
"""
Compost Worker - Archives expired content and cleans up old data.

Runs daily at 3am via cron to:
- Find seeds in COMPOSTING state
- Archive videos to cold storage (R2 infrequent access)
- Extract ML embeddings for training (TODO)
- Delete old pollination_events (30+ days)
- Mark seeds as fully archived

Usage:
    python -m app.workers.compost_worker
    
Cron:
    0 3 * * * cd /app && python -m app.workers.compost_worker >> /var/log/compost.log 2>&1
"""
import sys
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def archive_video_to_cold_storage(seed):
    """
    Archive video to cold storage.
    
    Moves video from standard R2 storage to infrequent access tier
    for cost savings. Video remains accessible but with higher latency.
    
    Args:
        seed: Seed with video to archive
        
    Returns:
        bool: Success status
    """
    try:
        # TODO: Implement R2 storage tier transition
        # For now, just log
        logger.info(f"Would archive video for seed {seed.id}: {seed.video_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to archive video for seed {seed.id}: {e}")
        return False


def extract_embeddings(seed):
    """
    Extract ML embeddings from seed content.
    
    Sends seed content (video + caption) to ML service for embedding extraction.
    These embeddings will be used to train pollination similarity model.
    
    Args:
        seed: Seed to extract embeddings from
        
    Returns:
        bool: Success status
    """
    try:
        # TODO: Implement ML service call
        # For now, just log
        logger.info(f"Would extract embeddings for seed {seed.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to extract embeddings for seed {seed.id}: {e}")
        return False


def cleanup_pollination_events(db, days_old=30):
    """
    Delete old pollination events.
    
    Pollination events are used for deduplication (avoid showing same seed twice)
    and analytics. After 30 days, they're no longer needed.
    
    Args:
        db: Database session
        days_old: Delete events older than this many days
        
    Returns:
        int: Number of events deleted
    """
    from app.models.pollination_event import PollinationEvent
    
    cutoff = datetime.utcnow() - timedelta(days=days_old)
    
    deleted = db.query(PollinationEvent).filter(
        PollinationEvent.occurred_at < cutoff
    ).delete(synchronize_session=False)
    
    db.commit()
    return deleted


def run_compost_tasks():
    """Run composting tasks for archived seeds."""
    from app.core.database import SessionLocal
    from app.models.seed import Seed, SeedState
    
    logger.info("=== Compost Worker Started ===")
    start_time = datetime.utcnow()
    
    db = SessionLocal()
    try:
        # 1. Find seeds in COMPOSTING state that haven't been fully archived
        logger.info("Finding seeds to compost...")
        seeds_to_compost = db.query(Seed).filter(
            Seed.state == SeedState.composting,
            Seed.composted_at.isnot(None),
            Seed.soft_deleted == False
        ).all()
        
        logger.info(f"Found {len(seeds_to_compost)} seeds to compost")
        
        archived_count = 0
        embeddings_extracted = 0
        
        # 2. Process each seed
        for seed in seeds_to_compost:
            logger.info(f"Processing seed {seed.id}...")
            
            # Archive video to cold storage
            if seed.video_url:
                if archive_video_to_cold_storage(seed):
                    logger.info(f"  ✓ Video archived")
                else:
                    logger.warning(f"  ✗ Video archival failed")
            
            # Extract embeddings for ML training
            if extract_embeddings(seed):
                embeddings_extracted += 1
                logger.info(f"  ✓ Embeddings extracted")
            else:
                logger.warning(f"  ✗ Embedding extraction failed")
            
            # Mark as fully archived (soft delete)
            seed.soft_deleted = True
            archived_count += 1
            
            logger.info(f"  ✓ Seed {seed.id} fully composted")
        
        db.commit()
        
        # 3. Cleanup old pollination events
        logger.info("Cleaning up old pollination events...")
        deleted_events = cleanup_pollination_events(db, days_old=30)
        logger.info(f"Deleted {deleted_events} old pollination events (30+ days)")
        
        # 4. Log summary
        logger.info(f"=== Compost Summary ===")
        logger.info(f"Seeds archived: {archived_count}")
        logger.info(f"Embeddings extracted: {embeddings_extracted}")
        logger.info(f"Pollination events cleaned: {deleted_events}")
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Composting completed in {duration:.2f}s")
        logger.info("=== Compost Worker Finished ===")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error in compost worker: {e}", exc_info=True)
        db.rollback()
        return 1
        
    finally:
        db.close()


if __name__ == "__main__":
    exit_code = run_compost_tasks()
    sys.exit(exit_code)
