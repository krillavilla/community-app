"""
Garden Feeds - Wild Garden (FYP), Garden Rows (Following), Greenhouse.

Builds different types of feeds:
- Wild Garden: Algorithm-driven discovery (For You Page)
- Garden Rows: Chronological following feed
- Greenhouse: Private/saved seeds
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.seed import Seed, SeedState, GardenType, FenceType
from app.models.vine import Vine
from app.models.fence import Fence
from app.models.pollination_event import PollinationEvent


class GardenFeedService:
    """Service for building garden feeds."""
    
    def __init__(self, db: Session):
        """Initialize feed service with database session."""
        self.db = db
    
    def get_wild_garden(
        self, 
        vine_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Seed]:
        """
        Get Wild Garden feed (For You Page).
        
        Algorithm prioritizes:
        1. Blooming seeds (active growth)
        2. High growth scores
        3. Diversity (not all from same vine)
        4. Seeds not seen recently
        
        Args:
            vine_id: Requesting vine ID
            skip: Pagination offset
            limit: Max results
        
        Returns:
            List[Seed]: Curated feed
        """
        # Get seeds seen in last 24 hours to avoid duplicates
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        seen_seed_ids = self.db.query(PollinationEvent.seed_id).filter(
            and_(
                PollinationEvent.vine_id == vine_id,
                PollinationEvent.occurred_at >= recent_cutoff
            )
        ).subquery()
        
        # Build query: blooming seeds, high growth, not recently seen, public
        seeds = self.db.query(Seed).filter(
            and_(
                Seed.state == SeedState.blooming,
                Seed.soft_deleted == False,
                Seed.privacy_fence == FenceType.PUBLIC,
                Seed.id.notin_(seen_seed_ids)
            )
        ).order_by(
            # Order by growth score (calculated in-query)
            desc(
                (Seed.water_level * 0.3) +
                (Seed.nutrient_score * 0.5) +
                (Seed.sunlight_hours * 0.2) *
                Seed.soil_health
            ),
            desc(Seed.planted_at)  # Secondary: newer seeds
        ).offset(skip).limit(limit).all()
        
        # Track pollination events
        for seed in seeds:
            event = PollinationEvent(
                seed_id=seed.id,
                vine_id=vine_id,
                pathway='wild_garden'
            )
            self.db.add(event)
        
        self.db.commit()
        return seeds
    
    def get_garden_rows(
        self,
        vine_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Seed]:
        """
        Get Garden Rows feed (Following).
        
        Chronological feed of seeds from connections.
        
        Args:
            vine_id: Requesting vine ID
            skip: Pagination offset
            limit: Max results
        
        Returns:
            List[Seed]: Chronological feed
        """
        # Get vines in fence (connections)
        fence_vine_ids = self.db.query(Fence.member_vine_id).filter(
            Fence.vine_id == vine_id
        ).subquery()
        
        # Get blooming/sprouting seeds from connections
        seeds = self.db.query(Seed).filter(
            and_(
                Seed.vine_id.in_(fence_vine_ids),
                or_(
                    Seed.state == SeedState.blooming,
                    Seed.state == SeedState.sprouting
                ),
                Seed.soft_deleted == False,
                or_(
                    Seed.privacy_fence == FenceType.PUBLIC,
                    Seed.privacy_fence == FenceType.FRIENDS
                )
            )
        ).order_by(
            desc(Seed.planted_at)  # Chronological
        ).offset(skip).limit(limit).all()
        
        # Track pollination events
        for seed in seeds:
            event = PollinationEvent(
                seed_id=seed.id,
                vine_id=vine_id,
                pathway='rows'
            )
            self.db.add(event)
        
        self.db.commit()
        return seeds
    
    def get_greenhouse(
        self,
        vine_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Seed]:
        """
        Get Greenhouse feed (Private/Saved).
        
        Shows:
        - Own seeds
        - Saved/bookmarked seeds
        
        Args:
            vine_id: Requesting vine ID
            skip: Pagination offset
            limit: Max results
        
        Returns:
            List[Seed]: Private feed
        """
        # Get own seeds (all states except composting)
        seeds = self.db.query(Seed).filter(
            and_(
                Seed.vine_id == vine_id,
                Seed.state != SeedState.composting,
                Seed.soft_deleted == False
            )
        ).order_by(
            desc(Seed.planted_at)
        ).offset(skip).limit(limit).all()
        
        return seeds
    
    def get_seed_by_id(self, seed_id: str, viewer_vine_id: str) -> Optional[Seed]:
        """
        Get specific seed by ID with privacy check.
        
        Args:
            seed_id: Seed ID
            viewer_vine_id: Vine viewing the seed
        
        Returns:
            Optional[Seed]: Seed if accessible, None otherwise
        """
        seed = self.db.query(Seed).filter(Seed.id == seed_id).first()
        if not seed:
            return None
        
        # Check privacy
        if seed.privacy_fence == FenceType.PUBLIC:
            # Public seed, anyone can view
            return seed
        
        # Check if viewer is creator
        if str(seed.vine_id) == str(viewer_vine_id):
            return seed
        
        # Check if viewer is in fence
        if seed.privacy_fence == FenceType.PRIVATE:
            # Private seeds only visible to creator
            return None
        
        # Check fence membership
        in_fence = self.db.query(Fence).filter(
            and_(
                Fence.vine_id == seed.vine_id,
                Fence.member_vine_id == viewer_vine_id,
                Fence.fence_type == seed.privacy_fence
            )
        ).first()
        
        if in_fence:
            return seed
        
        return None
    
    def search_seeds(
        self,
        query: str,
        vine_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Seed]:
        """
        Search seeds by content.
        
        Args:
            query: Search query
            vine_id: Requesting vine ID
            skip: Pagination offset
            limit: Max results
        
        Returns:
            List[Seed]: Search results
        """
        # Simple text search (TODO: upgrade to full-text search)
        seeds = self.db.query(Seed).filter(
            and_(
                Seed.content.ilike(f"%{query}%"),
                or_(
                    Seed.state == SeedState.blooming,
                    Seed.state == SeedState.sprouting
                ),
                Seed.soft_deleted == False,
                Seed.privacy_fence == FenceType.PUBLIC
            )
        ).order_by(
            desc(Seed.planted_at)
        ).offset(skip).limit(limit).all()
        
        # Track pollination events
        for seed in seeds:
            event = PollinationEvent(
                seed_id=seed.id,
                vine_id=vine_id,
                pathway='search'
            )
            self.db.add(event)
        
        self.db.commit()
        return seeds
