"""
Lifecycle Engine - Manages seed state transitions.

The lifecycle engine is responsible for transitioning seeds through states:
PLANTED → SPROUTING → BLOOMING → WILTING → COMPOSTING

Transitions are based on:
- Time elapsed since creation
- Growth metrics (water, nutrients, sunlight)
- Soil health
- Engagement patterns
"""
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.seed import Seed, SeedState
from app.models.vine import Vine
from app.models.soil import Soil


class LifecycleEngine:
    """Engine for managing seed lifecycle transitions."""
    
    # Lifecycle timing constants (in hours)
    SPROUTING_DELAY = 1  # Seed sprouts after 1 hour (video processing time)
    BLOOM_THRESHOLD = 10  # Minimum growth score to bloom
    WILT_WARNING_HOURS = 24  # Start wilting 24 hours before expiry
    DEFAULT_LIFESPAN_HOURS = 168  # Default: 7 days
    MAX_LIFESPAN_DAYS = 30  # Max: 30 days
    
    # Growth score weights
    WATER_WEIGHT = 0.3  # Views
    NUTRIENT_WEIGHT = 0.5  # Comment quality
    SUNLIGHT_WEIGHT = 0.2  # Shares
    
    def __init__(self, db: Session):
        """Initialize lifecycle engine with database session."""
        self.db = db
    
    def process_lifecycle_transitions(self) -> dict:
        """
        Process all seed lifecycle transitions.
        
        This should be called periodically (e.g., every 5 minutes) by a cron worker.
        
        Returns:
            dict: Summary of transitions made
        """
        summary = {
            "sprouted": 0,
            "bloomed": 0,
            "wilted": 0,
            "composted": 0,
            "errors": []
        }
        
        try:
            # 1. Transition PLANTED → SPROUTING
            planted_seeds = self._get_seeds_ready_to_sprout()
            for seed in planted_seeds:
                self._sprout_seed(seed)
                summary["sprouted"] += 1
            
            # 2. Transition SPROUTING → BLOOMING
            sprouting_seeds = self._get_seeds_ready_to_bloom()
            for seed in sprouting_seeds:
                self._bloom_seed(seed)
                summary["bloomed"] += 1
            
            # 3. Transition BLOOMING → WILTING
            blooming_seeds = self._get_seeds_ready_to_wilt()
            for seed in blooming_seeds:
                self._wilt_seed(seed)
                summary["wilted"] += 1
            
            # 4. Transition WILTING → COMPOSTING
            wilting_seeds = self._get_seeds_ready_to_compost()
            for seed in wilting_seeds:
                self._compost_seed(seed)
                summary["composted"] += 1
            
            self.db.commit()
        
        except Exception as e:
            self.db.rollback()
            summary["errors"].append(str(e))
        
        return summary
    
    def _get_seeds_ready_to_sprout(self) -> List[Seed]:
        """Get planted seeds ready to sprout."""
        cutoff = datetime.utcnow() - timedelta(hours=self.SPROUTING_DELAY)
        return self.db.query(Seed).filter(
            and_(
                Seed.state == SeedState.planted,
                Seed.planted_at <= cutoff,
                Seed.soft_deleted == False
            )
        ).all()
    
    def _get_seeds_ready_to_bloom(self) -> List[Seed]:
        """Get sprouting seeds with enough growth to bloom."""
        return self.db.query(Seed).filter(
            and_(
                Seed.state == SeedState.sprouting,
                Seed.soft_deleted == False
            )
        ).all()
    
    def _get_seeds_ready_to_wilt(self) -> List[Seed]:
        """Get blooming seeds approaching expiration."""
        now = datetime.utcnow()
        wilt_cutoff = now + timedelta(hours=self.WILT_WARNING_HOURS)
        
        return self.db.query(Seed).filter(
            and_(
                Seed.state == SeedState.blooming,
                or_(
                    and_(Seed.wilts_at.isnot(None), Seed.wilts_at <= wilt_cutoff),
                    Seed.wilts_at.is_(None)  # No expiry set, use default
                ),
                Seed.soft_deleted == False
            )
        ).all()
    
    def _get_seeds_ready_to_compost(self) -> List[Seed]:
        """Get wilting seeds past expiration."""
        now = datetime.utcnow()
        return self.db.query(Seed).filter(
            and_(
                Seed.state == SeedState.wilting,
                or_(
                    and_(Seed.wilts_at.isnot(None), Seed.wilts_at <= now),
                    Seed.wilts_at.is_(None)  # Fallback: wilt if no expiry
                ),
                Seed.soft_deleted == False
            )
        ).all()
    
    def _sprout_seed(self, seed: Seed):
        """Transition seed from PLANTED to SPROUTING."""
        seed.state = SeedState.sprouting
        seed.sprouts_at = datetime.utcnow()
        
        # Set initial expiration if not set
        if not seed.wilts_at:
            seed.wilts_at = seed.planted_at + timedelta(hours=self.DEFAULT_LIFESPAN_HOURS)
    
    def _bloom_seed(self, seed: Seed):
        """Transition seed from SPROUTING to BLOOMING."""
        growth_score = self._calculate_growth_score(seed)
        
        # Only bloom if growth score meets threshold
        if growth_score >= self.BLOOM_THRESHOLD:
            seed.state = SeedState.blooming
    
    def _wilt_seed(self, seed: Seed):
        """Transition seed from BLOOMING to WILTING."""
        seed.state = SeedState.wilting
        
        # Ensure wilts_at is set
        if not seed.wilts_at:
            seed.wilts_at = datetime.utcnow() + timedelta(hours=self.WILT_WARNING_HOURS)
    
    def _compost_seed(self, seed: Seed):
        """Transition seed from WILTING to COMPOSTING."""
        seed.state = SeedState.composting
        seed.composted_at = datetime.utcnow()
        
        # TODO: Extract embeddings for ML training
        # TODO: Archive video to cold storage
        # TODO: Update vine stats
    
    def _calculate_growth_score(self, seed: Seed) -> float:
        """
        Calculate seed growth score.
        
        Formula: (water * 0.3) + (nutrients * 0.5) + (sunlight * 0.2)
        Multiplied by soil_health.
        """
        base_score = (
            (seed.water_level * self.WATER_WEIGHT) +
            (seed.nutrient_score * self.NUTRIENT_WEIGHT) +
            (seed.sunlight_hours * self.SUNLIGHT_WEIGHT)
        )
        return base_score * seed.soil_health
    
    def apply_nutrient_to_seed(self, seed: Seed, soil: Soil):
        """
        Apply nutrient effects from soil to seed.
        
        Positive nutrients extend lifespan (+6 hours per upvote, max 30 days).
        Negative nutrients (5+ toxins) trigger immediate composting.
        """
        if soil.is_toxic:
            # Toxic comment: compost seed immediately
            seed.state = SeedState.composting
            seed.composted_at = datetime.utcnow()
            seed.wilts_at = datetime.utcnow()
        elif soil.is_nourishing:
            # Nourishing comment: extend lifespan
            hours_to_add = soil.nitrogen_count * 6  # 6 hours per upvote
            seed.extend_lifespan(hours_to_add)
            
            # Update nutrient score
            seed.nutrient_score += soil.nutrient_score
        
        self.db.commit()
    
    def water_seed(self, seed: Seed):
        """Add water (view) to seed."""
        seed.add_water(1)
        
        # Water the vine too
        vine = self.db.query(Vine).filter(Vine.id == seed.vine_id).first()
        if vine:
            vine.water()
        
        self.db.commit()
    
    def shine_sunlight(self, seed: Seed):
        """Add sunlight (share) to seed."""
        seed.add_sunlight(1)
        
        # Give sunlight to vine
        vine = self.db.query(Vine).filter(Vine.id == seed.vine_id).first()
        if vine:
            vine.receive_sunlight(1)
        
        self.db.commit()
