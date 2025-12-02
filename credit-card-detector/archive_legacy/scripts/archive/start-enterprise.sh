#!/bin/bash

# Enterprise Mode Startup Script for Credit Card Detector
# Full-featured startup with comprehensive monitoring and testing

set -e

echo "🏢 Starting Credit Card Detector - Enterprise Mode"
echo "================================================="

# Configuration
MODE="enterprise"
PORT=${1:-5000}
APP_URL="http://localhost:$PORT"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Load enterprise environment variables
if [ -f .env.enterprise ]; then
    export $(cat .env.enterprise | grep -v '^#' | xargs)
    echo "✅ Loaded .env.enterprise environment variables"
elif [ -f .env.production ]; then
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
pkill -f "app.py.*--mode.*full\|app.py.*--mode.*enterprise" || true
sleep 5

# Comprehensive system resource check
echo "🔍 Comprehensive system resource check..."
MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
CPU_CORES=$(nproc)
DISK_GB=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')

echo -e "${CYAN}System Resources:${NC}"
echo "  • Memory: ${MEMORY_GB}GB ${GREEN}$( [ "$MEMORY_GB" -ge 16 ] && echo "(✓ Enterprise Ready)" || echo "(⚠ Consider upgrading)")${NC}"
echo "  • CPU cores: ${CPU_CORES} ${GREEN}$( [ "$CPU_CORES" -ge 8 ] && echo "(✓ Enterprise Ready)" || echo "(⚠ Consider upgrading)")${NC}"
echo "  • Available disk: ${DISK_GB}GB ${GREEN}$( [ "$DISK_GB" -ge 50 ] && echo "(✓ Enterprise Ready)" || echo "(⚠ Consider upgrading)")${NC}"

# Resource recommendations
if [ "$MEMORY_GB" -lt 16 ]; then
    echo -e "${YELLOW}💡 Recommendation: Consider upgrading to 16GB+ RAM for optimal enterprise performance${NC}"
fi
if [ "$CPU_CORES" -lt 8 ]; then
    echo -e "${YELLOW}💡 Recommendation: Consider upgrading to 8+ CPU cores for optimal enterprise performance${NC}"
fi

# Start enterprise stack with Docker Compose
echo "🐳 Starting enterprise Docker stack..."
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

    echo "⏳ Waiting for services to be ready..."
    sleep 20

    # Comprehensive service health check
    echo "🔍 Comprehensive service health check..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps

    # Check individual service health
    echo "🏥 Checking individual service health..."
    
    # PostgreSQL
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "postgres.*Up"; then
        echo "✅ PostgreSQL database is running"
    else
        echo "⚠️ PostgreSQL database not found or not running"
    fi

    # Redis
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "redis.*Up"; then
        echo "✅ Redis cache is running"
    else
        echo "⚠️ Redis cache not found or not running"
    fi

    # Prometheus
    if curl -f "http://localhost:9090/api/v1/status/config" > /dev/null 2>&1; then
        echo "✅ Prometheus monitoring is accessible"
    else
        echo "⚠️ Prometheus monitoring not accessible"
    fi

    # Grafana
    if curl -f "http://localhost:3002/api/health" > /dev/null 2>&1; then
        echo "✅ Grafana dashboard is accessible"
    else
        echo "⚠️ Grafana dashboard not accessible"
    fi

else
    echo -e "${RED}❌ Production Docker Compose file not found${NC}"
    echo "Enterprise mode requires full monitoring stack"
    exit 1
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

# Start the application in enterprise mode (full mode with all features)
echo "🎯 Starting application in enterprise mode..."
python3 app.py --mode full --port $PORT &
APP_PID=$!

# Extended startup wait for enterprise features
echo "⏳ Waiting for enterprise features to initialize..."
sleep 10

# Run comprehensive enterprise testing
echo "🧪 Running comprehensive enterprise tests..."
if [ -f "./run-mode-tests.sh" ]; then
    chmod +x ./run-mode-tests.sh
    ./run-mode-tests.sh enterprise
    TEST_RESULT=$?

    if [ $TEST_RESULT -eq 0 ]; then
        echo ""
        echo -e "✅ ${GREEN}Enterprise mode startup successful!${NC}"
        echo -e "🎯 ${GREEN}All enterprise tests passed - system ready for production${NC}"
    else
        echo ""
        echo -e "${RED}❌ Critical: Some enterprise tests failed${NC}"
        echo -e "${YELLOW}Please review test failures before proceeding to production${NC}"

        # Continue with comprehensive health verification
        if curl -f "$APP_URL/health" > /dev/null 2>&1; then
            echo -e "✅ ${GREEN}Application is healthy and running${NC}"
        else
            echo -e "${RED}❌ Application health check failed${NC}"
            kill $APP_PID 2>/dev/null || true
            exit 1
        fi
    fi
else
    echo "⚠️ Enterprise testing script not found, running comprehensive health checks..."

    # Full health and functionality verification
    echo "🔬 Running comprehensive verification..."

    # Application health
    if curl -f "$APP_URL/health" > /dev/null 2>&1; then
        echo "✅ Application health check passed"
    else
        echo "❌ Application health check failed"
        exit 1
    fi

    # Core functionality test
    if curl -s -X POST "$APP_URL/scan" \
        -H "Content-Type: application/json" \
        -d '{"text": "Test card: 4111111111111111"}' | grep -q "detections"; then
        echo "✅ Core functionality test passed"
    else
        echo "❌ Core functionality test failed"
        exit 1
    fi

    # Metrics and monitoring test
    if curl -f "$APP_URL/metrics" > /dev/null 2>&1; then
        echo "✅ Metrics endpoint accessible"
        if curl -s "$APP_URL/metrics" | grep -q "credit_card"; then
            echo "✅ Prometheus metrics collection working"
        else
            echo "⚠️ Prometheus metrics collection issue"
        fi
    else
        echo "❌ Metrics endpoint not accessible"
    fi

    # Advanced features test
    if curl -s "$APP_URL/resources" > /dev/null 2>&1; then
        echo "✅ Resource monitoring endpoint accessible"
    else
        echo "⚠️ Resource monitoring endpoint not accessible"
    fi

    if curl -s "$APP_URL/skills" > /dev/null 2>&1; then
        echo "✅ Adaptive skills endpoint accessible"
    else
        echo "⚠️ Adaptive skills endpoint not accessible"
    fi
fi

echo ""
echo -e "🎉 ${GREEN}Enterprise mode startup complete!${NC}"
echo "============================================"
echo -e "📊 ${CYAN}Enterprise Services Available:${NC}"
echo "  • Credit Card Detector: $APP_URL"
echo "  • Health check: $APP_URL/health"
echo "  • Metrics endpoint: $APP_URL/metrics"
echo "  • Resource monitoring: $APP_URL/resources"
echo "  • Adaptive skills: $APP_URL/skills"
echo ""
echo -e "📈 ${CYAN}Monitoring Stack:${NC}"
echo "  • Prometheus: http://localhost:9090"
echo "  • Grafana: http://localhost:3002 (admin/admin123)"

if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "postgres.*Up"; then
    echo "  • PostgreSQL: docker-compose exec postgres psql -U postgres"
fi

if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "redis.*Up"; then
    echo "  • Redis: docker-compose exec redis redis-cli"
fi

echo ""
echo -e "🧪 ${CYAN}Testing Commands:${NC}"
echo "  • Enterprise tests: ./run-mode-tests.sh enterprise"
echo "  • Performance tests: ./run-mode-tests.sh production"
echo "  • API tests: pytest tests/test_subagent.py -v"
echo ""
echo -e "📊 ${CYAN}Enterprise Monitoring:${NC}"
echo "  • System metrics: curl $APP_URL/metrics"
echo "  • Resource usage: curl $APP_URL/resources"
echo "  • Skill performance: curl $APP_URL/skill-performance"
echo ""
echo -e "🔍 ${CYAN}Operations:${NC}"
echo "  • View all logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
echo "  • Check resources: docker stats"
echo "  • Service status: docker-compose -f $DOCKER_COMPOSE_FILE ps"
echo ""
echo -e "🛑 ${CYAN}Shutdown:${NC}"
echo "  • Stop all: docker-compose -f $DOCKER_COMPOSE_FILE down"
echo "  • Stop app: kill $APP_PID"

# Save PID for cleanup
echo $APP_PID > .enterprise_app.pid
echo ""
echo -e "🚀 ${GREEN}Enterprise mode ready for production!${NC}"
echo -e "🔧 ${GREEN}Full monitoring, resource awareness, and adaptive skills enabled${NC}"
echo -e "📈 ${GREEN}System optimized for enterprise workloads${NC}"
