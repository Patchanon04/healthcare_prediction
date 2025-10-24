#!/bin/bash
# ============================================
# Update Script สำหรับ AWS EC2
# Medical Diagnosis System
# ============================================

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🔄 Updating Medical Diagnosis System${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Step 1: Pull latest code
echo -e "${GREEN}📥 Step 1: Pulling latest code...${NC}"
git pull origin main

# Step 2: Rebuild images
echo -e "${GREEN}🏗️  Step 2: Rebuilding Docker images...${NC}"
sudo docker compose -f docker-compose.prod.yml build

# Step 3: Restart services
echo -e "${GREEN}🔄 Step 3: Restarting services...${NC}"
sudo docker compose -f docker-compose.prod.yml down
sudo docker compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready (20 seconds)...${NC}"
sleep 20

# Step 4: Run migrations
echo -e "${GREEN}📊 Step 4: Running database migrations...${NC}"
sudo docker compose -f docker-compose.prod.yml exec -T backend python manage.py makemigrations
sudo docker compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

# Step 5: Collect static files (if needed)
echo -e "${GREEN}📦 Step 5: Collecting static files...${NC}"
sudo docker compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput || true

# Step 6: Check status
echo -e "${GREEN}🏥 Step 6: Checking service status...${NC}"
sudo docker compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Update Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Show logs
echo -e "${YELLOW}Showing recent logs (press Ctrl+C to exit):${NC}"
sleep 2
sudo docker compose -f docker-compose.prod.yml logs --tail=50 -f
