#!/bin/bash

# Unified Management Script for Credit Card Detector
# Supports start/stop operations with mode selection

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default configuration
COMMAND=${1:-"start"}
MODE=${2:-"basic"}
PORT=${3:-5000}
TEST_MODE=${TEST_MODE:-"$MODE"}

echo -e "${BLUE}🚀 Credit Card Detector Manager${NC}"
echo "=================================="
echo -e "Command: ${YELLOW}${COMMAND}${NC}"
if [ "$COMMAND" != "stop" ]; then
    echo -e "Mode: ${YELLOW}${MODE}${NC}"
    echo -e "Port: ${YELLOW}${PORT}${NC}"
fi
echo ""

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [MODE] [PORT]"
    echo ""
    echo "Available commands:"
    echo "  start       - Start the Credit Card Detector"
    echo "  stop        - Stop all running instances"
    echo "  restart     - Stop and start with same mode"
    echo "  status      - Show running instances status"
    echo ""
    echo "Available modes:"
    echo "  basic      - Core functionality only (fastest startup)"
    echo "  metrics    - Core + Prometheus metrics"
    echo "  production - Full features with monitoring stack"
    echo "  enterprise - Full stack with comprehensive testing"
    echo ""
    echo "Examples:"
    echo "  $0 start basic            # Start basic mode on port 5000"
    echo "  $0 start metrics 5001     # Start metrics mode on port 5001"
    echo "  $0 stop                   # Stop all running instances"
    echo "  $0 restart production     # Restart production mode"
    echo "  $0 status                 # Show current status"
    echo ""
    echo "Environment variables:"
    echo "  TEST_MODE    - Override testing level (basic|metrics|production|enterprise)"
    echo "  SKIP_TESTS   - Set to 'true' to skip automated testing"
    exit 1
}

# Function to validate command
validate_command() {
    local command=$1
    case "$command" in
        start|stop|restart|status)
            return 0
            ;;
        *)
            echo -e "${RED}❌ Invalid command: $command${NC}"
            echo ""
            show_usage
            return 1
            ;;
    esac
}

# Function to validate mode
validate_mode() {
    local mode=$1
    case "$mode" in
        basic|metrics|production|enterprise)
            return 0
            ;;
        *)
            echo -e "${RED}❌ Invalid mode: $mode${NC}"
            echo ""
            show_usage
            return 1
            ;;
    esac
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${CYAN}🔍 Checking prerequisites...${NC}"
    
    # Check if we're in the right directory
    if [ ! -f "app.py" ]; then
        echo -e "${RED}❌ app.py not found. Please run from the project directory.${NC}"
        exit 1
    fi
    
    # Check virtual environment
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}⚠️ Virtual environment not found. Creating one...${NC}"
        python3 -m venv .venv
    fi
    
    if [ ! -f ".venv/bin/activate" ]; then
        echo -e "${RED}❌ Virtual environment activation script not found.${NC}"
        exit 1
    fi
    
    # Check dependencies
    source .venv/bin/activate
    if ! python -c "import flask" 2>/dev/null; then
        echo -e "${YELLOW}⚠️ Installing dependencies...${NC}"
        pip install -q flask requests prometheus-client
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Function to start application
start_application() {
    local mode=$1
    local port=$2
    
    echo -e "${CYAN}🎯 Starting application in $mode mode...${NC}"
    
    # Stop existing processes
    pkill -f "app.py.*--mode.*$mode\|app.py.*--port.*$port" || true
    sleep 2
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Start application in background
    case "$mode" in
        "basic")
            python3 app.py --mode basic --port $port &
            ;;
        "metrics")
            python3 app.py --mode metrics --port $port &
            ;;
        "production"|"enterprise")
            python3 app.py --mode full --port $port &
            ;;
    esac
    
    APP_PID=$!
    echo $APP_PID > ".${mode}_app.pid"
    echo -e "${GREEN}✅ Application started (PID: $APP_PID)${NC}"
    
    # Wait for startup
    echo -e "${CYAN}⏳ Waiting for application to start...${NC}"
    sleep 5
}

# Function to run tests
run_tests() {
    local test_mode=$1
    
    if [ "$SKIP_TESTS" = "true" ]; then
        echo -e "${YELLOW}⏭️ Skipping tests (SKIP_TESTS=true)${NC}"
        return 0
    fi
    
    echo -e "${CYAN}🧪 Running $test_mode mode tests...${NC}"
    
    if [ -f "./run-mode-tests.sh" ]; then
        chmod +x ./run-mode-tests.sh
        ./run-mode-tests.sh "$test_mode"
        TEST_RESULT=$?
        
        if [ $TEST_RESULT -eq 0 ]; then
            echo -e "${GREEN}✅ All tests passed${NC}"
        else
            echo -e "${YELLOW}⚠️ Some tests failed, but continuing${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Testing script not found, skipping tests${NC}"
    fi
}

# Function to show service information
show_service_info() {
    local mode=$1
    local port=$2
    local app_url="http://localhost:$port"
    
    echo ""
    echo -e "${GREEN}🎉 Startup complete!${NC}"
    echo "========================"
    echo -e "${CYAN}📊 Services Available:${NC}"
    echo "  • Credit Card Detector: $app_url"
    echo "  • Health check: $app_url/health"
    
    # Mode-specific endpoints
    case "$mode" in
        "metrics"|"production"|"enterprise")
            echo "  • Metrics endpoint: $app_url/metrics"
            ;;
    esac
    
    if [ "$mode" = "production" ] || [ "$mode" = "enterprise" ]; then
        if curl -f "http://localhost:9090/api/v1/status/config" > /dev/null 2>&1; then
            echo "  • Prometheus: http://localhost:9090"
        fi
        if curl -f "http://localhost:3002/api/health" > /dev/null 2>&1; then
            echo "  • Grafana: http://localhost:3002"
        fi
    fi
    
    echo ""
    echo -e "${CYAN}🧪 Test Commands:${NC}"
    echo "  curl -X POST $app_url/scan \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"text\": \"Test card: 4111111111111111\"}'"
    echo ""
    echo -e "${CYAN}🛑 To stop:${NC}"
    echo "  kill $(cat ".${mode}_app.pid" 2>/dev/null || echo "APP_PID")"
    
    if [ -f "docker-compose.local.yml" ] && ([ "$mode" = "production" ] || [ "$mode" = "enterprise" ]); then
        echo "  docker-compose -f docker-compose.local.yml down"
    fi
}

# Function to stop application
stop_application() {
    echo -e "${CYAN}🛑 Stopping Credit Card Detector instances...${NC}"

    local stopped=false

    # Stop using PID files
    for pid_file in .basic_app.pid .metrics_app.pid .production_app.pid .enterprise_app.pid; do
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}Stopping instance with PID $pid...${NC}"
                kill "$pid" 2>/dev/null || true
                sleep 2
                kill -9 "$pid" 2>/dev/null || true
                stopped=true
            fi
            rm -f "$pid_file"
        fi
    done

    # Stop any remaining app.py processes
    local app_pids=$(pgrep -f "python3.*app.py" || true)
    if [ -n "$app_pids" ]; then
        echo -e "${YELLOW}Stopping remaining Python app processes...${NC}"
        echo "$app_pids" | xargs kill 2>/dev/null || true
        sleep 2
        echo "$app_pids" | xargs kill -9 2>/dev/null || true
        stopped=true
    fi

    # Stop Docker services if running
    if [ -f "docker-compose.local.yml" ]; then
        if docker-compose -f docker-compose.local.yml ps -q | grep -q .; then
            echo -e "${YELLOW}Stopping Docker services...${NC}"
            docker-compose -f docker-compose.local.yml down 2>/dev/null || true
            stopped=true
        fi
    fi

    if [ "$stopped" = true ]; then
        echo -e "${GREEN}✅ All instances stopped${NC}"
    else
        echo -e "${YELLOW}⚠️ No running instances found${NC}"
    fi
}

# Function to show status
show_status() {
    echo -e "${CYAN}📊 Credit Card Detector Status${NC}"
    echo "================================="

    local running=false

    # Check PID files
    for mode in basic metrics production enterprise; do
        local pid_file=".${mode}_app.pid"
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                local port=$(lsof -p "$pid" 2>/dev/null | grep LISTEN | awk '{print $9}' | head -1 || echo "unknown")
                echo -e "${GREEN}✅ $mode mode running (PID: $pid, Port: ${port:-unknown})${NC}"
                running=true
            else
                echo -e "${RED}❌ $mode mode PID file exists but process not running${NC}"
                rm -f "$pid_file"
            fi
        fi
    done

    # Check for other app.py processes
    local app_pids=$(pgrep -f "python3.*app.py" || true)
    if [ -n "$app_pids" ]; then
        echo -e "${YELLOW}⚠️ Additional app processes found: $app_pids${NC}"
        running=true
    fi

    # Check Docker services
    if [ -f "docker-compose.local.yml" ]; then
        local docker_services=$(docker-compose -f docker-compose.local.yml ps --services --filter "status=running" 2>/dev/null || true)
        if [ -n "$docker_services" ]; then
            echo -e "${GREEN}✅ Docker services running:${NC}"
            echo "$docker_services" | sed 's/^/  - /'
            running=true
        fi
    fi

    if [ "$running" = false ]; then
        echo -e "${YELLOW}⚠️ No running instances found${NC}"
    fi

    echo ""
    echo -e "${CYAN}🌐 Port Check:${NC}"
    for port in 5000 5001 8080; do
        if lsof -i :$port >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Port $port is in use${NC}"
        else
            echo -e "${GRAY}⚪ Port $port is free${NC}"
        fi
    done
}

# Function to restart application
restart_application() {
    local mode=$1
    local port=$2

    echo -e "${CYAN}🔄 Restarting Credit Card Detector...${NC}"

    # Stop first
    stop_application

    # Wait a moment
    sleep 3

    # Start with same mode
    echo -e "${CYAN}🚀 Starting in $mode mode...${NC}"
    start_application "$mode" "$port"

    # Start additional services if needed
    case "$mode" in
        "production"|"enterprise")
            if [ -f "docker-compose.local.yml" ]; then
                echo -e "${CYAN}🐳 Starting monitoring stack...${NC}"
                docker-compose -f docker-compose.local.yml up -d postgres redis presidio-analyzer presidio-anonymizer prometheus grafana

                # Wait for services
                echo -e "${CYAN}⏳ Waiting for services to be ready...${NC}"
                sleep 15
            fi
            ;;
    esac

    # Run tests
    run_tests "$TEST_MODE"

    # Show service information
    show_service_info "$mode" "$port"
}

# Main execution
main() {
    # Parse arguments
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
    fi

    validate_command "$COMMAND"

    case "$COMMAND" in
        "start")
            validate_mode "$MODE"
            check_prerequisites

            # Start application
            start_application "$MODE" "$PORT"

            # Start additional services if needed
            case "$MODE" in
                "production"|"enterprise")
                    if [ -f "docker-compose.local.yml" ]; then
                        echo -e "${CYAN}🐳 Starting monitoring stack...${NC}"
                        docker-compose -f docker-compose.local.yml up -d postgres redis presidio-analyzer presidio-anonymizer prometheus grafana

                        # Wait for services
                        echo -e "${CYAN}⏳ Waiting for services to be ready...${NC}"
                        sleep 15
                    fi
                    ;;
            esac

            # Run tests
            run_tests "$TEST_MODE"

            # Show service information
            show_service_info "$MODE" "$PORT"
            ;;

        "stop")
            stop_application
            ;;

        "status")
            show_status
            ;;

        "restart")
            # For restart, use the last known mode or default to basic
            local last_mode="basic"
            for pid_file in .basic_app.pid .metrics_app.pid .production_app.pid .enterprise_app.pid; do
                if [ -f "$pid_file" ]; then
                    last_mode=$(echo "$pid_file" | sed 's/\/\./\//' | cut -d'_' -f1 | sed 's/^\.//')
                    break
                fi
            done

            # Override with provided mode if given
            if [ "$#" -ge 2 ] && [ "$2" != "" ]; then
                last_mode="$2"
            fi

            validate_mode "$last_mode"
            restart_application "$last_mode" "$PORT"
            ;;
    esac
}

# Trap for cleanup
trap 'echo -e "\n${YELLOW}⚠️ Startup interrupted${NC}"; exit 1' INT TERM

# Run main function
main "$@"
