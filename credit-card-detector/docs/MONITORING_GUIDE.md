# 📊 Production Monitoring Guide

Complete guide for monitoring the Credit Card Detection system in production environments.

## 🎯 Overview

The Credit Card Detection system includes enterprise-grade monitoring with:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Custom Metrics**: Application-specific performance data
- **Alerting**: Automated notifications for issues

## 🚀 Quick Start

### 1. Start Monitoring Stack

```bash
# Start production environment with monitoring
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# Verify all services are running
docker-compose -f docker-compose.production.yml ps
```

### 2. Access Monitoring Interfaces

| Service | URL | Purpose |
|---------|-----|---------|
| **Prometheus** | http://localhost:9090 | Metrics collection and querying |
| **Grafana** | http://localhost:3002 | Dashboards and visualization |
| **Application** | http://localhost:5000 | Main application API |

### 3. Verify Monitoring is Working

```bash
# Check Prometheus is collecting metrics
curl http://localhost:9090/api/v1/query?query=up

# Check Grafana is healthy
curl http://localhost:3002/api/health

# Run comprehensive monitoring test
python3 monitor_credit_card_performance.py
```

## 📈 Key Performance Indicators (KPIs)

### Core Application Metrics

| Metric | Description | Target | Query |
|--------|-------------|--------|-------|
| **Response Time** | 95th percentile latency | < 100ms | `histogram_quantile(0.95, rate(credit_card_detector_request_duration_seconds_bucket[5m]))` |
| **Throughput** | Requests per second | Baseline | `rate(credit_card_detector_requests_total[5m])` |
| **Error Rate** | Failed requests | < 1% | `rate(credit_card_scan_requests_total{has_detections="error"}[5m])` |
| **Detection Rate** | Cards found per minute | Volume tracking | `rate(credit_card_detections_total[5m])` |
| **Availability** | Service uptime | > 99.9% | `up{job="credit-card-detector"}` |

### Infrastructure Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **CPU Usage** | Processor utilization | < 80% |
| **Memory Usage** | RAM utilization | < 85% |
| **Disk Usage** | Storage utilization | < 90% |
| **Network I/O** | Data transfer rates | Monitor baseline |

## 🔍 Grafana Dashboard Setup

### Import Pre-built Dashboard

1. **Access Grafana**: http://localhost:3002
2. **Login** with your credentials
3. **Import Dashboard**:
   - Navigate to **Dashboards → Import**
   - Upload `monitoring/grafana/dashboards/credit-card-dashboard.json`
   - Select **Prometheus** as the data source
   - Click **Import**

### Dashboard Features

The pre-built dashboard includes:

- **📊 Request Metrics**: Rate, total count, response times
- **🎯 Detection Analytics**: Valid/invalid card ratios
- **💾 System Resources**: Memory, CPU, network usage
- **🚨 Health Status**: Service dependencies and uptime
- **📈 Performance Trends**: Historical data and predictions
- **🔍 Error Analysis**: Error rates and types

### Create Custom Dashboards

```json
{
  "dashboard": {
    "title": "Custom Credit Card Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(credit_card_detector_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      }
    ]
  }
}
```

## 📊 Prometheus Monitoring

### Core Configuration

The Prometheus configuration is in `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'credit-card-detector'
    static_configs:
      - targets: ['credit-card-detector:5000']
    scrape_interval: 15s
    metrics_path: /metrics
```

### Essential Queries

#### Service Health

```promql
# Service availability
up{job="credit-card-detector"}

# Target status
up{job=~".*"}
```

#### Performance Metrics

```promql
# Request rate (per second)
rate(credit_card_detector_requests_total[5m])

# Response time percentiles
histogram_quantile(0.50, rate(credit_card_detector_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(credit_card_detector_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(credit_card_detector_request_duration_seconds_bucket[5m]))

# Active connections
credit_card_detector_active_connections
```

#### Detection Metrics

```promql
# Credit card detection rate by validity
rate(credit_card_detections_total[5m]) by (valid_luhn)

# Cards detected per scan histogram
histogram_quantile(0.95, rate(credit_cards_found_per_scan_bucket[5m]))

# Scan success/failure rates
rate(credit_card_scan_requests_total[5m]) by (has_detections)
```

#### Error Monitoring

```promql
# Error rate
rate(credit_card_scan_requests_total{has_detections="error"}[5m])

# HTTP error rates
rate(credit_card_detector_requests_total{status=~"5.."}[5m])
```

## 🚨 Alerting Setup

### Alert Rules

Create alert rules in `monitoring/rules/credit-card-alerts.yml`:

```yaml
groups:
  - name: credit-card-detector
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(credit_card_detector_request_duration_seconds_bucket[5m])) > 0.1
        for: 2m
        labels:
          severity: warning
          service: credit-card-detector
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"

      - alert: HighErrorRate
        expr: rate(credit_card_scan_requests_total{has_detections="error"}[5m]) > 0.01
        for: 1m
        labels:
          severity: critical
          service: credit-card-detector
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: ServiceDown
        expr: up{job="credit-card-detector"} == 0
        for: 30s
        labels:
          severity: critical
          service: credit-card-detector
        annotations:
          summary: "Credit card detector service is down"
          description: "Service has been down for more than 30 seconds"

      - alert: HighMemoryUsage
        expr: (container_memory_usage_bytes{name="credit-card-detector"} / container_spec_memory_limit_bytes{name="credit-card-detector"}) > 0.9
        for: 5m
        labels:
          severity: warning
          service: credit-card-detector
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is {{ $value | humanizePercentage }}"
```

### AlertManager Configuration

Configure AlertManager in `monitoring/alertmanager.yml`:

```yaml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@company.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'team@company.com'
        subject: '[Alert] Credit Card Detector: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
```

## 🧪 Performance Testing

### Load Testing Script

```python
import requests
import time
import concurrent.futures
import statistics

def test_api_performance(text="Test card: 4111111111111111", url="http://localhost:5000/scan"):
    """Test API performance and return metrics."""
    start_time = time.time()

    try:
        response = requests.post(url, json={"text": text}, timeout=10)
        end_time = time.time()

        return {
            "success": response.status_code == 200,
            "response_time": end_time - start_time,
            "status_code": response.status_code,
            "detections": len(response.json().get("detections", [])) if response.status_code == 200 else 0
        }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "response_time": end_time - start_time,
            "error": str(e),
            "detections": 0
        }

def run_load_test(concurrent_users=10, requests_per_user=50):
    """Run load test with multiple concurrent users."""

    def user_session():
        times = []
        successes = 0

        for _ in range(requests_per_user):
            result = test_api_performance()
            times.append(result["response_time"])
            if result["success"]:
                successes += 1

        return times, successes

    # Run concurrent user sessions
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(user_session) for _ in range(concurrent_users)]
        results = [future.result() for future in futures]

    # Calculate statistics
    all_times = []
    total_successes = 0

    for times, successes in results:
        all_times.extend(times)
        total_successes += successes

    total_requests = concurrent_users * requests_per_user

    print(f"Load Test Results:")
    print(f"  Total requests: {total_requests}")
    print(f"  Successful requests: {total_successes}")
    print(f"  Success rate: {total_successes/total_requests:.2%}")
    print(f"  Average response time: {statistics.mean(all_times):.3f}s")
    print(f"  95th percentile: {statistics.quantiles(all_times, n=20)[18]:.3f}s")
    print(f"  99th percentile: {statistics.quantiles(all_times, n=100)[98]:.3f}s")

if __name__ == "__main__":
    run_load_test(concurrent_users=5, requests_per_user=20)
```

### Monitoring Test Script

```bash
#!/bin/bash
# comprehensive_monitoring_test.sh

echo "🔍 Starting Comprehensive Monitoring Test"

# Test service health
echo "📊 Testing service health..."
curl -f http://localhost:5000/health || echo "❌ Application health check failed"
curl -f http://localhost:9090/api/v1/status/config || echo "❌ Prometheus health check failed"
curl -f http://localhost:3002/api/health || echo "❌ Grafana health check failed"

# Test credit card detection
echo "🎯 Testing credit card detection..."
response=$(curl -s -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Test card: 4111111111111111"}')

echo "Detection response: $response"

# Test metrics collection
echo "📈 Testing metrics collection..."
curl -s "http://localhost:9090/api/v1/query?query=up" | jq '.data.result[] | {job: .labels.job, status: .value[1]}'

# Test performance
echo "⚡ Testing performance..."
python3 monitor_credit_card_performance.py

echo "✅ Monitoring test completed"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Prometheus Not Collecting Metrics

**Symptoms**: Targets showing as "DOWN" in Prometheus

**Solutions**:
```bash
# Check if application is running
docker-compose -f docker-compose.production.yml ps credit-card-detector

# Check if metrics endpoint is accessible
curl http://localhost:5000/metrics

# Check Prometheus configuration
docker exec prometheus-prod cat /etc/prometheus/prometheus.yml

# Restart Prometheus
docker-compose -f docker-compose.production.yml restart prometheus
```

#### 2. Grafana Dashboard Not Showing Data

**Symptoms**: Dashboard panels show "No data"

**Solutions**:
```bash
# Check Prometheus data source
curl -u "admin:YOUR_PASSWORD" http://localhost:3002/api/datasources

# Verify Prometheus is collecting data
curl "http://localhost:9090/api/v1/query?query=credit_card_detector_requests_total"

# Check data source configuration in Grafana
# Go to Configuration → Data Sources → Prometheus
```

#### 3. High Memory Usage

**Symptoms**: Memory usage consistently > 90%

**Solutions**:
```bash
# Check container memory usage
docker stats

# Monitor application memory patterns
curl "http://localhost:9090/api/v1/query?query=container_memory_usage_bytes"

# Restart application if needed
docker-compose -f docker-compose.production.yml restart credit-card-detector
```

#### 4. Missing Application Metrics

**Symptoms**: Only basic metrics available, no application-specific data

**Solutions**:
```bash
# Check if application is using the metrics-enabled version
# The file should be app_with_metrics.py, not app.py

# Verify metrics endpoint exists
curl http://localhost:5000/metrics

# Check for application logs
docker-compose logs -f credit-card-detector
```

### Debugging Commands

```bash
# Check all container statuses
docker-compose -f docker-compose.production.yml ps

# View application logs
docker-compose -f docker-compose.production.yml logs -f credit-card-detector

# View monitoring logs
docker-compose -f docker-compose.production.yml logs -f prometheus grafana

# Check resource usage
docker stats

# Test application endpoints
curl -v http://localhost:5000/health
curl -v http://localhost:5000/metrics

# Check Prometheus targets
curl "http://localhost:9090/api/v1/targets"

# Run full monitoring test
python3 monitor_credit_card_performance.py
```

## 📋 Monitoring Checklist

### Daily Checks

- [ ] All services running: `docker-compose ps`
- [ ] No critical alerts firing
- [ ] Response times < 100ms (95th percentile)
- [ ] Error rate < 1%
- [ ] Disk usage < 90%
- [ ] Memory usage < 85%

### Weekly Checks

- [ ] Review dashboard trends
- [ ] Check metric retention (30 days)
- [ ] Verify backup procedures
- [ ] Update alert thresholds if needed
- [ ] Review performance trends

### Monthly Checks

- [ ] Update monitoring configurations
- [ ] Review and optimize alerts
- [ ] Check storage capacity planning
- [ ] Performance baseline updates
- [ ] Documentation updates

## 📚 Additional Resources

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **Docker Monitoring**: https://docs.docker.com/config/daemon/prometheus/
- **Application Metrics**: `monitoring/prometheus.yml`
- **Dashboard Configurations**: `monitoring/grafana/dashboards/`

## 🆘 Support

For monitoring issues:

1. Check this guide first
2. Review logs: `docker-compose logs -f prometheus grafana`
3. Run diagnostic: `python3 monitor_credit_card_performance.py`
4. Check service health: `curl http://localhost:5000/health`
5. Review metrics: http://localhost:9090/targets