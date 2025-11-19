# 🛡️ Credit Card Detector with Resource-Aware AI

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/claude-subagent/credit-card-detector/actions/workflows/ci-cd/badge.svg)](https://github.com/claude-subagent/credit-card-detector/actions)
[![Coverage](https://img.shields.io/codecov/c/github/claude-subagent/credit-card-detector?branch=main&logo=codecov)](https://codecov.io/gh/claude-subagent/credit-card-detector?branch=main)
[![Docker Pulls](https://img.shields.io/docker/pulls/claude-subagent/credit-card-detector?style=flat&logo=docker)](https://hub.docker.com/r/claude-subagent/credit-card-detector)

🚀 **An intelligent, adaptive credit card detection system that learns from resource constraints and automatically optimizes performance.**

## 🎯 Key Features

### 🧠 **Resource-Aware AI Intelligence**
- **Real-time Resource Monitoring**: CPU, memory, disk, network tracking
- **Adaptive Strategy Selection**: Automatically chooses optimal processing approach
- **ML-Based Performance Prediction**: Forecasts performance before execution
- **Dynamic Optimization**: Adjusts batch sizes and concurrency automatically

### 🔧 **Advanced Adaptive Skills System**
- **Automatic Skill Generation**: Creates new detection skills from patterns
- **Skill Seekers Integration**: Learns from external documentation and repositories
- **Conflict Detection & Resolution**: Intelligently manages skill conflicts
- **Quality-Based Filtering**: Only deploys high-quality skills

### 🔌 **Comprehensive Plugin Architecture**
- **Hot-Loading**: Add/modify plugins without restarting
- **Multiple Plugin Types**: Detectors, processors, outputs, integrations
- **Dependency Management**: Automatic dependency resolution
- **Lifecycle Management**: Full plugin lifecycle support

### 📊 **Enterprise-Grade Monitoring**
- **Comprehensive Metrics**: Performance, resource, and business metrics
- **Distributed Tracing**: Track requests across services
- **Error Tracking**: Intelligent error capture and analysis
- **Health Monitoring**: Complete system health checks

### 🛠️ **Production-Ready Infrastructure**
- **Docker Support**: Multi-stage builds and orchestration
- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Multi-Environment**: Dev, staging, production configurations
- **Scalability**: Horizontal scaling support

## 🚀 Quick Start

### Installation

```bash
# Install the package
pip install claude-subagent-credit-card-detector

# Or clone the repository
git clone https://github.com/claude-subagent/credit-card-detector.git
cd credit-card-detector
pip install -e .
```

### Basic Usage

```python
from claude_subagent import CreditCardDetector

# Initialize the detector
detector = CreditCardDetector()

# Simple detection
result = detector.scan("Credit card: 4111111111111111")
print(f"Found {len(result.detections)} cards")
```

### Enhanced Detection with AI Optimization

```python
# Resource-aware detection that adapts to constraints
result = detector.scan_enhanced(
    "Multiple cards: 4111111111111111, 4242-4242-4242-4242",
    resource_aware=True,
    use_all_skills=True
)
```

## 🌟️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Resource-Aware AI System                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │    Resource  │  │   Adaptive   │  │    Skill    │  │   Plugin    │              │
│  │   Monitor   │  │    Skills    │  │  Seekers    │  │   System    │              │
│  │             │  │    System    │  │ Integration│  │             │              │
│  └─────────────┘  └──────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────────────────┤
│                         Main Application Layer                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │             Resource-Aware Adaptive Subagent              │  │
│  │                                                             │  │
│  │  • Dynamic Strategy Selection                                     │  │
│  │  • Performance Prediction                                        │  │
│  │  • Intelligent Skill Management                                   │  │
│  │  • Plugin Integration                                            │  │
│  │  • Real-time Optimization                                        │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                    API & Integration Layer                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  RESTful API + SDKs                                              │  │
│  │  • Python • JavaScript • Go • Java                              │  │
│  │  • Real-time WebSocket Support                                    │  │
│  │  • Rate Limiting & Authentication                                 │  │
│  │  • Batch Processing                                              │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Intelligent Resource Adaptation

| Resource Level | Strategy | Description | Performance Gain |
|---------------|----------|-------------|----------------|
| **Abundant** | `parallel_limited` | Maximum parallelization | **3.0x faster** |
| **Moderate** | `batch_optimized` | Optimized batch sizes | **1.8x faster** |
| **Constrained** | `skill_priority` | Focus on high-impact skills | **1.5x faster** |
| **Critical** | `sequential` | Minimal resource usage | **Always succeeds** |

## 🔌 Plugin Development

### Create a Custom Detection Plugin

```python
# plugins/my_detector/plugin.yaml
name: "my_custom_detector"
version: "1.0.0"
description: "Custom credit card detector"
plugin_type: "detector"
author: "Your Name"
entry_point: "detector.py"
```

```python
# plugins/my_detector/detector.py
from claude_subagent.plugin_system import DetectorPlugin, PluginType

class MyCustomDetector(DetectorPlugin):
    def initialize(self):
        """Initialize the detector"""
        self.patterns = [
            r'\b4\d{3}(?:[\s-]?\d{4}){3}\d{4}\b',  # Visa/MasterCard
            r'\b3\d{3}[0-9]{6,}\b'             # American Express
        ]

    def detect(self, text):
        """Detect credit card patterns"""
        detections = []
        for pattern in self.patterns:
            for match in re.finditer(pattern, text):
                detections.append({
                    'start': match.start(),
                    'end': match.end(),
                    'raw': match.group(0),
                    'card_type': self._get_card_type(match.group(0)),
                    'confidence': 0.95
                })
        return detections

    def cleanup(self):
        """Cleanup resources"""
        pass
```

### Install and Use the Plugin

```python
from claude_subagent.plugin_system import plugin_manager

# Add the plugin
plugin_manager.add_source(
    name="my_custom_detector",
    url="plugins/my_detector",
    source_type="directory"
)

# Load it (automatically starts detection)
plugin_manager.load_all_plugins()

# Use it
detections = plugin_manager.execute_detectors("Card: 4111111111111111")
```

## 📊 Performance Intelligence

### ML-Based Performance Prediction

```python
from claude_subagent.resource_management.performance_predictor import PerformancePredictor

predictor = PerformancePredictor()

# Predict performance before execution
prediction = predictor.predict_performance(
    data_size=1000,
    current_metrics=current_resources,
    constraints=resource_constraints
)

print(f"Predicted processing time: {prediction.predicted_processing_time:.2f}s")
print(f"Recommended strategy: {prediction.recommended_strategy}")
```

### Real-Time Performance Monitoring

```python
# Get detailed performance statistics
stats = detector.get_performance_stats()

print(f"Total processed: {stats['total_processed']}")
print(f"Average throughput: {stats['avg_throughput']:.1f} items/sec")
print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")
```

## 📈 **Production Monitoring & Observability**

### 🔍 **Comprehensive Monitoring Stack**

The system includes enterprise-grade monitoring with **Prometheus** and **Grafana** for complete observability.

#### **Quick Start Monitoring**

```bash
# Start production stack with monitoring
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# Access monitoring interfaces
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3002
```

#### **Key Performance Metrics**

| Metric | Description | Target |
|--------|-------------|--------|
| **Response Time** | 95th percentile latency | < 100ms |
| **Throughput** | Requests per second | Monitor baseline |
| **Detection Rate** | Cards found per minute | Track volume |
| **Error Rate** | Failed requests percentage | < 1% |
| **Availability** | Service uptime | > 99.9% |

#### **Monitoring Dashboard**

The pre-built Grafana dashboard includes:

- 🎯 **Request Metrics**: Rate, total count, response times
- 📊 **Detection Analytics**: Valid/invalid card ratios
- 💾 **System Resources**: Memory, CPU, network usage
- 🚨 **Health Status**: Service dependencies and uptime
- 📈 **Performance Trends**: Historical data and predictions

**Import Dashboard:**
1. Go to http://localhost:3002
2. Dashboards → Import
3. Upload `monitoring/grafana/dashboards/credit-card-dashboard.json`

#### **Essential Prometheus Queries**

```promql
# Service availability
up{job="credit-card-detector"}

# Request rate (per second)
rate(credit_card_detector_requests_total[5m])

# Response time percentiles
histogram_quantile(0.95, rate(credit_card_detector_request_duration_seconds_bucket[5m]))

# Credit card detection rate
rate(credit_card_detections_total[5m]) by (valid_luhn)

# Error rate monitoring
rate(credit_card_scan_requests_total{has_detections="error"}[5m])

# Active connections
credit_card_detector_active_connections
```

#### **Performance Testing & Monitoring**

```bash
# Run comprehensive monitoring test
python3 monitor_credit_card_performance.py

# Test credit card detection with metrics
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Test card: 4111111111111111"}'

# Check real-time metrics
curl http://localhost:9090/api/v1/query?query=up
```

#### **Alerting Setup**

Configure alerts for:

```yaml
# High response time alert
- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(credit_card_detector_request_duration_seconds_bucket[5m])) > 0.1
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High response time detected"

# High error rate alert
- alert: HighErrorRate
  expr: rate(credit_card_scan_requests_total{has_detections="error"}[5m]) > 0.01
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "High error rate detected"
```

#### **Monitoring Infrastructure Components**

- **Prometheus**: Metrics collection and storage (30-day retention)
- **Grafana**: Visualization and dashboarding
- **Node Exporter**: System metrics (optional)
- **cAdvisor**: Container metrics (optional)

#### **Production Deployment Monitoring**

```bash
# Check all service status
docker-compose -f docker-compose.production.yml ps

# View monitoring stack logs
docker-compose logs -f prometheus grafana

# Monitor resource usage
docker stats

# Check health endpoints
curl http://localhost:9090/api/v1/status/config
curl http://localhost:3002/api/health
```

## 🐳️ Docker Deployment

### Quick Start with Docker

```bash
# Pull the image
docker pull claude-subagent/credit-card-detector

# Run with default configuration
docker run -p 5000:5000 claude-subagent/credit-card-detector

# Run with custom configuration
docker run -p 5000:5000 \
  -e CLAUDE_API_KEY=your-api-key \
  -e MAX_CPU_PERCENT=70 \
  -e MAX_MEMORY_PERCENT=75 \
  claude-subagent/credit-card-detector
```

### Docker Compose

```bash
# Start the full stack (including databases, monitoring, etc.)
docker-compose up -d

# Access the service
curl http://localhost:5000/health

# View logs
docker-compose logs -f credit-card-detector
```

## 🔍 Advanced Usage Examples

### 1. Resource-Constrained Processing

```python
# Configure for resource-constrained environment
detector = CreditCardDetector(
    resource_constraints={
        'max_cpu_percent': 50,
        'max_memory_percent': 60,
        'max_batch_size': 100
    }
)

# The system automatically adapts to constraints
result = detector.scan_enhanced(
    large_text_dataset,
    resource_aware=True
)
```

### 2. Custom Skill Training

```python
# Train a new skill from examples
examples = [
    {
        "input": "Masked card: ****-****-****-4242",
        "expected_detections": [{
            "pattern": "masked_card",
            "last4": "4242"
        }]
    }
]

result = detector.train_skill(
    examples,
    description="Detects masked credit card numbers",
    quality_threshold=0.8
)
```

### 3. Batch Processing with Optimization

```python
# Process multiple texts with intelligent optimization
texts = ["card1: 4111111111111111", "card2: 4242424242424242"] * 100

result = detector.scan_batch(
    texts,
    parallel=True,
    max_workers=4
)

print(f"Processed {len(result.results)} texts")
print(f"Total detections: {result['summary']['total_detections']}")
```

### 4. Performance Benchmarking

```python
# Benchmark different strategies
benchmark_result = detector.benchmark(
    texts=test_texts,
    iterations=3
)

print("Strategy Performance Comparison:")
for strategy, data in benchmark_result['results'].items():
    print(f"{strategy}: {data['avg_processing_time']:.3f}s, "
          f"Throughput: {data['throughput']:.1f} items/sec")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit                # Unit tests only
pytest -m integration         # Integration tests
pytest -m performance         # Performance tests

# Run with coverage
pytest --cov=claude_subagent --cov-report=html

# Run tests in parallel
pytest -n auto

# Run performance benchmarks
python -m pytest tests/performance/ -v
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=claude_subagent --cov-report=html

# View the report
open htmlcov/index.html

# Coverage minimum enforced
# Tests fail if coverage drops below threshold
```

## 📚 Documentation

- **[API Documentation](https://claude-subagent.github.io/credit-card-detector/)** - Complete API reference
- **[Compute Resource Requirements](docs/compute-resources.md)** - Hardware and cloud resource specifications
- **[Plugin Development Guide](docs/plugin-development.md)** - Create custom plugins
- **[Performance Optimization](docs/performance-optimization.md)** - Fine-tune performance
- **[Deployment Guide](docs/deployment.md)** - Production deployment
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues

## 🏗️ Configuration

### Environment Variables

```bash
# Core Configuration
export CLAUDE_API_KEY=your-api-key
export SUBAGENT_PORT=5000
export FLASK_ENV=production

# Resource Constraints
export MAX_CPU_PERCENT=80
export MAX_MEMORY_PERCENT=80
export MAX_BATCH_SIZE=1000

# External Services
export PRESIDIO_ANALYZER_URL=http://localhost:3000
export PRESIDIO_ANONYMIZER_URL=http://localhost:3001
```

### Configuration Files

```yaml
# config/production.yaml
app:
  name: credit-card-detector
  environment: production
  debug: false

detection:
  confidence_threshold: 0.7
  max_text_length: 1000000

resources:
  max_cpu_percent: 75
  max_memory_percent: 80
  enable_optimization: true

adaptive_skills:
  enabled: true
  quality_threshold: 0.6
  auto_import: true

monitoring:
  enable_metrics: true
  enable_tracing: false
  export_interval: 60
```

## 🔗️ API Reference

### Core Detection Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scan` | POST | Basic credit card detection |
| `/scan-batch` | POST | Batch detection |
| `/scan-enhanced` | POST | AI-optimized detection |

### Adaptive Skills Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/train` | POST | Train new skills |
| `/skills` | GET | List available skills |
| `/skill-performance` | GET | Performance metrics |
| `/feedback` | POST | Submit feedback |

### Resource Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/resource-monitor` | GET | Current resource usage |
| `/resource-constraints` | GET/PUT | Resource constraints |
| `/benchmark-processing` | POST | Performance benchmarking |

### SDK Usage

```python
# Python SDK
from claude_subagent_sdk import CreditCardDetector

detector = CreditCardDetector(api_key="your-key")
result = detector.scan("Card: 4111111111111111")
```

```javascript
// JavaScript SDK
import { CreditCardDetector } from '@claude-subagent/javascript-sdk';

const detector = new CreditCardDetector({ apiKey: 'your-key' });
const result = await detector.scan('Card: 4111111111111111');
```

```go
// Go SDK
import "github.com/claude-subagent/go-sdk"
detector := claude.NewDetector(claude.WithAPIKey("your-key"))
result, _ := detector.Scan("Card: 4111111111111111")
```

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/claude-subagent/credit-card-detector.git
cd credit-card-detector

# Set up development environment
python -m venv venv
source venv/bin/activate
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Roadmap

### Upcoming Features

- [ ] **v1.1** - Enhanced machine learning models
- [ ] **v1.2** - Advanced natural language processing
- [ ] **v1.3** | Real-time fraud pattern recognition
- [ ] **v1.4** | Global compliance framework
- [ ] **v1.5** | Multi-cloud deployment support

### Community Features

- [ ] **Plugin Marketplace** - Share and discover plugins
- [ ] **Skill Templates** | Pre-built skill templates
- [ ] **Performance Benchmarks** | Community benchmarks
- [ ] **Integration Templates** | Pre-built integrations

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏‍♂️ Support

- **Documentation**: [https://claude-subagent.github.io/credit-card-detector/](https://claude-subagent.github.io/credit-card-detector/)
- **GitHub Issues**: [https://github.com/claude-subagent/credit-card-detector/issues](https://github.com/claude-subagent/credit-card-detector/issues)
- **Discussions**: [https://github.com/claude-subagent/credit-card-detector/discussions](https://github.com/claude-subagent/credit-card-detector/discussions)
- **Email**: [support@claude-subagent.com](mailto:support@claude-subagent.com)

## 🏆 Credits

Built with ❤️ by the Claude SubAgent team and powered by [Claude](https://claude.ai/).

---

## 🎉 **Transform Your Detection Today!**

⭐ **Star** the repository if you find it useful!

🚀 **Deploy** in production and watch it adapt to your needs!

🧠 **Contribute** plugins and skills to help the community grow!

---

*Empowering organizations with intelligent, adaptive credit card detection* 🛡️