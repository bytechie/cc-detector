# 🧪 Test Suite

This directory contains the complete test suite for the Credit Card Detector project.

## 📁 Test Structure

```
tests/
├── README.md                              # This file
├── conftest.py                            # pytest configuration and fixtures
├── load_testing/                          # Load testing utilities
│   └── generate_load_test.py              # Load testing script
├── test_adaptive_skills.py                # Adaptive skills tests
├── test_credit_card_detection.py          # Comprehensive detection tests
├── test_detector.py                       # Core detector functionality
├── test_health.py                         # Health check tests
├── test_skill_seekers_integration.py     # Integration tests
└── test_subagent.py                       # Subagent functionality tests
```

## 🚀 Running Tests

### **Run All Tests**
```bash
pytest tests/
```

### **Run Specific Test Categories**
```bash
# Core detection tests
pytest tests/test_credit_card_detection.py tests/test_detector.py

# Integration tests
pytest tests/test_skill_seekers_integration.py

# Adaptive skills tests
pytest tests/test_adaptive_skills.py

# Health check tests
pytest tests/test_health.py
```

### **Run with Coverage**
```bash
pytest --cov=skills tests/
```

### **Run with Verbose Output**
```bash
pytest -v tests/
```

## 📊 Test Categories

### **Core Functionality Tests**
- `test_detector.py` - Basic credit card detection
- `test_credit_card_detection.py` - Comprehensive detection scenarios
- `test_health.py` - API health checks

### **Advanced Features Tests**
- `test_adaptive_skills.py` - Adaptive learning capabilities
- `test_skill_seekers_integration.py` - External integrations

### **System Tests**
- `test_subagent.py` - Subagent system functionality

### **Performance Tests**
- `load_testing/generate_load_test.py` - Load testing utilities

## 🔧 Test Configuration

### **Environment Setup**
Tests use the configuration defined in `conftest.py`:
- Test fixtures for sample data
- Mock configurations for external services
- Test database setup and teardown

### **Test Data**
Sample credit card numbers and test text are provided via fixtures:
- Valid card numbers (Visa, Mastercard, Amex, etc.)
- Invalid card numbers for validation testing
- Various text formats and edge cases

## 📋 Test Coverage

### **Detection Features**
- ✅ Credit card number detection
- ✅ Luhn algorithm validation
- ✅ Multiple card formats (spaces, dashes, plain)
- ✅ Edge cases and error handling
- ✅ Performance and load testing

### **Integration Features**
- ✅ Presidio framework integration
- ✅ Skill Seekers platform integration
- ✅ Adaptive skills system
- ✅ External API connections

### **System Features**
- ✅ API health checks
- ✅ Metrics collection
- ✅ Error handling and logging
- ✅ Configuration management

## 🐛 Debugging Tests

### **Run with Debugging**
```bash
pytest -s -v tests/test_specific_file.py::test_function
```

### **Stop on First Failure**
```bash
pytest -x tests/
```

### **Run Specific Test Function**
```bash
pytest tests/test_credit_card_detection.py::test_basic_detection
```

## 📈 Performance Testing

Load testing is available in the `load_testing/` subdirectory:

```bash
# Run comprehensive load test
python tests/load_testing/generate_load_test.py

# Load test with specific parameters
python tests/load_testing/generate_load_test.py --users 10 --duration 60
```

## 🔄 Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Fast execution for quick feedback
- Comprehensive coverage for reliability
- Clear output for debugging
- Proper exit codes for automation

## 📝 Adding New Tests

1. **Naming Convention**: `test_*.py` for test files
2. **Test Functions**: `test_*()` for individual tests
3. **Fixtures**: Use fixtures in `conftest.py` for common setup
4. **Documentation**: Add docstrings explaining test purpose
5. ** assertions**: Use descriptive assertion messages

## 🔍 Test Data Privacy

All test data uses **test credit card numbers** that are safe for testing:
- Visa: `4111111111111111`
- Mastercard: `5555555555554444`
- Amex: `378282246310005`

These are industry-standard test numbers that will not work for real transactions.