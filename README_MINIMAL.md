# 🧬 GenomeGuard — Minimal AI-Powered Genetic Disease Predictor

GenomeGuard is a lightweight AI-based system that analyzes human genomic data to predict genetic disease risks. This minimal version removes external dependencies for easy deployment.

## 🚀 Quick Start

```bash
# Clone and start minimal version
git clone https://github.com/username/GenomeGuard.git
cd GenomeGuard

# Windows
.\deploy-minimal.ps1

# Linux/Mac
chmod +x deploy-minimal.sh
./deploy-minimal.sh

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

## ✨ Minimal Features

- **Lightweight Backend**: FastAPI with in-memory storage
- **No External Dependencies**: Removed bcrypt, MongoDB, loguru
- **Simple Authentication**: SHA-256 password hashing with JWT
- **Docker Ready**: Single command deployment
- **Health Monitoring**: Built-in health checks

## 🛠️ Tech Stack (Minimal)

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, Python 3.11+ |
| **Authentication** | JWT, SHA-256 hashing |
| **Frontend** | React, Tailwind CSS |
| **Deployment** | Docker, Docker Compose |

## 📂 Project Structure (Minimal)
```
GenomeGuard/
├── backend/
│   ├── main.py              # Minimal FastAPI app
│   ├── requirements.txt     # Essential dependencies only
│   └── Dockerfile          # Container definition
├── web/                     # React frontend
├── docker-compose.minimal.yml
├── deploy-minimal.ps1       # Windows deployment
└── deploy-minimal.sh        # Linux/Mac deployment
```

## ⚙️ Installation

### Option 1: Docker (Recommended)
```bash
# Windows
.\deploy-minimal.ps1

# Linux/Mac
./deploy-minimal.sh
```

### Option 2: Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (separate terminal)
cd web
npm install
npm start
```

## 📊 API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/token` - User login
- `GET /auth/me` - Get current user
- `GET /health` - Health check

## 🔒 Security Features

- SHA-256 password hashing with salt
- JWT-based authentication
- CORS enabled for frontend integration
- In-memory user storage (session-based)

## 🚀 Deployment Commands

```bash
# Start services
docker-compose -f docker-compose.minimal.yml up -d

# Stop services
docker-compose -f docker-compose.minimal.yml down

# View logs
docker-compose -f docker-compose.minimal.yml logs -f

# Rebuild
docker-compose -f docker-compose.minimal.yml up --build -d
```

## 📈 Performance

- **Startup Time**: < 5 seconds
- **Memory Usage**: < 100MB
- **Dependencies**: 5 Python packages only
- **Container Size**: < 200MB

## 🔧 Configuration

Environment variables:
- `SECRET_KEY`: JWT signing key (default: genomeguard-secret-key-dev)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiry (default: 30)

## 🆘 Troubleshooting

**Port conflicts:**
```bash
# Check what's using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac
```

**Container issues:**
```bash
# Clean up containers
docker system prune -a
```

## 📄 License

MIT License - see LICENSE file for details.