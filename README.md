🧬 GenomeGuard — AI-Powered Genetic Disease Predictor (Enterprise Edition)

GenomeGuard is an AI-based system that analyzes human genomic data (VCF files) to predict the risk of genetic diseases such as cancer, Alzheimer's, and inherited disorders.
Featuring a secure backend with user authentication, MongoDB database, and RESTful API architecture for scalable deployment.

## 🚀 Quick Start

```bash
# Clone and start with Docker (Recommended)
git clone https://github.com/username/GenomeGuard.git
cd GenomeGuard
docker-compose up -d

# Access the application
# Dashboard: http://localhost:8501
# API: http://localhost:8000/docs
```

🚀 Key Features

✅ **Secure Backend Architecture**
- FastAPI REST API with JWT authentication
- MongoDB database for scalable data storage
- User management and access control
- Background task processing

✅ **Genomic Analysis Pipeline**
- VCF file processing and variant extraction
- Disease-specific variant annotation
- Machine learning risk prediction (XGBoost)
- Comprehensive reporting and visualization

✅ **Enterprise Features**
- Multi-user support with personal dashboards
- Analysis history and result management
- Secure file upload and storage
- RESTful API for integration
- Docker containerization support

## 🧠 System Workflow
```
User Registration/Login
        ↓
Upload VCF File (API)
        ↓
Background Processing
        ↓
Variant Extraction & Annotation
        ↓
ML Risk Prediction
        ↓
Store Results (MongoDB)
        ↓
Interactive Dashboard
```

🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | FastAPI, Python 3.11+, Pydantic |
| **Database** | MongoDB, PyMongo |
| **Authentication** | JWT, bcrypt, OAuth2 |
| **ML/Analytics** | XGBoost, scikit-learn, pandas, numpy |
| **Frontend** | Streamlit, Plotly, requests |
| **Bioinformatics** | pysam, custom VCF processing |
| **DevOps** | Docker, Docker Compose |
| **Testing** | pytest, FastAPI TestClient |
| **Logging** | loguru |

📂 Project Structure
```
GenomeGuard/
├── backend/                 # Backend API
│   ├── api/                # API endpoints
│   │   ├── auth.py        # Authentication routes
│   │   └── analysis.py    # Analysis routes
│   ├── models/            # Data models
│   │   ├── database.py    # MongoDB connection
│   │   └── schemas.py     # Pydantic schemas
│   ├── services/          # Business logic
│   │   ├── auth_service.py
│   │   └── analysis_service.py
│   └── main.py           # FastAPI application
├── app/
│   └── dashboard.py      # Streamlit frontend
├── config/
│   └── settings.py       # Configuration
├── data/
│   ├── uploads/          # User uploaded files
│   └── raw/             # Sample data
├── models/              # ML models
├── tests/               # Test suite
├── logs/                # Application logs
├── docker-compose.yml   # Container orchestration
├── Dockerfile          # Container definition
└── requirements.txt    # Dependencies
```

## ⚙️ Installation & Setup

### Option 1: Docker Deployment (Recommended)

```bash
# Clone repository
git clone https://github.com/username/GenomeGuard.git
cd GenomeGuard

# Start services with Docker
docker-compose up -d

# Access the application
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development Setup

```bash
# 1. Clone and setup environment
git clone https://github.com/username/GenomeGuard.git
cd GenomeGuard
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup MongoDB
# Install MongoDB locally or use Docker:
docker run -d -p 27017:27017 --name genomeguard-mongo mongo:7.0

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Start services
python start_services.py
```

## ▶️ Using GenomeGuard

### 1. Access the Application
- **Frontend Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000

### 2. User Workflow
1. **Register/Login**: Create account or login to existing account
2. **Upload VCF**: Upload your genomic data file (.vcf format)
3. **Analysis**: System automatically processes and analyzes variants
4. **Results**: View risk predictions and detailed reports
5. **History**: Access previous analyses and results

### 3. API Usage
```python
import requests

# Login
response = requests.post("http://localhost:8000/auth/token", 
                        data={"username": "user", "password": "pass"})
token = response.json()["access_token"]

# Upload VCF
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("sample.vcf", "rb")}
response = requests.post("http://localhost:8000/analysis/upload", 
                        headers=headers, files=files)
```

## 📊 Features & Capabilities

### 🔐 Security Features
- JWT-based authentication
- Bcrypt password hashing
- User session management
- Secure file upload validation
- Access control and authorization

### 🧬 Genomic Analysis
- VCF file processing and validation
- Variant extraction and quality filtering
- Disease-specific annotation (BRCA1/2, APOE, TP53)
- Machine learning risk prediction
- Comprehensive reporting

### 📈 Visualization & Reports
- Interactive risk assessment gauges
- Variant category breakdowns
- Historical analysis tracking
- Detailed variant tables
- Export capabilities

### 🏗️ Architecture Benefits
- Scalable MongoDB backend
- RESTful API design
- Async processing for large files
- Containerized deployment
- Comprehensive logging and monitoring

### 🧪 Testing & Quality
- Automated API testing with pytest
- Code formatting with black
- Linting with flake8
- Environment-based configuration
- Error handling and logging

## 🔧 Development

### Prerequisites
```bash
# Install development dependencies
pip install -r requirements.txt
python scripts/train.py  # Train ML model
```

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black backend/ app/ tests/
flake8 backend/ app/ tests/
```

### Database Management
```bash
# Access MongoDB shell
docker exec -it genomeguard-mongo mongosh

# Backup database
mongodump --host localhost:27017 --db genomeguard --out backup/

# Restore database
mongorestore --host localhost:27017 --db genomeguard backup/genomeguard/
```

## 📝 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints:
- `POST /auth/register` - User registration
- `POST /auth/token` - User login
- `GET /auth/me` - Get current user
- `POST /analysis/upload` - Upload VCF file
- `GET /analysis/results/{id}` - Get analysis results
- `GET /analysis/history` - Get user's analysis history
- `DELETE /analysis/results/{id}` - Delete analysis

### Response Examples:
```json
// Analysis Result
{
  "id": "analysis_id",
  "status": "completed",
  "risk_probability": 0.75,
  "risk_classification": "high",
  "total_variants": 1250,
  "high_risk_variants": 15
}
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Scale API instances
docker-compose up -d --scale api=3
```

## 🔒 Security & Privacy

- **Local Processing**: All genomic data processed locally
- **Encrypted Storage**: User passwords hashed with bcrypt
- **Access Control**: JWT-based authentication
- **Data Isolation**: User data completely separated
- **GDPR Compliant**: Full data deletion capabilities

## 🧬 Supported Genetic Variants

| Gene | Chromosome | Associated Diseases |
|------|------------|--------------------|
| BRCA1 | 17 | Breast/Ovarian Cancer |
| BRCA2 | 13 | Breast/Ovarian Cancer |
| APOE | 19 | Alzheimer's Disease |
| TP53 | 17 | Li-Fraumeni Syndrome |

## 📈 Performance

- **Processing Speed**: ~1000 variants/second
- **File Size Limit**: 100MB VCF files
- **Concurrent Users**: Supports multiple simultaneous analyses
- **Database**: Optimized MongoDB indexes for fast queries

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: Full API docs at `/docs` endpoint
- **Community**: Join our discussions for help and updates