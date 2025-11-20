# 📊 Monitoring Cheat Sheet

Quick reference for monitoring the Credit Card Detection system.

## 🚀 5-Minute Setup

```bash
# 1. Start monitoring stack
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# 2. Check services
docker-compose -f docker-compose.production.yml ps

# 3. Access interfaces
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3002

# 4. Test monitoring
python3 monitor_credit_card_performance.py
```

## 📈 Key Metrics Dashboard

### Grafana Dashboard Import
1. Go to http://localhost:3002
2. Dashboards → Import
3. Upload `monitoring/grafana/dashboards/credit-card-dashboard.json`

### Must-Have Metrics
| Metric | Target | Check |
|--------|--------|-------|
| Response Time | < 100ms | 95th percentile |
| Error Rate | < 1% | Failed requests |
| Throughput | Baseline | Requests/sec |
| Availability | > 99.9% | Uptime |

## 🔍 Essential Queries

### Service Health
```promql
up{job="credit-card-detector"}
```

### Performance
```promql
# Response time
histogram_quantile(0.95, rate(credit_card_detector_request_duration_seconds_bucket[5m]))

# Request rate
rate(credit_card_detector_requests_total[5m])

# Error rate
rate(credit_card_scan_requests_total{has_detections="error"}[5m])
```

### Detection Metrics
```promql
# Detection rate
rate(credit_card_detections_total[5m]) by (valid_luhn)

# Active connections
credit_card_detector_active_connections
```

## 🧪 Quick Tests

```bash
# Test API
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Card: 4111111111111111"}'

# Check metrics
curl http://localhost:9090/api/v1/query?query=up

# Health checks
curl http://localhost:5000/health
curl http://localhost:9090/api/v1/status/config
curl http://localhost:3002/api/health
```

## 🚨 Critical Alerts

```yaml
# High response time
histogram_quantile(0.95, rate(credit_card_detector_request_duration_seconds_bucket[5m])) > 0.1

# High error rate
rate(credit_card_scan_requests_total{has_detections="error"}[5m]) > 0.01

# Service down
up{job="credit-card-detector"} == 0
```

## 📋 Daily Checklist

- [ ] Services running: `docker-compose ps`
- [ ] Prometheus accessible: http://localhost:9090
- [ ] Grafana accessible: http://localhost:3002
- [ ] API responding: `curl http://localhost:5000/health`
- [ ] No critical alerts
- [ ] Response times < 100ms
- [ ] Error rate < 1%

## 🔧 Troubleshooting

### Service Not Running
```bash
docker-compose -f docker-compose.production.yml restart credit-card-detector
```

### No Metrics in Grafana
```bash
# Check Prometheus targets
curl "http://localhost:9090/api/v1/targets"

# Check metrics endpoint
curl http://localhost:5000/metrics
```

### High Memory Usage
```bash
# Check usage
docker stats

# Restart if needed
docker-compose -f docker-compose.production.yml restart credit-card-detector
```

## 📚 Full Documentation

- **Complete Guide**: `MONITORING_GUIDE.md`
- **Quick Start**: `QUICK_START.md`
- **Main README**: `README.md`
- **Test Script**: `monitor_credit_card_performance.py`

## 🆘 Emergency Commands

```bash
# Stop everything
docker-compose -f docker-compose.production.yml down

# Restart monitoring stack
docker-compose -f docker-compose.production.yml up -d prometheus grafana

# View logs
docker-compose -f docker-compose.production.yml logs -f credit-card-detector
```