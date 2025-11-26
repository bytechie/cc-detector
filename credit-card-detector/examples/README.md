# Credit Card Detector - Examples

This directory contains comprehensive examples demonstrating the capabilities of the Credit Card Detector system.

## 📁 **Directory Structure**

```
examples/
├── README.md                    # This file - Overview of all examples
├── README_integration_examples.md # Detailed integration examples guide
├── integration_demo.py          # Complete demonstration of all integrations
├── basic_usage/                 # Basic usage examples
│   ├── simple_detection.py      # Simple credit card detection
│   └── basic_redaction.py       # Basic credit card redaction
├── advanced/                    # Advanced feature examples
│   └ presidio_integration.py    # Presidio integration examples
├── performance/                 # Performance and benchmarking
│   ├── load_testing.py          # Load testing examples
│   └── performance_comparison.py # Performance comparison tools
├── monitoring/                  # Monitoring and metrics
│   └ metrics_demo.py            # Prometheus metrics demo
├── api_integrations/            # Direct API integration examples
│   ├── README.md                # API integration guide
│   ├── basic_api.py             # Simple API client examples
│   └── webhook_server.py        # Production webhook server
├── claude_skills/               # Claude AI skills integration
│   ├── README.md                # Claude skills guide and examples
│   └── claude_skills_example.py # Complete Claude skills implementation
└── n8n_workflows/              # n8n workflow automation
    ├── README.md                # n8n setup and workflow examples
    └── n8n_integration.py       # n8n webhook server and tools
```

## 🚀 **Getting Started**

### **Basic Detection Example**

```python
from skills.core.detect_credit_cards import detect

text = "My credit card is 4111-1111-1111-1111"
detections = detect(text)
print(f"Found {len(detections)} potential credit card numbers")
```

### **Basic Redaction Example**

```python
from skills.core.detect_credit_cards import detect
from skills.core.redact_credit_cards import redact

text = "Card: 4111 1111 1111 1111 expires 12/25"
detections = detect(text)
redacted = redact(text, detections)
print(f"Original: {text}")
print(f"Redacted: {redacted}")
```

## 📊 **Example Categories**

### **1. Basic Usage Examples**
- **Purpose**: Simple, getting-started examples
- **Features**: Core detection and redaction functionality
- **Ideal for**: New users learning the system

### **2. Advanced Examples**
- **Purpose**: Sophisticated usage patterns
- **Features**: Presidio integration, adaptive skills, custom patterns
- **Ideal for**: Advanced users extending functionality

### **3. Performance Examples**
- **Purpose**: Performance testing and optimization
- **Features**: Load testing, benchmarking, comparison tools
- **Ideal for**: Performance optimization and capacity planning

### **4. Monitoring Examples**
- **Purpose**: System monitoring and observability
- **Features**: Prometheus metrics, health checks, dashboard setup
- **Ideal for**: Production deployments and operations

## 🔧 **Running Examples**

### **Prerequisites**
- Python 3.8+
- Required dependencies installed (`pip install -r requirements.txt`)
- Optional: Docker for containerized examples

### **Basic Examples**
```bash
# Run basic detection example
cd examples/basic_usage
python simple_detection.py

# Run command line demo
python command_line_demo.py --text "Card: 4111 1111 1111 1111"
```

### **Advanced Examples**
```bash
# Run Presidio integration
cd examples/advanced
python presidio_integration.py

# Run adaptive skills demo
python adaptive_skills.py
```

### **Performance Examples**
```bash
# Run load testing
cd examples/performance
python load_testing.py --requests 1000 --concurrency 10

# Run performance comparison
python performance_comparison.py
```

### **Monitoring Examples**
```bash
# Start metrics demo
cd examples/monitoring
python metrics_demo.py

# Visit http://localhost:5000/metrics for Prometheus metrics
# Visit http://localhost:5000/health for health status
```

## 🎯 **Use Case Examples**

### **1. Log File Processing**
```python
# Process log files for credit card numbers
import re
from skills.core import detect_credit_cards, redact_credit_cards

def process_log_file(log_path):
    with open(log_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            detections = detect_credit_cards.detect(line)
            if detections:
                redacted = redact_credit_cards.redact(line, detections)
                print(f"Line {line_num}: {redacted}")
```

### **2. API Integration**
```python
# Integrate with existing API
from flask import Flask, request
from skills.core import detect_credit_cards

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan_text():
    data = request.get_json()
    text = data.get('text', '')
    detections = detect_credit_cards.detect(text)
    return {'detections': detections}
```

### **3. Batch Processing**
```python
# Process multiple texts efficiently
from skills.core import detect_credit_cards
import concurrent.futures

def batch_process(texts, max_workers=4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(detect_credit_cards.detect, texts))
    return results
```

## 📚 **Additional Resources**

- [Main Documentation](../docs/)
- [API Reference](../docs/api/)
- [Configuration Guide](../docs/configuration/)
- [Development Setup](../docs/development/)

## 🤝 **Contributing Examples**

To contribute new examples:

1. **Choose the right category** (basic, advanced, performance, monitoring)
2. **Follow naming conventions** (snake_case, descriptive names)
3. **Include comprehensive documentation** (docstrings, comments)
4. **Add error handling** where appropriate
5. **Test your examples** before submitting

### **Example Template**
```python
#!/usr/bin/env python3
"""
[Example Description]

This example demonstrates [specific functionality].

Usage:
    python example_name.py [arguments]

Features:
- [Feature 1]
- [Feature 2]
- [Feature 3]
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from skills.core import detect_credit_cards

def main():
    """Main example function."""
    # Implementation here
    pass

if __name__ == "__main__":
    main()
```

## 📞 **Getting Help**

- **Issues**: Report bugs or request features via GitHub issues
- **Questions**: Use GitHub discussions for questions
- **Documentation**: Check the main documentation for detailed guides

---

**Happy Coding!** 🎉

These examples are designed to help you understand and effectively use the Credit Card Detector system. Start with basic examples and gradually explore more advanced features as you become familiar with the system.