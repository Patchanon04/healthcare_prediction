# 🐕 Dog Breed Prediction Web App

A **production-ready full-stack application** that predicts dog breeds from uploaded images using machine learning. Built with Vue.js, Django REST Framework, FastAPI, PostgreSQL, and Docker.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Configuration](#configuration)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### Frontend (Vue.js)
- 📤 **Image Upload**: Drag-and-drop or browse to upload dog images (JPG/PNG, max 10MB)
- 🎯 **Real-time Prediction**: Get instant breed predictions with confidence scores
- 📊 **History View**: Paginated list of all predictions with sorting
- 🎨 **Modern UI**: Beautiful, responsive interface with TailwindCSS
- 🔔 **Toast Notifications**: User-friendly success/error messages
- ⚡ **Loading States**: Visual feedback during operations

### Backend (Django REST Framework)
- 🚀 **RESTful API**: Versioned API endpoints (`/api/v1/`)
- ☁️ **AWS S3 Integration**: Upload images to cloud storage
- 🔄 **Retry Logic**: Automatic retry for transient ML service failures
- 🗄️ **PostgreSQL Database**: Persistent storage with optimized indexing
- 🏥 **Health Checks**: Monitor service status
- 📝 **Comprehensive Logging**: Track all operations
- 🔒 **CORS Enabled**: Secure cross-origin requests

### ML Microservice (FastAPI)
- 🧠 **Prediction API**: Mock dog breed prediction (easily replaceable with real model)
- ⚡ **Fast Response**: Optimized for low latency
- 📈 **Versioned Models**: Track model versions
- 🏥 **Health Endpoint**: Service monitoring

## 🏗️ Architecture

```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   Frontend  │────▶ │   Backend   │────▶ │ ML Service   │
│  (Vue.js)   │      │   (Django)  │      │  (FastAPI)   │
│   Port 80   │      │  Port 8000  │      │  Port 5000   │
└─────────────┘      └──────┬──────┘      └──────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ PostgreSQL  │
                     │  Port 5432  │
                     └─────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **Vue.js 3** (Composition API)
- **Axios** for HTTP requests
- **TailwindCSS** for styling
- **Vue Toastification** for notifications
- **Nginx** for production serving

### Backend
- **Django 4.2** with REST Framework
- **PostgreSQL 15** for database
- **boto3** for AWS S3 integration
- **tenacity** for retry logic
- **Gunicorn** for production server

### ML Service
- **FastAPI** for high-performance API
- **Uvicorn** for ASGI server
- **httpx** for async HTTP requests

### DevOps
- **Docker & Docker Compose** for containerization
- **pytest** for testing
- **Health checks** for all services

## 📦 Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd MLOPs
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration (optional for local development)
```

### 3. Build and Start Services

```bash
docker-compose up --build
```

This will:
- Build all Docker images
- Start PostgreSQL, ML Service, Backend, and Frontend
- Run database migrations
- Expose services on their respective ports

### 4. Access the Application

- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/v1/
- **ML Service Docs**: http://localhost:5001/docs
- **PostgreSQL**: localhost:5432

### 5. Test the Application

1. Open http://localhost:80 in your browser
2. Upload a dog image (JPG or PNG)
3. View the prediction result in the modal
4. Check the history section for all predictions

## 📁 Project Structure

```
MLOPs/
├── frontend/                 # Vue.js frontend application
│   ├── public/              # Static assets
│   ├── src/
│   │   ├── components/      # Vue components
│   │   │   ├── UploadForm.vue
│   │   │   ├── ResultModal.vue
│   │   │   └── HistoryList.vue
│   │   ├── services/        # API service layer
│   │   │   └── api.js
│   │   ├── assets/          # Styles and assets
│   │   ├── App.vue          # Main app component
│   │   └── main.js          # App entry point
│   ├── Dockerfile
│   ├── nginx.conf           # Nginx configuration
│   └── package.json
│
├── backend/                 # Django backend application
│   ├── config/              # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── predictions/         # Main Django app
│   │   ├── models.py        # Database models
│   │   ├── serializers.py   # DRF serializers
│   │   ├── views.py         # API views
│   │   ├── urls.py          # URL routing
│   │   ├── admin.py         # Admin interface
│   │   └── tests.py         # Unit tests
│   ├── manage.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
│
├── ml_service/              # FastAPI ML microservice
│   ├── main.py              # FastAPI application
│   ├── test_main.py         # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml       # Docker Compose configuration
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 📚 API Documentation

### Backend Endpoints

#### 1. Upload Image
```http
POST /api/v1/upload/
Content-Type: multipart/form-data

Body:
{
  "image": <file>
}

Response (201 Created):
{
  "id": "uuid",
  "image_url": "https://...",
  "breed": "Labrador Retriever",
  "confidence": 0.92,
  "model_version": "v1.0",
  "processing_time": 0.5,
  "uploaded_at": "2024-01-01T12:00:00Z",
  "total_processing_time": 1.2
}
```

#### 2. Get History
```http
GET /api/v1/history/?page=1&page_size=10

Response (200 OK):
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/history/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "breed": "Golden Retriever",
      "confidence": 0.95,
      ...
    }
  ]
}
```

#### 3. Health Check
```http
GET /api/v1/health/

Response (200 OK):
{
  "status": "ok",
  "service": "backend",
  "db": "ok",
  "ml_service": "ok"
}
```

### ML Service Endpoints

#### 1. Predict Breed
```http
POST /predict/
Content-Type: application/json

Body:
{
  "image_url": "https://example.com/dog.jpg"
}

Response (200 OK):
{
  "breed": "Labrador Retriever",
  "confidence": 0.92,
  "model_version": "v1.0",
  "processing_time": 0.27
}
```

#### 2. Health Check
```http
GET /health/

Response (200 OK):
{
  "model": "ready",
  "version": "v1.0"
}
```

## 🧪 Testing

### Run Backend Tests

```bash
# Using Docker
docker-compose exec backend pytest

# Local development
cd backend
pytest
```

### Run ML Service Tests

```bash
# Using Docker
docker-compose exec ml_service pytest

# Local development
cd ml_service
pytest
```

### Test Coverage

- ✅ Health check endpoints
- ✅ Image upload validation
- ✅ Prediction flow with mocks
- ✅ History pagination
- ✅ Database model operations
- ✅ ML service prediction endpoint

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | PostgreSQL database name | `dogbreed_db` |
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `DJANGO_SECRET_KEY` | Django secret key | Dev key |
| `DEBUG` | Django debug mode | `True` |
| `USE_S3` | Enable AWS S3 storage | `False` |
| `AWS_ACCESS_KEY_ID` | AWS access key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name | - |
| `AWS_S3_REGION_NAME` | S3 region | `us-east-1` |

### AWS S3 Configuration (Production)

**📚 Complete Guide:** See [S3_SETUP_GUIDE.md](S3_SETUP_GUIDE.md) for detailed Thai instructions

**Quick Setup:**
1. Create S3 bucket: `dogbreed-images` in AWS Console
2. Set up IAM user with S3 access
3. Create Access Keys and save them
4. Update `.env` file:
   ```env
   USE_S3=True
   AWS_ACCESS_KEY_ID=your-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_STORAGE_BUCKET_NAME=dogbreed-images
   AWS_S3_REGION_NAME=us-east-1
   ```
5. Restart services: `docker-compose restart backend`

**📝 Quick Reference:** See [S3_QUICK_SETUP.txt](S3_QUICK_SETUP.txt)

### Database Indexing

The `Transaction` model includes optimized indexing:
- Index on `uploaded_at` for efficient time-based queries
- UUID primary key for distributed systems

## 🚀 Production Deployment

### Pre-deployment Checklist

- [ ] Set strong `DJANGO_SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure AWS S3 for file storage
- [ ] Set up PostgreSQL with strong password
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure monitoring and logging
- [ ] Set up backup strategy for database

### Production Environment Variables

```env
DEBUG=False
DJANGO_SECRET_KEY=<generate-strong-secret-key>
USE_S3=True
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Deployment Options

1. **Docker Swarm**: Use `docker-compose.yml` as base
2. **Kubernetes**: Convert to K8s manifests
3. **Cloud Platforms**: AWS ECS, Google Cloud Run, Azure Container Instances

### Scaling Considerations

- **Backend**: Increase Gunicorn workers in `Dockerfile`
- **ML Service**: Deploy multiple instances behind load balancer
- **Database**: Use managed PostgreSQL service (RDS, Cloud SQL)
- **Frontend**: Use CDN for static assets

## 🐛 Troubleshooting

### Issue: Services won't start

**Solution:**
```bash
# Check Docker logs
docker-compose logs <service-name>

# Restart services
docker-compose down
docker-compose up --build
```

### Issue: Database connection error

**Solution:**
```bash
# Ensure PostgreSQL is running
docker-compose ps

# Check database health
docker-compose exec db pg_isready -U postgres

# Recreate database
docker-compose down -v
docker-compose up --build
```

### Issue: ML service unreachable

**Solution:**
```bash
# Check ML service logs
docker-compose logs ml_service

# Test ML service directly
curl http://localhost:5001/health/
```

### Issue: Frontend can't reach backend

**Solution:**
1. Check CORS configuration in `backend/config/settings.py`
2. Verify `VUE_APP_API_URL` in frontend `.env`
3. Check network connectivity between containers

### Issue: File upload fails

**Solution:**
1. Check file size (max 10MB)
2. Verify file format (JPG/PNG only)
3. If using S3, check AWS credentials
4. Check backend logs: `docker-compose logs backend`

## 📝 Development

### Local Development (without Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### ML Service
```bash
cd ml_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 5000
```

#### Frontend
```bash
cd frontend
npm install
npm run serve
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

Built with ❤️ as a production-ready MLOps demonstration project.

## 🙏 Acknowledgments

- FastAPI for excellent ML service framework
- Django REST Framework for robust backend
- Vue.js for reactive frontend
- Docker for seamless containerization

---

**Happy Dog Breed Predicting! 🐕🎉**
