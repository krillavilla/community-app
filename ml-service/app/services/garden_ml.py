"""
Garden System ML Service.

Provides ML functionality for:
- Pollination: Content-based seed recommendations
- Soil Health: Reputation scoring from vote patterns
- Climate: Toxicity detection and forecasting
- Compost Learning: Embedding extraction from expired content
"""
from typing import List, Dict, Tuple
import numpy as np
from app.services.embeddings import embedding_service


class GardenMLService:
    """ML service for Garden System."""
    
    def calculate_pollination_similarity(
        self,
        seed_content: str,
        seed_embedding: List[float],
        candidate_seeds: List[Dict]
    ) -> List[Tuple[str, float]]:
        """
        Calculate pollination similarity between seed and candidates.
        
        Used for pollination-based recommendations (similar content discovery).
        
        Args:
            seed_content: Text content of seed
            seed_embedding: Precomputed embedding (or None to compute)
            candidate_seeds: List of dicts with 'id', 'content', 'embedding'
        
        Returns:
            List of (seed_id, similarity_score) tuples, sorted by score descending
        """
        # Get query embedding
        if seed_embedding is None:
            query_embedding = embedding_service.get_embedding(seed_content)
        else:
            query_embedding = np.array(seed_embedding)
        
        # Calculate similarities
        similarities = []
        for candidate in candidate_seeds:
            candidate_id = candidate['id']
            
            # Get candidate embedding
            if 'embedding' in candidate and candidate['embedding']:
                cand_embedding = np.array(candidate['embedding'])
            else:
                cand_embedding = embedding_service.get_embedding(candidate['content'])
            
            # Cosine similarity
            similarity = float(np.dot(query_embedding, cand_embedding))
            similarities.append((candidate_id, similarity))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities
    
    def extract_seed_embedding(self, seed_content: str) -> List[float]:
        """
        Extract embedding from seed content for pollination.
        
        Called by compost worker when archiving seeds.
        Embeddings stored for future similarity calculations.
        
        Args:
            seed_content: Text content of seed
        
        Returns:
            Embedding vector as list of floats
        """
        embedding = embedding_service.get_embedding(seed_content)
        return embedding.tolist()
    
    def score_soil_health(
        self,
        vine_vote_history: List[Dict]
    ) -> Dict[str, float]:
        """
        Score vine soil health based on voting patterns.
        
        Analyzes vine's voting behavior to detect:
        - Consistent quality contribution (upvotes good content)
        - Toxic behavior (downvotes everything)
        - Spam patterns (random voting)
        
        Args:
            vine_vote_history: List of dicts with 'type', 'soil_id', 'timestamp'
        
        Returns:
            Dict with health metrics
        """
        if not vine_vote_history:
            return {
                'health_score': 0.5,
                'consistency': 0.5,
                'quality_signal': 0.5
            }
        
        # Calculate metrics
        total_votes = len(vine_vote_history)
        nitrogen_votes = sum(1 for v in vine_vote_history if v['type'] == 'nitrogen')
        toxin_votes = total_votes - nitrogen_votes
        
        # Nitrogen ratio (0.0 = all toxins, 1.0 = all nitrogen)
        nitrogen_ratio = nitrogen_votes / total_votes if total_votes > 0 else 0.5
        
        # Healthy voting patterns: 60-80% nitrogen
        if 0.6 <= nitrogen_ratio <= 0.8:
            quality_signal = 1.0
        elif 0.4 <= nitrogen_ratio <= 0.9:
            quality_signal = 0.7
        else:
            quality_signal = 0.3  # Too extreme (all upvotes or all downvotes = suspicious)
        
        # Consistency: variance in voting behavior over time
        # TODO: Implement time-based consistency check
        consistency = 0.7
        
        # Overall health score
        health_score = (quality_signal * 0.7) + (consistency * 0.3)
        
        return {
            'health_score': health_score,
            'consistency': consistency,
            'quality_signal': quality_signal,
            'nitrogen_ratio': nitrogen_ratio
        }
    
    def detect_climate_anomalies(
        self,
        recent_readings: List[Dict]
    ) -> Dict[str, any]:
        """
        Detect anomalies in climate readings.
        
        Uses simple statistical methods to detect:
        - Sudden toxicity spikes
        - Unusual drought patterns
        - Pest incident surges
        
        Args:
            recent_readings: Last N climate readings
        
        Returns:
            Dict with anomaly flags and scores
        """
        if len(recent_readings) < 5:
            return {
                'has_anomaly': False,
                'anomalies': []
            }
        
        # Extract metrics
        toxicity_levels = [r['toxicity_level'] for r in recent_readings]
        drought_risks = [r['drought_risk'] for r in recent_readings]
        pest_incidents = [r['pest_incidents'] for r in recent_readings]
        
        # Calculate means and stds
        toxicity_mean = np.mean(toxicity_levels)
        toxicity_std = np.std(toxicity_levels)
        
        drought_mean = np.mean(drought_risks)
        drought_std = np.std(drought_risks)
        
        pest_mean = np.mean(pest_incidents)
        pest_std = np.std(pest_incidents)
        
        # Detect anomalies (values > 2 std from mean)
        anomalies = []
        latest = recent_readings[-1]
        
        if latest['toxicity_level'] > toxicity_mean + 2 * toxicity_std:
            anomalies.append({
                'type': 'toxicity_spike',
                'severity': 'high',
                'value': latest['toxicity_level'],
                'baseline': toxicity_mean
            })
        
        if latest['drought_risk'] > drought_mean + 2 * drought_std:
            anomalies.append({
                'type': 'drought_surge',
                'severity': 'medium',
                'value': latest['drought_risk'],
                'baseline': drought_mean
            })
        
        if latest['pest_incidents'] > pest_mean + 2 * pest_std:
            anomalies.append({
                'type': 'pest_surge',
                'severity': 'high',
                'value': latest['pest_incidents'],
                'baseline': pest_mean
            })
        
        return {
            'has_anomaly': len(anomalies) > 0,
            'anomalies': anomalies,
            'baseline_metrics': {
                'toxicity_mean': toxicity_mean,
                'drought_mean': drought_mean,
                'pest_mean': pest_mean
            }
        }


# Singleton instance
garden_ml_service = GardenMLService()
