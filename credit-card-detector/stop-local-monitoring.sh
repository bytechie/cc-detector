#!/bin/bash

# Local Credit Card Detection Monitoring Stop Script

echo "🛑 Stopping Local Credit Card Detection Monitoring"
echo "=================================================="

# Stop Docker services
echo "📊 Stopping Docker services..."
docker-compose -f docker-compose.local.yml down

# Stop the Python app
if [ -f .local_app.pid ]; then
    APP_PID=$(cat .local_app.pid)
    if kill -0 $APP_PID 2>/dev/null; then
        echo "🎯 Stopping Python app (PID: $APP_PID)..."
        kill $APP_PID
        # Wait a moment for graceful shutdown
        sleep 2
        # Force kill if still running
        if kill -0 $APP_PID 2>/dev/null; then
            kill -9 $APP_PID
        fi
        echo "✅ Python app stopped"
    else
        echo "ℹ️ Python app already stopped"
    fi
    rm .local_app.pid
else
    echo "ℹ️ No app PID file found"
fi

# Also kill any remaining app processes
echo "🧹 Cleaning up any remaining processes..."
pkill -f "app_metrics_demo.py" || true

echo ""
echo "✅ All services stopped successfully!"
echo "To restart, run: ./start-local-monitoring.sh"