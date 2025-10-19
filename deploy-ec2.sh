#!/bin/bash
# ============================================
# Deploy Script สำหรับ AWS EC2
# Dog Breed Prediction System
# ============================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 Dog Breed Prediction - EC2 Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running on EC2
if [ ! -f /sys/hypervisor/uuid ] || ! grep -q ec2 /sys/hypervisor/uuid 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: This script is designed for AWS EC2${NC}"
    echo -e "${YELLOW}   Continue anyway? (y/n)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ============================================
# Step 1: Update System
# ============================================
echo -e "${GREEN}📦 Step 1: Updating system...${NC}"
sudo apt update
sudo apt upgrade -y

# ============================================
# Step 2: Install Docker
# ============================================
if ! command -v docker &> /dev/null; then
    echo -e "${GREEN}🐋 Step 2: Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# ============================================
# Step 3: Install Docker Compose
# ============================================
if ! command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}🔧 Step 3: Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# ============================================
# Step 4: Install Utilities
# ============================================
echo -e "${GREEN}🛠️  Step 4: Installing utilities...${NC}"
sudo apt install -y htop vim curl wget git

# ============================================
# Step 5: Check .env file
# ============================================
echo -e "${GREEN}⚙️  Step 5: Checking configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your credentials:${NC}"
    echo -e "${YELLOW}   - AWS credentials${NC}"
    echo -e "${YELLOW}   - Django secret key${NC}"
    echo -e "${YELLOW}   - Strong password${NC}"
    echo ""
    echo -e "${YELLOW}Edit .env now? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        nano .env
    else
        echo -e "${RED}Please edit .env before continuing${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# ============================================
# Step 6: Validate .env
# ============================================
echo -e "${GREEN}🔍 Step 6: Validating .env...${NC}"

# Check critical variables
if grep -q "your-aws-access-key-id" .env || grep -q "YOUR_STRONG_PASSWORD_HERE" .env; then
    echo -e "${RED}❌ .env contains placeholder values!${NC}"
    echo -e "${YELLOW}Please update the following in .env:${NC}"
    echo -e "${YELLOW}   - AWS_ACCESS_KEY_ID${NC}"
    echo -e "${YELLOW}   - AWS_SECRET_ACCESS_KEY${NC}"
    echo -e "${YELLOW}   - POSTGRES_PASSWORD${NC}"
    echo -e "${YELLOW}   - DJANGO_SECRET_KEY${NC}"
    exit 1
fi

echo -e "${GREEN}✅ .env validation passed${NC}"

# ============================================
# Step 7: Setup Firewall (UFW)
# ============================================
echo -e "${GREEN}🔥 Step 7: Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    sudo ufw allow 22/tcp    # SSH
    sudo ufw allow 80/tcp    # HTTP
    sudo ufw allow 443/tcp   # HTTPS
    sudo ufw --force enable
    echo -e "${GREEN}✅ Firewall configured${NC}"
fi

# ============================================
# Step 8: Build Docker Images
# ============================================
echo -e "${GREEN}🏗️  Step 8: Building Docker images...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes...${NC}"
docker-compose build

# ============================================
# Step 9: Start Services
# ============================================
echo -e "${GREEN}🚀 Step 9: Starting services...${NC}"
docker-compose up -d

echo -e "${YELLOW}Waiting for services to be ready (30 seconds)...${NC}"
sleep 30

# ============================================
# Step 10: Run Migrations
# ============================================
echo -e "${GREEN}📊 Step 10: Running database migrations...${NC}"
docker-compose exec -T backend python manage.py migrate

# ============================================
# Step 11: Health Checks
# ============================================
echo -e "${GREEN}🏥 Step 11: Running health checks...${NC}"

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Services are running${NC}"
else
    echo -e "${RED}❌ Some services are not running${NC}"
    docker-compose ps
    exit 1
fi

# Check backend health
if curl -s http://localhost:8000/api/v1/health/ | grep -q "ok"; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Backend health check failed${NC}"
fi

# Check ML service health
if curl -s http://localhost:5001/health/ | grep -q "ready"; then
    echo -e "${GREEN}✅ ML service is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  ML service health check failed${NC}"
fi

# ============================================
# Step 12: Setup Auto-start
# ============================================
echo -e "${GREEN}⚙️  Step 12: Setting up auto-start on reboot...${NC}"

sudo tee /etc/systemd/system/dogbreed.service > /dev/null <<EOF
[Unit]
Description=Dog Breed Prediction Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable dogbreed.service
echo -e "${GREEN}✅ Auto-start configured${NC}"

# ============================================
# Step 13: Show Summary
# ============================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get public IP
if command -v curl &> /dev/null; then
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "UNABLE_TO_DETECT")
else
    PUBLIC_IP="UNABLE_TO_DETECT"
fi

echo -e "${GREEN}📍 Access your application:${NC}"
echo ""
echo -e "   Frontend:  ${YELLOW}http://${PUBLIC_IP}${NC}"
echo -e "   Backend:   ${YELLOW}http://${PUBLIC_IP}:8000/api/v1/${NC}"
echo -e "   ML Docs:   ${YELLOW}http://${PUBLIC_IP}:5001/docs${NC}"
echo ""

echo -e "${GREEN}📊 Useful commands:${NC}"
echo ""
echo -e "   View logs:         ${YELLOW}docker-compose logs -f${NC}"
echo -e "   Restart services:  ${YELLOW}docker-compose restart${NC}"
echo -e "   Stop services:     ${YELLOW}docker-compose down${NC}"
echo -e "   Check status:      ${YELLOW}docker-compose ps${NC}"
echo ""

echo -e "${GREEN}🔐 Security reminders:${NC}"
echo ""
echo -e "   1. ${YELLOW}Update Security Group${NC} to restrict access"
echo -e "   2. ${YELLOW}Setup SSL/HTTPS${NC} for production"
echo -e "   3. ${YELLOW}Regular backups${NC} of database"
echo -e "   4. ${YELLOW}Monitor logs${NC} for security issues"
echo ""

echo -e "${GREEN}🎉 Happy predicting!${NC}"
echo ""

# Optional: Create superuser
echo -e "${YELLOW}Create Django superuser now? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    docker-compose exec backend python manage.py createsuperuser
fi
