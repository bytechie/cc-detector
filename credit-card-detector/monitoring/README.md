# 📊 Monitoring and Observability Stack

This directory contains the complete monitoring and observability configuration for the Credit Card Detector system, organized into logical components.

## 📁 Monitoring Structure

```
claude_subagent/monitoring/
├── README.md                              # This documentation
├── __init__.py                             # Core monitoring classes and functions
├── grafana/                               # Grafana dashboard and datasource configurations
│   ├── dashboards/                        # Dashboard definitions
│   │   ├── credit-card-dashboard.json    # Auto-provisioned dashboard
│   │   └── credit-card-detector-dashboard.yml
│   └── datasources/                       # Datasource configurations
│       └── prometheus.yml                # Prometheus datasource for Grafana
└── prometheus/                           # Prometheus monitoring configuration
    ├── prometheus.yml                    # Production Prometheus configuration
    ├── prometheus-local.yml              # Local development configuration
    └── rules/                             # Alerting and recording rules
```

## 🚀 Components Overview

### **Core Monitoring Module (`__init__.py`)**
- **Metrics Collection**: Prometheus metrics integration
- **Performance Tracking**: Request timing, throughput, error rates
- **Health Monitoring**: Application and dependency health checks
- **Custom Metrics**: Business logic and domain-specific metrics

### **Grafana Configuration (`grafana/`)**
- **Auto-Provisioned Dashboards**: Ready-to-use monitoring dashboards
- **Data Sources**: Prometheus integration configuration
- **Alerting**: Pre-configured alerts for critical metrics
- **Visualization**: Time-series data visualization

### **Prometheus Configuration (`prometheus/`)**
- **Service Discovery**: Automatic service endpoint discovery
- **Metrics Scraping**: Collection intervals and targets
- **Data Retention**: Storage and retention policies
- **Alert Rules**: Condition-based alerting

## 🔧 Configuration Files

### **Prometheus Configurations**

#### **`prometheus/prometheus.yml`** (Production)
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'credit-card-detector'
    static_configs:
      - targets: ['app:5000']
    metrics_path: '/metrics'
```

#### **`prometheus/prometheus-local.yml`** (Development)
```yaml
global:
  scrape_interval: 10s

scrape_configs:
  - job_name: 'credit-card-detector-local'
    static_configs:
      - targets: ['host.docker.internal:5000']
```

### **Grafana Configuration**

#### **Dashboard Auto-Provisioning**
- **Credit Card Detector Dashboard**: Real-time monitoring dashboard
- **Metrics**: Request rates, response times, detection accuracy
- **Alerts**: Performance degradation and error thresholds

## 📊 Available Metrics

### **Application Metrics**
- `credit_card_detector_requests_total` - Total API requests
- `credit_card_scan_requests_total` - Credit card scan operations
- `credit_card_detections_total` - Cards detected (valid/invalid)
- `credit_card_detector_request_duration_seconds` - Response times

### **System Metrics**
- `credit_card_detector_active_connections` - Active connections
- `credit_card_detector_latest_scan_timestamp` - Last scan time
- `cpu_usage_percent` - Resource utilization
- `memory_usage_bytes` - Memory consumption

## 🚨 Alerting Rules

### **Performance Alerts**
- **High Response Time**: Alert when 95th percentile > 100ms
- **Error Rate**: Alert when error rate > 1%
- **Service Downtime**: Alert when service becomes unavailable
- **Resource Exhaustion**: Alert on high CPU/memory usage

### **Business Alerts**
- **Detection Accuracy**: Alert when valid detection rate drops
- **Throughput**: Alert when request processing rate falls
- **Integration Health**: Alert when external integrations fail

## 🔄 Deployment Integration

### **Docker Compose Integration**
The monitoring configuration is integrated with Docker Compose:

```yaml
# Local Development
volumes:
  - ./claude_subagent/monitoring/prometheus/prometheus-local.yml:/etc/prometheus/prometheus.yml:ro
  - ./claude_subagent/monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro

# Production
volumes:
  - ./claude_subagent/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
```

### **Service Discovery**
Prometheus automatically discovers services:
- **Credit Card Detector**: `localhost:5000/metrics`
- **Health Checks**: `/health` endpoint monitoring
- **Dependencies**: External service health monitoring

## 📈 Monitoring Dashboards

### **Credit Card Detector Dashboard**
- **Overview**: Request volume and response times
- **Detection Metrics**: Card detection rates and accuracy
- **Performance**: Request duration histograms
- **Errors**: Error rates and types
- **Resources**: CPU, memory, and connection metrics

### **Access URLs**
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3002 (admin/admin123)
- **Health Check**: http://localhost:5000/health
- **Metrics**: http://localhost:5000/metrics

## 🛠️ Troubleshooting

### **Common Issues**

#### **Prometheus Not Scraping**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify metrics endpoint
curl http://localhost:5000/metrics
```

#### **Grafana Dashboard Not Loading**
```bash
# Check dashboard provisioning
curl http://localhost:3002/api/dashboards

# Verify datasource connection
curl http://localhost:3002/api/datasources
```

#### **High Memory Usage**
```bash
# Check container resource usage
docker stats

# Adjust Prometheus retention
# Edit prometheus.yml: --storage.tsdb.retention.time
```

## 🧪 Testing Configuration

### **Local Development Setup**
```bash
# Start monitoring stack
./start-local-monitoring.sh

# Verify configuration
docker-compose -f docker-compose.local.yml config
```

### **Configuration Validation**
```bash
# Validate Prometheus configuration
docker run --rm -v $(pwd)/claude_subagent/monitoring/prometheus:/etc/prometheus \
  prom/prometheus --config.file=/etc/prometheus/prometheus.yml --dry-run
```

## 📚 Best Practices

### **Metrics Design**
- Use consistent naming conventions
- Include informative labels
- Track business-relevant metrics
- Monitor both technical and business KPIs

### **Alerting Strategy**
- Set meaningful thresholds
- Avoid alert fatigue
- Include runbooks for common issues
- Test alert delivery regularly

### **Dashboard Design**
- Focus on actionable insights
- Use appropriate visualizations
- Include context and annotations
- Regular review and optimization

## 🔗 Integration Points

### **Application Integration**
- **Metrics Export**: `/metrics` endpoint
- **Health Checks**: `/health` endpoint
- **Custom Metrics**: Business logic metrics

### **External Systems**
- **Skill Seekers**: Integration health monitoring
- **Presidio Services**: Dependency monitoring
- **Database**: Performance and connection metrics

---

*This monitoring stack provides comprehensive observability for the Credit Card Detector system, enabling proactive issue detection and performance optimization.*