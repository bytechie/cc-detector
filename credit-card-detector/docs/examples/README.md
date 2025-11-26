# 🔗 Credit Card Detector Integrations

This directory contains comprehensive integration examples for using the Credit Card Detector with Claude skills and n8n AI agents.

## 📁 Files Overview

### **Core Integration Files**

| File | Purpose | Key Features |
|------|---------|--------------|
| `claude_skills_example.py` | Claude Skills integration | Security analysis, risk assessment, comprehensive detection |
| `n8n_integration.py` | n8n workflow integration | Webhook endpoints, batch processing, tool interface |
| `demo.py` | Complete integration demonstration | Shows all integration patterns in action |
| `README.md` | This file | Overview and usage instructions |

## 🚀 Quick Start

### **1. Start the Credit Card Detector**
```bash
./start.sh start basic
```

### **2. Run the Complete Demo**
```bash
source .venv/bin/activate
python3 docs/examples/integration_demo.py
```

### **3. Choose Your Integration Path**

#### **🤖 For Claude Skills Integration**
```bash
source .venv/bin/activate
python3 docs/examples/claude_skills/claude_skills_example.py
```

#### **🔄 For n8n Workflow Integration**
```python
from docs.examples.n8n_workflows.n8n_integration import N8NIntegration
service = N8NIntegration()
service.run(port=8080)  # Available at http://localhost:8080
```

#### **🌐 For Direct API Integration**
```bash
source .venv/bin/activate
python3 docs/examples/api_integrations/basic_api.py
```

## 🤖 Claude Skills Integration

### **Basic Usage**
```python
from docs.examples.claude_skills.claude_skills_example import CreditCardDetectorSkill

# Initialize the skill
detector = CreditCardDetectorSkill()

# Simple detection
result = detector.detect_credit_cards("My card is 4111111111111111")
print(f"Cards found: {len(result['detections'])}")
print(f"Redacted: {result['redacted']}")

# Comprehensive security analysis
analysis = detector.analyze_text_security("Customer data with cards...")
print(f"Risk level: {analysis['security_analysis']['risk_level']}")
print(f"Security score: {analysis['security_analysis']['security_score']}")
```

### **Use Cases**
- ✅ **Document Processing**: Scan uploaded documents for credit cards
- ✅ **Customer Support**: Redact sensitive information from support tickets
- ✅ **Data Validation**: Ensure databases don't contain unencrypted card numbers
- ✅ **Compliance Checking**: Verify text data meets PCI DSS requirements

## 🔄 n8n AI Agent Integration

### **Webhook Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/scan` | POST | Scan single text for credit cards |
| `/webhook/batch-scan` | POST | Scan multiple texts in one request |
| `/tools/scan` | POST | n8n tool interface |
| `/health` | GET | Service health check |

### **Example n8n Workflow**

1. **Trigger**: Manual trigger, webhook, or schedule
2. **Process**: Use HTTP Request node to call `/webhook/scan`
3. **Decision**: Route based on detection results
4. **Action**: Redact data, alert security team, or process safely

#### **HTTP Request Node Configuration**
```json
{
  "method": "POST",
  "url": "http://localhost:8080/webhook/scan",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "text": "{{$json.text}}",
    "workflow_id": "{{$workflow.id}}",
    "node_id": "{{$node.id}}"
  }
}
```

## 🌐 API Integration

### **Direct API Calls**
```python
import requests

# Health check
health = requests.get("http://localhost:5000/health")

# Scan text
response = requests.post(
    "http://localhost:5000/scan",
    json={"text": "Card number: 4111111111111111"},
    headers={"Content-Type": "application/json"}
)

result = response.json()
print(f"Detected: {len(result['detections'])} cards")
```

## 📊 Integration Patterns

### **1. Real-time Processing**
```python
# Process streaming data for credit cards
for text_chunk in data_stream:
    result = detector.detect_credit_cards(text_chunk)
    if result['detections']:
        trigger_security_alert(result)
```

### **2. Batch Document Processing**
```python
# Process multiple documents efficiently
documents = load_documents_from_database()
results = []

for doc in documents:
    analysis = detector.analyze_text_security(doc.content)
    if analysis['security_analysis']['risk_level'] != 'LOW':
        results.append(append_security_flags(doc, analysis))
```

### **3. Compliance Automation**
```python
def check_document_compliance(text):
    """Check if document meets compliance requirements"""
    analysis = detector.analyze_text_security(text)

    return {
        "compliant": len(analysis['detections']) == 0,
        "risk_level": analysis['security_analysis']['risk_level'],
        "required_actions": analysis['security_analysis']['recommendations']
    }
```

## 🔧 Configuration Options

### **Claude Skills Configuration**
```python
# Custom detector URL
detector = CreditCardDetectorSkill(api_url="http://your-server:5000")

# Custom timeout
detector.session.timeout = 30
```

### **n8n Integration Configuration**
```python
# Custom ports and hosts
service = N8NIntegration(
    detector_url="http://your-detector:5000"
)

# Run on different port
service.run(port=9090, host="0.0.0.0")
```

## 📁 Directory Structure

```
docs/examples/
├── README.md                    # This file - Overview and quick start
├── integration_demo.py          # Complete demonstration of all integrations
├── claude_skills/               # Claude AI skills integration
│   ├── README.md                # Claude skills guide and examples
│   └── claude_skills_example.py # Complete Claude skills implementation
├── n8n_workflows/              # n8n workflow automation
│   ├── README.md                # n8n setup and workflow examples
│   └── n8n_integration.py       # n8n webhook server and tools
└── api_integrations/           # Direct API integration examples
    ├── README.md                # API integration guide
    ├── basic_api.py             # Simple API client examples
    └── webhook_server.py        # Production webhook server
```

## 🎯 Integration Options

### **Claude Skills Integration** `claude_skills/`
- **Best for**: AI-powered document processing, intelligent analysis
- **Features**: Security scoring, risk assessment, automated recommendations
- **Use Cases**: Compliance checking, content moderation, data validation

### **n8n Workflow Integration** `n8n_workflows/`
- **Best for**: Automated business processes, workflow orchestration
- **Features**: Webhook endpoints, batch processing, visual workflow builder
- **Use Cases**: Document processing pipelines, compliance automation, customer support

### **API Integration** `api_integrations/`
- **Best for**: Custom applications, microservices, direct integration
- **Features**: REST API, webhook server, multiple language examples
- **Use Cases**: Web applications, mobile apps, backend services

## 🛡️ Security Considerations

### **API Security**
- Use HTTPS in production
- Implement API key authentication
- Rate limit API calls
- Log all access attempts

### **Data Protection**
- Encrypt sensitive data at rest
- Use secure connections for API calls
- Implement proper access controls
- Regular security audits

## 📈 Performance Tips

### **Optimization Strategies**
- Batch multiple scans together
- Cache results for repeated text
- Use connection pooling for API calls
- Monitor response times and error rates

### **Scaling**
- Deploy detector services behind load balancer
- Use message queues for high-volume processing
- Implement circuit breakers for API reliability
- Monitor resource usage and auto-scale

## 🔍 Monitoring & Logging

### **Health Monitoring**
```python
# Check all services
def check_integration_health():
    services = {
        "Detector": "http://localhost:5000/health",
        "n8n Integration": "http://localhost:8080/health"
    }

    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            print(f"{name}: {'✅' if response.status_code == 200 else '❌'}")
        except:
            print(f"{name}: ❌ Unreachable")
```

### **Performance Metrics**
- Track scan response times
- Monitor error rates
- Log detection statistics
- Alert on performance degradation

## 🆘 Troubleshooting

### **Common Issues**

**Problem**: Connection refused error
**Solution**: Ensure Credit Card Detector is running (`./start.sh start basic`)

**Problem**: Timeouts during processing
**Solution**: Increase timeout values or implement retry logic

**Problem**: Integration service won't start
**Solution**: Check port availability and dependencies

### **Debug Mode**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with known examples
test_cases = [
    "Valid card: 4111111111111111",
    "Invalid card: 1234567890123456",
    "No cards here"
]
```

## 📚 Additional Resources

- **Main Documentation**: `docs/INTEGRATION_GUIDE.md`
- **API Reference**: Check `/health` endpoint for current version
- **Examples**: See `demo.py` for comprehensive usage examples
- **Testing**: Use `run-mode-tests.sh` for validation

## 🤝 Contributing

To add new integration examples:
1. Create a new file in this directory
2. Follow the existing code style and patterns
3. Add comprehensive documentation
4. Include test cases and examples
5. Update this README file

## 📞 Support

For integration support:
1. Check the troubleshooting section above
2. Review the main project documentation
3. Run the demo to test your setup
4. Create an issue in the project repository

---

**Ready to integrate!** 🚀

Start with the basic examples and gradually build up to more complex integration patterns as needed for your specific use case.