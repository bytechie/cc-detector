# 🌐 API Integration Examples

This directory contains examples of how to integrate with the Credit Card Detector REST API for various use cases and applications.

## 📁 Files Overview

| File | Purpose | Key Features |
|------|---------|--------------|
| `basic_api.py` | Basic API client examples | Simple integration, error handling |
| `webhook_server.py` | Webhook server for web apps | HTTP endpoints, batch processing |

## 🚀 Quick Start

### **1. Start the Credit Card Detector**
```bash
./start.sh start basic
```

### **2. Run Basic API Example**
```bash
source .venv/bin/activate
python3 docs/examples/api_integrations/basic_api.py
```

### **3. Start Webhook Server**
```bash
source .venv/bin/activate
python3 docs/examples/api_integrations/webhook_server.py --port 8080
```

## 📡 API Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/health` | Health check | `curl http://localhost:5000/health` |
| POST | `/scan` | Scan text for cards | `curl -X POST -d '{"text":"test"}' http://localhost:5000/scan` |

### **Response Format**
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

## 💻 Integration Examples

### **Basic Python Client**
```python
import requests

def scan_text(text: str) -> dict:
    """Scan text for credit cards"""
    response = requests.post(
        "http://localhost:5000/scan",
        json={"text": text},
        headers={"Content-Type": "application/json"}
    )
    return response.json()

# Usage
result = scan_text("My Visa: 4111111111111111")
print(f"Cards found: {len(result['detections'])}")
```

### **JavaScript/Node.js Client**
```javascript
const axios = require('axios');

async function scanText(text) {
  try {
    const response = await axios.post('http://localhost:5000/scan', {
      text: text
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.message);
    return null;
  }
}

// Usage
scanText('Card: 4111111111111111').then(result => {
  console.log(`Cards found: ${result.detections.length}`);
});
```

### **cURL Examples**
```bash
# Health check
curl http://localhost:5000/health

# Scan text
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "My card is 4111111111111111"}'

# With pretty output
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Card: 4111111111111111"}' | jq .
```

## 🔧 Advanced Integration

### **Batch Processing**
```python
import requests
import time

def batch_scan(texts, batch_size=10):
    """Process multiple texts efficiently"""
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]

        for text in batch:
            result = scan_text(text)
            results.append({
                'text': text,
                'result': result,
                'timestamp': time.time()
            })

    return results
```

### **Error Handling**
```python
import requests
from requests.exceptions import RequestException

def safe_scan(text, retries=3):
    """Scan with retry logic"""
    for attempt in range(retries):
        try:
            response = requests.post(
                "http://localhost:5000/scan",
                json={"text": text},
                timeout=10
            )
            return response.json()
        except RequestException as e:
            if attempt == retries - 1:
                return {"error": str(e), "detections": []}
            time.sleep(2 ** attempt)  # Exponential backoff
```

### **Asynchronous Processing**
```python
import aiohttp
import asyncio

async def async_scan(text):
    """Asynchronous scanning for high throughput"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:5000/scan",
            json={"text": text}
        ) as response:
            return await response.json()

async def batch_async_scan(texts):
    """Process multiple texts concurrently"""
    tasks = [async_scan(text) for text in texts]
    return await asyncio.gather(*tasks)
```

## 🌍 Web Framework Integration

### **Flask Integration**
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api/scan', methods=['POST'])
def scan_endpoint():
    text = request.json.get('text', '')

    # Call the detector
    response = requests.post(
        'http://localhost:5000/scan',
        json={'text': text}
    )

    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=3000)
```

### **FastAPI Integration**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class ScanRequest(BaseModel):
    text: str

class ScanResponse(BaseModel):
    detections: list
    redacted: str
    scan_duration_seconds: float

@app.post("/scan", response_model=ScanResponse)
async def scan_text(request: ScanRequest):
    try:
        response = requests.post(
            "http://localhost:5000/scan",
            json={"text": request.text}
        )
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **Django Integration**
```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

@csrf_exempt
def scan_credit_cards(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')

            response = requests.post(
                "http://localhost:5000/scan",
                json={"text": text}
            )

            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
```

## 🚀 Production Deployment

### **Configuration Management**
```python
import os
from dataclasses import dataclass

@dataclass
class APIClientConfig:
    base_url: str = os.getenv('DETECTOR_URL', 'http://localhost:5000')
    timeout: int = int(os.getenv('DETECTOR_TIMEOUT', '10'))
    retries: int = int(os.getenv('DETECTOR_RETRIES', '3'))
    api_key: str = os.getenv('DETECTOR_API_KEY', '')

config = APIClientConfig()
```

### **Connection Pooling**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class CreditCardAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def scan(self, text: str):
        response = self.session.post(
            f"{self.base_url}/scan",
            json={"text": text},
            timeout=10
        )
        return response.json()
```

### **Monitoring and Logging**
```python
import logging
import time
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            logger.info(f"{func.__name__} completed in {duration:.3f}s")

            # Log if slow
            if duration > 1.0:
                logger.warning(f"Slow {func.__name__}: {duration:.3f}s")

            return result

        except Exception as e:
            logger.error(f"{func.__name__} failed: {str(e)}")
            raise

    return wrapper

@monitor_performance
def scan_text(text: str):
    """Monitored scan function"""
    # Implementation here
    pass
```

## 📊 Performance Optimization

### **Caching**
```python
import hashlib
from functools import lru_cache

class CachingAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.cache = {}

    def get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode()).hexdigest()

    def scan(self, text: str):
        cache_key = self.get_cache_key(text)

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Call API
        result = self._call_api(text)

        # Cache result
        self.cache[cache_key] = result

        return result
```

### **Load Balancing**
```python
import random
from typing import List

class LoadBalancedClient:
    def __init__(self, detector_urls: List[str]):
        self.urls = detector_urls
        self.current_index = 0

    def get_next_url(self) -> str:
        """Round-robin URL selection"""
        url = self.urls[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.urls)
        return url

    def scan(self, text: str):
        for attempt in range(len(self.urls)):
            try:
                url = self.get_next_url()
                response = requests.post(f"{url}/scan", json={"text": text})
                return response.json()
            except Exception:
                if attempt == len(self.urls) - 1:
                    raise
                continue
```

## 🔒 Security Best Practices

### **API Key Authentication**
```python
import requests

class SecureAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def scan(self, text: str):
        response = self.session.post(
            f"{self.base_url}/scan",
            json={"text": text}
        )
        return response.json()
```

### **Input Validation**
```python
def validate_input(text: str) -> str:
    """Validate and sanitize input"""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    if len(text) > 10000:  # Max 10KB
        raise ValueError("Input too long")

    # Remove null bytes and other control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')

    return text.strip()
```

## 📈 Monitoring and Metrics

### **Health Check Implementation**
```python
import requests
from datetime import datetime

class HealthMonitor:
    def __init__(self, detector_url: str):
        self.detector_url = detector_url
        self.last_check = None
        self.status_history = []

    def check_health(self) -> dict:
        """Check detector health"""
        try:
            response = requests.get(f"{self.detector_url}/health", timeout=5)
            result = response.json()

            status = {
                'healthy': response.status_code == 200,
                'timestamp': datetime.now().isoformat(),
                'details': result
            }

        except Exception as e:
            status = {
                'healthy': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

        self.status_history.append(status)
        self.last_check = datetime.now()

        return status

    def get_uptime_percentage(self) -> float:
        """Calculate uptime percentage"""
        if not self.status_history:
            return 0.0

        healthy_checks = sum(1 for s in self.status_history if s['healthy'])
        return (healthy_checks / len(self.status_history)) * 100
```

## 🔍 Troubleshooting

### **Common Issues**

**Problem**: Connection refused
```bash
# Check if detector is running
curl http://localhost:5000/health

# Start detector
./start.sh start basic
```

**Problem**: Timeout errors
```python
# Increase timeout
response = requests.post(url, json=data, timeout=30)
```

**Problem**: Invalid JSON response
```python
# Add error handling
try:
    result = response.json()
except ValueError:
    print("Invalid JSON response:", response.text)
```

### **Debug Tools**
```python
# Debug request/response
import logging
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
```

## 📚 Additional Resources

- **Claude Skills Examples**: `../claude_skills/`
- **n8n Workflows**: `../n8n_workflows/`
- **Main Integration Guide**: `../INTEGRATION_GUIDE.md`
- **API Documentation**: Check `/health` endpoint

---

**Ready for API integration!** 🚀

These examples provide everything you need to integrate the Credit Card Detector API into your applications, from simple scripts to production-ready services.