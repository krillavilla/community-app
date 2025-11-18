# API Specification

**Purpose**: Complete REST API specification for Community App MVP  
**Scope**: All endpoints, request/response schemas, authentication, rate limiting  
**Status**: Production-Ready  
**Last Updated**: 2025-11-17

---

## Table of Contents

1. [API Conventions](#api-conventions)
2. [Authentication Endpoints](#authentication-endpoints)
3. [User Endpoints](#user-endpoints)
4. [Story Endpoints](#story-endpoints)
5. [Habit Endpoints](#habit-endpoints)
6. [Garden Endpoints](#garden-endpoints)
7. [Matching Endpoints](#matching-endpoints)
8. [Health Endpoint](#health-endpoint)
9. [Error Responses](#error-responses)
10. [Rate Limiting](#rate-limiting)

---

## API Conventions

### Base Path
```
/api/v1
```

### Authentication
- **Method**: Bearer JWT (RS256) from Auth0
- **Header**: `Authorization: Bearer <token>`
- **Token**: Must include `permissions` claim with RBAC scopes

### Content Type
- **Request**: `application/json`
- **Response**: `application/json`

### HTTP Methods
- `GET` - Retrieve resources
- `POST` - Create resources
- `PUT` - Update resources (full replacement)
- `PATCH` - Update resources (partial)
- `DELETE` - Delete resources

### Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content (successful deletion)
- `400` - Bad Request
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (valid token, missing permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `429` - Too Many Requests
- `500` - Internal Server Error

### Pagination
For list endpoints:
```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

### Timestamps
All timestamps in ISO 8601 format: `2025-01-01T00:00:00Z`

---

## Authentication Endpoints

### GET /auth/me

Get current user information with claims.

**Authentication**: Required  
**Scopes**: `read:users`

**Request**:
```http
GET /api/v1/auth/me HTTP/1.1
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200**:
```json
{
  "user": {
    "id": "auth0|abc123",
    "email": "user@example.com",
    "created_at": "2025-01-01T00:00:00Z"
  },
  "profile": {
    "display_name": "Ada Lovelace",
    "bio": "First programmer, building community",
    "journaling_frequency": 5
  },
  "claims": {
    "sub": "auth0|abc123",
    "iss": "https://dev-xxxxx.us.auth0.com/",
    "aud": ["https://community.api"],
    "permissions": [
      "read:users",
      "update:users",
      "create:stories",
      "read:stories",
      "create:habits",
      "read:habits",
      "create:gardens",
      "read:gardens",
      "read:match"
    ]
  }
}
```

**Errors**:
- `401` - Invalid or missing token
- `403` - Missing `read:users` permission

---

### GET /auth/logout

Placeholder endpoint (SPA handles logout via Auth0 SDK).

**Authentication**: Optional  
**Scopes**: None

**Response 200**:
```json
{
  "message": "Logout successful. Please clear client-side session."
}
```

---

### GET /auth/callback

Placeholder for OAuth callback (handled by Auth0 SDK in SPA).

**Authentication**: None  
**Scopes**: None

**Response 200**:
```json
{
  "message": "Auth0 callback placeholder. SPA handles token exchange."
}
```

---

## User Endpoints

### GET /users/me

Get current user's profile.

**Authentication**: Required  
**Scopes**: `read:users`

**Request**:
```http
GET /api/v1/users/me HTTP/1.1
Authorization: Bearer <token>
```

**Response 200**:
```json
{
  "id": "auth0|abc123",
  "email": "user@example.com",
  "created_at": "2025-01-01T00:00:00Z",
  "profile": {
    "display_name": "Ada Lovelace",
    "bio": "First programmer",
    "journaling_frequency": 5,
    "updated_at": "2025-01-15T10:30:00Z"
  }
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `read:users` scope
- `404` - User not found (should not happen if token is valid)

---

### PUT /users/me

Update current user's profile.

**Authentication**: Required  
**Scopes**: `update:users`  
**Ownership**: Implicit (updates current user)

**Request**:
```http
PUT /api/v1/users/me HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "display_name": "Ada L.",
  "bio": "Software pioneer building community tools",
  "journaling_frequency": 7
}
```

**Request Body Schema**:
```json
{
  "display_name": "string (1-80 chars, optional)",
  "bio": "string (0-1000 chars, optional)",
  "journaling_frequency": "integer (0-7, optional)"
}
```

**Response 200**:
```json
{
  "id": "auth0|abc123",
  "email": "user@example.com",
  "created_at": "2025-01-01T00:00:00Z",
  "profile": {
    "display_name": "Ada L.",
    "bio": "Software pioneer building community tools",
    "journaling_frequency": 7,
    "updated_at": "2025-01-16T14:20:00Z"
  }
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `update:users` scope
- `422` - Validation error (e.g., display_name too long)

---

### GET /users/{id}

Get public profile of another user.

**Authentication**: Required  
**Scopes**: `read:users`  
**Ownership**: Public info only (no email)

**Request**:
```http
GET /api/v1/users/auth0|xyz789 HTTP/1.1
Authorization: Bearer <token>
```

**Response 200**:
```json
{
  "id": "auth0|xyz789",
  "profile": {
    "display_name": "Grace Hopper",
    "bio": "Debugging the world",
    "account_age_days": 120
  },
  "public_tags": ["technology", "mentorship", "debugging"],
  "public_habits_count": 5,
  "public_stories_count": 12
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `read:users` scope
- `404` - User not found

---

## Story Endpoints

### POST /stories

Create a new story.

**Authentication**: Required  
**Scopes**: `create:stories`

**Request**:
```http
POST /api/v1/stories HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My First Contribution to Open Source",
  "content": "Today I submitted my first pull request...",
  "visibility": "public",
  "tags": ["open-source", "growth", "coding"]
}
```

**Request Body Schema**:
```json
{
  "title": "string (1-140 chars, required)",
  "content": "string (1-10000 chars, required)",
  "visibility": "enum: private|public|friends (default: private)",
  "tags": "array of strings (optional, max 10 tags)"
}
```

**Response 201**:
```json
{
  "id": 42,
  "user_id": "auth0|abc123",
  "title": "My First Contribution to Open Source",
  "content": "Today I submitted my first pull request...",
  "visibility": "public",
  "tags": ["open-source", "growth", "coding"],
  "created_at": "2025-01-16T14:30:00Z",
  "updated_at": "2025-01-16T14:30:00Z"
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `create:stories` scope
- `422` - Validation error (title too long, invalid visibility, etc.)

---

### GET /stories

List stories (filtered).

**Authentication**: Required  
**Scopes**: `read:stories`

**Query Parameters**:
- `user_id` (optional) - Filter by user ID (default: current user)
- `visibility` (optional) - Filter by visibility (`public`, `private`, `all`)
- `tags` (optional) - Comma-separated tag names
- `page` (optional) - Page number (default: 1)
- `page_size` (optional) - Items per page (default: 20, max: 100)

**Request**:
```http
GET /api/v1/stories?visibility=public&tags=growth&page=1&page_size=10 HTTP/1.1
Authorization: Bearer <token>
```

**Response 200**:
```json
{
  "items": [
    {
      "id": 42,
      "user_id": "auth0|abc123",
      "author": {
        "display_name": "Ada Lovelace"
      },
      "title": "My First Contribution",
      "content": "Today I submitted...",
      "visibility": "public",
      "tags": ["open-source", "growth"],
      "created_at": "2025-01-16T14:30:00Z",
      "updated_at": "2025-01-16T14:30:00Z"
    }
  ],
  "total": 24,
  "page": 1,
  "page_size": 10,
  "pages": 3
}
```

**Ownership Rules**:
- If `user_id` not specified: returns current user's stories (all visibilities)
- If `user_id` specified: returns only `public` stories (unless requester is owner)
- `visibility=all` only works for own stories

**Errors**:
- `401` - Unauthorized
- `403` - Missing `read:stories` scope or trying to access private stories

---

### GET /stories/{id}

Get a single story by ID.

**Authentication**: Required  
**Scopes**: `read:stories`  
**Ownership**: Visibility + ownership enforced

**Request**:
```http
GET /api/v1/stories/42 HTTP/1.1
Authorization: Bearer <token>
```

**Response 200**:
```json
{
  "id": 42,
  "user_id": "auth0|abc123",
  "author": {
    "id": "auth0|abc123",
    "display_name": "Ada Lovelace"
  },
  "title": "My First Contribution",
  "content": "Today I submitted my first pull request...",
  "visibility": "public",
  "tags": ["open-source", "growth", "coding"],
  "created_at": "2025-01-16T14:30:00Z",
  "updated_at": "2025-01-16T14:30:00Z"
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `read:stories` scope or story is private
- `404` - Story not found

---

### PUT /stories/{id}

Update a story.

**Authentication**: Required  
**Scopes**: `update:stories`  
**Ownership**: Required (must be story author)

**Request**:
```http
PUT /api/v1/stories/42 HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My First OSS Contribution (Updated)",
  "content": "Today I submitted my first pull request and it got merged!",
  "visibility": "public",
  "tags": ["open-source", "growth", "success"]
}
```

**Response 200**: Same as GET /stories/{id}

**Errors**:
- `401` - Unauthorized
- `403` - Missing `update:stories` scope or not story owner
- `404` - Story not found
- `422` - Validation error

---

### DELETE /stories/{id}

Delete a story.

**Authentication**: Required  
**Scopes**: `delete:stories`  
**Ownership**: Required

**Request**:
```http
DELETE /api/v1/stories/42 HTTP/1.1
Authorization: Bearer <token>
```

**Response 204**: No content

**Errors**:
- `401` - Unauthorized
- `403` - Missing `delete:stories` scope or not story owner
- `404` - Story not found

---

## Habit Endpoints

### POST /habits

Create a new habit.

**Authentication**: Required  
**Scopes**: `create:habits`

**Request**:
```http
POST /api/v1/habits HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Morning Meditation",
  "frequency": "daily",
  "meta": {
    "minutes": 10,
    "time_of_day": "morning"
  }
}
```

**Request Body Schema**:
```json
{
  "name": "string (1-80 chars, required)",
  "frequency": "enum: daily|weekly|monthly|custom (required)",
  "meta": "object (optional, any valid JSON)"
}
```

**Response 201**:
```json
{
  "id": 5,
  "user_id": "auth0|abc123",
  "name": "Morning Meditation",
  "frequency": "daily",
  "meta": {
    "minutes": 10,
    "time_of_day": "morning"
  },
  "created_at": "2025-01-16T15:00:00Z"
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `create:habits` scope
- `422` - Validation error (duplicate habit name, invalid frequency)

---

### GET /habits

List current user's habits.

**Authentication**: Required  
**Scopes**: `read:habits`

**Request**:
```http
GET /api/v1/habits HTTP/1.1
Authorization: Bearer <token>
```

**Response 200**:
```json
{
  "items": [
    {
      "id": 5,
      "user_id": "auth0|abc123",
      "name": "Morning Meditation",
      "frequency": "daily",
      "meta": {
        "minutes": 10
      },
      "created_at": "2025-01-16T15:00:00Z"
    }
  ],
  "total": 8
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `read:habits` scope

---

### GET /habits/{id}

Get a single habit by ID.

**Authentication**: Required  
**Scopes**: `read:habits`  
**Ownership**: Required

**Response 200**: Same schema as single habit in list

**Errors**:
- `401` - Unauthorized
- `403` - Missing `read:habits` scope or not habit owner
- `404` - Habit not found

---

### PUT /habits/{id}

Update a habit.

**Authentication**: Required  
**Scopes**: `update:habits`  
**Ownership**: Required

**Request**: Same schema as POST

**Response 200**: Updated habit

**Errors**:
- `401` - Unauthorized
- `403` - Missing `update:habits` scope or not habit owner
- `404` - Habit not found
- `422` - Validation error

---

### DELETE /habits/{id}

Delete a habit.

**Authentication**: Required  
**Scopes**: `delete:habits`  
**Ownership**: Required

**Response 204**: No content

**Errors**:
- `401` - Unauthorized
- `403` - Missing `delete:habits` scope or not habit owner
- `404` - Habit not found

---

## Garden Endpoints

### POST /gardens

Create user's garden.

**Authentication**: Required  
**Scopes**: `create:gardens`  
**Note**: One garden per user (UNIQUE constraint)

**Request**:
```http
POST /api/v1/gardens HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Growth Garden",
  "theme": "vineyard"
}
```

**Request Body Schema**:
```json
{
  "name": "string (1-80 chars, required)",
  "theme": "string (1-40 chars, optional)"
}
```

**Response 201**:
```json
{
  "id": 12,
  "user_id": "auth0|abc123",
  "name": "My Growth Garden",
  "theme": "vineyard",
  "created_at": "2025-01-16T16:00:00Z"
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `create:gardens` scope
- `409` - Conflict (garden already exists for user)
- `422` - Validation error

---

### GET /gardens/me

Get current user's garden.

**Authentication**: Required  
**Scopes**: `read:gardens`

**Response 200**:
```json
{
  "id": 12,
  "user_id": "auth0|abc123",
  "name": "My Growth Garden",
  "theme": "vineyard",
  "created_at": "2025-01-16T16:00:00Z",
  "stats": {
    "stories_count": 12,
    "habits_count": 8,
    "days_active": 45
  }
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `read:gardens` scope
- `404` - Garden not found (user hasn't created one yet)

---

### PUT /gardens/me

Update current user's garden.

**Authentication**: Required  
**Scopes**: `update:gardens`

**Request**: Same schema as POST

**Response 200**: Updated garden

**Errors**:
- `401` - Unauthorized
- `403` - Missing `update:gardens` scope
- `404` - Garden not found
- `422` - Validation error

---

### DELETE /gardens/me

Delete current user's garden.

**Authentication**: Required  
**Scopes**: `delete:gardens`

**Response 204**: No content

**Errors**:
- `401` - Unauthorized
- `403` - Missing `delete:gardens` scope
- `404` - Garden not found

---

## Matching Endpoints

### POST /match/recommend

Get personalized user recommendations.

**Authentication**: Required  
**Scopes**: `read:match`

**Request**:
```http
POST /api/v1/match/recommend HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "k": 10,
  "filters": {
    "tags": ["growth", "technology"],
    "min_similarity": 0.5
  }
}
```

**Request Body Schema**:
```json
{
  "k": "integer (1-50, default: 10) - number of recommendations",
  "filters": {
    "tags": "array of strings (optional) - match users with these tags",
    "min_similarity": "float (0.0-1.0, default: 0.3) - minimum similarity score"
  }
}
```

**Response 200**:
```json
{
  "user_id": "auth0|abc123",
  "recommendations": [
    {
      "user_id": "auth0|xyz789",
      "score": 0.87,
      "profile": {
        "display_name": "Grace Hopper",
        "bio": "Debugging the world"
      },
      "overlap_tags": ["growth", "technology", "mentorship"],
      "common_habits": 3
    },
    {
      "user_id": "auth0|def456",
      "score": 0.72,
      "profile": {
        "display_name": "Alan Turing",
        "bio": "Computing enthusiast"
      },
      "overlap_tags": ["technology", "mathematics"],
      "common_habits": 2
    }
  ],
  "generated_at": "2025-01-16T17:00:00Z",
  "filters_applied": {
    "tags": ["growth", "technology"],
    "min_similarity": 0.5
  }
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `read:match` scope
- `422` - Validation error (invalid k, filters)
- `503` - ML service unavailable

---

### GET /match/clusters

Get clustering insights.

**Authentication**: Required  
**Scopes**: `read:match`

**Query Parameters**:
- `n` (optional) - Number of top clusters to return (default: 5)

**Request**:
```http
GET /api/v1/match/clusters?n=5 HTTP/1.1
Authorization: Bearer <token>
```

**Response 200**:
```json
{
  "clusters": [
    {
      "id": 0,
      "size": 124,
      "label": "Technology Enthusiasts",
      "top_tags": ["technology", "coding", "open-source"],
      "exemplars": ["auth0|xyz789", "auth0|def456"]
    },
    {
      "id": 1,
      "size": 98,
      "label": "Wellness Practitioners",
      "top_tags": ["meditation", "mindfulness", "health"],
      "exemplars": ["auth0|ghi012"]
    }
  ],
  "total_clusters": 8,
  "generated_at": "2025-01-15T12:00:00Z",
  "model_version": "kmeans_v1"
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Missing `read:match` scope
- `503` - ML service unavailable

---

## Health Endpoint

### GET /health

Check API health status.

**Authentication**: None  
**Scopes**: None

**Request**:
```http
GET /api/v1/health HTTP/1.1
```

**Response 200**:
```json
{
  "status": "ok",
  "service": "community-api",
  "version": "0.1.0",
  "uptime_seconds": 12345,
  "dependencies": {
    "database": "ok",
    "ml_service": "ok"
  }
}
```

**Response 503** (if unhealthy):
```json
{
  "status": "degraded",
  "service": "community-api",
  "version": "0.1.0",
  "dependencies": {
    "database": "ok",
    "ml_service": "unavailable"
  }
}
```

---

## Error Responses

All error responses follow RFC 7807-like format:

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Token missing or invalid",
  "code": "AUTH_TOKEN_INVALID"
}
```

### 403 Forbidden
```json
{
  "error": "forbidden",
  "message": "Missing required permission",
  "required": ["create:stories"],
  "code": "AUTH_INSUFFICIENT_PERMISSIONS"
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Story not found",
  "resource": "story",
  "resource_id": "42"
}
```

### 422 Unprocessable Entity
```json
{
  "error": "validation_error",
  "message": "Validation failed",
  "details": [
    {
      "field": "title",
      "message": "Title must be between 1 and 140 characters",
      "value": ""
    },
    {
      "field": "visibility",
      "message": "Invalid visibility value. Must be one of: private, public, friends",
      "value": "invalid"
    }
  ]
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60,
  "limit": "30 requests per minute"
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "request_id": "req_abc123xyz"
}
```

---

## Rate Limiting

### Strategy

**Unauthenticated requests**:
- Limit: 30 requests per minute per IP
- Scope: Global (all unauthenticated endpoints)

**Authenticated requests (general)**:
- Limit: 120 requests per minute per user
- Scope: GET endpoints

**Authenticated requests (write operations)**:
- Limit: 30 requests per minute per user
- Scope: POST, PUT, DELETE endpoints

### Implementation

- **Library**: slowapi (FastAPI)
- **Storage**: In-memory (MVP), Redis (production)
- **Headers**:
  ```
  X-RateLimit-Limit: 30
  X-RateLimit-Remaining: 25
  X-RateLimit-Reset: 1642348800
  ```

### Exemptions

- `/health` endpoint - no rate limiting
- Admin users (optional) - higher limits

### Production Enhancement

- Nginx `limit_req` module for DDoS protection
- Redis-based distributed rate limiting
- Per-endpoint granular limits

---

## Acceptance Criteria

✅ All MVP endpoints documented with methods and paths  
✅ Request/response schemas provided with examples  
✅ Authentication requirements specified (scopes)  
✅ Ownership rules documented  
✅ Error responses standardized (RFC 7807-like)  
✅ Rate limiting strategy defined  
✅ Pagination format specified  
✅ Timestamp format specified (ISO 8601)  
✅ HTTP status codes documented  

---

## Quick Reference

| Endpoint | Method | Auth | Scopes | Description |
|----------|--------|------|--------|-------------|
| `/health` | GET | ❌ | - | Health check |
| `/auth/me` | GET | ✅ | read:users | Get current user with claims |
| `/users/me` | GET | ✅ | read:users | Get current user profile |
| `/users/me` | PUT | ✅ | update:users | Update current user profile |
| `/users/{id}` | GET | ✅ | read:users | Get public user profile |
| `/stories` | POST | ✅ | create:stories | Create story |
| `/stories` | GET | ✅ | read:stories | List stories |
| `/stories/{id}` | GET | ✅ | read:stories | Get story |
| `/stories/{id}` | PUT | ✅ | update:stories | Update story |
| `/stories/{id}` | DELETE | ✅ | delete:stories | Delete story |
| `/habits` | POST | ✅ | create:habits | Create habit |
| `/habits` | GET | ✅ | read:habits | List habits |
| `/habits/{id}` | GET | ✅ | read:habits | Get habit |
| `/habits/{id}` | PUT | ✅ | update:habits | Update habit |
| `/habits/{id}` | DELETE | ✅ | delete:habits | Delete habit |
| `/gardens` | POST | ✅ | create:gardens | Create garden |
| `/gardens/me` | GET | ✅ | read:gardens | Get my garden |
| `/gardens/me` | PUT | ✅ | update:gardens | Update my garden |
| `/gardens/me` | DELETE | ✅ | delete:gardens | Delete my garden |
| `/match/recommend` | POST | ✅ | read:match | Get recommendations |
| `/match/clusters` | GET | ✅ | read:match | Get clustering insights |

**Total Endpoints**: 20 (1 public, 19 protected)

---

## Next Steps

1. **Implement Pydantic schemas** in `backend/app/schemas/`
2. **Create routers** in `backend/app/api/routers/`
3. **Implement service layer** with ownership checks
4. **Write integration tests** for each endpoint
5. **Generate OpenAPI docs** via FastAPI auto-docs at `/docs`
6. **Test with Postman** or similar tool

---

**Document Status**: ✅ Complete  
**Implementation Status**: Routers pending (health endpoint exists)  
**Dependencies**: Phase 1 complete, database schema documented
