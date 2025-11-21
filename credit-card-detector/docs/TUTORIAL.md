# 🎓 Credit Card Detector - Complete Tutorial

This comprehensive tutorial will guide you through using the Credit Card Detector project, from basic setup to enterprise deployment with automated testing.

## 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Quick Start](#-quick-start)
3. [Understanding Application Modes](#-understanding-application-modes)
4. [Basic Usage](#-basic-usage)
5. [Working with Different Startup Scripts](#-working-with-different-startup-scripts)
6. [Testing Your Setup](#-testing-your-setup)
7. [Advanced Usage](#-advanced-usage)
8. [Monitoring and Health Checks](#-monitoring-and-health-checks)
9. [Docker Deployment](#-docker-deployment)
10. [Production Best Practices](#-production-best-practices)
11. [Troubleshooting](#-troubleshooting)

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

### System Requirements
- **Python 3.11+** - Required for the application
- **2GB RAM minimum** - For basic mode
- **2 CPU cores minimum** - For optimal performance
- **20GB disk space** - For the project and dependencies

### Optional Requirements
- **Docker & Docker Compose** - For containerized deployment
- **Git** - For cloning the repository

### Install Dependencies (if not using Docker)

```bash
# Clone the repository
git clone https://github.com/bytechie/cc-detector.git
cd credit-card-detector

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ⚡ Quick Start

### The Easiest Way to Start

The **unified startup script** is the recommended approach for all use cases:

```bash
# Basic development with testing
./start.sh basic

# Production deployment with comprehensive testing
./start.sh production

# Enterprise deployment with full validation
./start.sh enterprise
```

### What Happens During Startup?
1. **Prerequisites Check** - Verifies virtual environment and dependencies
2. **Application Start** - Starts the credit card detector in the specified mode
3. **Mode-Appropriate Testing** - Automatically runs tests based on startup complexity
4. **Service Information** - Displays available endpoints and usage examples

### Verify Installation

After startup, test the API:

```bash
# Test detection functionality
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "My Visa card is 4111111111111111"}'
```

Expected response:
```json
{
  "detections": [
    {
      "number": "4111111111111111",
      "valid": true,
      "start": 17,
      "end": 33,
      "raw": "4111111111111111"
    }
  ],
  "redacted": "My Visa card is [REDACTED]"
}
```

## 🎯 Understanding Application Modes

The Credit Card Detector supports four distinct modes, each with different features and testing levels:

| Mode | Command | Testing Level | Resources | Best For |
|------|---------|---------------|-----------|----------|
| **Basic** | `./start.sh basic` | Core functionality tests | ~2GB RAM | Fast development, learning |
| **Metrics** | `./start.sh metrics` | Core + API + monitoring tests | ~4GB RAM | Development with metrics |
| **Production** | `./start.sh production` | Comprehensive + performance tests | ~8GB RAM | Staging, production |
| **Enterprise** | `./start.sh enterprise` | Full suite + advanced features | ~16GB RAM | Enterprise deployment |

### Mode Details

#### Basic Mode
- **Features**: Core credit card detection and redaction
- **Testing**: Health checks + unit tests
- **Startup Time**: ~30 seconds
- **Use Case**: Quick development and testing

#### Metrics Mode
- **Features**: Basic + Prometheus monitoring
- **Testing**: All basic tests + API tests + monitoring verification
- **Startup Time**: ~60 seconds
- **Use Case**: Development with performance tracking

#### Production Mode
- **Features**: All features + monitoring stack (PostgreSQL, Redis, Prometheus, Grafana)
- **Testing**: Comprehensive tests + performance testing + load testing
- **Startup Time**: ~120 seconds
- **Use Case**: Production deployment with full validation

#### Enterprise Mode
- **Features**: Full feature set + resource awareness + adaptive skills
- **Testing**: Complete test suite + advanced features validation
- **Startup Time**: ~180 seconds
- **Use Case**: Enterprise deployment with comprehensive validation

## 🎮 Basic Usage

### Direct API Usage

#### 1. Basic Credit Card Detection

```bash
# Detect credit cards in text
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Payment using Visa 4111111111111111 and Mastercard 5555555555554444"}'
```

#### 2. Different Card Formats

```bash
# Cards with spaces
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Card: 4111 1111 1111 1111"}'

# Cards with dashes
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Card: 4111-1111-1111-1111"}'
```

#### 3. Health Check

```bash
# Check application health
curl http://localhost:5000/health
```

#### 4. Service Information

```bash
# Get available endpoints and service info
curl http://localhost:5000/
```

### Python SDK Usage

```python
from skills.core.detect_credit_cards import detect
from skills.core.redact_credit_cards import redact

# Simple detection
text = "Customer payment: Visa 4111111111111111"
detections = detect(text)
print(f"Found {len(detections)} cards")

# Redaction
redacted = redact(text, detections)
print(f"Redacted: {redacted}")

# Multiple cards
text = "Cards: 4111111111111111, 5555555555554444"
detections = detect(text)
for detection in detections:
    print(f"Card: {detection['number']} (Valid: {detection['valid']})")
```

## 🚀 Working with Different Startup Scripts

### 1. Unified Startup Script (Recommended)

```bash
# Help and usage information
./start.sh --help

# Different modes
./start.sh basic              # Port 5000
./start.sh metrics 5001       # Port 5001
./start.sh production         # Port 5000
./start.sh enterprise 8080    # Port 8080
```

### 2. Mode-Specific Scripts

```bash
# Fast development startup
./start-basic.sh

# Production deployment
./start-production.sh

# Enterprise deployment
./start-enterprise.sh
```

### 3. Development with Monitoring

```bash
# Start with full monitoring stack
./start-local-monitoring.sh

# This starts:
# - PostgreSQL database
# - Redis cache
# - Presidio services (analyzer, anonymizer)
# - Prometheus monitoring
# - Grafana dashboards
# - Application with comprehensive testing
```

### 4. Custom Startup Options

```bash
# Override testing level
TEST_MODE=enterprise ./start.sh basic

# Skip tests for faster startup
SKIP_TESTS=true ./start.sh production

# Custom port
./start.sh basic 8080
```

## 🧪 Testing Your Setup

### Manual Testing

#### Run Mode-Specific Tests

```bash
# Test basic functionality
./run-mode-tests.sh basic

# Test with monitoring
./run-mode-tests.sh metrics

# Full production testing
./run-mode-tests.sh production

# Enterprise-level testing
./run-mode-tests.sh enterprise
```

#### Test Results Explanation

**Basic Mode Tests:**
- ✅ Application health verification
- ✅ Core functionality tests (3/3 PASS)
- ✅ Basic API functionality validation

**Metrics Mode Tests:**
- ✅ All basic mode tests
- ✅ API integration tests (17/17 PASS)
- ✅ Metrics endpoint verification
- ✅ External service connectivity

**Production Mode Tests:**
- ✅ All metrics mode tests
- ✅ Performance and load testing
- ✅ Response time analysis

**Enterprise Mode Tests:**
- ✅ Full test suite with coverage analysis
- ✅ Advanced features testing
- ✅ Enterprise-grade validation

### Automated Testing with pytest

```bash
# Run all working tests
pytest tests/test_detector.py tests/test_credit_card_detection.py tests/test_subagent.py -v

# Run with coverage
pytest --cov=skills --cov-report=html

# Run specific test categories
pytest tests/test_detector.py -v          # Core detection
pytest tests/test_credit_card_detection.py -v  # Detection scenarios
pytest tests/test_subagent.py -v         # API integration
```

### Performance Testing

```bash
# Run load testing
python3 tests/load_testing/generate_load_test.py

# Expected results:
# - 100% success rate
# - Average response time < 1s
# - Handles multiple card detection in single request
```

## 🎓 Advanced Usage

### 1. Resource-Aware Processing

```python
# Configure for resource-constrained environment
from app import CreditCardDetectorApp

app = CreditCardDetectorApp(
    mode='resource_aware',
    max_cpu_percent=60,
    max_memory_percent=70
)
```

### 2. Batch Processing

```python
# Process multiple texts efficiently
texts = [
    "Card 1: 4111111111111111",
    "Card 2: 5555555555554444",
    "Card 3: 378282246310005"
]

# Use the API for batch processing
results = []
for text in texts:
    response = client.post('/scan', json={'text': text})
    results.append(response.get_json())
```

### 3. Custom Configuration

```python
# Use custom configuration
app = CreditCardDetectorApp(
    mode='full',
    config_file='config/custom-config.yaml'
)
```

### 4. Working with Different Card Types

The system detects and validates multiple card types:

```bash
# Visa (starts with 4, 13 or 16 digits)
curl -X POST http://localhost:5000/scan \
  -d '{"text": "Visa: 4111111111111111"}' \
  -H "Content-Type: application/json"

# Mastercard (starts with 51-55, 16 digits)
curl -X POST http://localhost:5000/scan \
  -d '{"text": "Mastercard: 5555555555554444"}' \
  -H "Content-Type: application/json"

# American Express (starts with 34/37, 15 digits)
curl -X POST http://localhost:5000/scan \
  -d '{"text": "Amex: 378282246310005"}' \
  -H "Content-Type: application/json"

# Discover (starts with 6011, 16 digits)
curl -X POST http://localhost:5000/scan \
  -d '{"text": "Discover: 6011111111111117"}' \
  -H "Content-Type: application/json"
```

## 📊 Monitoring and Health Checks

### Health Monitoring Script

```bash
# Comprehensive health check
./check-health.sh
```

This script checks:
- ✅ Main application health
- ✅ Metrics endpoint accessibility
- ✅ Prometheus status (if running)
- ✅ Grafana status (if running)
- ✅ Docker services status
- ✅ Detection functionality

### Manual Health Checks

```bash
# Application health
curl http://localhost:5000/health

# Metrics availability (if in metrics/production/enterprise mode)
curl http://localhost:5000/metrics

# Prometheus (if running)
curl http://localhost:9090/api/v1/status/config

# Grafana (if running)
curl http://localhost:3002/api/health
```

### Monitoring Stack Access

When using production or enterprise mode:

- **Application**: http://localhost:5000
- **Metrics**: http://localhost:5000/metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3002 (admin/admin123)

### Key Metrics to Monitor

```bash
# Check service availability
curl "http://localhost:9090/api/v1/query?query=up"

# Monitor request rate
curl "http://localhost:9090/api/v1/query?query=rate(credit_card_detector_requests_total[5m])"

# Check response times
curl "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, rate(credit_card_detector_request_duration_seconds_bucket[5m]))"
```

## 🐳 Docker Deployment

### Quick Docker Setup

```bash
# Using Docker Compose
docker-compose up -d

# Check services
docker-compose ps

# Test the API
curl http://localhost:5000/health
```

### Production Docker Deployment

```bash
# Production deployment with full stack
docker-compose -f docker-compose.production.yml up -d

# Check all services
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### Docker Testing Integration

```bash
# Run tests with Docker
docker-compose -f docker-compose.testing.yml up test-runner

# Load testing
docker-compose -f docker-compose.testing.yml --profile performance up load-tester

# Health monitoring
docker-compose -f docker-compose.testing.yml --profile monitoring up health-monitor
```

## 🏭 Production Best Practices

### 1. Choose the Right Mode

- **Development**: Use `./start.sh basic` for quick iteration
- **Staging**: Use `./start.sh production` with full testing
- **Production**: Use `./start.sh enterprise` for comprehensive validation

### 2. Monitor Performance

```bash
# Always check health after deployment
./check-health.sh

# Monitor key metrics
curl http://localhost:5000/metrics | grep credit_card
```

### 3. Use Proper Configuration

```bash
# Use production environment
cp config/environments/production.env .env

# Start with production settings
./start.sh production
```

### 4. Implement Health Checks

```bash
# Regular health monitoring
while true; do
    ./check-health.sh
    sleep 60
done
```

### 5. Load Testing Before Production

```bash
# Run comprehensive load testing
./run-mode-tests.sh production

# Verify performance meets requirements
python3 tests/load_testing/generate_load_test.py
```

### 6. Monitor Resources

```bash
# Check resource usage
docker stats  # For Docker deployments
top           # For direct deployments

# Monitor application resources
curl http://localhost:5000/resources  # If in enterprise mode
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Application Won't Start

**Problem**: Application fails to start
```bash
# Check virtual environment
source .venv/bin/activate
pip install -r requirements.txt

# Check port conflicts
lsof -ti:5000 | xargs kill  # Kill existing processes
```

#### 2. Tests Fail

**Problem**: Tests are failing
```bash
# Check application health first
curl http://localhost:5000/health

# Run tests manually for debugging
./run-mode-tests.sh basic

# Check test output for specific errors
pytest tests/test_detector.py -v -s
```

#### 3. Docker Issues

**Problem**: Docker services not starting
```bash
# Check Docker status
docker ps
docker-compose ps

# Clean up and restart
docker-compose down
docker system prune -f
docker-compose up -d
```

#### 4. Performance Issues

**Problem**: Slow response times
```bash
# Check resource usage
curl http://localhost:5000/resources

# Run performance tests
./run-mode-tests.sh production

# Optimize based on resource constraints
export MAX_CPU_PERCENT=70
export MAX_MEMORY_PERCENT=80
```

#### 5. Monitoring Services Not Available

**Problem**: Prometheus/Grafana not accessible
```bash
# Check if services are running
docker ps | grep -E "(prometheus|grafana)"

# Check service logs
docker-compose logs -f prometheus grafana

# Restart monitoring services
./start-local-monitoring.sh
```

### Getting Help

#### 1. Check Documentation
- **[Startup Guide](../STARTUP_GUIDE.md)** - Complete startup documentation
- **[README](../README.md)** - Main project documentation
- **[Testing Guide](../tests/README.md)** - Testing infrastructure details

#### 2. Use Built-in Help
```bash
# Startup script help
./start.sh --help

# Application endpoints
curl http://localhost:5000/
```

#### 3. Check Logs
```bash
# Application logs
tail -f logs/app.log

# Docker logs
docker-compose logs -f

# Service-specific logs
docker-compose logs -f credit-card-detector
```

#### 4. Verify Configuration
```bash
# Check environment variables
env | grep -E "(APP_|MODE_|RESOURCE_)"

# Check configuration files
cat config/app-config.yaml
```

## 🎓 Next Steps

### 1. Explore Advanced Features
- Try different application modes
- Experiment with batch processing
- Implement custom configuration

### 2. Integrate with Your Stack
- Use the Python SDK in your applications
- Set up monitoring with your existing tools
- Deploy to your infrastructure

### 3. Contribute to the Project
- Report issues and suggest improvements
- Submit pull requests
- Share your use cases and configurations

### 4. Stay Updated
- Check the GitHub repository for updates
- Review the documentation for new features
- Join community discussions

---

## 🎉 Tutorial Complete!

Congratulations! You've learned how to:

✅ **Set up** the Credit Card Detector in multiple modes
✅ **Use** the API and Python SDK for detection
✅ **Run** comprehensive testing based on deployment needs
✅ **Monitor** application health and performance
✅ **Deploy** using Docker for production use
✅ **Troubleshoot** common issues

The Credit Card Detector is now ready for use in your projects, from development to enterprise production deployments!

**Next Steps**: Start building with the API and explore the advanced features for your specific use case.

---

**🚀 Happy detecting!** Need help? Check the [documentation](../README.md) or [open an issue](https://github.com/bytechie/cc-detector/issues).