"""
Garden Platform ML Service.

FastAPI service for content recommendations, similarity, and moderation.
"""
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from app.config import settings
from app.services.embeddings import embedding_service
from app.services.recommendations import recommendation_service
from app.services.moderation import moderation_service

# API key security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key."""
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key


# Pydantic models
class SimilarityRequest(BaseModel):
    """Request for similarity calculation."""
    text_a: str = Field(..., min_length=1)
    text_b: str = Field(..., min_length=1)


class SimilarityResponse(BaseModel):
    """Similarity calculation response."""
    similarity: float
    text_a: str
    text_b: str


class RecommendationRequest(BaseModel):
    """Request for content recommendations."""
    user_id: str
    user_history: List[str] = Field(default_factory=list)
    candidates: List[Dict[str, Any]]
    top_k: int = 10


class ModerationRequest(BaseModel):
    """Request for content moderation."""
    text: str = Field(..., min_length=1)


class ModerationResponse(BaseModel):
    """Content moderation response."""
    is_safe: bool
    safety_score: float
    toxicity: Dict[str, Any]
    spam: Dict[str, Any]
    recommended_action: str


class FindSimilarRequest(BaseModel):
    """Request to find similar content."""
    query_text: str
    candidates: List[str]
    top_k: int = 10
    threshold: float = 0.3


# FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ML service for Garden Platform"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models": {
            "embedding": settings.EMBEDDING_MODEL,
            "device": settings.DEVICE
        }
    }


@app.post("/api/ml/similarity", response_model=SimilarityResponse)
async def calculate_similarity(
    request: SimilarityRequest,
    api_key: str = Security(verify_api_key)
):
    """
    Calculate semantic similarity between two texts.
    
    Returns cosine similarity score (0.0 to 1.0).
    """
    try:
        similarity = embedding_service.compute_similarity(
            request.text_a,
            request.text_b
        )
        
        return SimilarityResponse(
            similarity=similarity,
            text_a=request.text_a,
            text_b=request.text_b
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similarity calculation failed: {str(e)}"
        )


@app.post("/api/ml/find-similar")
async def find_similar(
    request: FindSimilarRequest,
    api_key: str = Security(verify_api_key)
):
    """
    Find most similar texts to query.
    
    Returns list of (index, similarity_score) pairs.
    """
    try:
        results = embedding_service.find_similar(
            request.query_text,
            request.candidates,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        return {
            "query_text": request.query_text,
            "results": [
                {"index": idx, "similarity": score}
                for idx, score in results
            ],
            "total_candidates": len(request.candidates)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similar search failed: {str(e)}"
        )


@app.post("/api/ml/recommend")
async def recommend_content(
    request: RecommendationRequest,
    api_key: str = Security(verify_api_key)
):
    """
    Get personalized content recommendations.
    
    Based on user history and candidate content.
    """
    try:
        recommendations = recommendation_service.recommend_content(
            user_id=request.user_id,
            user_history=request.user_history,
            candidate_contents=request.candidates,
            top_k=request.top_k
        )
        
        return {
            "user_id": request.user_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation failed: {str(e)}"
        )


@app.post("/api/ml/moderate", response_model=ModerationResponse)
async def moderate_content(
    request: ModerationRequest,
    api_key: str = Security(verify_api_key)
):
    """
    Analyze content for toxicity and spam.
    
    Returns safety scores and recommended moderation action.
    """
    try:
        result = moderation_service.analyze_content(request.text)
        
        return ModerationResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Moderation failed: {str(e)}"
        )


@app.post("/api/ml/cluster")
async def cluster_content(
    request: Dict[str, Any],
    api_key: str = Security(verify_api_key)
):
    """
    Cluster content for topic discovery.
    
    Groups similar content into clusters.
    """
    try:
        contents = request.get("contents", [])
        n_clusters = request.get("n_clusters", 8)
        
        result = recommendation_service.cluster_content(
            contents=contents,
            n_clusters=n_clusters
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clustering failed: {str(e)}"
        )


@app.post("/api/ml/find-similar-users")
async def find_similar_users(
    request: Dict[str, Any],
    api_key: str = Security(verify_api_key)
):
    """
    Find users with similar interests.
    
    Based on user interest embeddings.
    """
    try:
        user_id = request.get("user_id")
        user_interests = request.get("user_interests", [])
        candidates = request.get("candidates", [])
        top_k = request.get("top_k", 10)
        
        results = recommendation_service.find_similar_users(
            user_id=user_id,
            user_interests=user_interests,
            candidate_users=candidates,
            top_k=top_k
        )
        
        return {
            "user_id": user_id,
            "similar_users": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User similarity search failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
