# ⚠️ Port 5000 Conflict Fix

## Problem
Port 5000 was already in use by macOS **AirPlay Receiver** (ControlCenter), preventing the ML service from starting.

## Solution Applied
Changed the ML service external port mapping from **5000 → 5001**

### Changes Made:

1. **docker-compose.yml**
   - Changed: `"5000:5000"` → `"5001:5000"`
   - Internal container port remains 5000
   - External host port is now 5001

2. **Documentation Updates**
   - README.md
   - QUICKSTART.md
   - verify-setup.sh
   - Makefile

### Access the ML Service:
- **API Docs (Swagger)**: http://localhost:5001/docs
- **Health Check**: http://localhost:5001/health/
- **Predict Endpoint**: http://localhost:5001/predict/

### Note:
The backend service automatically connects to the ML service via the internal Docker network at `http://ml_service:5000`, so no changes were needed in the backend code.

---

## Alternative Solutions (Not Used)

### Option 1: Kill the AirPlay Process
```bash
# Find the process
lsof -i :5000

# Kill it (not recommended for system services)
kill -9 <PID>
```

### Option 2: Disable AirPlay Receiver in macOS
1. System Preferences → Sharing
2. Uncheck "AirPlay Receiver"

### Option 3: Use Docker Host Network Mode
Not recommended as it reduces isolation between containers.

---

## Current Port Mapping

| Service | External Port | Internal Port | URL |
|---------|---------------|---------------|-----|
| Frontend | 80 | 80 | http://localhost:80 |
| Backend | 8000 | 8000 | http://localhost:8000 |
| ML Service | **5001** | 5000 | http://localhost:5001 |
| PostgreSQL | 5432 | 5432 | localhost:5432 |

---

**Status: ✅ Fixed - Services starting...**
