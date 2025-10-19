#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Dog Breed Prediction - Setup Verification Script"
echo "=================================================="
echo ""

# Check if Docker is running
echo "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Check if docker-compose is available
echo "Checking docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ docker-compose not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ docker-compose is available${NC}"
echo ""

# Check if .env file exists
echo "Checking environment configuration..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found, creating from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi
echo ""

# Check required ports
echo "Checking port availability..."
PORTS=(80 5001 5432 8000)
ALL_PORTS_FREE=true

for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}✗ Port $port is already in use${NC}"
        ALL_PORTS_FREE=false
    else
        echo -e "${GREEN}✓ Port $port is available${NC}"
    fi
done

if [ "$ALL_PORTS_FREE" = false ]; then
    echo ""
    echo -e "${YELLOW}⚠ Some ports are in use. Stop those services or change ports in docker-compose.yml${NC}"
    exit 1
fi
echo ""

# Check directory structure
echo "Checking project structure..."
REQUIRED_DIRS=("frontend" "backend" "ml_service")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ $dir/ directory exists${NC}"
    else
        echo -e "${RED}✗ $dir/ directory missing${NC}"
        exit 1
    fi
done
echo ""

# Check Dockerfiles
echo "Checking Dockerfiles..."
DOCKERFILES=("frontend/Dockerfile" "backend/Dockerfile" "ml_service/Dockerfile")
for dockerfile in "${DOCKERFILES[@]}"; do
    if [ -f "$dockerfile" ]; then
        echo -e "${GREEN}✓ $dockerfile exists${NC}"
    else
        echo -e "${RED}✗ $dockerfile missing${NC}"
        exit 1
    fi
done
echo ""

echo -e "${GREEN}✅ All checks passed!${NC}"
echo ""
echo "You can now start the application with:"
echo -e "${YELLOW}docker-compose up --build${NC}"
echo ""
echo "After services start, access:"
echo "  • Frontend:     http://localhost:80"
echo "  • Backend API:  http://localhost:8000/api/v1/"
echo "  • ML Service:   http://localhost:5001/docs"
echo ""
echo "To monitor startup:"
echo -e "${YELLOW}docker-compose logs -f${NC}"
