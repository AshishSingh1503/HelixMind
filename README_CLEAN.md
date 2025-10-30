# GenomeGuard - Clean Setup

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
cd web && npm install && cd ..
```

2. **Start the application:**
```bash
python start.py
```

3. **Access the application:**
- Web App: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure (Cleaned)

```
GenomeGuard/
├── backend/
│   ├── api/                # API endpoints
│   ├── models/             # Data models
│   └── simple_app.py       # Main backend app
├── web/                    # React frontend
├── config/                 # Configuration
├── data/                   # Data storage
├── models/                 # ML models
├── scripts/                # Processing scripts
├── tests/                  # Tests
├── start.py               # Main startup script
└── requirements.txt       # Python dependencies
```

## Features

- User registration and authentication
- JWT-based security
- React frontend with modern UI
- FastAPI backend
- In-memory storage (no database required)
- File upload and processing
- ML-based genetic analysis

## Development

- Backend: FastAPI with Python
- Frontend: React with modern JavaScript
- Authentication: JWT tokens
- Storage: In-memory (can be upgraded to MongoDB)