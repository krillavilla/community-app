"""
ClimateReading model - Community health snapshots.

Climate readings capture overall community health metrics over time.
Used for anomaly detection and community moderation.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ClimateReading(Base):
    """
    ClimateReading model - community health snapshot.
    
    Periodic measurements of community health including toxicity,
    growth rate, drought risk (inactivity), and pest incidents (reports).
    """
    __tablename__ = "climate_readings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Timestamp
    measured_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Health metrics
    toxicity_level = Column(Float, nullable=False, default=0.0)      # Avg toxin ratio (0-1)
    growth_rate = Column(Float, nullable=False, default=0.0)         # New seeds per day
    drought_risk = Column(Float, nullable=False, default=0.0)        # Inactivity level (0-1)
    pest_incidents = Column(Integer, nullable=False, default=0)      # Reports filed
    temperature = Column(Float, nullable=False, default=0.5)         # Community mood (0-1)
    
    @property
    def is_healthy(self) -> bool:
        """
        Check if community is in healthy state.
        
        Healthy: low toxicity, moderate growth, low drought, few pests, neutral temp.
        """
        return (
            self.toxicity_level < 0.3 and
            self.drought_risk < 0.5 and
            self.pest_incidents < 10 and
            0.4 <= self.temperature <= 0.7
        )
    
    @property
    def needs_intervention(self) -> bool:
        """
        Check if community needs Guardian intervention.
        
        Critical: high toxicity OR high drought OR excessive pests.
        """
        return (
            self.toxicity_level > 0.7 or
            self.drought_risk > 0.8 or
            self.pest_incidents > 50
        )
    
    @property
    def health_score(self) -> float:
        """
        Calculate overall health score (0-100).
        
        Weighted combination of all metrics.
        """
        toxicity_penalty = self.toxicity_level * 40
        drought_penalty = self.drought_risk * 20
        pest_penalty = min(self.pest_incidents / 100.0, 1.0) * 20
        growth_bonus = min(self.growth_rate / 10.0, 1.0) * 10
        temp_score = (1.0 - abs(self.temperature - 0.5) * 2) * 10
        
        return max(0, 100 - toxicity_penalty - drought_penalty - pest_penalty + growth_bonus + temp_score)
    
    def __repr__(self):
        return f"<ClimateReading at {self.measured_at} - health {self.health_score:.1f}>"
