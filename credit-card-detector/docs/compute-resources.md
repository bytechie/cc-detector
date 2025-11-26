# 💻 Compute Resource Requirements

This guide provides detailed information about compute resources needed to run the Credit Card Detector project at different scales.

## 🎯 Quick Reference

| Deployment Size | CPU | Memory | Storage | Use Case |
|----------------|-----|--------|---------|----------|
| **Development** | 2 cores | 4 GB | 20 GB SSD | Development & testing |
| **Production** | 4-8 cores | 8-16 GB | 50-100 GB SSD | Medium-scale production |
| **Enterprise** | 16+ cores | 32-64 GB | 200+ GB SSD | Large-scale enterprise |

## 🔧 Minimum Requirements (Development/Small Scale)

**System Requirements:**
```
CPU:    2 cores
Memory: 4 GB RAM
Storage: 20 GB SSD
Network: 100 Mbps
```

**What you can run:**
- Development and testing environment
- Processing < 1,000 texts/hour
- Single-user usage
- Basic plugin usage (1-3 plugins)
- SQLite database

**Example Setup:**
```bash
# Runs with minimum resources
docker-compose up -d
```

**Resource Usage Breakdown:**
- Base Application: ~500 MB RAM
- Plugin System: ~200 MB RAM
- Web API: ~200 MB RAM
- Database: ~100 MB RAM
- Operating System: ~2-3 GB RAM

---

## ⚡ Recommended Requirements (Production/Medium Scale)

**System Requirements:**
```
CPU:    4-8 cores
Memory: 8-16 GB RAM
Storage: 50-100 GB SSD
Network: 1 Gbps
```

**What you can run:**
- Production deployment
- Processing 1,000-10,000 texts/hour
- Multiple concurrent users (10-50)
- Full plugin ecosystem (10+ plugins)
- PostgreSQL database
- Redis caching
- Active ML model training

**Example Setup:**
```bash
# Production-ready deployment
docker-compose -f docker-compose.prod.yml up -d
```

**Performance Expectations:**
- Response Time: 50-100ms
- Throughput: 5,000-15,000 texts/hour
- Concurrent Users: 10-50
- Uptime: 99.9%

---

## 🏢 Enterprise Requirements (Large Scale)

**System Requirements:**
```
CPU:    16+ cores
Memory: 32-64 GB RAM
Storage: 200+ GB SSD (+ additional for databases)
Network: 10 Gbps
Load Balancer: Yes
```

**What you can run:**
- High-volume processing (10,000+ texts/hour)
- Enterprise teams (100+ users)
- Complex skill workflows
- Real-time API integration
- Multi-region deployment
- Full monitoring stack

**Example Setup:**
```bash
# Enterprise deployment with full monitoring
docker-compose -f docker-compose.enterprise.yml up -d
```

**Performance Expectations:**
- Response Time: 20-50ms
- Throughput: 50,000+ texts/hour
- Concurrent Users: 100+
- Uptime: 99.99%

---

## 📊 Detailed Resource Usage Breakdown

### Core Application Components

| Component | CPU Usage | Memory Usage | Storage | Dependencies |
|-----------|-----------|--------------|---------|--------------|
| **Base Detection** | 0.5-1 core | 500MB-1GB | 100MB | Presidio |
| **Plugin System** | 0.2-0.5 core | 200-500MB | 50MB | None |
| **Adaptive Skills** | 1-2 cores | 1-2GB | 500MB | Scikit-learn |
| **Resource Monitor** | 0.1 core | 100MB | 10MB | psutil |
| **Web API** | 0.5-1 core | 200-500MB | 50MB | Flask |
| **ML Models** | 1-4 cores | 2-8GB | 1-5GB | TensorFlow/PyTorch |

### Database & Storage Requirements

| Database | CPU | Memory | Storage | IOPS | Use Case |
|----------|-----|--------|---------|------|----------|
| **SQLite** | 0.1 core | 50MB | 100MB | 100 | Development |
| **PostgreSQL** | 1-2 cores | 2-4GB | 10-100GB | 1000+ | Production |
| **Redis Cache** | 0.5 core | 512MB | 1-10GB | 5000+ | Caching |
| **MongoDB** | 1-2 cores | 2-4GB | 20-200GB | 1000+ | Document Store |

### Monitoring & Observability

| Component | CPU | Memory | Storage | Network |
|-----------|-----|--------|---------|---------|
| **Prometheus** | 0.5 core | 500MB | 10-50GB | 1 Gbps |
| **Grafana** | 0.5 core | 256MB | 1-5GB | 100 Mbps |
| **Jaeger** | 1 core | 1GB | 20-100GB | 1 Gbps |
| **Sentry** | 1 core | 2GB | 50-200GB | 1 Gbps |

---

## 🚀 Performance Scaling Analysis

### Processing Throughput Estimates

| Resource Level | Texts/Hour | Avg Response Time | Concurrent Users | Batch Size |
|----------------|------------|-------------------|------------------|------------|
| **Minimum** | 500-1,000 | 100-200ms | 1-5 | 50 |
| **Recommended** | 5,000-15,000 | 50-100ms | 10-50 | 100 |
| **Enterprise** | 50,000+ | 20-50ms | 100+ | 200 |

### Scaling Formula

```
Required Cores = (Base Processing + Plugin Overhead + ML Inference) × Concurrency Factor
Required Memory = (Base Memory + Plugin Memory + Model Memory + Cache) × Safety Factor (1.5)
Required Storage = (Base Storage + Log Storage + Database Growth) × Retention Period
```

### Example Calculation

For processing 10,000 texts/hour with 20 concurrent users:

```
CPU Required = (1 core base + 0.5 core plugins + 2 cores ML) × 2 = 7 cores
Memory Required = (1GB base + 0.5GB plugins + 4GB ML + 1GB cache) × 1.5 = 9.75GB
Storage Required = (500MB base + 10GB logs/year + 20GB database) = 30.5GB
```

---

## 💡 Cloud Deployment Recommendations

### AWS Instance Recommendations

| Use Case | Instance Type | vCPUs | Memory | Monthly Cost* |
|----------|---------------|-------|---------|---------------|
| **Development** | t3.medium | 2 | 4GB | ~$30 |
| **Small Production** | m5.large | 2 | 8GB | ~$70 |
| **Medium Production** | m5.xlarge | 4 | 16GB | ~$140 |
| **Large Production** | m5.2xlarge | 8 | 32GB | ~$280 |
| **Enterprise** | m5.4xlarge | 16 | 64GB | ~$560 |

### GCP Instance Recommendations

| Use Case | Instance Type | vCPUs | Memory | Monthly Cost* |
|----------|---------------|-------|---------|---------------|
| **Development** | e2-medium | 2 | 4GB | ~$25 |
| **Small Production** | n2-standard-2 | 2 | 8GB | ~$60 |
| **Medium Production** | n2-standard-4 | 4 | 16GB | ~$120 |
| **Large Production** | n2-standard-8 | 8 | 32GB | ~$240 |
| **Enterprise** | n2-standard-16 | 16 | 64GB | ~$480 |

### Azure Instance Recommendations

| Use Case | Instance Type | vCPUs | Memory | Monthly Cost* |
|----------|---------------|-------|---------|---------------|
| **Development** | B2s | 2 | 4GB | ~$30 |
| **Small Production** | D2s_v3 | 2 | 8GB | ~$70 |
| **Medium Production** | D4s_v3 | 4 | 16GB | ~$140 |
| **Large Production** | D8s_v3 | 8 | 32GB | ~$280 |
| **Enterprise** | D16s_v3 | 16 | 64GB | ~$560 |

_*Approximate costs, may vary by region and configuration._

---

## 🔧 Resource Optimization Strategies

### 1. Adaptive Resource Management

The system automatically optimizes resource usage based on constraints:

```python
# Automatic resource adaptation
if cpu_usage > 80%:
    strategy = "sequential"          # Minimal resource usage
    max_concurrent = 1
elif cpu_usage > 60%:
    strategy = "skill_priority"      # Focus on high-impact skills
    max_concurrent = 2
elif cpu_usage > 40%:
    strategy = "batch_optimized"     # Optimized batch processing
    max_concurrent = 4
else:
    strategy = "parallel_limited"    # Maximum parallelization
    max_concurrent = 8
```

### 2. Memory Optimization Techniques

- **LRU Cache**: Intelligent caching with configurable limits
- **Plugin Unloading**: Unused plugins automatically unloaded after inactivity
- **Model Quantization**: ML models can be quantized for memory efficiency
- **Batch Processing**: Groups similar operations for memory efficiency

### 3. CPU Optimization Strategies

- **Parallel Processing**: Multi-core utilization for CPU-intensive tasks
- **Asynchronous Operations**: Non-blocking I/O for network operations
- **Smart Batching**: Dynamic batch size adjustment based on load
- **Resource Pooling**: Reuse expensive resources (connections, models)

---

## 🐳 Docker Resource Configuration

### Development Docker Compose

```yaml
# docker-compose.yml (development)
version: '3.8'
services:
  credit-card-detector:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

### Production Docker Compose

```yaml
# docker-compose.prod.yml (production)
version: '3.8'
services:
  credit-card-detector:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
  redis:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
  postgres:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
```

### Kubernetes Resource Configuration

```yaml
# k8s-deployment.yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: credit-card-detector
    resources:
      requests:
        cpu: "2"
        memory: "4Gi"
      limits:
        cpu: "8"
        memory: "16Gi"
```

---

## 📈 Monitoring Resource Usage

### Key Metrics to Monitor

```bash
# Get current resource usage
curl http://localhost:5000/resource-monitor

# Get performance statistics
curl http://localhost:5000/performance-stats

# Health check
curl http://localhost:5000/health
```

### Recommended Alerting Thresholds

| Metric | Warning | Critical | Duration |
|--------|---------|----------|----------|
| **CPU Usage** | > 70% | > 85% | 5 minutes |
| **Memory Usage** | > 75% | > 90% | 5 minutes |
| **Disk Usage** | > 80% | > 95% | 1 minute |
| **Response Time** | > 200ms | > 500ms | 1 minute |
| **Error Rate** | > 2% | > 5% | 5 minutes |
| **Queue Size** | > 100 | > 500 | 1 minute |

### Prometheus Metrics

The system exposes comprehensive metrics for monitoring:

```promql
# CPU usage rate
rate(process_cpu_seconds_total[5m])

# Memory usage
process_resident_memory_bytes

# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Processing time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

---

## 💰 Cost Optimization Tips

### 1. Right-Sizing Strategy

- **Start Small**: Begin with minimum resources, scale up based on metrics
- **Monitor Usage**: Use monitoring data to identify actual needs
- **Auto-Scaling**: Implement automatic scaling for variable workloads
- **Scheduled Scaling**: Scale down during off-peak hours

### 2. Spot Instance Usage

- **Cost Savings**: 30-70% savings compared to on-demand instances
- **Fault Tolerance**: Implement checkpointing for long-running tasks
- **Mixed Strategy**: Combine spot and on-demand for reliability
- **Capacity Buffers**: Maintain spare capacity for spot instance termination

### 3. Resource Scheduling

- **Off-Peak Processing**: Schedule heavy processing during low-cost periods
- **Queue-Based Processing**: Use message queues for batch jobs
- **Priority Allocation**: Implement priority-based resource allocation
- **Geographic Optimization**: Deploy in regions with lower costs

### 4. Storage Optimization

- **Lifecycle Policies**: Automatically delete old logs and data
- **Compression**: Compress historical data and logs
- **Tiered Storage**: Use different storage classes based on access patterns
- **Data Retention**: Implement appropriate data retention policies

---

## 🎯 Getting Started Guides

### Quick Development Setup

```bash
# Clone and set up
git clone https://github.com/claude-subagent/credit-card-detector.git
cd credit-card-detector

# Start with minimum resources (2GB RAM, 1-2 CPU cores)
docker-compose up -d

# Check resource usage
docker stats
```

### Production Deployment

```bash
# Deploy with production resources (8GB RAM, 4+ CPU cores)
docker-compose -f docker-compose.prod.yml up -d

# Setup monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# View resource dashboard
open http://localhost:3000  # Grafana
```

### Enterprise Deployment

```bash
# Full enterprise stack (16GB+ RAM, 8+ CPU cores)
docker-compose -f docker-compose.enterprise.yml up -d

# Setup load balancer
kubectl apply -f k8s-load-balancer.yaml

# Monitor at scale
open http://localhost:3000  # Grafana Dashboard
```

---

## 🔍 Troubleshooting Resource Issues

### Common Issues and Solutions

**High Memory Usage**
```bash
# Check memory usage
docker stats

# Restart services to clear memory
docker-compose restart

# Adjust memory limits in docker-compose.yml
```

**High CPU Usage**
```bash
# Check CPU usage
top

# Reduce concurrent processing
curl -X PUT http://localhost:5000/resource-constraints \
  -H "Content-Type: application/json" \
  -d '{"max_cpu_percent": 60}'
```

**Disk Space Issues**
```bash
# Clean up old logs
docker system prune -f

# Rotate log files
logrotate -f /etc/logrotate.d/credit-card-detector
```

**Performance Bottlenecks**
```bash
# Check performance metrics
curl http://localhost:5000/performance-stats

# Run benchmark
curl -X POST http://localhost:5000/benchmark-processing \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test text 1", "test text 2"], "iterations": 3}'
```

---

## 📞 Support

For resource-related questions:

- **Documentation**: [https://claude-subagent.github.io/credit-card-detector/](https://claude-subagent.github.io/credit-card-detector/)
- **Issues**: [GitHub Issues](https://github.com/claude-subagent/credit-card-detector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/claude-subagent/credit-card-detector/discussions)
- **Email**: [support@claude-subagent.com](mailto:support@claude-subagent.com)

*Last updated: November 2024*