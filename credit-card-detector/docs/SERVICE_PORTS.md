# Service Port Configuration Documentation

## 🔧 Complete Port Mapping

This document provides the authoritative source of truth for all service ports in the Credit Card Detector project to prevent future conflicts.

### **Production Service Ports**

| Service | Internal Port | External Port | Environment Variable | Purpose | Status |
|---------|---------------|---------------|---------------------|---------|--------|
| **Flask API** | 5000 | 5000 | `DETECTOR_PORT` | Main REST API | ✅ Stable |
| **Presidio Analyzer** | 3000 | 3000 | `PRESIDIO_ANALYZER_PORT` | Text analysis service | ✅ Stable |
| **Presidio Anonymizer** | 3001 | 3001 | `PRESIDIO_ANONYMIZER_PORT` | Data anonymization service | ✅ Stable |
| **Grafana** | 3000 | **3002** | `GRAFANA_PORT` | Monitoring dashboards | ✅ **CONFLICT RESOLVED** |
| **Prometheus** | 9090 | 9090 | `PROMETHEUS_PORT` | Metrics collection | ✅ Stable |
| **PostgreSQL** | 5432 | 5432 | `POSTGRES_PORT` | Primary database | ✅ Stable |
| **Redis** | 6379 | 6379 | `REDIS_PORT` | Caching layer | ✅ Stable |
| **Nginx** | 80 | 80 | `NGINX_PORT` | Reverse proxy | ✅ Stable |
| **Nginx SSL** | 443 | 443 | `NGINX_SSL_PORT` | HTTPS proxy | ✅ Stable |

### **Development & Testing Ports**

| Service | Port | Environment Variable | Purpose |
|---------|------|---------------------|---------|
| **Test Flask API** | 5001 | `TEST_DETECTOR_PORT` | API testing instance |
| **Development API** | 8000 | `DEV_DETECTOR_PORT` | Development debugging |
| **Mock Services** | 9000-9099 | Various | Testing mocks |

### **Reserved Port Ranges**

To prevent conflicts, these port ranges are reserved:

| Range | Purpose | Status |
|-------|---------|--------|
| **3000-3009** | Presidio Services & Grafana | ⚠️ **CONFLICT ZONE** |
| **5000-5009** | Flask API Instances | ✅ Reserved |
| **9000-9099** | Monitoring Services | ✅ Reserved |
| **9100-9199** | Custom Metrics | ✅ Reserved |
| **8000-8099** | Development Services | ✅ Reserved |

## 🚨 **CRITICAL CONFLICT RESOLUTION**

### **Historical Port Conflict (RESOLVED)**
```
CONFLICT: Grafana (3000) vs Presidio Analyzer (3000)
SOLUTION: Moved Grafana to port 3002
STATUS: ✅ RESOLVED
```

### **Why Port 3002 for Grafana?**
- 3002 is the standard alternative Grafana port
- Maintains proximity to 3000 series (monitoring stack)
- No conflicts with existing services
- Easily memorable pattern: 3000 (Presidio), 3001 (Presidio), 3002 (Grafana)

## 🔄 **Port Configuration Hierarchy**

### **1. Environment Variables (Highest Priority)**
```bash
export GRAFANA_PORT=3002
export PRESIDIO_ANALYZER_PORT=3000
export PRESIDIO_ANONYMIZER_PORT=3001
export DETECTOR_PORT=5000
```

### **2. Docker Compose Defaults**
```yaml
# docker-compose.yml
ports:
  - "${GRAFANA_PORT:-3002}:3000"  # Grafana
  - "${PRESIDIO_ANALYZER_PORT:-3000}:3000"  # Analyzer
  - "${PRESIDIO_ANONYMIZER_PORT:-3001}:3001"  # Anonymizer
```

### **3. Configuration Files**
```yaml
# config/app-config.yaml
presidio:
  analyzer_url: "http://presidio-analyzer:3000"
  anonymizer_url: "http://presidio-anonymizer:3001"
```

### **4. start.sh Script Automation**
```bash
# Automatically set by start.sh
export GRAFANA_PORT=3002
export PRESIDIO_ANALYZER_PORT=3000
export PRESIDIO_ANONYMIZER_PORT=3001
```

## 🛡️ **Port Conflict Prevention Guidelines**

### **Before Adding New Services:**
1. **Check this document first** - Ensure port is not reserved
2. **Use environment variables** - Make ports configurable
3. **Add to this document** - Update the port mapping
4. **Test port availability** - Verify no conflicts

### **Port Assignment Rules:**
1. **Never use 3000** - Reserved for Presidio Analyzer
2. **Never use 3001** - Reserved for Presidio Anonymizer
3. **Use 3002+ for monitoring** - Grafana and monitoring tools
4. **Use 5000+ for API services** - Flask and API instances
5. **Use 8000+ for development** - Development and testing
6. **Use 9000+ for infrastructure** - Monitoring and system services

### **Validation Commands:**
```bash
# Check port usage
netstat -tulpn | grep -E "(3000|3001|3002|5000|9090|5432|6379)"

# Check Docker port mappings
docker-compose ps

# Test service availability
curl -f http://localhost:3000/health  # Presidio Analyzer
curl -f http://localhost:3001/health  # Presidio Anonymizer
curl -f http://localhost:3002/api/health  # Grafana
curl -f http://localhost:5000/health  # Flask API
curl -f http://localhost:9090/api/v1/status/config  # Prometheus
```

## 📋 **Service Startup Sequence**

### **Production Mode:**
1. **Infrastructure First:**
   - PostgreSQL (5432)
   - Redis (6379)

2. **AI Services:**
   - Presidio Analyzer (3000)
   - Presidio Anonymizer (3001)

3. **Application:**
   - Flask API (5000)

4. **Monitoring:**
   - Prometheus (9090)
   - Grafana (3002)

### **Docker Dependencies:**
```yaml
# Services depend on these ports being available
depends_on:
  - postgres      # 5432
  - redis         # 6379
  - presidio-analyzer     # 3000
  - presidio-anonymizer   # 3001
```

## 🔍 **Troubleshooting Port Conflicts**

### **Symptoms:**
- Services fail to start
- "Port already in use" errors
- Health checks failing
- Docker container restart loops

### **Diagnosis:**
```bash
# Find process using port
lsof -i :3000
lsof -i :3002

# Check Docker containers
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Kill conflicting processes
sudo fuser -k 3000/tcp
sudo fuser -k 3002/tcp
```

### **Resolution:**
1. **Stop conflicting services**: `./start.sh stop`
2. **Check port usage**: `lsof -i :3002`
3. **Kill processes**: `sudo fuser -k 3002/tcp`
4. **Restart services**: `./start.sh start production`

## 📝 **Change Management**

### **When Modifying Ports:**
1. **Update this document first**
2. **Update all environment files**
3. **Update Docker Compose configurations**
4. **Update documentation**
5. **Update start.sh script**
6. **Test all service modes**
7. **Verify monitoring stack**
8. **Update CLAUDE.md**

### **Files Requiring Updates:**
- `docs/SERVICE_PORTS.md` ⭐ (This file)
- `CLAUDE.md`
- `.env.example`
- `docker-compose.yml`
- `start.sh`
- `monitoring/prometheus/prometheus.yml`
- `config/environments/*.env`
- Service documentation files

---

**🎯 RULE: Always check this document before assigning ports to prevent conflicts!**