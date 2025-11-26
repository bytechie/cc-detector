#!/bin/bash

# Basic Mode Startup Script for Credit Card Detector
# Fastest startup with core functionality only

set -e

echo "🚀 Starting Credit Card Detector - Basic Mode"
echo "============================================"

# Configuration
MODE="basic"
PORT=${1:-5000}
APP_URL="http://localhost:$PORT"

# Load local environment variables
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
    echo "✅ Loaded .env.local environment variables"
else
    echo "⚠️ .env.local not found, using defaults"
fi

# Stop existing processes
echo "🛑 Stopping existing processes..."
pkill -f "app.py.*--mode.*basic" || true
sleep 2

# Activate virtual environment
echo "📦 Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Start the application
echo "🎯 Starting application in basic mode..."
python3 app.py --mode basic --port $PORT &
APP_PID=$!

# Wait for startup
echo "⏳ Waiting for application to start..."
sleep 5

# Run mode-appropriate tests
echo "🧪 Running basic mode tests..."
if [ -f "./run-mode-tests.sh" ]; then
    chmod +x ./run-mode-tests.sh
    ./run-mode-tests.sh basic
    TEST_RESULT=$?

    if [ $TEST_RESULT -eq 0 ]; then
        echo ""
        echo -e "✅ ${GREEN}Basic mode startup successful!${NC}"
    else
        echo ""
        echo -e "⚠️ ${YELLOW}Some tests failed, but application is running${NC}"
    fi
else
    echo "⚠️ Testing script not found, running basic health check..."
    if curl -f "$APP_URL/health" > /dev/null 2>&1; then
        echo "✅ Application is healthy"
    else
        echo "❌ Application health check failed"
        kill $APP_PID 2>/dev/null || true
        exit 1
    fi
fi

echo ""
echo "🎉 Basic mode startup complete!"
echo "==============================="
echo "📊 Services available:"
echo "  • Credit Card Detector: $APP_URL"
echo "  • Health check: $APP_URL/health"
echo ""
echo "🧪 To test detection:"
echo "  curl -X POST $APP_URL/scan \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"text\": \"Test card: 4111111111111111\"}'"
echo ""
echo "🔍 To view logs:"
echo "  tail -f logs/app.log 2>/dev/null || echo 'No log file found'"
echo ""
echo "🛑 To stop:"
echo "  kill $APP_PID"

# Save PID for cleanup
echo $APP_PID > .basic_app.pid
echo ""
echo "✅ Basic mode ready for development!"