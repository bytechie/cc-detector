#!/bin/bash

# Credit Card Detector Health Check Script
# Checks the health of all running services

echo "🔍 Checking Credit Card Detector Health"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check main application
echo -n "🎯 Credit Card Detector: "
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Unhealthy${NC}"
fi

# Check metrics endpoint
echo -n "📊 Metrics Endpoint: "
if curl -f http://localhost:5000/metrics > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Accessible${NC}"
else
    echo -e "${RED}❌ Not Accessible${NC}"
fi

# Check Prometheus
echo -n "📈 Prometheus: "
if curl -f http://localhost:9090/api/v1/status/config > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${YELLOW}⚠️ Not Running (Optional)${NC}"
fi

# Check Grafana
echo -n "📋 Grafana: "
if curl -f http://localhost:3002/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${YELLOW}⚠️ Not Running (Optional)${NC}"
fi

# Check Docker services if running
echo ""
echo "🐳 Docker Services Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=credit-card\|presidio\|prometheus\|grafana\|postgres\|redis" 2>/dev/null || echo "No Docker services found"

# Test detection functionality
echo ""
echo "🧪 Testing Detection Functionality:"
RESPONSE=$(curl -s -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Test card: 4111111111111111"}' 2>/dev/null)

if [[ $RESPONSE == *"4111111111111111"* ]]; then
    echo -e "✅ ${GREEN}Detection working correctly${NC}"
else
    echo -e "❌ ${RED}Detection test failed${NC}"
fi

echo ""
echo "🏁 Health check complete!"