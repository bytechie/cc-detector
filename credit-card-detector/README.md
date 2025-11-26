# 🛡️ Credit Card Detector

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

> **Intelligent credit card detection and redaction with enterprise-grade monitoring and AI-powered analysis**

## 🚀 Quick Start

### 1. Start the Service
```bash
# Basic mode (core functionality)
./start.sh start basic

# Enterprise mode (full monitoring + AI features)
./start.sh start enterprise
```

### 2. Try the API
```bash
# Health check
curl http://localhost:5000/health

# Detect credit cards
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "My card is 4111111111111111"}'
```

### 3. Run Examples
```bash
# Complete integration demo
source .venv/bin/activate
python3 examples/integration_demo.py

# API integration examples
python3 examples/api_integrations/basic_api.py

# Claude AI skills integration
python3 examples/claude_skills/claude_skills_example.py
```

## 📋 What It Does

- **✅ Detect Credit Cards**: Visa, MasterCard, Amex, Discover, and more
- **🔒 Secure Redaction**: Remove sensitive data automatically
- **🤖 AI Analysis**: Security scoring and risk assessment
- **📊 Real-time Monitoring**: Performance metrics and health checks
- **🔄 Workflow Integration**: n8n, Claude Skills, and REST API support

## 🏗️ Project Structure

```
credit-card-detector/
├── README.md                    # This file
├── app.py                      # Main Flask application
├── start.sh                    # Unified startup script
├── examples/                   # Usage examples and integrations
│   ├── basic_usage/            # Simple detection examples
│   ├── api_integrations/       # REST API integrations
│   ├── claude_skills/          # Claude AI integration
│   └── n8n_workflows/          # n8n automation workflows
├── docs/                       # Documentation
│   ├── quickstart.md           # Detailed setup guide
│   └── DOCUMENTATION_INDEX.md  # Complete documentation index
├── config/                     # Configuration files
├── skills/                     # Detection and processing skills
├── tests/                      # Test suite
└── monitoring/                 # Prometheus + Grafana setup
```

## 🔧 Available Commands

### Startup Commands
```bash
./start.sh start basic          # Core functionality only
./start.sh start metrics        # Basic + Prometheus metrics
./start.sh start production     # Full features + monitoring
./start.sh start enterprise     # Full stack + AI + testing
./start.sh stop                 # Stop all services
./start.sh status              # Show running services
```

### Example Usage
```bash
# Basic credit card detection
python3 -c "
import requests
r = requests.post('http://localhost:5000/scan', json={'text': 'Card: 4111111111111111'})
print(r.json()['redacted'])  # Card: [REDACTED]
"

# Advanced security analysis
source .venv/bin/activate
python3 examples/claude_skills/claude_skills_example.py
```

## 📚 Documentation

- **[Quick Start Guide](docs/quickstart.md)** - Detailed setup instructions
- **[Documentation Index](docs/DOCUMENTATION_INDEX.md)** - Complete documentation
- **[Examples Directory](examples/)** - Practical implementation guides
- **[API Reference](docs/README.md)** - Full API documentation

## 🐳 Docker Support

```bash
# Build and run
docker-compose up --build

# Production mode
docker-compose -f docker-compose.production.yml up
```

## 🧪 Testing

```bash
# Run all tests
./run-mode-tests.sh

# Health check
curl http://localhost:5000/health
```

## 🔍 Monitoring

Enterprise mode includes:
- **Prometheus Metrics**: Performance and resource monitoring
- **Grafana Dashboards**: Visual monitoring dashboards
- **Health Checks**: Automated system health validation
- **Error Tracking**: Intelligent error analysis

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📄 License

MIT License - see [LICENSE.md](LICENSE.md) for details.

---

**🚀 Ready to get started?** Run `./start.sh start basic` and check the [examples](examples/) directory for integration patterns!