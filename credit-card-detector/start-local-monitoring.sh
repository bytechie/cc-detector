#!/bin/bash

# Local Credit Card Detection Monitoring Startup Script
# This script sets up local testing with proper Docker networking

set -e

echo "🚀 Starting Local Credit Card Detection Monitoring"
echo "================================================="

# Load local environment variables
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
    echo "✅ Loaded .env.local environment variables"
else
    echo "⚠️ .env.local not found, using defaults"
fi

# Stop any existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.local.yml down || true

# Kill the existing Python app if running
echo "🛑 Stopping existing Python app..."
pkill -f "app_metrics_demo.py" || true

# Wait a moment for cleanup
sleep 2

# Start the monitoring stack (without the credit card app)
echo "📊 Starting monitoring stack..."
docker-compose -f docker-compose.local.yml up -d postgres redis presidio-analyzer presidio-anonymizer prometheus grafana

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🔍 Checking service health..."
docker-compose -f docker-compose.local.yml ps

# Start the enhanced metrics app
echo "🎯 Starting enhanced metrics app..."
source .venv/bin/activate
python3 app_metrics_demo.py &
APP_PID=$!

# Wait for the app to start
sleep 3

# Test if everything is working
echo "🧪 Testing endpoints..."

# Test app health
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Credit Card Detector app is healthy"
else
    echo "❌ Credit Card Detector app health check failed"
fi

# Test metrics endpoint
if curl -f http://localhost:5000/metrics > /dev/null 2>&1; then
    echo "✅ Metrics endpoint is accessible"
else
    echo "❌ Metrics endpoint check failed"
fi

# Test Prometheus
if curl -f http://localhost:9090/api/v1/status/config > /dev/null 2>&1; then
    echo "✅ Prometheus is accessible"
else
    echo "❌ Prometheus check failed"
fi

# Test Grafana
if curl -f http://localhost:3002/api/health > /dev/null 2>&1; then
    echo "✅ Grafana is accessible"
else
    echo "❌ Grafana check failed"
fi

echo ""
echo "🎉 Local monitoring setup complete!"
echo "=================================="
echo "📊 Services available:"
echo "  • Credit Card Detector: http://localhost:5000"
echo "  • Metrics endpoint: http://localhost:5000/metrics"
echo "  • Health check: http://localhost:5000/health"
echo "  • Prometheus: http://localhost:9090"
echo "  • Grafana: http://localhost:3002 (admin/admin123)"
echo ""
echo "🧪 To test detection:"
echo "  curl -X POST http://localhost:5000/scan \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"text\": \"Test card: 4111111111111111\"}'"
echo ""
echo "📊 To check Prometheus targets:"
echo "  curl http://localhost:9090/api/v1/targets"
echo ""
echo "🔍 To view logs:"
echo "  docker-compose -f docker-compose.local.yml logs -f"
echo ""
echo "🛑 To stop everything:"
echo "  docker-compose -f docker-compose.local.yml down"
echo "  kill $APP_PID"

# Save the PID for later cleanup
echo $APP_PID > .local_app.pid

echo ""
echo "🚀 All systems ready! Start monitoring your credit card detection performance."