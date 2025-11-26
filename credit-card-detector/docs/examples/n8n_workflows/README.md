# 🔄 n8n Workflow Integration Examples

This directory contains examples and tools for integrating the Credit Card Detector with n8n AI agent workflows.

## 📁 Files Overview

| File | Purpose | Key Features |
|------|---------|--------------|
| `n8n_integration.py` | Complete n8n integration service | Webhook endpoints, batch processing, tool interface |

## 🚀 Quick Start

### **1. Start the Credit Card Detector**
```bash
./start.sh start basic
```

### **2. Start the n8n Integration Service**
```python
from docs.examples.n8n_workflows.n8n_integration import N8NIntegration

# Create and run the service
service = N8NIntegration()
service.run(port=8080)  # Available at http://localhost:8080
```

### **3. Configure n8n Workflow**
Use the HTTP Request node to call the webhook endpoints.

## 🌐 Webhook Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/scan` | POST | Scan single text for credit cards |
| `/webhook/batch-scan` | POST | Scan multiple texts in one request |
| `/tools/scan` | POST | n8n tool interface |
| `/health` | GET | Health check for monitoring |

## 📋 n8n Workflow Examples

### **Example 1: Simple Credit Card Scan**

**Workflow Steps:**
1. **Manual Trigger** → **Text Input** → **HTTP Request** → **IF Node** → **Results**

**HTTP Request Node Configuration:**
- **Method**: POST
- **URL**: `http://localhost:8080/webhook/scan`
- **Headers**: `Content-Type: application/json`
- **Body**: JSON
```json
{
  "text": "{{$json.text}}",
  "workflow_id": "{{$workflow.id}}",
  "node_id": "{{$node.id}}"
}
```

**IF Node Configuration:**
```json
{
  "conditions": [
    {
      "leftValue": "={{$json.detections}}",
      "rightValue": "",
      "operator": {
        "type": "array",
        "operation": "notEmpty"
      }
    }
  ]
}
```

### **Example 2: Batch Document Processing**

**Workflow Steps:**
1. **CSV Reader** → **Split in Batches** → **HTTP Request** → **Process Results**

**HTTP Request Node for Batch Processing:**
- **Method**: POST
- **URL**: `http://localhost:8080/webhook/batch-scan`
- **Body**: JSON
```json
{
  "texts": "={{$json}}"
}
```

### **Example 3: Customer Support Automation**

**Workflow Steps:**
1. **Webhook Trigger** → **Scan Text** → **Risk Assessment** → **Route to Team**

**Risk Assessment Logic:**
```javascript
// Function node to assess risk
const detections = $json.detections || [];
const riskLevel = detections.length > 2 ? 'HIGH' :
                  detections.length > 0 ? 'MEDIUM' : 'LOW';

return [
  {
    json: {
      ...$json,
      riskLevel,
      needsReview: riskLevel !== 'LOW'
    }
  }
];
```

## 🛠️ Tool Integration

For n8n's native tool interface:

### **Tool Call Format**
```json
{
  "tool": "scan_credit_cards",
  "parameters": {
    "text": "Text to scan for credit cards"
  }
}
```

### **Tool Response Format**
```json
{
  "tool": "scan_credit_cards",
  "result": {
    "detections": [...],
    "redacted": "Text with [REDACTED] cards",
    "scan_duration_seconds": 0.00015
  },
  "success": true
}
```

## 📊 Sample n8n Workflows

### **Workflow 1: Document Security Check**

```json
{
  "name": "Document Security Check",
  "nodes": [
    {
      "id": "1",
      "name": "Document Input",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [250, 300],
      "parameters": {
        "text": "Enter document text to scan"
      }
    },
    {
      "id": "2",
      "name": "Scan for Cards",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "parameters": {
        "url": "http://localhost:8080/webhook/scan",
        "method": "POST",
        "jsonParameters": true,
        "jsonBody": {
          "text": "={{$json.text}}"
        }
      }
    },
    {
      "id": "3",
      "name": "Check Results",
      "type": "n8n-nodes-base.if",
      "position": [650, 300],
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "leftValue": "={{$json.detections}}",
              "rightValue": "",
              "operator": {
                "type": "array",
                "operation": "notEmpty"
              }
            }
          ]
        }
      }
    }
  ]
}
```

### **Workflow 2: Compliance Validation**

```json
{
  "name": "Compliance Validation Pipeline",
  "nodes": [
    {
      "id": "1",
      "name": "Document Batch",
      "type": "n8n-nodes-base.readCsvFile",
      "position": [250, 300]
    },
    {
      "id": "2",
      "name": "Batch Scan",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "parameters": {
        "url": "http://localhost:8080/webhook/batch-scan",
        "method": "POST",
        "jsonParameters": true,
        "jsonBody": {
          "texts": "={{$json}}"
        }
      }
    },
    {
      "id": "3",
      "name": "Filter Results",
      "type": "n8n-nodes-base.switch",
      "position": [650, 300],
      "parameters": {
        "values": [
          {
            "conditions": [
              {
                "leftValue": "={{$json.results}}",
                "rightValue": "",
                "operator": {
                  "type": "array",
                  "operation": "notEmpty"
                }
              }
            ],
            "output": 0
          }
        ]
      }
    }
  ]
}
```

## 🔧 Configuration Options

### **Custom Detector URL**
```python
service = N8NIntegration(detector_url="http://your-detector:5000")
```

### **Custom Port**
```python
service.run(port=9090)  # Run on port 9090
```

### **Custom Host**
```python
service.run(host="192.168.1.100")  # Bind to specific IP
```

## 📈 Monitoring and Logging

### **Health Check**
```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "detector_health": true,
  "service": "n8n_integration",
  "timestamp": "2025-01-26T10:30:00Z"
}
```

### **Service Statistics**
```bash
curl http://localhost:8080/stats
```

### **Log Monitoring**
The service logs all scan requests and results:
```
INFO - Scan #123: Found 2 credit cards
INFO - Batch scan completed: 10 texts, 3 cards found
```

## 🔒 Security Features

### **Request Validation**
- JSON schema validation for all inputs
- Request size limits to prevent abuse
- Rate limiting support (configure in reverse proxy)

### **Error Handling**
- Graceful degradation when detector is unavailable
- Comprehensive error logging
- Standardized error response format

### **Data Protection**
- No persistent storage of sensitive data
- Automatic data redaction in responses
- Secure communication with detector service

## 🚀 Advanced Usage

### **Custom Webhook Processing**
```python
from flask import Flask, request
from docs.examples.n8n_workflows.n8n_integration import N8NIntegration

# Extend the base service
app = Flask(__name__)
n8n_service = N8NIntegration()

@app.route('/custom-scan', methods=['POST'])
def custom_scan():
    """Custom scan endpoint with additional logic"""
    data = request.get_json()

    # Pre-processing
    text = preprocess_text(data.get('text', ''))

    # Call n8n integration
    result = n8n_service.scan_credit_cards(text)

    # Post-processing
    result['custom_metadata'] = {
        'processed_at': datetime.now().isoformat(),
        'custom_rules': apply_custom_rules(text)
    }

    return jsonify(result)
```

### **Integration with Message Queues**
```python
import redis
import json

# Redis integration for high-volume processing
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def process_queue():
    """Process scan requests from Redis queue"""
    while True:
        try:
            # Get request from queue
            _, request_data = redis_client.blpop(['scan_queue'], timeout=1)
            request = json.loads(request_data)

            # Process the request
            result = n8n_service.scan_credit_cards(request['text'])

            # Store result
            redis_client.set(f"result:{request['id']}", json.dumps(result))

        except Exception as e:
            logger.error(f"Queue processing error: {e}")
```

## 🔍 Troubleshooting

### **Common Issues**

**Problem**: Webhook endpoint not responding
```bash
# Check if service is running
curl http://localhost:8080/health

# Check service logs
python3 docs/examples/n8n_workflows/n8n_integration.py
```

**Problem**: n8n can't connect to webhook
- Verify the service is running on correct port
- Check firewall settings
- Ensure n8n can reach the webhook URL

**Problem**: Slow response times
- Monitor detector service health
- Check network connectivity
- Consider implementing request queuing

### **Debug Mode**
```python
# Run with debug logging
service.run(debug=True)
```

## 📚 Additional Resources

- **n8n Documentation**: [https://docs.n8n.io/](https://docs.n8n.io/)
- **Claude Skills Examples**: `../claude_skills/`
- **API Integration**: `../api_integrations/`
- **Main Integration Guide**: `../INTEGRATION_GUIDE.md`

## 🤝 Contributing

To add new n8n workflow examples:
1. Create workflow JSON files
2. Add documentation with screenshots
3. Include step-by-step instructions
4. Update this README file

---

**Ready for n8n integration!** 🚀

These examples provide everything you need to build powerful credit card detection workflows in n8n, from simple scanning to complex compliance automation pipelines.