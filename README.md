# ASCIIme API

An API service built with FastAPI that provides access to curated anime GIFs from multiple sources. The API features smart caching, failover mechanisms, and category-based searching.

## Key Features

- 🚀 High-performance FastAPI architecture
- 📦 Multi-source GIF aggregation (Tenor + Reddit + Giphy)
- 🔄 Automatic source failover
- 💾 Redis-based caching
- 🎯 Category-based searching
- ⚡ Concurrent API requests
- 🛡️ Rate limiting and retry mechanisms
- 🌐 CORS-enabled endpoints

## API Reference

### Get Random GIF
```http
GET /api/random?category={category}
```

Retrieves a random GIF, optionally filtered by category.

| Parameter  | Type     | Description                |
|------------|----------|----------------------------|
| `category` | `string` | Optional category filter   |

Response:
```json
{
    "success": true,
    "data": {
        "id": "string",
        "url": "string",
        "size": "number",
        "dims": ["width", "height"],
        "source": "tenor|reddit|giphy",
        "category": "string"
    }
}
```

### Batch GIF Retrieval
```http
GET /api/batch?count={count}&category={category}
```

Retrieves multiple GIFs in a single request.

| Parameter  | Type     | Description                |
|------------|----------|----------------------------|
| `count`    | `number` | Number of GIFs (max: 50)  |
| `category` | `string` | Optional category filter   |

Response:
```json
{
    "success": true,
    "data": [{
        "id": "string",
        "url": "string",
        "size": "number",
        "dims": ["width", "height"],
        "source": "tenor|reddit|giphy",
        "category": "string"
    }]
}
```

### Get Categories
```http
GET /api/categories
```

Returns available categories and their associated search terms.

Response:
```json
{
    "success": true,
    "data": [{
        "id": "string",
        "terms": ["string"],
        "subreddits": ["string"]
    }]
}
```

## Development Setup

1. Clone the repository
```bash
git clone https://github.com/Felixdiamond/asciime-api.git
cd asciime-api
```

2. Create and activate a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
TENOR_API_KEY=your_tenor_key
GIPHY_API_KEY=your_giphy_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDIS_URL=your_redis_url
```

5. Start development server
```bash
uvicorn main:app --reload
```

or 

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

## Docker Deployment

1. Build the Docker image
```bash
docker build -t asciime-api .
```

2. Run the container
```bash
docker run -p 8000:8000 --env-file .env asciime-api
```

## Technical Details

### Project Structure
```
app/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Project dependencies
├── Dockerfile             # Docker configuration
├── .env.example           # Environment variables template
├── api/
│   ├── routes/            # API endpoints
│   └── models/            # Pydantic models
├── core/                  # Core configuration
└── services/             # External service integrations
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Open a Pull Request