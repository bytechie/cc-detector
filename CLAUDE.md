# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Starting the Application
```bash
# Basic mode (core functionality only)
./start.sh start basic

# Metrics mode (core + Prometheus metrics)
./start.sh start metrics

# Production mode (full features + monitoring)
./start.sh start production

# Enterprise mode (full stack + AI + testing)
./start.sh start enterprise

# Stop all services
./start.sh stop

# Show running instances
./start.sh status

# Restart application
./start.sh restart [mode]
```

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .
```

### Testing
```bash
# Run all tests
./run-mode-tests.sh

# Run specific test types
./run-mode-tests.sh basic
./run-mode-tests.sh metrics
./run-mode-tests.sh production
./run-mode-tests.sh enterprise

# Run tests with pytest directly
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term
```

### Code Quality
```bash
# Format code
black src/ tests/

# Check code formatting
black --check src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Docker Operations
```bash
# Build and run all services
docker-compose up --build

# Run production configuration
docker-compose -f docker-compose.production.yml up

# Run development configuration
docker-compose -f docker-compose.development.yml up

# Stop services
docker-compose down
```

## High-Level Architecture

### Core Components
- **Flask REST API**: Main HTTP service for credit card detection and redaction
- **Detection Engine**: Pattern-based and AI-powered credit card detection
- **Monitoring Stack**: Prometheus metrics and Grafana dashboards
- **Integration Layer**: Support for Claude Skills, n8n workflows, and webhooks

### Application Structure
```
credit-card-detector/
├── src/                    # Core application source code
│   ├── api/               # Flask application and API endpoints
│   ├── detectors/         # Credit card detection logic
│   ├── integrations/      # External service integrations
│   └── utils/             # Utility functions and configuration
├── examples/              # Usage examples and integration demos
│   ├── basic/            # Simple detection examples
│   ├── api/              # REST API integration examples
│   ├── integrations/     # Claude Skills and n8n examples
│   └── integration_demo.py # Complete integration demo
├── tests/                # Test suite (unit, integration, performance)
├── config/               # Configuration files and settings
├── monitoring/           # Prometheus and Grafana configurations
└── docker-compose*.yml   # Docker service definitions
```

### Service Modes
1. **Basic Mode**: Core Flask API with detection functionality
2. **Metrics Mode**: Adds Prometheus metrics endpoint
3. **Production Mode**: Includes monitoring stack (PostgreSQL, Redis, Grafana)
4. **Enterprise Mode**: Full stack with comprehensive testing and AI features

### Key Configuration Files
- **pyproject.toml**: Python project configuration with build system and dependencies
- **requirements.txt**: Core runtime dependencies
- **requirements-dev.txt**: Development and testing dependencies
- **start.sh**: Unified startup script with mode selection
- **docker-compose.yml**: Docker service orchestration

### API Endpoints
- **GET /health**: Health check endpoint
- **POST /scan**: Credit card detection endpoint
- **GET /metrics**: Prometheus metrics (available in metrics/production/enterprise modes)

### Service Port Configuration

**🚨 CRITICAL: Port conflicts have been resolved! See `docs/SERVICE_PORTS.md` for complete port mapping.**

| Service | Port | Environment Variable | Status |
|---------|------|---------------------|--------|
| Flask API | 5000 | `DETECTOR_PORT` | ✅ Stable |
| Presidio Analyzer | 3000 | `PRESIDIO_ANALYZER_PORT` | ✅ Stable |
| Presidio Anonymizer | 3001 | `PRESIDIO_ANONYMIZER_PORT` | ✅ Stable |
| **Grafana** | **3002** | `GRAFANA_PORT` | ✅ **CONFLICT RESOLVED** |
| Prometheus | 9090 | `PROMETHEUS_PORT` | ✅ Stable |
| PostgreSQL | 5432 | `POSTGRES_PORT` | ✅ Stable |
| Redis | 6379 | `REDIS_PORT` | ✅ Stable |

**Historical Conflict**: Grafana was moved from port 3000 to 3002 to resolve conflicts with Presidio Analyzer.

**Port Assignment Rules:**
- Never use ports 3000-3001 (Reserved for Presidio services)
- Use port 3002 for Grafana
- Use ports 5000+ for API services
- Use ports 9000+ for infrastructure services

**Reference Document**: `docs/SERVICE_PORTS.md` - Complete port mapping and conflict prevention guidelines

### Integration Points
- **Claude Skills**: AI-powered detection with adaptive intelligence
- **n8n Workflows**: Automation and workflow integration
- **Webhook Support**: Event-driven integrations
- **REST API**: Standard HTTP interface for external applications

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: API and service integration testing
- **Performance Tests**: Load and stress testing
- **Mode-specific Tests**: Tests tailored to each operational mode

### Monitoring and Observability
- **Prometheus Metrics**: Application performance and custom metrics
- **Grafana Dashboards**: Visual monitoring and alerting
- **Health Checks**: Automated system health validation
- **Structured Logging**: JSON-formatted logs for analysis

## Development Workflow

1. **Feature Development**: Work in feature branches, use the unified `start.sh` script for testing
2. **Testing**: Use mode-specific testing with `./run-mode-tests.sh`
3. **Code Review**: Ensure code quality with automated formatting and linting
4. **Integration Testing**: Validate with examples in `examples/integrations/`
5. **Deployment**: Use Docker Compose for consistent environments

## Important Notes

- Always use the `start.sh` script for application management to ensure proper mode configuration
- The application supports multiple operational modes - choose based on your development needs
- Integration examples are provided in the `examples/` directory for common use cases
- Monitoring is automatically available in production and enterprise modes
- The codebase follows a modular architecture with clear separation of concerns