# 🚀 Quick Start Guide

Get the Dog Breed Prediction app running in 5 minutes!

## Prerequisites
- Docker Desktop installed and running
- 8GB RAM available
- Ports 80, 5000, 5432, 8000 available

## Step-by-Step Instructions

### 1. Navigate to Project Directory
```bash
cd /Users/emperor/Desktop/Xtax/MLOPs
```

### 2. Create Environment File
```bash
cp .env.example .env
# Default values work for local development
```

### 3. Start All Services
```bash
docker-compose up --build
```

Wait for all services to start (2-3 minutes). You'll see:
- ✅ Database migrations completed
- ✅ Backend running on port 8000
- ✅ ML service ready on port 5001
- ✅ Frontend available on port 80

### 4. Access the Application
Open your browser and go to: **http://localhost:80**

### 5. Test the App
1. Click "Browse Files" or drag-drop a dog image
2. Click "Predict Breed"
3. View results in the popup modal
4. Check the "Prediction History" section below

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Run tests
docker-compose exec backend pytest
docker-compose exec ml_service pytest

# Check health
curl http://localhost:8000/api/v1/health/
curl http://localhost:5001/health/

# Access Django admin (after creating superuser)
docker-compose exec backend python manage.py createsuperuser
# Then visit: http://localhost:8000/admin/
```

## Troubleshooting

**Services won't start?**
```bash
docker-compose down -v
docker-compose up --build
```

**Port already in use?**
```bash
# Check what's using the port
lsof -i :80
lsof -i :8000
lsof -i :5000
```

**Need to reset everything?**
```bash
docker-compose down -v --rmi all
docker-compose up --build
```

## What's Next?

- **View API Docs**: http://localhost:5001/docs (FastAPI Swagger UI)
- **Django Admin**: http://localhost:8000/admin/ (after creating superuser)
- **Configure AWS S3**: Edit `.env` and set `USE_S3=True`
- **Deploy to Production**: See README.md for deployment guide

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                    User Browser                       │
└─────────────────────┬────────────────────────────────┘
                      │ HTTP
                      ▼
┌──────────────────────────────────────────────────────┐
│  Frontend (Vue.js + Nginx) - Port 80                 │
│  - Image upload form                                  │
│  - Prediction results modal                           │
│  - History view with pagination                       │
└─────────────────────┬────────────────────────────────┘
                      │ Axios REST API
                      ▼
┌──────────────────────────────────────────────────────┐
│  Backend (Django + DRF) - Port 8000                  │
│  - /api/v1/upload/  (receives image)                 │
│  - /api/v1/history/ (returns transactions)           │
│  - /api/v1/health/  (health check)                   │
└──────────┬────────────────────────┬──────────────────┘
           │                        │
           │ HTTP POST              │ PostgreSQL
           ▼                        ▼
┌─────────────────────┐   ┌─────────────────────┐
│  ML Service         │   │  Database           │
│  (FastAPI)          │   │  (PostgreSQL)       │
│  Port 5001          │   │  Port 5432          │
│  - /predict/        │   │  - transactions     │
│  - /health/         │   │  - indexed queries  │
└─────────────────────┘   └─────────────────────┘
```

## Next Steps

1. **Customize ML Model**: Replace mock prediction in `ml_service/main.py` with real model
2. **Add Authentication**: Implement user auth in Django
3. **Configure S3**: Set up AWS S3 for production image storage
4. **Monitor Logs**: Set up logging aggregation (ELK, CloudWatch)
5. **Scale Services**: Deploy with Kubernetes or Docker Swarm

Enjoy building with the Dog Breed Prediction app! 🐕
