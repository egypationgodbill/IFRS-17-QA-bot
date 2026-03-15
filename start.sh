#!/bin/bash
set -e

echo "=== PagerDuty Clone ==="

# Backend
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt -q

echo "Starting backend server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend running (PID $BACKEND_PID) on http://localhost:8000"

cd ..

# Frontend
echo "Installing frontend dependencies..."
cd frontend
npm install -q

echo "Starting frontend dev server..."
npm run dev &
FRONTEND_PID=$!
echo "Frontend running (PID $FRONTEND_PID) on http://localhost:3000"

echo ""
echo "==============================="
echo "PagerDuty Clone is running!"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Demo login: admin@example.com / admin123"
echo "==============================="

wait
