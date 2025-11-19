#!/bin/bash

# Grafana Dashboard Verification Script
echo "🔍 Verifying Grafana Dashboard Setup"
echo "=================================="

# Check if Grafana is accessible
echo "1. Checking Grafana accessibility..."
GRAFANA_HEALTH=$(curl -s http://localhost:3002/api/health)
if [[ $GRAFANA_HEALTH == *"database\": \"ok"* ]]; then
    echo "✅ Grafana is accessible and healthy"
else
    echo "❌ Grafana is not accessible"
    exit 1
fi

# Check if dashboard exists
echo "2. Checking dashboard provisioning..."
DASHBOARD_CHECK=$(curl -s -u admin:admin123 "http://localhost:3002/api/search?query=credit%20card")
if [[ $DASHBOARD_CHECK == *"Credit Card Detector Dashboard"* ]]; then
    echo "✅ Credit Card Detector Dashboard found"

    # Extract dashboard URL
    DASHBOARD_URL=$(echo $DASHBOARD_CHECK | python3 -c "
import json, sys, re
data = json.load(sys.stdin)
for item in data:
    if item['title'] == 'Credit Card Detector Dashboard':
        print(item['url'])
        break
")
    echo "✅ Dashboard URL: http://localhost:3002$DASHBOARD_URL"
else
    echo "❌ Dashboard not found"
    exit 1
fi

# Check if Prometheus has metrics
echo "3. Checking Prometheus metrics..."
PROMETHEUS_CHECK=$(curl -s http://localhost:9090/api/v1/query?query=credit_card_detector_requests_total)
if [[ $PROMETHEUS_CHECK == *"success"* ]]; then
    echo "✅ Prometheus has credit card detector metrics"
else
    echo "❌ Prometheus metrics not available"
    exit 1
fi

# Check if dashboard is receiving data
echo "4. Checking dashboard data flow..."
METRICS_COUNT=$(curl -s http://localhost:9090/api/v1/query?query=credit_card_detector_requests_total | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data['status'] == 'success' and data['data']['result']:
    value = data['data']['result'][0]['value'][1]
    print(int(float(value)))
else:
    print(0)
")

if [[ $METRICS_COUNT -gt 0 ]]; then
    echo "✅ Dashboard is receiving data ($METRICS_COUNT requests recorded)"
else
    echo "⚠️ Dashboard exists but no metrics data yet"
fi

echo ""
echo "🎉 Grafana Dashboard Verification Complete!"
echo "📊 Access your dashboard at: http://localhost:3002$DASHBOARD_URL"
echo "🔍 Grafana credentials: admin/admin123"
echo "📈 Prometheus: http://localhost:9090"