# 🚀 Quick Start Guide

Get up and running with the Credit Card Detector in minutes.

## ⚡ Quick Start (Development)

### Prerequisites
- Python 3.11+ or Docker
- 2 GB RAM minimum
- 2 CPU cores minimum
- 20 GB disk space

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/claude-subagent/credit-card-detector.git
cd credit-card-detector

# Start with minimum resources (2GB RAM, 1-2 CPU cores)
docker-compose up -d

# Check resource usage
docker stats

# Test the API
curl http://localhost:5000/health
```

### Option 2: Python Package

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

## 📈 Monitoring Resources

### Check Resource Usage
```bash
# Docker stats
docker stats

# System resources
curl http://localhost:5000/resource-monitor

# Performance stats
curl http://localhost:5000/performance-stats

# Health check
curl http://localhost:5000/health
```

### Resource Recommendations
```bash
# Get optimization recommendations
curl http://localhost:5000/resource-recommendations
```

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

### High Memory Usage
```bash
# Check memory usage
docker stats

# Restart to clear memory
docker-compose restart

# Adjust memory limits
export MAX_MEMORY_PERCENT=60
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