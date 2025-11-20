# Skill Seekers + Adaptive Skills Integration

This document describes the powerful integration between **Skill Seekers** and the **Adaptive Skills System** to create a comprehensive, self-improving credit card detection platform.

## 🚀 **Overview**

The integration combines two powerful systems:

1. **Skill Seekers**: Automatically discovers and imports skills from external sources (documentation, GitHub repositories, PDFs)
2. **Adaptive Skills System**: Generates, validates, and manages custom detection skills based on performance gaps

## 🏗️ **Architecture**

### Core Components

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   External Sources  │───▶│  Skill Discovery     │───▶│  Conflict       │
│                     │    │  Engine              │    │  Resolution     │
│ • Documentation     │    │                      │    │                 │
│ • GitHub Repos      │    │ • llms.txt parsing   │    │ • Name collision│
│ • PDFs              │    │ • Quality assessment │    │ • Overlap detect│
│ • Security blogs    │    │ • Dependency extract │    │ • Auto-resolve  │
└─────────────────────┘    └──────────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   Enhanced API      │◀───│   Adaptive Skills    │◀───│  Imported       │
│                     │    │   Manager            │    │  Skills         │
│ • /scan-enhanced    │    │                      │    │                 │
│ • /discover-skills  │    │ • Skill generation   │    │ • Quality scoring│
│ • /external-sources │    │ • Performance track  │    │ • Test validation│
│ • /training-dashboard│   │ • Auto-deployment    │    │ • Metadata store │
└─────────────────────┘    └──────────────────────┘    └─────────────────┘
```

## 📋 **Key Features**

### 1. **Automatic Skill Discovery**
- **llms.txt Support**: Fast documentation parsing using standardized llms.txt files
- **Multi-Source**: Combine documentation, GitHub repos, and PDFs
- **Quality Filtering**: Only import high-quality skills (configurable threshold)
- **Async Processing**: 2-3x faster than traditional scraping

### 2. **Intelligent Conflict Resolution**
- **Name Collisions**: Automatic renaming with unique suffixes
- **Functionality Overlap**: Pattern similarity detection
- **Dependency Conflicts**: Identify and resolve dependency issues
- **Auto-Resolvable**: Many conflicts resolved automatically

### 3. **Quality Assessment**
- **Code Complexity**: Analyze function structure and patterns
- **Documentation Quality**: Check docstrings and comments
- **Example Coverage**: Validate usage examples
- **Error Handling**: Assess robustness and exception handling

### 4. **Continuous Learning**
- **Scheduled Scans**: Automatically scan external sources periodically
- **Performance Monitoring**: Track skill effectiveness over time
- **Feedback Integration**: Learn from user corrections
- **Adaptive Improvement**: System gets smarter over time

## 🛠️ **Installation & Setup**

### Prerequisites
```bash
# Install the project dependencies
pip install -r requirements.txt

# Install Skill Seekers
pip install skill-seekers
```

### Basic Setup
```python
from claude_subagent.adaptive_skills import AdaptiveSkillManager
from claude_subagent.skill_seekers_integration import SkillSeekersIntegration

# Initialize the systems
adaptive_manager = AdaptiveSkillManager(skills_dir="my_skills")
integration = SkillSeekersIntegration(adaptive_manager)

# Add external sources
integration.add_external_source(
    name="OWASP_Security",
    url="https://cheatsheetseries.owasp.org/cheatsheets/Credit_Card_Cheat_Sheet.html",
    source_type="documentation",
    description="OWASP Credit Card Security Guidelines",
    tags=["security", "credit_card", "owasp"]
)
```

## 🚀 **Quick Start**

### 1. **Start the Enhanced Server**
```bash
# Start the enhanced adaptive server
python -m claude_subagent.enhanced_adaptive_app

# Or use the original adaptive server
python -m claude_subagent.adaptive_app
```

### 2. **Setup Security Sources**
```bash
curl -X POST http://localhost:5000/setup-security-sources \
  -H "Content-Type: application/json"
```

### 3. **Discover New Skills**
```bash
curl -X POST http://localhost:5000/discover-skills \
  -H "Content-Type: application/json"
```

### 4. **Use Enhanced Detection**
```bash
curl -X POST http://localhost:5000/scan-enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Credit cards: 4111111111111111, 4242-4242-4242-4242",
    "use_all_skills": true,
    "include_external": true
  }'
```

## 📚 **API Endpoints**

### Detection
- `POST /scan` - Original credit card detection
- `POST /scan-enhanced` - Enhanced detection with all adaptive + external skills

### Skill Management
- `POST /train` - Train new skills from examples
- `GET /skills` - List all adaptive skills
- `POST /feedback` - Submit performance feedback

### Skill Seekers Integration
- `GET /external-sources` - List external skill sources
- `POST /external-sources` - Add new external source
- `POST /discover-skills` - Scan external sources for new skills
- `POST /setup-security-sources` - Setup security-focused sources
- `POST /analyze-conflicts` - Analyze skill conflicts

### Analytics & Monitoring
- `GET /health` - Comprehensive system health check
- `GET /skill-quality-report` - Quality assessment report
- `GET /training-dashboard` - Learning status dashboard
- `POST /run-example-scenarios` - Run demonstration scenarios

## 🔧 **Configuration**

### Environment Variables
```bash
# Claude API for LLM-powered skill generation
export CLAUDE_API_KEY="your-claude-api-key"
export CLAUDE_API_ENDPOINT="https://api.anthropic.com/v1/messages"

# Presidio services (optional)
export PRESIDIO_ANALYZER_URL="http://localhost:3000"
export PRESIDIO_ANONYMIZER_URL="http://localhost:3001"

# Server configuration
export SUBAGENT_PORT=5000
```

### Integration Configuration
```python
integration.config = {
    'auto_import': True,                    # Automatically import discovered skills
    'quality_threshold': 0.6,               # Minimum quality score for import
    'max_conflicts': 5,                     # Max conflicts before manual review
    'scan_interval_hours': 24               # How often to scan external sources
}
```

## 📖 **Usage Examples**

### Basic Skill Discovery
```python
import asyncio
from claude_subagent.skill_seekers_integration import SkillSeekersIntegration
from claude_subagent.adaptive_skills import AdaptiveSkillManager

async def discover_security_skills():
    adaptive_manager = AdaptiveSkillManager()
    integration = SkillSeekersIntegration(adaptive_manager)

    # Add security sources
    integration.discover_credit_card_security_skills()

    # Scan for new skills
    results = await integration.scan_external_sources()

    print(f"Discovered {results['discovered_skills']} new skills")
    print(f"Imported {results['imported_skills']} skills")

asyncio.run(discover_security_skills())
```

### Custom External Source
```python
# Add a custom documentation source
integration.add_external_source(
    name="Custom_Pattern_Library",
    url="https://docs.example.com/pattern-detection/",
    source_type="documentation",
    description="Custom pattern detection documentation",
    tags=["patterns", "custom", "detection"]
)
```

### Quality Assessment
```python
# Get quality report for all skills
response = requests.get("http://localhost:5000/skill-quality-report")
quality_report = response.json()

print(f"Total skills: {quality_report['summary']['total_skills']}")
print(f"Average quality: {quality_report['summary']['average_quality']:.2f}")

# Show top performing skills
for skill in quality_report['skills'][:5]:
    print(f"- {skill['name']}: {skill['quality_score']:.2f} ({skill['quality_grade']})")
```

### Conflict Analysis
```python
# Analyze potential conflicts
response = requests.post("http://localhost:5000/analyze-conflicts")
conflict_analysis = response.json()

print(f"Conflicts detected: {conflict_analysis['conflicts_detected']}")
for conflict in conflict_analysis['conflicts']:
    print(f"- {conflict['type']}: {conflict['description']}")
    if conflict['auto_resolvable']:
        print(f"  Auto-resolution: {conflict['resolution_suggestion']}")
```

## 🔍 **Example Scenarios**

### 1. **Security Compliance Enhancement**
```python
# Setup security-focused sources
integration.discover_credit_card_security_skills()

# Discover PCI DSS and OWASP guidelines
await integration.scan_external_sources()

# Enhanced detection now includes:
# - PCI DSS compliant validation
# - OWASP security best practices
# - Industry-standard patterns
```

### 2. **Continuous Learning Pipeline**
```python
# Schedule regular skill discovery
import schedule

def daily_skill_discovery():
    asyncio.run(integration.scan_external_sources())

schedule.every().day.at("02:00").do(daily_skill_discovery)

# Monitor and improve continuously
```

### 3. **Quality-Driven Skill Management**
```python
# Set high quality threshold for production
integration.config['quality_threshold'] = 0.8

# Only import skills with comprehensive documentation and examples
high_quality_skills = await integration.discover_from_documentation(security_source)
```

## 🧪 **Testing**

### Run Tests
```bash
# Run adaptive skills tests
python -m pytest tests/test_adaptive_skills.py -v

# Run integration tests
python -m pytest tests/test_skill_seekers_integration.py -v

# Run all tests
python -m pytest tests/ -v
```

### Example Integration Tests
```bash
# Run the example integration scenarios
python claude_subagent/skill_seekers_integration/example_integration.py

# Run via API
curl -X POST http://localhost:5000/run-example-scenarios \
  -H "Content-Type: application/json" \
  -d '{"scenario": "all"}'
```

## 📈 **Performance Monitoring**

### Dashboard Metrics
- **Total Skills**: Number of managed skills
- **External Sources**: Active external knowledge sources
- **Quality Distribution**: A-F grade distribution
- **Conflict Resolution**: Auto vs manual resolution rates
- **Discovery Success**: Import success rate by source

### Key Performance Indicators
- **Detection Accuracy**: F1 score improvement over time
- **Skill Effectiveness**: Performance of individual skills
- **System Reliability**: Uptime and error rates
- **Learning Velocity**: New skills discovered per week

## 🚧 **Troubleshooting**

### Common Issues

1. **Skill Seekers Not Available**
   ```bash
   # Install the dependency
   pip install skill-seekers
   ```

2. **Claude API Key Missing**
   ```bash
   # Set the environment variable
   export CLAUDE_API_KEY="your-api-key"
   ```

3. **Quality Threshold Too High**
   ```python
   # Lower the threshold for testing
   integration.config['quality_threshold'] = 0.3
   ```

4. **Dependency Conflicts**
   ```python
   # Analyze and resolve conflicts
   conflicts = integration.conflict_resolver.detect_conflicts(existing_skills, new_skills)
   resolutions = integration.conflict_resolver.resolve_conflicts(conflicts)
   ```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose logging for troubleshooting
```

## 🔮 **Future Enhancements**

### Planned Features
1. **Advanced Pattern Clustering**: Group similar skills automatically
2. **Skill Versioning**: Track evolution and enable rollbacks
3. **Distributed Learning**: Share improvements across instances
4. **Custom Template Engine**: Create organization-specific templates
5. **Performance Optimization**: Skill caching and lazy loading

### Roadmap
- **Q1 2025**: Advanced conflict resolution algorithms
- **Q2 2025**: Multi-tenant skill management
- **Q3 2025**: GPU-accelerated pattern matching
- **Q4 2025**: Enterprise governance features

## 🤝 **Contributing**

To contribute to the integration:

1. **Fork the repository**
2. **Create a feature branch**
3. **Add comprehensive tests**
4. **Document new features**
5. **Submit pull request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings with examples
- Write tests for new functionality
- Update documentation

## 📄 **License**

This integration follows the same MIT license as the parent project. See [LICENSE.md](LICENSE.md) for details.

## 🙋‍♂️ **Support**

For questions or issues:
1. Check the [troubleshooting guide](#troubleshooting)
2. Review the [API documentation](#api-endpoints)
3. Run the [example scenarios](#example-scenarios)
4. Open an issue in the project repository

---

**The Skill Seekers + Adaptive Skills Integration transforms your credit card detection system from static rules into a dynamic, self-improving platform that continuously learns from external knowledge sources.** 🚀