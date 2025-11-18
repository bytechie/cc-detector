# Credit Card Detector API Documentation

Welcome to the comprehensive API documentation for the Credit Card Detector system. This intelligent platform combines adaptive AI, resource management, and extensible plugin architecture to provide state-of-the-art credit card detection and redaction capabilities.

## 🚀 Quick Start

### Base URL
```
Development: http://localhost:5000
Production: https://your-domain.com
```

### Authentication
The API supports API key authentication:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/health
```

## 📋 Table of Contents

1. [Core Detection APIs](#core-detection-apis)
2. [Adaptive Skills APIs](#adaptive-skills-apis)
3. [Resource Management APIs](#resource-management-apis)
4. [Plugin System APIs](#plugin-system-apis)
5. [Skill Seekers Integration APIs](#skill-seekers-integration-apis)
6. [Monitoring & Observability APIs](#monitoring--observability-apis)
7. [Configuration APIs](#configuration-apis)
8. [Error Codes](#error-codes)
9. [Rate Limiting](#rate-limiting)
10. [SDKs and Client Libraries](#sdks-and-client-libraries)

---

## 🔍 Core Detection APIs

### Detect Credit Cards
**POST** `/scan`

Detect credit card numbers in provided text.

**Request Body:**
```json
{
  "text": "Credit card: 4111111111111111",
  "options": {
    "include_metadata": true,
    "confidence_threshold": 0.7
  }
}
```

**Response:**
```json
{
  "detections": [
    {
      "start": 14,
      "end": 30,
      "raw": "4111111111111111",
      "number": "4111111111111111",
      "valid": true,
      "confidence": 0.95,
      "card_type": "visa"
    }
  ],
  "redacted": "Credit card: 4111111111111111",
  "stats": {
    "total_detections": 1,
    "processing_time_ms": 15.2,
    "confidence_score": 0.95
  }
}
```

### Batch Detection
**POST** `/scan-batch`

Detect credit cards in multiple texts.

**Request Body:**
```json
{
  "texts": [
    "Card: 4111111111111111",
    "No card here",
    "Another: 4242424242424242"
  ],
  "options": {
    "parallel": true,
    "max_workers": 4
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "index": 0,
      "text": "Card: 4111111111111111",
      "detections": [...],
      "redacted": "Card: 4111111111111111"
    },
    {
      "index": 1,
      "text": "No card here",
      "detections": [],
      "redacted": "No card here"
    },
    {
      "index": 2,
      "text": "Another: 4242424242424242",
      "detections": [...],
      "redacted": "Another: 4242424242424242"
    }
  ],
  "summary": {
    "total_texts": 3,
    "total_detections": 2,
    "processing_time_ms": 45.8
  }
}
```

### Enhanced Detection with Adaptive Skills
**POST** `/scan-enhanced`

Use all available adaptive skills for enhanced detection.

**Request Body:**
```json
{
  "text": "Multiple cards: 4111111111111111, 4242-4242-4242-4242",
  "options": {
    "use_all_skills": true,
    "include_external": true,
    "resource_aware": true,
    "max_processing_time": 30
  }
}
```

**Response:**
```json
{
  "detections": [
    {
      "start": 16,
      "end": 32,
      "raw": "4111111111111111",
      "skill_source": "detect_credit_cards",
      "confidence": 0.98
    },
    {
      "start": 34,
      "end": 50,
      "raw": "4242-4242-4242-4242",
      "skill_source": "enhanced_hyphen_detector",
      "confidence": 0.92
    }
  ],
  "stats": {
    "base_detections": 2,
    "adaptive_detections": 0,
    "total_detections": 2,
    "skills_used": ["detect_credit_cards", "enhanced_hyphen_detector"],
    "resource_optimization": {
      "enabled": true,
      "strategy": "parallel_limited",
      "constraint_level": "low"
    }
  }
}
```

---

## 🧠 Adaptive Skills APIs

### Train New Skills
**POST** `/train`

Generate new adaptive skills from examples.

**Request Body:**
```json
{
  "examples": [
    {
      "input": "Card ending in 4242: ****-****-****-4242",
      "expected_detections": [
        {
          "raw": "****-****-****-4242",
          "pattern": "masked_card",
          "last4": "4242"
        }
      ]
    }
  ],
  "description": "Skills for detecting masked credit cards",
  "options": {
    "quality_threshold": 0.6,
    "auto_deploy": true
  }
}
```

**Response:**
```json
{
  "message": "Generated 1 new skills",
  "new_skills": [
    {
      "name": "detect_masked_cards_8191",
      "description": "Template-based skill for detecting masked credit card numbers",
      "test_cases_count": 3,
      "quality_score": 0.78
    }
  ],
  "total_skills": 5
}
```

### List Skills
**GET** `/skills`

List all available adaptive skills.

**Response:**
```json
{
  "total_skills": 5,
  "skills": [
    {
      "name": "detect_credit_cards",
      "description": "Basic credit card detection",
      "dependencies": ["re"],
      "test_cases_count": 3,
      "performance": {
        "f1_score": 0.95,
        "precision": 0.94,
        "recall": 0.96,
        "last_updated": 1642784400.0
      },
      "quality_score": 0.95,
      "quality_grade": "A"
    }
  ]
}
```

### Skill Performance
**GET** `/skill-performance`

Get detailed performance metrics for all skills.

**Response:**
```json
{
  "skills_performance": {
    "detect_credit_cards": {
      "true_positives": 245,
      "false_positives": 12,
      "false_negatives": 8,
      "accuracy": 0.94,
      "precision": 0.95,
      "recall": 0.97,
      "f1_score": 0.96,
      "last_updated": 1642784400.0
    }
  },
  "total_skills": 3
}
```

### Submit Skill Feedback
**POST** `/feedback`

Submit feedback to improve skill performance.

**Request Body:**
```json
{
  "input_text": "Card: 4242424242424242",
  "skill_name": "detect_credit_cards",
  "feedback_type": "false_negative",
  "expected_detections": [
    {
      "raw": "4242424242424242",
      "start": 6,
      "end": 22
    }
  ],
  "context": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

---

## ⚙️ Resource Management APIs

### Resource Monitoring
**GET** `/resource-monitor`

Get current system resource usage.

**Response:**
```json
{
  "current": {
    "cpu_percent": 45.2,
    "memory_percent": 62.8,
    "memory_available_mb": 7344.1,
    "active_threads": 12,
    "timestamp": 1642784400.0
  },
  "average_5min": {
    "cpu_percent": 47.1,
    "memory_percent": 60.3
  },
  "monitoring_active": true,
  "history_size": 1000,
  "constraint_level": "low"
}
```

### Resource Constraints
**GET** `/resource-constraints`

Get current resource constraints and recommendations.

**Response:**
```json
{
  "constraints": {
    "max_cpu_percent": 80.0,
    "max_memory_percent": 80.0,
    "max_batch_size": 1000,
    "max_concurrent_tasks": 4
  },
  "current_constraint_level": "low",
  "recommendations": [
    "System operating under optimal conditions",
    "Consider enabling parallel processing for better performance"
  ]
}
```

**POST** `/resource-constraints`

Update resource constraints.

**Request Body:**
```json
{
  "max_cpu_percent": 70.0,
  "max_memory_percent": 75.0,
  "max_batch_size": 500
}
```

### Optimization Strategies
**GET** `/optimization-strategies`

Get available optimization strategies and their performance.

**Response:**
```json
{
  "available_strategies": [
    "sequential",
    "batch_optimized",
    "parallel_limited",
    "skill_priority",
    "adaptive_sampling",
    "caching_aggressive"
  ],
  "current_strategy": "batch_optimized",
  "strategy_performance": {
    "sequential": 0.3,
    "batch_optimized": 0.8,
    "parallel_limited": 0.9,
    "skill_priority": 0.7,
    "adaptive_sampling": 0.6,
    "caching_aggressive": 0.5
  }
}
```

### Benchmark Processing
**POST** `/benchmark-processing`

Benchmark different processing strategies.

**Request Body:**
```json
{
  "texts": ["sample", "data", "with", "cards"],
  "iterations": 3
}
```

**Response:**
```json
{
  "benchmark_config": {
    "text_count": 4,
    "iterations": 3
  },
  "results": {
    "sequential": {
      "avg_processing_time": 0.012,
      "throughput": 333.3,
      "success_rate": 1.0
    },
    "parallel_limited": {
      "avg_processing_time": 0.008,
      "throughput": 500.0,
      "success_rate": 1.0
    }
  },
  "recommendation": "Recommended strategy: parallel_limited (throughput: 500.0/sec)"
}
```

### Simulate Resource Constraints
**POST** `/simulate-resource-constraints`

Test different resource constraint scenarios.

**Request Body:**
```json
{
  "scenarios": [
    {
      "name": "critical",
      "max_cpu_percent": 30,
      "max_memory_percent": 30
    }
  ],
  "texts": ["test", "data"]
}
```

---

## 🔌 Plugin System APIs

### List Plugins
**GET** `/plugins`

List all available plugins.

**Response:**
```json
{
  "total_plugins": 3,
  "active_plugins": 2,
  "plugins_by_type": {
    "detector": 2,
    "processor": 1,
    "output": 0
  },
  "plugins": {
    "credit_card_detector": {
      "status": "active",
      "version": "1.0.0",
      "type": "detector",
      "load_time": 1642784400.0,
      "usage_count": 245
    }
  }
}
```

### Install Plugin
**POST** `/plugins/install`

Install a new plugin.

**Request Body:**
```json
{
  "source": "github",
  "repository": "user/plugin-name",
  "version": "1.0.0",
  "auto_enable": true
}
```

### Plugin Details
**GET** `/plugins/{plugin_name}`

Get detailed information about a specific plugin.

---

## 🔗 Skill Seekers Integration APIs

### External Sources
**GET** `/external-sources`

List external skill sources.

**Response:**
```json
{
  "sources": [
    {
      "name": "OWASP_Documentation",
      "url": "https://owasp.org/",
      "type": "documentation",
      "active": true,
      "last_scanned": 1642784400.0,
      "skill_count": 5
    }
  ],
  "total_sources": 3,
  "active_sources": 2
}
```

### Discover Skills
**POST** `/discover-skills`

Discover and import skills from external sources.

**Response:**
```json
{
  "message": "Skill discovery completed",
  "results": {
    "scanned_sources": 2,
    "discovered_skills": 3,
    "imported_skills": 2,
    "conflicts_detected": 1,
    "conflicts_resolved": 1
  }
}
```

---

## 📊 Monitoring & Observability APIs

### Health Check
**GET** `/health`

Comprehensive health check of all system components.

**Response:**
```json
{
  "status": "ok",
  "service": "resource-aware-claude-subagent",
  "timestamp": "2023-01-01T12:00:00Z",
  "dependencies": {
    "analyzer": {
      "name": "presidio-analyzer",
      "status": "healthy",
      "url": "http://localhost:3000"
    },
    "anonymizer": {
      "name": "presidio-anonymizer",
      "status": "healthy",
      "url": "http://localhost:3001"
    }
  },
  "resource_management": {
    "constraints": {...},
    "current_strategy": "batch_optimized",
    "constraint_level": "low"
  }
}
```

### Metrics
**GET** `/metrics`

Get application metrics in Prometheus format.

### Performance Stats
**GET** `/performance-stats`

Get detailed performance statistics.

**Response:**
```json
{
  "processing_performance": {
    "total_processed": 10000,
    "avg_processing_time": 0.015,
    "peak_throughput": 2500.0,
    "total_strategies_used": 5
  },
  "system_info": {
    "cpu_count": 4,
    "memory_total_gb": 16.0,
    "disk_usage_percent": 45.2
  }
}
```

### Monitoring Dashboard
**GET** `/monitoring-dashboard`

Get monitoring dashboard data.

---

## ⚙️ Configuration APIs

### Configuration
**GET** `/config`

Get current configuration.

**Response:**
```json
{
  "app": {
    "name": "credit-card-detector",
    "environment": "production",
    "debug": false
  },
  "detection": {
    "confidence_threshold": 0.7,
    "max_text_length": 1000000
  },
  "adaptive_skills": {
    "enabled": true,
    "quality_threshold": 0.6
  }
}
```

**PUT** `/config`

Update configuration.

---

## ❌ Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request format or parameters |
| `TEXT_TOO_LONG` | 400 | Input text exceeds maximum length |
| `PROCESSING_TIMEOUT` | 408 | Processing took too long |
| `RESOURCE_CONSTRAINTS` | 429 | System under resource constraints |
| `SKILL_NOT_FOUND` | 404 | Requested skill not found |
| `PLUGIN_ERROR` | 500 | Plugin execution error |
| `INTERNAL_ERROR` | 500 | Internal server error |

**Error Response Format:**
```json
{
  "error": {
    "code": "TEXT_TOO_LONG",
    "message": "Input text exceeds maximum length of 1000000 characters",
    "details": {
      "max_length": 1000000,
      "provided_length": 1500000
    }
  },
  "request_id": "req_123456789"
}
```

---

## 🚦 Rate Limiting

The API implements rate limiting to ensure fair usage:

| Endpoint | Rate Limit | Window |
|----------|------------|--------|
| `/scan` | 100 requests/minute | Per API key |
| `/scan-batch` | 50 requests/minute | Per API key |
| `/train` | 10 requests/hour | Per API key |
| All others | 1000 requests/hour | Per API key |

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642785000
```

---

## 📚 SDKs and Client Libraries

### Python SDK
```python
from claude_subagent import CreditCardDetector

# Initialize client
detector = CreditCardDetector(
    api_key="your-api-key",
    base_url="http://localhost:5000"
)

# Simple detection
result = detector.scan("Credit card: 4111111111111111")
print(result.detections)

# Batch detection
texts = ["Card 1: 4111111111111111", "Card 2: 4242424242424242"]
results = detector.scan_batch(texts)

# Resource-aware detection
result = detector.scan_enhanced(
    "Multiple cards: 4111111111111111, 4242-4242-4242-4242",
    resource_aware=True
)
```

### JavaScript SDK
```javascript
import { CreditCardDetector } from '@claude-subagent/js-sdk';

const detector = new CreditCardDetector({
  apiKey: 'your-api-key',
  baseUrl: 'http://localhost:5000'
});

// Simple detection
const result = await detector.scan('Credit card: 4111111111111111');
console.log(result.detections);

// Batch detection
const texts = ['Card 1: 4111111111111111', 'Card 2: 4242424242424242'];
const results = await detector.scanBatch(texts);
```

### Go SDK
```go
package main

import (
    "github.com/claude-subagent/go-sdk"
    "fmt"
)

func main() {
    detector := claude_subagent.NewCreditCardDetector(
        claude_subagent.WithAPIKey("your-api-key"),
        claude_subagent.WithBaseURL("http://localhost:5000"),
    )

    result, err := detector.Scan("Credit card: 4111111111111111")
    if err != nil {
        panic(err)
    }

    fmt.Printf("Found %d detections\n", len(result.Detections))
}
```

### Java SDK
```java
import com.claude_subagent.CreditCardDetector;
import com.claude_subagent.models.DetectionResult;

public class Main {
    public static void main(String[] args) {
        CreditCardDetector detector = new CreditCardDetector.Builder()
            .apiKey("your-api-key")
            .baseUrl("http://localhost:5000")
            .build();

        DetectionResult result = detector.scan("Credit card: 4111111111111111");
        System.out.println("Found " + result.getDetections().size() + " detections");
    }
}
```

---

## 🔗 Links

- [Getting Started Guide](./getting-started.md)
- [Advanced Configuration](./advanced-configuration.md)
- [Plugin Development](./plugin-development.md)
- [Performance Optimization](./performance-optimization.md)
- [Deployment Guide](./deployment.md)
- [Troubleshooting](./troubleshooting.md)

---

## 📞 Support

- **Documentation**: https://docs.credit-card-detector.com
- **GitHub Issues**: https://github.com/your-org/credit-card-detector/issues
- **Community**: https://discord.gg/credit-card-detector
- **Email**: support@credit-card-detector.com

---

*Last updated: January 1, 2024*