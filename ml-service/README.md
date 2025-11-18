# Garden Platform - ML Service

PyTorch-based machine learning service for content recommendations, similarity analysis, and content moderation.

## Features

- ✅ **Semantic Embeddings** - sentence-transformers for text understanding
- ✅ **Content Similarity** - Cosine similarity for text matching
- ✅ **Recommendations** - Personalized content recommendations
- ✅ **User Similarity** - Find users with similar interests
- ✅ **Content Clustering** - Topic discovery with K-means
- ✅ **Content Moderation** - Toxicity and spam detection
- ✅ **API Key Security** - Protected endpoints

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment file
cp .env.example .env

# 3. Start service
uvicorn app.main:app --host 0.0.0.0 --port 8001

# 4. Visit API docs
# http://localhost:8001/docs
```

## Project Structure

```
ml-service/
├── app/
│   ├── services/
│   │   ├── embeddings.py      # Text embedding service
│   │   ├── recommendations.py # Recommendation engine
│   │   └── moderation.py      # Content moderation
│   ├── config.py              # Service configuration
│   └── main.py                # FastAPI application
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## API Endpoints

### Health & Status

- `GET /` - Service info
- `GET /health` - Health check with model info

### Content Similarity

```bash
POST /api/ml/similarity
{
  "text_a": "I love running in the morning",
  "text_b": "Morning jogs are my favorite"
}
# Returns: {"similarity": 0.85, ...}
```

### Find Similar Content

```bash
POST /api/ml/find-similar
{
  "query_text": "meditation techniques",
  "candidates": ["mindfulness practice", "yoga poses", ...],
  "top_k": 5,
  "threshold": 0.3
}
```

### Content Recommendations

```bash
POST /api/ml/recommend
{
  "user_id": "user-123",
  "user_history": ["habit tracking", "fitness goals"],
  "candidates": [
    {"id": "1", "text": "nutrition tips"},
    {"id": "2", "text": "workout routines"}
  ],
  "top_k": 10
}
```

### Content Moderation

```bash
POST /api/ml/moderate
{
  "text": "Some user-generated content"
}
# Returns: {
#   "is_safe": true,
#   "safety_score": 0.95,
#   "toxicity": {...},
#   "spam": {...},
#   "recommended_action": "approve"
# }
```

### Content Clustering

```bash
POST /api/ml/cluster
{
  "contents": [
    {"id": "1", "text": "fitness content"},
    {"id": "2", "text": "meditation guide"},
    ...
  ],
  "n_clusters": 5
}
```

### Find Similar Users

```bash
POST /api/ml/find-similar-users
{
  "user_id": "user-123",
  "user_interests": ["fitness", "meditation"],
  "candidates": [
    {"id": "user-456", "interests": ["yoga", "wellness"]},
    ...
  ],
  "top_k": 10
}
```

## Authentication

All endpoints (except `/` and `/health`) require API key authentication:

```bash
curl -X POST http://localhost:8001/api/ml/similarity \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"text_a": "hello", "text_b": "hi"}'
```

## Models Used

### Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Size**: ~80MB
- **Dimensions**: 384
- **Speed**: Fast, suitable for real-time inference
- **Use Cases**: Similarity, recommendations, clustering

### Moderation (MVP)
- **Implementation**: Keyword-based heuristics
- **TODO**: Integrate proper toxicity detection model
- **Planned**: `unitary/toxic-bert` or similar

## Configuration

Edit `.env` file:

```bash
# API Security
API_KEY="your-secret-api-key"

# Model Selection
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Performance
DEVICE="cpu"  # or "cuda" if GPU available
BATCH_SIZE=32
MAX_LENGTH=512

# Recommendations
TOP_K_RECOMMENDATIONS=10
SIMILARITY_THRESHOLD=0.3
```

## GPU Support

To use GPU acceleration:

1. Install CUDA-enabled PyTorch:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

2. Update `.env`:
```bash
DEVICE="cuda"
```

## Development

### Run with Auto-Reload

```bash
uvicorn app.main:app --reload --port 8001
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

### Example Test Request

```python
import httpx

response = httpx.post(
    "http://localhost:8001/api/ml/similarity",
    headers={"X-API-Key": "dev-ml-key-12345"},
    json={
        "text_a": "I enjoy morning runs",
        "text_b": "Running in the AM is great"
    }
)

print(response.json())
# {"similarity": 0.87, "text_a": "...", "text_b": "..."}
```

## Performance

### Embedding Speed
- **CPU**: ~100-200 texts/second
- **GPU**: ~1000+ texts/second

### Memory Usage
- **Model**: ~500MB (embedding model loaded)
- **Batch Processing**: Configurable via `BATCH_SIZE`

### Caching
- Models cached in `./model_cache/`
- Embeddings can be cached in Redis (TODO)

## Production Deployment

### Docker

```bash
# Build image
docker build -t garden-ml-service .

# Run container
docker run -p 8001:8001 \
  -e API_KEY=prod-key \
  garden-ml-service
```

### Environment Variables

Required for production:
- `API_KEY` - Strong secret key
- `DEVICE` - "cpu" or "cuda"
- `CACHE_DIR` - Persistent volume for models

## Monitoring

Health check endpoint for monitoring:

```bash
curl http://localhost:8001/health
```

Response:
```json
{
  "status": "healthy",
  "models": {
    "embedding": "sentence-transformers/all-MiniLM-L6-v2",
    "device": "cpu"
  }
}
```

## Future Improvements

- [ ] Integrate proper toxicity detection model
- [ ] Add Redis caching for embeddings
- [ ] Implement user preference learning
- [ ] Add A/B testing support
- [ ] Metrics and logging with Prometheus
- [ ] Batch processing optimization
- [ ] Model versioning
- [ ] Fine-tuning on Garden Platform data

## Integration with Backend

The backend API service calls this ML service via HTTP:

```python
# backend/app/services/ml_client.py
response = await client.post(
    f"{ML_SERVICE_URL}/api/ml/recommend",
    headers={"X-API-Key": ML_API_KEY},
    json={
        "user_id": user_id,
        "user_history": history,
        "candidates": candidates
    }
)
```

## License

[Your License Here]

## Support

For issues or questions, see project documentation.
