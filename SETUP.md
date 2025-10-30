# 🧬 GenomeGuard Local Setup Guide

## Prerequisites

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **Node.js 16+** - [Download Node.js](https://nodejs.org/)
3. **MongoDB** - Use Docker or [install locally](https://www.mongodb.com/try/download/community)

## Quick Setup (Windows)

```bash
# Run the automated setup script
run_local.bat
```

## Manual Setup

### 1. Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Web Frontend

```bash
cd web
npm install
cd ..
```

### 3. Database Setup

```bash
# Start MongoDB with Docker
docker run -d -p 27017:27017 --name genomeguard-mongo mongo:7.0

# Or install MongoDB locally and start service
```

### 4. Initialize System

```bash
# Create directories
mkdir data\uploads data\processed logs models

# Train ML model
python scripts/train.py
```

## Running the Application

### Option 1: Full Stack (Recommended)

```bash
# Start all services
python start_web.py
```

**Access Points:**
- 🌐 **Web App**: http://localhost:3000
- 📡 **API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 📊 **Streamlit** (optional): http://localhost:8501

### Option 2: Individual Services

```bash
# Terminal 1: Backend API
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Web Frontend
cd web
npm start

# Terminal 3: Streamlit Dashboard (optional)
streamlit run app/dashboard.py --server.port 8501
```

## Testing the Setup

1. **Open Web App**: http://localhost:3000
2. **Register Account**: Create new user account
3. **Upload VCF**: Use the sample file in `data/raw/sample.vcf`
4. **View Results**: Check analysis results and dashboard

## Troubleshooting

### MongoDB Issues
```bash
# Check if MongoDB is running
docker ps | grep mongo

# Restart MongoDB
docker restart genomeguard-mongo

# View MongoDB logs
docker logs genomeguard-mongo
```

### Python Issues
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version
```

### Web Frontend Issues
```bash
# Clear npm cache and reinstall
cd web
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Port Conflicts
- **Backend (8000)**: Change in `config/settings.py`
- **Web (3000)**: Change in `web/package.json` start script
- **MongoDB (27017)**: Change in `.env` file

## Development Commands

```bash
# Run tests
pytest tests/ -v

# Format code
black backend/ app/ tests/

# Lint code
flake8 backend/ app/ tests/

# Build web for production
cd web && npm run build
```

## File Structure After Setup

```
GenomeGuard/
├── venv/                    # Python virtual environment
├── web/node_modules/        # Node.js dependencies
├── data/
│   ├── uploads/            # User uploaded files
│   ├── processed/          # Processed data
│   └── raw/sample.vcf      # Sample VCF file
├── models/model.pkl        # Trained ML model
└── logs/                   # Application logs
```

## Next Steps

1. **Explore the Web Interface** at http://localhost:3000
2. **Check API Documentation** at http://localhost:8000/docs
3. **Upload Sample Data** using `data/raw/sample.vcf`
4. **View Analysis Results** in the dashboard
5. **Customize Configuration** in `.env` file

## Support

If you encounter issues:
1. Check the logs in `logs/genomeguard.log`
2. Verify all prerequisites are installed
3. Ensure MongoDB is running
4. Check port availability (8000, 3000, 27017)