#!/bin/bash
echo "=== Siatki Kramer — Generator Ofert ==="
echo ""

# Backend
echo "Uruchamianie backendu (Python/FastAPI)..."
cd backend
if [ ! -d ".venv" ]; then
  echo "Tworzenie środowiska wirtualnego..."
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt -q
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Skopiowano .env.example → .env (skonfiguruj SMTP!)"
fi
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Frontend
echo "Uruchamianie frontendu (React/Vite)..."
cd frontend
npm install --silent
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✓ Backend: http://localhost:8000"
echo "✓ Frontend: http://localhost:5173"
echo "✓ API Docs: http://localhost:8000/docs"
echo ""
echo "Naciśnij Ctrl+C aby zatrzymać"

wait $BACKEND_PID $FRONTEND_PID
