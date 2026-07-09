#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[Spirit Bird] Initializing AdaptEngineV1 Development Environment...${NC}"

# 1. Handle Environment Variables (.env)
if [ ! -f .env ]; then
    echo -e "${YELLOW}[INFO] .env file not found. Creating it from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}[ACTION] Please edit the .env file now if you need to change default passwords.${NC}"
    read -p "Press [Enter] to continue after saving .env..."
fi

# 2. Docker Engine Status Check
echo "[Spirit Bird] Checking Docker Engine status..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}[ERROR] Docker Engine is not running.${NC}"
    echo "Please start Docker Desktop/Engine and try again."
    exit 1
fi

# 3. Docker Compose Installation Check
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}[ERROR] docker-compose could not be found.${NC}"
    echo "Please install Docker Compose."
    exit 1
fi

# 4. Orchestration
echo -e "${GREEN}[Spirit Bird] Spinning up containers...${NC}"
if ! docker-compose up -d; then
    echo -e "${RED}[ERROR] Failed to start Docker containers.${NC}"
    exit 1
fi

echo -e "${GREEN}[Spirit Bird] 🚀 Infrastructure is booting.${NC}"
echo "[Spirit Bird] Waiting for PostgreSQL (pgvector) to stabilize..."

# Dynamic validation: wait for pg_isready
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker-compose exec -T db pg_isready > /dev/null 2>&1; then
        echo -e "${GREEN}[Spirit Bird] PostgreSQL is ready!${NC}"
        break
    fi
    echo "Waiting for PostgreSQL... ($((RETRY_COUNT+1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}[ERROR] PostgreSQL failed to start in time. Check docker-compose logs.${NC}"
    exit 1
fi

# 5. Python Environment & Database Initialization
echo -e "${GREEN}[Spirit Bird] Setting up Python Environment...${NC}"
if [ ! -f "backend/venv/bin/activate" ]; then
    echo -e "${YELLOW}[Spirit Bird] Creating virtual environment...${NC}"
    python3 -m venv backend/venv
fi
source backend/venv/bin/activate
echo -e "${GREEN}[Spirit Bird] Installing/Updating dependencies...${NC}"
pip install -r backend/requirements.txt > /dev/null

echo -e "${GREEN}[Spirit Bird] Running database schema initialization...${NC}"
python3 db_init.py

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Database initialization failed. Check if your .env settings match docker-compose.${NC}"
    exit 1
fi

echo -e "${GREEN}[Spirit Bird] 🟢 System is ONLINE.${NC}"
echo "[Spirit Bird] Monitoring logs: 'docker-compose logs -f'"
