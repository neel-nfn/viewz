#!/bin/bash

# Viewz - Start All Servers Script
# This script helps start database, backend, and frontend in one go

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           Viewz Development Servers Launcher              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd /Users/mddeloarhossain/Desktop/Viewz-Workspace

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# Start database if not running
if docker ps | grep -q viewz_db; then
    echo -e "${GREEN}✓ Database already running${NC}"
else
    echo -e "${BLUE}Starting database...${NC}"
    docker compose up -d
    echo -e "${GREEN}✓ Database started${NC}"
fi

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Starting Backend and Frontend in separate terminals...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}⚠️  backend/.env not found. Creating from template...${NC}"
    cp backend/.env.template backend/.env
    echo -e "${RED}⚠️  IMPORTANT: Edit backend/.env with your Google OAuth credentials!${NC}"
    echo ""
fi

# Open Terminal windows for backend and frontend
echo -e "${BLUE}Opening Backend terminal...${NC}"
osascript -e 'tell application "Terminal"
    do script "cd /Users/mddeloarhossain/Desktop/Viewz-Workspace/backend && source .venv/bin/activate && echo \"Running migrations...\" && alembic upgrade head 2>/dev/null || true && echo \"\" && echo \"Starting FastAPI backend...\" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    activate
end tell'

sleep 2

echo -e "${BLUE}Opening Frontend terminal...${NC}"
osascript -e 'tell application "Terminal"
    do script "cd /Users/mddeloarhossain/Desktop/Viewz-Workspace/frontend && echo \"Starting Vite frontend...\" && npm run dev"
    activate
end tell'

echo ""
echo -e "${GREEN}✓ Terminals opened!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Wait ~10 seconds, then visit:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "  ${GREEN}Frontend:${NC}  http://localhost:5173/app"
echo -e "  ${GREEN}Backend:${NC}   http://localhost:8000/api/v1/health"
echo -e "  ${GREEN}API Docs:${NC}  http://localhost:8000/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

