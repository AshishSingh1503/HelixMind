# 🧬 GenomeGuard Local Setup Guide

## Prerequisites

1. **Python 3.13** - [Download Python](https://www.python.org/downloads/) (Required for latest package versions)
2. **Node.js 16+** - [Download Node.js](https://nodejs.org/)
3. **MongoDB** - Use Docker or [install locally](https://www.mongodb.com/try/download/community)

> ⚠️ **Note:** This project requires Python 3.13 for compatibility with the latest package versions. If you have multiple Python installations, make sure to use Python 3.13.

## Quick Setup (Windows)

```bash
# Option 1: Create virtual environment (Recommended)
create_venv.bat
venv\Scripts\activate
pip install -r requirements.txt

# Option 2: Start backend directly
start_backend.bat
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
# Terminal 1: Backend API (run from PROJECT ROOT, not from backend/ directory)
C:\Users\arpit\AppData\Local\Programs\Python\Python313\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

# Or use the batch file (easier):
start_backend.bat

# Terminal 2: Web Frontend
cd web
npm install  # First time only
npm start

# Terminal 3: Streamlit Dashboard (optional)
streamlit run app/dashboard.py --server.port 8501
```

> ⚠️ **Important:** Always run the backend command from the project root directory (`C:\Arpit\HelixMind`), NOT from inside the `backend/` folder. The `start_backend.bat` script handles this automatically.

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
# Check Python version (must be 3.13)
python --version

# If wrong Python version, use the full path:
C:\Users\arpit\AppData\Local\Programs\Python\Python313\python.exe --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or create a virtual environment (recommended):
create_venv.bat
```

### Multiple Python Installations
If you have multiple Python versions installed:
1. Use `create_venv.bat` to create a virtual environment with Python 3.13
2. Activate it with `venv\Scripts\activate`
3. Or use `start_backend.bat` which uses the correct Python automatically

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