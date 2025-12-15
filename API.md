# API Documentation

## MisinfoGuard API Reference

### Base URLs

- **Backend API**: `http://localhost:5000`
- **Python Service**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000`

---

## Backend API Endpoints

### 1. Health Check

**Endpoint:** `GET /api/health`

**Description:** Check if the backend service is running

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "uptime": 123.456,
  "service": "MisinfoGuard Backend"
}
```

---

### 2. Upload File

**Endpoint:** `POST /api/upload`

**Description:** Upload an image or PDF file

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (File)

**Supported Formats:** JPG, JPEG, PNG, GIF, BMP, PDF

**Max Size:** 10MB

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "file": {
    "filename": "file-1234567890.jpg",
    "originalname": "my-image.jpg",
    "mimetype": "image/jpeg",
    "size": 123456,
    "path": "./uploads/file-1234567890.jpg"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "No file uploaded"
}
```

---

### 3. Analyze Image

**Endpoint:** `POST /api/analyze/image`

**Description:** Analyze an uploaded image for misinformation

**Request:**
```json
{
  "filePath": "./uploads/file-1234567890.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "success": true,
    "extracted_text": "Extracted text from image...",
    "claims": [
      {
        "text": "Claim extracted from image",
        "entities": [...],
        "sentiment": "neutral",
        "confidence": 0.85
      }
    ],
    "language": "en"
  },
  "factCheck": [
    {
      "claim": "Claim text",
      "verdict": "LIKELY FALSE",
      "confidence": 75.5,
      "explanation": "Why this verdict...",
      "sources": [...],
      "total_sources_found": 10,
      "red_flags": 2
    }
  ]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Content rejected: Inappropriate or sensitive material detected"
}
```

---

### 4. Analyze Text

**Endpoint:** `POST /api/analyze/text`

**Description:** Analyze pasted text for misinformation

**Request:**
```json
{
  "text": "The claim you want to verify..."
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "success": true,
    "claims": [
      {
        "text": "Extracted claim",
        "entities": [...],
        "sentiment": "neutral",
        "confidence": 0.85
      }
    ],
    "language": "en"
  },
  "factCheck": [...]
}
```

---

## Python Service Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "ocr": "operational",
    "nlp": "operational",
    "fact_checker": "operational"
  }
}
```

---

### 2. Analyze Image (OCR)

**Endpoint:** `POST /api/analyze/image`

**Description:** Extract text and claims from image using OCR

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (File)

**Response:**
```json
{
  "success": true,
  "extracted_text": "Text extracted from image...",
  "claims": [
    {
      "text": "Factual claim found in text",
      "entities": [
        {
          "text": "Entity name",
          "type": "PERSON",
          "start": 0,
          "end": 10
        }
      ],
      "sentiment": "neutral",
      "confidence": 0.85
    }
  ],
  "language": "en"
}
```

---

### 3. Analyze Text (NLP)

**Endpoint:** `POST /api/analyze/text`

**Description:** Extract claims from text using NLP

**Request:**
```json
{
  "text": "Your text to analyze..."
}
```

**Response:**
```json
{
  "success": true,
  "claims": [...],
  "language": "en"
}
```

---

### 4. Fact Check

**Endpoint:** `POST /api/fact-check`

**Description:** Verify claims using Google APIs

**Request:**
```json
{
  "claims": [
    {
      "text": "Claim to verify",
      "entities": [],
      "sentiment": "neutral",
      "confidence": 0.85
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "claim": "Claim text",
      "verdict": "LIKELY TRUE",
      "confidence": 85.5,
      "explanation": "Found 10 highly credible sources supporting this assessment. Based on our analysis, this claim appears to be accurate.",
      "sources": [
        {
          "url": "https://www.reuters.com/article",
          "title": "Article Title",
          "snippet": "Article snippet...",
          "credibility": 0.95,
          "source_name": "reuters.com"
        }
      ],
      "total_sources_found": 10,
      "red_flags": 0,
      "timestamp": "2024-01-01T00:00:00.000000"
    }
  ]
}
```

---

## Data Models

### Claim Object
```typescript
{
  text: string,           // The claim text
  entities: Entity[],     // Named entities found
  sentiment: string,      // "positive" | "negative" | "neutral"
  confidence: number      // 0.0 - 1.0
}
```

### Entity Object
```typescript
{
  text: string,          // Entity text
  type: string,          // PERSON, ORG, GPE, DATE, etc.
  start: number,         // Start character position
  end: number            // End character position
}
```

### Fact Check Result
```typescript
{
  claim: string,                    // Original claim
  verdict: "LIKELY TRUE" | "LIKELY FALSE",
  confidence: number,               // 0-100
  explanation: string,              // Human-friendly explanation
  sources: Source[],                // Top sources (max 5)
  total_sources_found: number,      // Total sources analyzed
  red_flags: number,                // Misinformation indicators
  timestamp: string                 // ISO datetime
}
```

### Source Object
```typescript
{
  url: string,              // Source URL
  title: string,            // Article/page title
  snippet: string,          // Relevant excerpt
  credibility: number,      // 0.0 - 1.0
  source_name: string       // Domain name
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400  | Bad Request - Invalid input |
| 404  | Not Found - Resource not found |
| 413  | Payload Too Large - File too big |
| 429  | Too Many Requests - Rate limit exceeded |
| 500  | Internal Server Error |

---

## Rate Limiting

- **Window:** 15 minutes
- **Max Requests:** 100 per IP
- **Response Header:** `X-RateLimit-Remaining`

---

## Content Safety

The system automatically rejects:
- NSFW/inappropriate images
- Offensive text content
- Content with excessive profanity

**Rejection Response:**
```json
{
  "success": false,
  "error": "Content rejected: Inappropriate or sensitive material detected"
}
```

---

## Trusted Sources

The fact-checker gives higher credibility to:

| Source | Credibility Score |
|--------|-------------------|
| factcheck.org | 0.98 |
| who.int | 0.97 |
| cdc.gov | 0.97 |
| nature.com | 0.96 |
| politifact.com | 0.96 |
| reuters.com | 0.95 |
| apnews.com | 0.95 |
| snopes.com | 0.95 |
| bbc.com | 0.92 |
| npr.org | 0.90 |

---

## Example Usage

### cURL Example - Upload and Analyze Image

```bash
# 1. Upload file
curl -X POST http://localhost:5000/api/upload \
  -F "file=@/path/to/image.jpg"

# Response: {"success": true, "file": {"path": "./uploads/file-123.jpg"}}

# 2. Analyze image
curl -X POST http://localhost:5000/api/analyze/image \
  -H "Content-Type: application/json" \
  -d '{"filePath": "./uploads/file-123.jpg"}'
```

### JavaScript Example - Analyze Text

```javascript
const response = await fetch('http://localhost:5000/api/analyze/text', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'The claim I want to verify'
  })
});

const result = await response.json();
console.log(result);
```

### Python Example - Fact Check

```python
import requests

response = requests.post(
    'http://localhost:8000/api/fact-check',
    json={
        'claims': [
            {
                'text': 'Claim to verify',
                'entities': [],
                'sentiment': 'neutral',
                'confidence': 0.85
            }
        ]
    }
)

print(response.json())
```

---

## Google API Setup

### Required APIs

1. **Google Custom Search API**
   - Enable in Google Cloud Console
   - Create API key
   - Set in `GOOGLE_API_KEY` environment variable

2. **Custom Search Engine**
   - Create at [Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Search entire web (use `*` in sites to search)
   - Get Search Engine ID (cx)
   - Set in `GOOGLE_CX_ID` environment variable

### Environment Variables

```env
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_CX_ID=your-search-engine-id
```

---

## Deployment

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Service URLs (Docker)

- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- Python Service: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

For more information, see [README.md](README.md)
