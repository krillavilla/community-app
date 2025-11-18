"""
Content recommendation service.

Provides personalized recommendations based on user history and preferences.
"""
from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import KMeans
from app.services.embeddings import embedding_service
from app.config import settings


class RecommendationService:
    """
    Recommendation engine for personalized content.
    
    Uses collaborative filtering and content-based approaches.
    """
    
    def __init__(self):
        """Initialize recommendation service."""
        self.user_profiles = {}  # In-memory user profile cache
        self.content_clusters = None
        print("✅ Recommendation service initialized")
    
    def recommend_content(
        self,
        user_id: str,
        user_history: List[str],
        candidate_contents: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommend content based on user history.
        
        Args:
            user_id: User identifier
            user_history: List of content texts user has interacted with
            candidate_contents: List of candidate content dicts with 'id' and 'text'
            top_k: Number of recommendations
            
        Returns:
            List of recommended content dicts with scores
        """
        if not candidate_contents:
            return []
        
        # Build user profile from history
        user_profile = self._build_user_profile(user_history)
        
        # Extract candidate texts
        candidate_texts = [item['text'] for item in candidate_contents]
        
        # Encode candidates
        candidate_embs = embedding_service.encode(candidate_texts)
        
        # Compute similarity to user profile
        similarities = np.dot(candidate_embs, user_profile.T).flatten()
        
        # Get top k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build recommendations
        recommendations = []
        for idx in top_indices:
            rec = candidate_contents[idx].copy()
            rec['score'] = float(similarities[idx])
            rec['reason'] = 'based_on_your_interests'
            recommendations.append(rec)
        
        return recommendations
    
    def find_similar_users(
        self,
        user_id: str,
        user_interests: List[str],
        candidate_users: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find users with similar interests.
        
        Args:
            user_id: Query user ID
            user_interests: List of user's interest texts
            candidate_users: List of user dicts with 'id' and 'interests'
            top_k: Number of similar users to return
            
        Returns:
            List of similar users with similarity scores
        """
        if not candidate_users or not user_interests:
            return []
        
        # Encode query user interests
        query_profile = self._build_user_profile(user_interests)
        
        # Encode candidate user interests
        similar_users = []
        for candidate in candidate_users:
            if candidate['id'] == user_id:
                continue  # Skip self
            
            candidate_profile = self._build_user_profile(candidate.get('interests', []))
            
            # Compute similarity
            similarity = float(np.dot(query_profile, candidate_profile.T))
            
            if similarity >= settings.SIMILARITY_THRESHOLD:
                result = candidate.copy()
                result['similarity'] = similarity
                similar_users.append(result)
        
        # Sort and return top k
        similar_users.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_users[:top_k]
    
    def cluster_content(
        self,
        contents: List[Dict[str, Any]],
        n_clusters: int = 8
    ) -> Dict[str, Any]:
        """
        Cluster content for topic discovery.
        
        Args:
            contents: List of content dicts with 'id' and 'text'
            n_clusters: Number of clusters
            
        Returns:
            Dict with cluster assignments and centroids
        """
        if len(contents) < n_clusters:
            n_clusters = max(1, len(contents) // 2)
        
        # Extract texts and encode
        texts = [item['text'] for item in contents]
        embeddings = embedding_service.encode(texts)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)
        
        # Organize by clusters
        clusters = {i: [] for i in range(n_clusters)}
        for idx, label in enumerate(labels):
            content_with_cluster = contents[idx].copy()
            content_with_cluster['cluster'] = int(label)
            clusters[label].append(content_with_cluster)
        
        return {
            'clusters': clusters,
            'n_clusters': n_clusters,
            'centroids': kmeans.cluster_centers_.tolist()
        }
    
    def _build_user_profile(self, texts: List[str]) -> np.ndarray:
        """
        Build user profile from interaction history.
        
        Args:
            texts: List of texts user has interacted with
            
        Returns:
            Averaged embedding vector representing user profile
        """
        if not texts:
            # Return zero vector if no history
            return np.zeros(384)  # MiniLM embedding dimension
        
        # Encode all texts
        embeddings = embedding_service.encode(texts)
        
        # Average embeddings to create profile
        profile = np.mean(embeddings, axis=0)
        
        # Normalize
        profile = profile / (np.linalg.norm(profile) + 1e-8)
        
        return profile


# Global instance
recommendation_service = RecommendationService()
