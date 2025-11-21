# 🚀 Quick Start Tutorial

Get up and running with the Credit Card Detector in under 5 minutes!

## ⚡ Lightning Fast Start

### 1. Clone and Start (Recommended)

```bash
# Clone the repository
git clone https://github.com/bytechie/cc-detector.git
cd credit-card-detector

# Start with automatic testing (one command!)
./start.sh start basic
```

That's it! The system will:
- ✅ Check prerequisites
- ✅ Start the application
- ✅ Run automatic tests
- ✅ Show you how to use it

### 2. Test It Works

```bash
# Test credit card detection
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "My Visa card is 4111111111111111"}'
```

**Expected Response:**
```json
{
  "detections": [
    {
      "number": "4111111111111111",
      "valid": true,
      "start": 17,
      "end": 33
    }
  ],
  "redacted": "My Visa card is [REDACTED]"
}
```

🎉 **You're done! The detector is working!**

## 🎯 Different Ways to Start

### For Development
```bash
./start.sh start basic          # Fast startup, basic features
```

### For Production
```bash
./start.sh start production     # Full monitoring, comprehensive testing
```

### For Enterprise
```bash
./start.sh start enterprise     # All features, maximum testing
```

### Custom Port
```bash
./start.sh start basic 8080     # Use port 8080
```

### Process Management
```bash
./start.sh stop                 # Stop all instances
./start.sh restart              # Restart with same mode
./start.sh status               # Check running status
./stop.sh                       # Quick stop
```

## 🔧 What Just Happened?

When you ran `./start.sh start basic`, the system automatically:

1. **Checked** if you have the right dependencies
2. **Started** the credit card detector application
3. **Ran tests** to make sure everything works
4. **Displayed** service information and usage examples

## 📊 Available Endpoints

After startup, you have access to:

- **Main API**: `http://localhost:5000/scan`
- **Health Check**: `http://localhost:5000/health`
- **Service Info**: `http://localhost:5000/`
- **Metrics** (if in production/enterprise mode): `http://localhost:5000/metrics`

## 🧪 Quick Testing Examples

### Different Card Formats
```bash
# Spaces
curl -X POST http://localhost:5000/scan \
  -d '{"text": "Card: 4111 1111 1111 1111"}' \
  -H "Content-Type: application/json"

# Dashes
curl -X POST http://localhost:5000/scan \
  -d '{"text": "Card: 4111-1111-1111-1111"}' \
  -H "Content-Type: application/json"

# Multiple cards
curl -X POST http://localhost:5000/scan \
  -d '{"text": "Visa: 4111111111111111, MC: 5555555555554444"}' \
  -H "Content-Type: application/json"
```

### Health Check
```bash
curl http://localhost:5000/health
```

## 🐳 Docker Alternative

If you prefer Docker:

```bash
# Quick start with Docker
docker-compose up -d

# Test it
curl http://localhost:5000/health
```

## 📚 Need More?

- **Complete Tutorial**: See [TUTORIAL.md](TUTORIAL.md) for comprehensive guide
- **Startup Options**: See [STARTUP_GUIDE.md](../STARTUP_GUIDE.md) for all startup options
- **Main Documentation**: See [../README.md](../README.md) for full project documentation

## 🆘 Troubleshooting

### Port Already in Use?
```bash
# Use a different port
./start.sh start basic 8080

# Or kill existing process
lsof -ti:5000 | xargs kill
```

### Dependencies Missing?
```bash
# Install manually
pip install -r requirements.txt

# Or use the startup script (it handles this automatically)
./start.sh start basic
```

### Tests Failed?
```bash
# Check what failed
./run-mode-tests.sh basic

# Usually just needs more time for services to start
```

## 🎯 What's Next?

### 1. Try Production Mode
```bash
./start.sh start production
```
This includes monitoring, dashboards, and comprehensive testing.

### 2. Use Python SDK
```python
from skills.core.detect_credit_cards import detect

text = "My card is 4111111111111111"
detections = detect(text)
print(f"Found {len(detections)} cards!")
```

### 3. Explore Monitoring (Production Mode)
- **Grafana Dashboard**: http://localhost:3002 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Application Metrics**: http://localhost:5000/metrics

---

## 🎉 You're Ready!

**In under 5 minutes, you have:**
✅ A working credit card detector
✅ Automatic testing and validation
✅ Multiple deployment options
✅ Production-ready monitoring

**🚀 Start building your applications with reliable credit card detection!**

---

**Need help?** Check the [complete tutorial](TUTORIAL.md) or [open an issue](https://github.com/bytechie/cc-detector/issues).