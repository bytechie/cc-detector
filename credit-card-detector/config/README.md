# Credit Card Detector - Configuration

This directory contains all configuration files for the Credit Card Detector system. The configuration has been reorganized to provide better separation of concerns and environment-specific settings.

## 📁 **Configuration Structure**

```
config/
├── README.md                           # This file
├── app-config.yaml                     # Main application configuration
├── resource-profiles.yaml             # Resource optimization profiles
└── environments/                       # Environment-specific configurations
    ├── development.env                 # Development environment
    ├── staging.env                     # Staging environment
    ├── production.env                  # Production environment
    └── .env.example                    # Environment variable template
```

## 🔧 **Configuration Files**

### **1. `app-config.yaml` - Main Application Configuration**

This is the primary configuration file that defines:
- Global application settings
- Mode-specific configurations (basic, metrics, adaptive, resource_aware, full)
- Environment-specific overrides
- Performance tuning settings
- Security configurations
- Monitoring and alerting settings

### **2. `resource-profiles.yaml` - Resource Management**

Defines resource requirements and optimization strategies for different deployment sizes:
- **Development**: Lightweight settings for local development
- **Production**: Medium-scale deployment with optimization
- **Enterprise**: Large-scale deployment with advanced features

### **3. Environment Files**

Each environment has its own `.env` file with specific settings:

#### **Development Environment** (`environments/development.env`)
- Debug mode enabled
- Local service URLs
- SQLite database
- Verbose logging
- Basic feature set

#### **Staging Environment** (`environments/staging.env`)
- Production-like settings
- Staging service URLs
- PostgreSQL database
- Info-level logging
- Metrics and adaptive features enabled

#### **Production Environment** (`environments/production.env`)
- Full production configuration
- Production service URLs
- High-performance settings
- Security hardening
- All monitoring features enabled

## 🚀 **Usage Examples**

### **Running in Different Modes**

```bash
# Basic mode - simple detection and redaction
python app.py --mode basic

# Metrics mode - with Prometheus monitoring
python app.py --mode metrics

# Adaptive mode - with AI-powered skills
python app.py --mode adaptive

# Resource-aware mode - with system monitoring
python app.py --mode resource_aware

# Full mode - all features enabled
python app.py --mode full
```

### **Using Environment Configuration**

```bash
# Load environment-specific configuration
export ENV=production
python app.py --config config/app-config.yaml

# Override environment variables
export APP_MODE=metrics
export LOG_LEVEL=DEBUG
python app.py
```

### **Development Setup**

```bash
# Use development environment
cp config/environments/development.env .env
python app.py --mode basic --debug
```

### **Production Deployment**

```bash
# Use production environment
cp config/environments/production.env .env
# Set required environment variables
export POSTGRES_PASSWORD=your-secure-password
export PRODUCTION_SECRET_KEY=your-secret-key
export PRODUCTION_CLAUDE_API_KEY=your-claude-key
python app.py --mode full
```

## ⚙️ **Configuration Hierarchy**

Configuration is applied in the following order (later overrides earlier):

1. **Default values** - Built-in application defaults
2. **`app-config.yaml`** - Main configuration file
3. **Environment files** - Environment-specific settings
4. **Environment variables** - Runtime overrides
5. **Command-line arguments** - Highest priority

## 🔒 **Security Configuration**

### **Environment Variables**

Security-sensitive values should be set as environment variables:

```bash
# Database credentials
export POSTGRES_PASSWORD=secure-password

# Application secrets
export SECRET_KEY=your-secret-key
export CLAUDE_API_KEY=your-claude-api-key

# External service URLs
export PRESIDIO_ANALYZER_URL=http://presidio-analyzer:3000
export PRESIDIO_ANONYMIZER_URL=http://presidio-anonymizer:3001
```

### **Production Security**

Production configuration includes:
- HTTPS enforcement
- Security headers
- Rate limiting
- CORS restrictions
- Input validation

## 📊 **Resource Profiles**

### **Development Profile**
- **CPU**: 2 cores, 80% max
- **Memory**: 4GB, 75% max
- **Features**: Basic detection only
- **Concurrency**: Sequential processing

### **Production Profile**
- **CPU**: 6 cores, 75% max
- **Memory**: 12GB, 80% max
- **Features**: All features enabled
- **Concurrency**: Batch optimized

### **Enterprise Profile**
- **CPU**: 16 cores, 85% max
- **Memory**: 32GB, 85% max
- **Features**: Full feature set + distributed processing
- **Concurrency**: Parallel processing with auto-scaling

## 🎯 **Mode-Specific Features**

### **Basic Mode**
- Credit card detection and redaction
- Basic health checks
- Simple API endpoints

### **Metrics Mode**
- All basic features
- Prometheus metrics
- Performance monitoring
- Request tracking

### **Adaptive Mode**
- All basic features
- AI-powered skill system
- Dynamic skill generation
- Performance optimization

### **Resource-Aware Mode**
- All basic features
- System resource monitoring
- Auto-scaling based on load
- Performance thresholds

### **Full Mode**
- All features from all modes
- Comprehensive monitoring
- Advanced optimization
- Production-ready configuration

## 🔍 **Monitoring Configuration**

### **Prometheus Metrics**
- Request counters and duration
- Detection performance metrics
- System resource usage
- Error rates and alerts

### **Health Checks**
- Application health status
- Dependency health checks
- Resource utilization
- Performance metrics

### **Alerting**
- CPU/Memory thresholds
- Response time alerts
- Error rate monitoring
- Resource exhaustion warnings

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Configuration not loading**:
   - Check file permissions
   - Verify YAML syntax
   - Check environment variable substitution

2. **Environment variables not working**:
   - Ensure `.env` file is in correct location
   - Check variable naming conventions
   - Verify export syntax

3. **Resource limits exceeded**:
   - Check resource profile settings
   - Monitor system usage
   - Adjust limits in configuration

4. **Services not connecting**:
   - Verify service URLs
   - Check network connectivity
   - Confirm service health status

### **Debug Mode**

Enable debug mode for detailed logging:

```bash
export LOG_LEVEL=DEBUG
python app.py --debug
```

## 📚 **Additional Resources**

- [Application Modes](../docs/configuration/modes.md)
- [Resource Management](../docs/configuration/resources.md)
- [Security Configuration](../docs/configuration/security.md)
- [Monitoring Setup](../docs/configuration/monitoring.md)
- [Deployment Guide](../docs/deployment/)

---

**💡 Tip**: Always test configuration changes in development before applying to production. Use environment-specific configuration files to avoid exposing sensitive data.