# Credit Card Detector Examples

This directory contains simple, focused examples for using the Credit Card Detector.

## 📁 **Structure**

```
examples/
├── README.md                    # This file
├── basic/                       # Basic usage examples
│   ├── simple_detection.py     # Simple credit card detection
│   └── basic_redaction.py       # Basic credit card redaction
├── api/                         # API integration examples
│   ├── basic_api.py              # Simple API client
│   ├── webhook_server.py         # Production webhook server
│   └── metrics_demo.py           # Monitoring examples
└── integrations/                # External integrations
    ├── claude_skills/            # Claude AI integration
    └── n8n_workflows/            # n8n workflow automation
```

## 🚀 **Quick Start**

### **1. Basic Usage**
```bash
# Simple detection
source .venv/bin/activate
python3 examples/basic/simple_detection.py

# Basic redaction
python3 examples/basic/basic_redaction.py
```

### **2. API Integration**
```bash
# API client examples
python3 examples/api/basic_api.py

# Start webhook server
python3 examples/api/webhook_server.py
```

### **3. External Integrations**
```bash
# Claude AI skills integration
python3 examples/integrations/claude_skills/claude_skills_example.py

# n8n workflow integration
python3 examples/integrations/n8n_workflows/n8n_integration.py
```

## 📖 **Example Categories**

### **Basic Examples** (`basic/`)
- Simple credit card detection
- Text redaction (redact vs mask)
- Getting started with the core library

### **API Examples** (`api/`)
- REST API client usage
- Webhook server implementation
- Performance monitoring
- Production deployment patterns

### **Integration Examples** (`integrations/`)
- Claude AI skills integration
- n8n workflow automation
- Third-party service connections

## 🔧 **Prerequisites**

1. **Start the Credit Card Detector**:
   ```bash
   ./start.sh start basic
   ```

2. **Install dependencies**:
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run examples**:
   ```bash
   python3 examples/your_chosen_example.py
   ```

## 📚 **Learn More**

- **Main README**: See the root `README.md` for complete project information
- **API Documentation**: See `/docs/api.md` for detailed API reference
- **Configuration**: See `config/default.yaml` for configuration options

## 🎯 **Get Help**

- Check the error messages in the console
- Ensure the detector is running on `localhost:5000`
- Verify Python dependencies are installed
- Review the example source code for detailed usage patterns