#!/bin/bash

# Production Mode Startup Script for Credit Card Detector
# Comprehensive startup with monitoring and full testing

set -e

echo "🚀 Starting Credit Card Detector - Production Mode"
echo "=================================================="

# Configuration
MODE="production"
PORT=${1:-5000}
APP_URL="http://localhost:$PORT"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load production environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
    echo "✅ Loaded .env.production environment variables"
elif [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Loaded .env environment variables"
else
    echo "⚠️ No environment file found, using defaults"
fi

# Stop existing services
echo "🛑 Stopping existing services..."
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    docker-compose -f "$DOCKER_COMPOSE_FILE" down || true
fi
pkill -f "app.py.*--mode.*full\|app.py.*--mode.*production" || true
sleep 5

# Check system resources
echo "🔍 Checking system resources..."
MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
CPU_CORES=$(nproc)

echo "  • Memory: ${MEMORY_GB}GB"
echo "  • CPU cores: ${CPU_CORES}"

if [ "$MEMORY_GB" -lt 4 ]; then
    echo -e "${YELLOW}⚠️ Warning: Less than 4GB RAM detected${NC}"
fi

if [ "$CPU_CORES" -lt 2 ]; then
    echo -e "${YELLOW}⚠️ Warning: Less than 2 CPU cores detected${NC}"
fi

# Start production stack with Docker Compose (if available)
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    echo "🐳 Starting production Docker stack..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

    echo "⏳ Waiting for services to be ready..."
    sleep 15

    # Check service health
    echo "🔍 Checking service health..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
else
    echo -e "${YELLOW}⚠️ Production Docker Compose file not found${NC}"
    echo "Starting application only..."
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Start the application in production mode
echo "🎯 Starting application in production mode..."
python3 app.py --mode full --port $PORT &
APP_PID=$!

# Wait for startup
echo "⏳ Waiting for application to start..."
sleep 8

# Run comprehensive production tests
echo "🧪 Running production mode tests..."
if [ -f "./run-mode-tests.sh" ]; then
    chmod +x ./run-mode-tests.sh
    ./run-mode-tests.sh production
    TEST_RESULT=$?

    if [ $TEST_RESULT -eq 0 ]; then
        echo ""
        echo -e "✅ ${GREEN}Production mode startup successful!${NC}"
        echo -e "🎯 ${GREEN}All tests passed - system ready for production${NC}"
    else
        echo ""
        echo -e "⚠️ ${YELLOW}Some tests failed - review before production use${NC}"

        # Continue with basic health verification
        if curl -f "$APP_URL/health" > /dev/null 2>&1; then
            echo -e "✅ ${GREEN}Application is healthy and running${NC}"
        else
            echo -e "❌ ${RED}Application health check failed${NC}"
            kill $APP_PID 2>/dev/null || true
            exit 1
        fi
    fi
else
    echo "⚠️ Testing script not found, running comprehensive health checks..."

    # Application health
    if curl -f "$APP_URL/health" > /dev/null 2>&1; then
        echo "✅ Application health check passed"
    else
        echo "❌ Application health check failed"
        exit 1
    fi

    # Basic functionality test
    if curl -s -X POST "$APP_URL/scan" \
        -H "Content-Type: application/json" \
        -d '{"text": "Test card: 4111111111111111"}' | grep -q "detections"; then
        echo "✅ Basic functionality test passed"
    else
        echo "❌ Basic functionality test failed"
        exit 1
    fi

    # Metrics test
    if curl -f "$APP_URL/metrics" > /dev/null 2>&1; then
        echo "✅ Metrics endpoint accessible"
    else
        echo "⚠️ Metrics endpoint not accessible (check configuration)"
    fi
fi

echo ""
echo "🎉 Production mode startup complete!"
echo "===================================="
echo "📊 Services available:"
echo "  • Credit Card Detector: $APP_URL"
echo "  • Health check: $APP_URL/health"
echo "  • Metrics endpoint: $APP_URL/metrics"

# Check for external services
if curl -f "http://localhost:9090/api/v1/status/config" > /dev/null 2>&1; then
    echo "  • Prometheus: http://localhost:9090"
fi

if curl -f "http://localhost:3002/api/health" > /dev/null 2>&1; then
    echo "  • Grafana: http://localhost:3002"
fi

echo ""
echo "🧪 To run additional tests:"
echo "  ./run-mode-tests.sh enterprise"
echo ""
echo "📊 Production commands:"
echo "  • Check status: curl $APP_URL/health"
echo "  • Test API: curl -X POST $APP_URL/scan -H \"Content-Type: application/json\" -d '{\"text\": \"Test card: 4111111111111111\"}'"
echo "  • View metrics: curl $APP_URL/metrics"
echo ""
echo "🔍 Monitoring:"
echo "  • View logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f 2>/dev/null || tail -f logs/app.log"
echo "  • Check resources: docker stats 2>/dev/null || top"
echo ""
echo "🛑 To stop:"
echo "  docker-compose -f $DOCKER_COMPOSE_FILE down 2>/dev/null || echo 'No Docker stack running'"
echo "  kill $APP_PID"

# Save PID for cleanup
echo $APP_PID > .production_app.pid
echo ""
echo -e "🚀 ${GREEN}Production mode ready!${NC}"
echo -e "⚡ ${YELLOW}System configured for production workloads${NC}"
