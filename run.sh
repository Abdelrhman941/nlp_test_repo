#!/bin/bash

# ============================================================
# Pet Health RAG Chatbot - Full System Runner (WSL)
# ============================================================

echo "------------------------------------------------------------"
echo "🐾 Pet Health RAG Chatbot"
echo "------------------------------------------------------------"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ------------------------------------------------------------
# Basic checks
# ------------------------------------------------------------

if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${RED}❌ No active conda environment detected${NC}"
    echo -e "${YELLOW}👉 Please activate your environment first:${NC}"
    echo "   conda activate project_test"
    exit 1
fi

echo -e "${GREEN}✅ Conda environment active: $CONDA_DEFAULT_ENV${NC}"

# Python check
if command -v python >/dev/null 2>&1; then
    PYTHON_CMD=python
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD=python3
else
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python: $($PYTHON_CMD --version)${NC}"

# ------------------------------------------------------------
# Kill existing servers (if any)
# ------------------------------------------------------------

echo -e "${BLUE}-> Checking existing services...${NC}"

for PORT in 8000 8080; do
    PID=$(lsof -ti :$PORT)
    if [ -n "$PID" ]; then
        echo -e "${YELLOW}⚠️  Port $PORT in use, killing process $PID${NC}"
        kill -9 $PID 2>/dev/null
    fi
done

# ------------------------------------------------------------
# Start Backend
# ------------------------------------------------------------

echo -e "${BLUE}-> Starting backend (FastAPI)...${NC}"

$PYTHON_CMD -m uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload &

BACKEND_PID=$!
sleep 3

if ! ps -p $BACKEND_PID >/dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend running (PID: $BACKEND_PID)${NC}"

# ------------------------------------------------------------
# Start Frontend
# ------------------------------------------------------------

echo -e "${BLUE}-> Starting frontend (static server)...${NC}"

cd frontend || {
    echo -e "${RED}❌ frontend directory not found${NC}"
    exit 1
}

$PYTHON_CMD -m http.server 8080 >/dev/null 2>&1 &
FRONTEND_PID=$!

sleep 2

echo -e "${GREEN}✅ Frontend running (PID: $FRONTEND_PID)${NC}"

# ------------------------------------------------------------
# Open browser (WSL-safe)
# ------------------------------------------------------------

echo -e "${BLUE}-> Opening browser...${NC}"

if command -v wslview >/dev/null 2>&1; then
    wslview http://localhost:8080
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:8080
else
    echo -e "${YELLOW}⚠️  Open manually: http://localhost:8080${NC}"
fi

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

echo ""
echo "------------------------------------------------------------"
echo -e "${GREEN}✅ System is running${NC}"
echo "------------------------------------------------------------"
echo -e "Frontend : ${BLUE}http://localhost:8080${NC}"
echo -e "Backend  : ${BLUE}http://localhost:8000${NC}"
echo -e "API Docs : ${BLUE}http://localhost:8000/docs${NC}"
echo "------------------------------------------------------------"
echo -e "${YELLOW}Press Ctrl+C to stop everything${NC}"
echo "------------------------------------------------------------"

# ------------------------------------------------------------
# Graceful shutdown
# ------------------------------------------------------------

trap "echo -e '\n${YELLOW}Stopping services...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT

wait
