# 🔗 Integration Guide: Credit Card Detector with Claude Skills & n8n AI Agents

This comprehensive guide shows you how to integrate the Credit Card Detector with Claude skills and n8n AI agent workflows.

## 📋 Table of Contents

- [API Overview](#-api-overview)
- [Claude Skills Integration](#-claude-skills-integration)
- [n8n AI Agent Integration](#-n8n-ai-agent-integration)
- [Advanced Integration Patterns](#-advanced-integration-patterns)
- [Security Best Practices](#-security-best-practices)
- [Troubleshooting](#-troubleshooting)

## 🌐 API Overview

The Credit Card Detector provides a RESTful API for credit card detection and analysis.

### **Base URL**: `http://localhost:5000`

### **Available Endpoints**

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/health` | Health check | `curl http://localhost:5000/health` |
| POST | `/scan` | Detect credit cards in text | `curl -X POST http://localhost:5000/scan -d '{"text":"test"}'` |

### **API Response Format**

```json
{
  "detections": [
    {
      "number": "4111111111111111",
      "valid": true,
      "start": 16,
      "end": 32,
      "raw": "4111111111111111"
    }
  ],
  "redacted": "My card is [REDACTED]",
  "scan_duration_seconds": 0.00015
}
```

## 🤖 Claude Skills Integration

### **Option 1: Direct API Call**

Create a Claude skill that directly calls the Credit Card Detector API:

```python
import requests
import json

def credit_card_detector_skill(text: str) -> dict:
    """Claude skill for credit card detection"""
    try:
        response = requests.post(
            "http://localhost:5000/scan",
            json={"text": text},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "detections": [], "redacted": text}
```

### **Option 2: Use the Provided Integration Class**

```python
from integrations.claude_skills_example import CreditCardDetectorSkill

# Initialize the skill
detector = CreditCardDetectorSkill()

# Basic detection
result = detector.detect_credit_cards("My Visa is 4111111111111111")

# Comprehensive security analysis
analysis = detector.analyze_text_security("Customer data with cards...")
```

### **Claude Skill Usage Examples**

#### **Basic Text Scanning**
```python
# In your Claude skill implementation
def scan_for_sensitive_data(text: str) -> dict:
    """Scan text for credit cards and return security analysis"""
    detector = CreditCardDetectorSkill()
    return detector.analyze_text_security(text)
```

#### **Batch Processing**
```python
def process_document_batch(texts: list) -> list:
    """Process multiple texts for credit card detection"""
    detector = CreditCardDetectorSkill()
    results = []

    for text in texts:
        result = detector.analyze_text_security(text)
        results.append({
            "text": text,
            "analysis": result
        })

    return results
```

#### **Risk Assessment**
```python
def assess_data_risk(text: str) -> dict:
    """Assess risk level of text containing financial data"""
    detector = CreditCardDetectorSkill()
    analysis = detector.analyze_text_security(text)

    return {
        "risk_level": analysis["security_analysis"]["risk_level"],
        "security_score": analysis["security_analysis"]["security_score"],
        "recommendations": analysis["security_analysis"]["recommendations"],
        "cards_detected": len(analysis["detections"])
    }
```

## 🔄 n8n AI Agent Integration

### **Option 1: Webhook Integration**

Start the n8n integration service:

```python
# File: n8n_service.py
from integrations.n8n_integration import N8NIntegration

# Create and run the service
service = N8NIntegration()
service.run(port=8080)  # Runs on http://localhost:8080
```

### **n8n Workflow Examples**

#### **Simple Credit Card Scan Workflow**

1. **Manual Trigger** → **Text Input** → **HTTP Request** → **IF Node** → **Results**

**HTTP Request Node Configuration:**
- Method: POST
- URL: `http://localhost:8080/webhook/scan`
- Body: JSON
```json
{
  "text": "{{$json.text}}",
  "workflow_id": "{{$workflow.id}}",
  "node_id": "{{$node.id}}"
}
```

#### **Batch Processing Workflow**

1. **CSV Reader** → **HTTP Request** → **Split in Batches** → **Process Results**

**HTTP Request Node Configuration:**
- Method: POST
- URL: `http://localhost:8080/webhook/batch-scan`
- Body: JSON
```json
{
  "texts": "={{$json}}"
}
```

### **n8n Tool Integration**

For n8n's tool interface:

```python
# Tool endpoint configuration
{
  "tool": "scan_credit_cards",
  "parameters": {
    "text": "Text to scan for credit cards"
  }
}
```

**HTTP Request for Tools:**
- Method: POST
- URL: `http://localhost:8080/tools/scan`
- Body: JSON

## 🚀 Advanced Integration Patterns

### **1. Real-time Processing Pipeline**

```python
import asyncio
from integrations.claude_skills_example import CreditCardDetectorSkill

class RealtimeProcessor:
    def __init__(self):
        self.detector = CreditCardDetectorSkill()
        self.processed_count = 0

    async def process_stream(self, text_stream):
        """Process text stream in real-time"""
        async for text in text_stream:
            result = self.detector.analyze_text_security(text)
            self.processed_count += 1

            # Trigger alerts for high-risk content
            if result["security_analysis"]["risk_level"] == "HIGH":
                await self.trigger_security_alert(result)

            yield result

    async def trigger_security_alert(self, result):
        """Trigger security alerts for high-risk detections"""
        # Integration with alerting systems
        pass
```

### **2. Multi-Service Integration**

```python
class ComplianceChecker:
    """Multi-service compliance checker"""

    def __init__(self):
        self.card_detector = CreditCardDetectorSkill()
        # Add other services

    def check_compliance(self, text: str) -> dict:
        """Comprehensive compliance check"""
        results = {
            "credit_cards": self.card_detector.analyze_text_security(text),
            # Add other compliance checks
        }

        return {
            "compliant": not any(r["detections"] for r in results.values()),
            "checks": results,
            "overall_risk": self.calculate_overall_risk(results)
        }
```

### **3. Event-Driven Architecture**

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/event/text-submitted', methods=['POST'])
def handle_text_event():
    """Handle text submission events"""
    data = request.get_json()
    text = data.get('text')

    # Process with credit card detector
    detector = CreditCardDetectorSkill()
    result = detector.analyze_text_security(text)

    # Publish results to event bus
    publish_event('text-processed', {
        'original_text': text,
        'analysis_result': result,
        'timestamp': data.get('timestamp')
    })

    return jsonify(result)

def publish_event(event_type: str, data: dict):
    """Publish event to message queue"""
    # Integration with RabbitMQ, Kafka, etc.
    pass
```

## 🔒 Security Best Practices

### **1. API Security**

```python
import secrets
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != secrets.API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/secure-scan', methods=['POST'])
@require_api_key
def secure_scan():
    """Secure scanning endpoint with API key authentication"""
    pass
```

### **2. Data Encryption**

```python
import cryptography.fernet

class SecureDetector:
    def __init__(self, encryption_key):
        self.cipher_suite = cryptography.fernet.Fernet(encryption_key)
        self.detector = CreditCardDetectorSkill()

    def encrypt_and_scan(self, text: str) -> dict:
        """Encrypt sensitive data before processing"""
        # Implementation for encrypted processing
        pass
```

### **3. Rate Limiting**

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

@app.route('/scan', methods=['POST'])
@limiter.limit("100 per minute")
def rate_limited_scan():
    """Rate-limited scanning endpoint"""
    pass
```

## 🔧 Troubleshooting

### **Common Issues**

#### **1. Connection Refused**
```bash
# Check if the detector is running
curl http://localhost:5000/health

# Start the detector
./start.sh start basic
```

#### **2. Integration Service Not Working**
```python
# Check the n8n integration service
curl http://localhost:8080/health

# Check logs for errors
python3 integrations/n8n_integration.py
```

#### **3. Claude Skill Timeout**
```python
# Increase timeout in requests
response = requests.post(
    "http://localhost:5000/scan",
    json={"text": text},
    timeout=30  # Increase from default 10
)
```

### **Debugging Tools**

#### **Health Check Script**
```python
def check_all_services():
    """Check all integration services"""
    services = {
        "Credit Card Detector": "http://localhost:5000/health",
        "n8n Integration": "http://localhost:8080/health"
    }

    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            status = "✅ OK" if response.status_code == 200 else "❌ ERROR"
        except:
            status = "❌ UNREACHABLE"

        print(f"{name}: {status}")
```

#### **Performance Monitoring**
```python
import time

def measure_performance(text: str):
    """Measure detection performance"""
    start_time = time.time()
    detector = CreditCardDetectorSkill()
    result = detector.detect_credit_cards(text)
    end_time = time.time()

    print(f"Scan time: {end_time - start_time:.3f}s")
    print(f"Cards found: {len(result['detections'])}")
    return result
```

## 📚 Additional Resources

- **Credit Card Detector Documentation**: [Link to main docs]
- **Claude Skills Framework**: [Link to Claude skills docs]
- **n8n Documentation**: [https://docs.n8n.io/](https://docs.n8n.io/)
- **API Reference**: Check `/health` endpoint for current API version

## 🤝 Support

For integration support:
1. Check the troubleshooting section above
2. Review the main project documentation
3. Create an issue in the project repository

---

**Ready to integrate!** 🚀

You now have everything you need to integrate the Credit Card Detector with Claude skills and n8n AI agents. Start with the basic examples and gradually build up to more complex workflows as needed.