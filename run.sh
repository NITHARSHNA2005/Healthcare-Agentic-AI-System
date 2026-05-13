#!/bin/bash
# run.sh - Start Healthcare AI System (Backend + Frontend)

echo "🏥 Starting Healthcare Agentic AI System..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "🚀 Starting FastAPI backend on http://localhost:8000 ..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 3

echo "🎨 Starting Streamlit frontend on http://localhost:8501 ..."
streamlit run frontend/app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "✅ System is running!"
echo "   Backend API:  http://localhost:8000"
echo "   Frontend UI:  http://localhost:8501"
echo "   API Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
