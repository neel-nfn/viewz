#!/bin/bash

# Viewz Local Development Quick Start Script
# This script helps set up and verify the local development environment

set -e

echo "==================================="
echo "Viewz Local Development Quick Start"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker Desktop and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check if Python is installed
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"

# Check if Node.js is installed
echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm $NPM_VERSION${NC}"

echo ""
echo "==================================="
echo "Setting up Database"
echo "==================================="

# Start Docker Compose
if docker ps | grep -q viewz_db; then
    echo -e "${YELLOW}⚠ Database container already running${NC}"
else
    echo "Starting Postgres container..."
    docker compose up -d
    echo -e "${GREEN}✓ Database started${NC}"
fi

# Wait for database to be ready
echo "Waiting for database to be ready..."
for i in {1..30}; do
    if docker exec viewz_db pg_isready -U viewz -d viewz > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Database is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Database failed to start within 30 seconds${NC}"
        exit 1
    fi
    sleep 1
done

echo ""
echo "==================================="
echo "Setting up Backend"
echo "==================================="

cd backend

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.template .env
    echo -e "${YELLOW}⚠ Please edit backend/.env and add your Google OAuth credentials${NC}"
else
    echo -e "${YELLOW}⚠ .env already exists, skipping...${NC}"
fi

# Create virtual environment if it doesn't exist
if [ ! -d .venv ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source .venv/bin/activate
pip install -q -U pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Run migrations
echo "Running database migrations..."
if alembic upgrade head; then
    echo -e "${GREEN}✓ Migrations completed${NC}"
else
    echo -e "${YELLOW}⚠ Migration warning (this is OK for first run)${NC}"
fi

cd ..

echo ""
echo "==================================="
echo "Setting up Frontend"
echo "==================================="

cd frontend

# Install npm dependencies if node_modules doesn't exist
if [ ! -d node_modules ]; then
    echo "Installing npm dependencies..."
    npm install
    echo -e "${GREEN}✓ npm dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ node_modules already exists, skipping npm install${NC}"
fi

cd ..

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. ${YELLOW}Edit backend/.env with your Google OAuth credentials${NC}"
echo "   Get credentials from: https://console.cloud.google.com/"
echo ""
echo "2. Open THREE terminal tabs/windows and run:"
echo ""
echo "   ${GREEN}Terminal 1 (Database - already running):${NC}"
echo "   cd $(pwd)"
echo "   docker compose logs -f db"
echo ""
echo "   ${GREEN}Terminal 2 (Backend):${NC}"
echo "   cd $(pwd)/backend"
echo "   source .venv/bin/activate"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "   ${GREEN}Terminal 3 (Frontend):${NC}"
echo "   cd $(pwd)/frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser to:"
echo "   ${GREEN}http://localhost:5173/app${NC} (Dashboard Today)"
echo "   ${GREEN}http://localhost:5173/app/workflow${NC} (Kanban)"
echo "   ${GREEN}http://localhost:8000/api/v1/health${NC} (API Health)"
echo ""
echo "For detailed instructions, see: LOCAL_DEV_SETUP.md"
echo ""

