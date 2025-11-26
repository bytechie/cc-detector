# Configuration Guide

This directory contains all configuration files for the Credit Card Detector project.

## 📁 **Configuration Structure**

```
config/
├── README.md                   # This file
├── app-config.yaml            # Main application configuration
├── resource-profiles.yaml     # Resource management profiles
└── environments/               # Environment-specific configurations
    ├── development.env         # Development environment settings
    ├── staging.env            # Staging environment settings
    └── production.env         # Production environment settings
```

## 🚀 **Quick Configuration**

### **Development Setup**
```bash
# Copy development environment
cp config/environments/development.env .env.local

# Start in development mode
./start.sh start basic
```

### **Production Setup**
```bash
# Copy production environment
cp config/environments/production.env .env.local

# Start in production mode
./start.sh start production
```

## 🔧 **Configuration Files**

### **app-config.yaml**
Main application configuration including:
- Server settings (host, port, debug)
- Logging configuration
- Feature flags
- Security settings

### **resource-profiles.yaml**
Resource management profiles including:
- CPU and memory limits
- Performance optimization settings
- Resource scaling parameters

### **environments/*.env**
Environment-specific variables:
- Database connection strings
- API keys and secrets
- External service URLs
- Environment-specific feature flags

## 🐳 **Docker Configuration**

The project uses multiple Docker Compose files for different environments:

- **docker-compose.yml** - Basic development setup
- **docker-compose.local.yml** - Local development with monitoring
- **docker-compose.testing.yml** - Testing environment
- **docker-compose.production.yml** - Production deployment

### **Usage**
```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.production.yml up

# Testing
docker-compose -f docker-compose.testing.yml up
```

## 🎯 **Configuration Priority**

1. **Environment Variables** (highest priority)
2. **.env.local file**
3. **Environment-specific .env files**
4. **YAML configuration files**
5. **Default values** (lowest priority)

## 📖 **Getting Help**

- See [../docs/quickstart.md](../docs/quickstart.md) for setup instructions
- Check [../examples/](../examples/) for configuration examples
- Review [../README.md](../README.md) for general project information