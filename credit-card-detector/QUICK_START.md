# 🚀 Quick Start Guide

Get up and running with the Credit Card Detector in minutes.

## ⚡ Quick Start (Development)

### Prerequisites
- Python 3.11+ or Docker
- 2 GB RAM minimum
- 2 CPU cores minimum
- 20 GB disk space

### Option 1: Local Development with Monitoring (Recommended)

```bash
# Clone the repository
git clone https://github.com/claude-subagent/credit-card-detector.git
cd credit-card-detector

# Start local monitoring stack (includes enhanced metrics)
./start-local-monitoring.sh

# Services available:
# • Credit Card Detector: http://localhost:5000
# • Metrics endpoint: http://localhost:5000/metrics
# • Health check: http://localhost:5000/health
# • Prometheus: http://localhost:9090
# • Grafana: http://localhost:3002 (admin/admin123)

# Test the API
curl http://localhost:5000/health

# Stop services when done
./stop-local-monitoring.sh
```

### Option 2: Docker Basic

```bash
# Start with minimum resources (2GB RAM, 1-2 CPU cores)
docker-compose up -d

# Check resource usage
docker stats

# Test the API
curl http://localhost:5000/health
```

### Option 3: Python Package

```bash
# Install the package
pip install claude-subagent-credit-card-detector

# Basic usage
python -c "
from claude_subagent import CreditCardDetector
detector = CreditCardDetector()
result = detector.scan('Credit card: 4111111111111111')
print(f'Found {len(result.detections)} cards')
"
```

## 🔧 Basic Usage

### Python SDK
```python
from claude_subagent import CreditCardDetector

# Initialize
detector = CreditCardDetector()

# Simple detection
result = detector.scan("Card: 4111111111111111")
print(f"Detections: {len(result.detections)}")

# Enhanced detection with AI optimization
result = detector.scan_enhanced(
    "Multiple cards: 4111111111111111, 4242-4242-4242-4242",
    resource_aware=True,
    use_all_skills=True
)
```

### REST API
```bash
# Basic scan
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Card: 4111111111111111"}'

# Example response:
# {
#   "detections": [{"end": 25, "number": "4111111111111111", "raw": "4111111111111111", "start": 9, "valid": true}],
#   "metrics": {"cards_detected": 1, "invalid_cards": 0, "scan_duration_seconds": 0.0001, "valid_cards": 1},
#   "redacted": "Card: [REDACTED]"
# }

# Test different card formats
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Cards: 4111 1111 1111 1111, 5555-5555-5555-4444, 378282246310005"}'

# Enhanced scan
curl -X POST http://localhost:5000/scan-enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Card: 4111111111111111",
    "options": {
      "resource_aware": true,
      "use_all_skills": true
    }
  }'
```

### JavaScript SDK
```javascript
import { CreditCardDetector } from '@claude-subagent/javascript-sdk';

const detector = new CreditCardDetector();
const result = await detector.scan('Card: 4111111111111111');
console.log(`Found ${result.detections.length} cards`);
```

## 📊 Resource Requirements

| Deployment | CPU | Memory | Storage | Use Case |
|------------|-----|--------|---------|----------|
| **Development** | 2 cores | 4 GB | 20 GB | Development & testing |
| **Production** | 4-8 cores | 8-16 GB | 50-100 GB | Medium-scale production |
| **Enterprise** | 16+ cores | 32-64 GB | 200+ GB | Large-scale enterprise |

**For detailed resource requirements, see [docs/compute-resources.md](docs/compute-resources.md)**

## 🐳 Deployment Options

### Development Setup
```bash
# Runs with minimum resources (~2GB RAM, 1-2 CPU cores)
docker-compose up -d
```

### Production Setup
```bash
# Production deployment (~8GB RAM, 4+ CPU cores)
docker-compose -f docker-compose.prod.yml up -d

# Include monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d
```

### Enterprise Setup
```bash
# Full enterprise stack (~16GB+ RAM, 8+ CPU cores)
docker-compose -f docker-compose.enterprise.yml up -d
```

## 🎯 Resource Profiles

The system automatically detects your resources and configures itself:

- **Development Profile**: Minimal resources, basic features
- **Production Profile**: Balanced resources, full features
- **Enterprise Profile**: Maximum resources, advanced features

You can also manually specify a profile:

```python
from claude_subagent.resource_management import initialize_resource_manager

# Initialize with production profile
rm = initialize_resource_manager(profile="production")
```

## 📈 Production Monitoring & Observability

### 🚀 Local Development Monitoring (Recommended)

```bash
# Start local monitoring stack with enhanced metrics
./start-local-monitoring.sh

# Access monitoring interfaces:
# • Credit Card Detector: http://localhost:5000
# • Metrics endpoint: http://localhost:5000/metrics
# • Health check: http://localhost:5000/health
# • Prometheus: http://localhost:9090
# • Grafana: http://localhost:3002 (admin/admin123)

# Stop when done
./stop-local-monitoring.sh
```

### 🚀 Production Monitoring

```bash
# Start production stack with monitoring
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# Access monitoring interfaces
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3002
```

### 📊 Essential Monitoring Commands

```bash
# Check all service status
docker-compose -f docker-compose.production.yml ps

# Check resource usage
docker stats

# Run comprehensive monitoring test
python3 monitor_credit_card_performance.py

# View monitoring stack logs
docker-compose logs -f prometheus grafana
```

### 🎯 Key Metrics to Monitor

| Metric | Command | Target |
|--------|---------|--------|
| **Service Status** | `curl http://localhost:9090/api/v1/query?query=up` | All services up |
| **Response Time** | See Grafana dashboard | < 100ms (95th percentile) |
| **Error Rate** | See Grafana dashboard | < 1% |
| **Throughput** | See Grafana dashboard | Baseline monitoring |

### 📈 Grafana Dashboard Setup

1. **Access Grafana**: http://localhost:3002
2. **Login** with your credentials
3. **Import Dashboard**:
   - Go to Dashboards → Import
   - Upload `monitoring/grafana/dashboards/credit-card-dashboard.json`
   - Select Prometheus as data source

### 🔍 Prometheus Queries

```bash
# Check service availability
curl "http://localhost:9090/api/v1/query?query=up"

# Monitor request rate
curl "http://localhost:9090/api/v1/query?query=rate(credit_card_detector_requests_total[5m])"

# Check response times
curl "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, rate(credit_card_detector_request_duration_seconds_bucket[5m]))"
```

### 🧪 Test Detection Performance

```bash
# Test the detection API
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Test card: 4111111111111111"}'

# Test different card formats
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Cards: 4111 1111 1111 1111, 5555-5555-5555-4444, 378282246310005"}'

# Test invalid cards (should be detected but marked as invalid)
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Invalid card: 1234 5678 9012 3456"}'

# Test multiple cards in one text
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Multiple cards: 4111111111111111 (Visa), 5555555555554444 (Mastercard), 378282246310005 (Amex)"}'

# Run performance test suite
python3 test_credit_card_detection.py

# Check metrics after testing
curl -s http://localhost:5000/metrics | grep credit_card
```

### 🚨 Basic Alerting

The system includes pre-configured alerts for:
- High response times (>100ms)
- High error rates (>1%)
- Service downtime
- Resource exhaustion

### 📋 Monitoring Checklist

- [ ] Services running: `docker ps` or `docker-compose ps`
- [ ] API health check: `curl http://localhost:5000/health`
- [ ] Metrics endpoint: `curl http://localhost:5000/metrics`
- [ ] Prometheus accessible: http://localhost:9090
- [ ] Grafana accessible: http://localhost:3002 (admin/admin123)
- [ ] Dashboard imported and showing data
- [ ] Metrics being collected: Check Prometheus targets
- [ ] No critical alerts firing

### 🧪 Enhanced Testing Examples

The system has been tested with various credit card formats and scenarios:

**Valid Card Detection:**
```bash
# Visa (valid Luhn)
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "My Visa: 4111111111111111"}'

# Mastercard (valid Luhn)
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Mastercard: 5555555555554444"}'

# Amex (valid Luhn)
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Amex: 378282246310005"}'
```

**Format Variations:**
```bash
# Spaces and dashes are handled correctly
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Cards: 4111 1111 1111 1111, 5555-5555-5555-4444"}'
```

**Validation Testing:**
```bash
# Invalid Luhn checksum (detected but marked invalid)
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Invalid: 1234 5678 9012 3456"}'

# Phone numbers (correctly ignored)
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Call me at 123-456-7890"}'
```

**Performance Metrics (from recent tests):**
- ✅ Detection Speed: ~0.0001 seconds per scan
- ✅ Multiple Cards: Detects 3+ cards in one text
- ✅ Format Support: Spaces, dashes, plain numbers
- ✅ Validation: Distinguishes valid vs invalid Luhn checksums
- ✅ Redaction: Properly masks detected cards

### 🔧 Advanced Monitoring

For detailed monitoring setup, see:
- **README.md**: Complete monitoring guide
- **monitoring/grafana/dashboards/**: Dashboard configurations
- **monitoring/prometheus.yml**: Prometheus configuration

## ⚡ Performance Tips

### 1. Resource Optimization
The system automatically optimizes based on available resources:

```python
# Enable resource-aware processing
result = detector.scan_enhanced(text, resource_aware=True)
```

### 2. Batch Processing
```python
# Process multiple texts efficiently
texts = ["text1", "text2", "text3"]
result = detector.scan_batch(texts, parallel=True)
```

### 3. Plugin Management
```python
# Check available plugins
plugins = detector.list_plugins()

# Enable/disable plugins based on resources
detector.configure_plugins(enabled_plugins=['basic_detector', 'regex_enhancer'])
```

## 🔧 Configuration

### Environment Variables
```bash
# Basic configuration
export CLAUDE_API_KEY=your-api-key
export SUBAGENT_PORT=5000

# Resource constraints
export MAX_CPU_PERCENT=80
export MAX_MEMORY_PERCENT=80
export MAX_BATCH_SIZE=1000

# Resource profile
export RESOURCE_PROFILE=production  # development, production, enterprise
```

### Configuration File
```yaml
# config/production.yaml
app:
  name: credit-card-detector
  environment: production

resources:
  max_cpu_percent: 75
  max_memory_percent: 80
  profile: production

detection:
  confidence_threshold: 0.7
  enable_optimization: true
```

## 🧪 Testing

### Run Tests
```bash
# Basic tests
pytest

# Performance tests
pytest -m performance

# Resource-intensive tests
pytest -m resource_intensive

# Coverage
pytest --cov=claude_subagent --cov-report=html
```

### Benchmark Performance
```bash
# Quick benchmark
curl -X POST http://localhost:5000/benchmark-processing \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test text 1", "test text 2"], "iterations": 3}'
```

## 🚨 Common Issues

### Services Won't Start
```bash
# Check for port conflicts
netstat -tulpn | grep -E "(5000|3000|3001|9090|3002|5432|6379)"

# Stop existing services
./stop-local-monitoring.sh

# Clean up orphaned containers
docker container prune -f

# Restart fresh
./start-local-monitoring.sh
```

### High Memory Usage
```bash
# Check memory usage
docker stats

# Restart to clear memory
docker-compose restart

# Adjust memory limits
export MAX_MEMORY_PERCENT=60

# Stop and restart services
./stop-local-monitoring.sh
./start-local-monitoring.sh
```

### High CPU Usage
```bash
# Check CPU usage
docker stats

# Reduce concurrent processing
curl -X PUT http://localhost:5000/resource-constraints \
  -H "Content-Type: application/json" \
  -d '{"max_cpu_percent": 60}'
```

### Slow Performance
```bash
# Check current metrics
curl http://localhost:5000/resource-monitor

# Get recommendations
curl http://localhost:5000/resource-recommendations

# Switch to performance profile
export RESOURCE_PROFILE=enterprise
```

### Grafana/Prometheus Not Accessible
```bash
# Check if services are running
docker ps | grep -E "(grafana|prometheus)"

# Check logs
docker-compose logs -f grafana prometheus

# Restart monitoring services
./stop-local-monitoring.sh
./start-local-monitoring.sh
```

## 📚 Next Steps

- **[Compute Resource Requirements](docs/compute-resources.md)** - Detailed hardware and cloud specifications
- **[API Documentation](https://claude-subagent.github.io/credit-card-detector/)** - Complete API reference
- **[Plugin Development](docs/plugin-development.md)** - Create custom plugins
- **[Performance Optimization](docs/performance-optimization.md)** - Advanced performance tuning
- **[Deployment Guide](docs/deployment.md)** - Production deployment
- **[Monitoring Guide](docs/monitoring.md)** - Set up monitoring and alerting

## 🆘 Support

- **Documentation**: [https://claude-subagent.github.io/credit-card-detector/](https://claude-subagent.github.io/credit-card-detector/)
- **Issues**: [GitHub Issues](https://github.com/claude-subagent/credit-card-detector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/claude-subagent/credit-card-detector/discussions)
- **Email**: [support@claude-subagent.com](mailto:support@claude-subagent.com)

---

🎉 **Congratulations!** You're now ready to use the Credit Card Detector.

The system will automatically adapt to your available resources and optimize performance accordingly. Start with the development profile and scale up as needed!