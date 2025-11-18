import httpx
from typing import List, Dict, Optional
from app.core.config import settings

class MLClient:
    """Client for ML service integration"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'ML_SERVICE_URL', 'http://localhost:8001')
        self.api_key = getattr(settings, 'ML_API_KEY', 'dev-ml-key')
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    async def extract_features(self, user_id: str, habits: List[Dict]) -> Dict:
        """
        Extract feature vector from user habits
        
        Args:
            user_id: User identifier
            habits: List of habit dictionaries with name, category, frequency
            
        Returns:
            Dict with user_id, feature_vector, habit_tags, dimension
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/features/extract",
                    headers=self.headers,
                    json={
                        "user_id": user_id,
                        "habits": habits
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error extracting features: {e}")
                return {
                    "user_id": user_id,
                    "feature_vector": [],
                    "habit_tags": [],
                    "dimension": 0
                }
    
    async def find_similar_users(
        self,
        query_user: Dict,
        candidate_users: List[Dict],
        top_k: int = 10,
        min_score: float = 0.3
    ) -> Dict:
        """
        Find similar users using ML service
        
        Args:
            query_user: Dict with user_id, feature_vector, habit_tags
            candidate_users: List of candidate user dicts
            top_k: Number of top matches to return
            min_score: Minimum similarity score threshold
            
        Returns:
            Dict with query_user_id, matches (list), total_candidates
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/similarity",
                    headers=self.headers,
                    json={
                        "query_user": query_user,
                        "candidate_users": candidate_users,
                        "top_k": top_k,
                        "min_score": min_score
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error finding similar users: {e}")
                return {
                    "query_user_id": query_user.get("user_id"),
                    "matches": [],
                    "total_candidates": len(candidate_users)
                }
    
    async def train_clustering(
        self,
        user_features: List[Dict],
        n_clusters: int = 8
    ) -> Dict:
        """
        Train clustering model on user features
        
        Args:
            user_features: List of dicts with user_id, feature_vector, habit_tags
            n_clusters: Number of clusters to create
            
        Returns:
            Dict with clusters info and total_users
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/cluster/train",
                    headers=self.headers,
                    json={
                        "user_features": user_features,
                        "n_clusters": n_clusters
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error training clustering: {e}")
                return {
                    "clusters": [],
                    "total_users": len(user_features)
                }
    
    async def predict_cluster(self, feature_vector: List[float]) -> Optional[int]:
        """
        Predict cluster for a feature vector
        
        Args:
            feature_vector: User feature vector
            
        Returns:
            Cluster ID or None if error
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/cluster/predict",
                    headers=self.headers,
                    json=feature_vector,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                return result.get("cluster_id")
            except httpx.HTTPError as e:
                print(f"Error predicting cluster: {e}")
                return None

ml_client = MLClient()
