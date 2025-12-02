"""
Soil Service - Manages comments (soil) and voting (nutrients).

Handles:
- Adding soil (comments) to seeds
- Voting on soil (nitrogen/toxin)
- Applying nutrient effects to seeds and vines
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.seed import Seed
from app.models.vine import Vine
from app.models.soil import Soil
from app.models.nutrient import Nutrient, NutrientType
from app.garden.lifecycle import LifecycleEngine


class SoilService:
    """Service for managing soil (comments) and nutrients (votes)."""
    
    def __init__(self, db: Session):
        """Initialize soil service with database session."""
        self.db = db
        self.lifecycle = LifecycleEngine(db)
    
    def add_soil(self, seed_id: str, vine_id: str, content: str) -> Soil:
        """
        Add soil (comment) to a seed.
        
        Args:
            seed_id: ID of seed to comment on
            vine_id: ID of vine (user) commenting
            content: Comment text
        
        Returns:
            Soil: Created comment
        """
        # Create soil
        soil = Soil(
            seed_id=seed_id,
            vine_id=vine_id,
            content=content
        )
        self.db.add(soil)
        
        # Update vine stats
        vine = self.db.query(Vine).filter(Vine.id == vine_id).first()
        if vine:
            vine.add_soil()
        
        self.db.commit()
        self.db.refresh(soil)
        return soil
    
    def add_nitrogen(self, soil_id: str, vine_id: str) -> Nutrient:
        """
        Add nitrogen (upvote) to soil.
        
        Extends parent seed lifespan by 6 hours.
        
        Args:
            soil_id: ID of soil to upvote
            vine_id: ID of vine voting
        
        Returns:
            Nutrient: Created nutrient vote
        
        Raises:
            IntegrityError: If vine already voted on this soil
        """
        # Get soil and seed
        soil = self.db.query(Soil).filter(Soil.id == soil_id).first()
        if not soil:
            raise ValueError(f"Soil {soil_id} not found")
        
        seed = self.db.query(Seed).filter(Seed.id == soil.seed_id).first()
        if not seed:
            raise ValueError(f"Seed {soil.seed_id} not found")
        
        # Check if already voted
        existing = self.db.query(Nutrient).filter(
            Nutrient.soil_id == soil_id,
            Nutrient.vine_id == vine_id
        ).first()
        
        if existing:
            # Change vote to nitrogen if was toxin
            if existing.type == NutrientType.TOXIN:
                soil.remove_toxin()
                existing.type = NutrientType.NITROGEN
                soil.add_nitrogen()
            else:
                # Already upvoted, no-op
                self.db.commit()
                return existing
        else:
            # Create new nitrogen vote
            nutrient = Nutrient(
                soil_id=soil_id,
                vine_id=vine_id,
                type=NutrientType.NITROGEN
            )
            self.db.add(nutrient)
            soil.add_nitrogen()
        
        # Apply effects to seed
        self.lifecycle.apply_nutrient_to_seed(seed, soil)
        
        # Update vine soil health (positive contribution)
        commenter_vine = self.db.query(Vine).filter(Vine.id == soil.vine_id).first()
        if commenter_vine:
            commenter_vine.adjust_soil_health(0.01)  # Small boost for upvoted comment
        
        self.db.commit()
        
        if existing:
            return existing
        return nutrient
    
    def add_toxin(self, soil_id: str, vine_id: str) -> Nutrient:
        """
        Add toxin (downvote) to soil.
        
        If soil reaches 5+ toxins, it's deleted and parent seed composted.
        
        Args:
            soil_id: ID of soil to downvote
            vine_id: ID of vine voting
        
        Returns:
            Nutrient: Created nutrient vote
        """
        # Get soil and seed
        soil = self.db.query(Soil).filter(Soil.id == soil_id).first()
        if not soil:
            raise ValueError(f"Soil {soil_id} not found")
        
        seed = self.db.query(Seed).filter(Seed.id == soil.seed_id).first()
        if not seed:
            raise ValueError(f"Seed {soil.seed_id} not found")
        
        # Check if already voted
        existing = self.db.query(Nutrient).filter(
            Nutrient.soil_id == soil_id,
            Nutrient.vine_id == vine_id
        ).first()
        
        if existing:
            # Change vote to toxin if was nitrogen
            if existing.type == NutrientType.NITROGEN:
                soil.remove_nitrogen()
                existing.type = NutrientType.TOXIN
                soil.add_toxin()
            else:
                # Already downvoted, no-op
                self.db.commit()
                return existing
        else:
            # Create new toxin vote
            nutrient = Nutrient(
                soil_id=soil_id,
                vine_id=vine_id,
                type=NutrientType.TOXIN
            )
            self.db.add(nutrient)
            soil.add_toxin()
        
        # Apply effects to seed (may trigger composting if toxic)
        self.lifecycle.apply_nutrient_to_seed(seed, soil)
        
        # Update vine soil health (negative contribution)
        commenter_vine = self.db.query(Vine).filter(Vine.id == soil.vine_id).first()
        if commenter_vine and soil.is_toxic:
            commenter_vine.adjust_soil_health(-0.1)  # Penalty for toxic comment
        
        self.db.commit()
        
        if existing:
            return existing
        return nutrient
    
    def remove_vote(self, soil_id: str, vine_id: str) -> bool:
        """
        Remove vote from soil.
        
        Args:
            soil_id: ID of soil
            vine_id: ID of vine
        
        Returns:
            bool: True if vote was removed
        """
        nutrient = self.db.query(Nutrient).filter(
            Nutrient.soil_id == soil_id,
            Nutrient.vine_id == vine_id
        ).first()
        
        if not nutrient:
            return False
        
        # Get soil
        soil = self.db.query(Soil).filter(Soil.id == soil_id).first()
        if not soil:
            return False
        
        # Remove vote
        if nutrient.type == NutrientType.NITROGEN:
            soil.remove_nitrogen()
        else:
            soil.remove_toxin()
        
        self.db.delete(nutrient)
        self.db.commit()
        return True
    
    def get_soil_for_seed(self, seed_id: str, skip: int = 0, limit: int = 50) -> list[Soil]:
        """
        Get soil (comments) for a seed.
        
        Args:
            seed_id: ID of seed
            skip: Pagination offset
            limit: Max results
        
        Returns:
            list[Soil]: List of soil comments
        """
        return self.db.query(Soil).filter(
            Soil.seed_id == seed_id,
            Soil.soft_deleted == False
        ).order_by(
            Soil.nutrient_score.desc(),  # Best comments first
            Soil.added_at.desc()
        ).offset(skip).limit(limit).all()
