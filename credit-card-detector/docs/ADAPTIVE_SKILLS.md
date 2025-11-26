# Adaptive Skill System

This document describes the adaptive skill system that automatically creates, validates, and deploys Claude Skills to adapt to new patterns and requirements.

## Overview

The adaptive skill system is a meta-learning framework that can:

1. **Analyze Performance Gaps**: Identify patterns where current skills fail to detect expected results
2. **Generate New Skills**: Create new detection skills using templates or LLM-powered generation
3. **Validate Skills**: Test generated skills against expected outputs
4. **Deploy Skills**: Automatically integrate successful skills into the detection pipeline
5. **Track Performance**: Monitor skill effectiveness over time

## Architecture

### Core Components

- **AdaptiveSkillManager**: Main orchestrator that manages the entire adaptive pipeline
- **SkillTemplate**: Abstract base class for template-based skill generation
- **LLMSkillGenerator**: Uses Claude to generate skills for complex patterns
- **SkillPerformance**: Tracks metrics (precision, recall, F1) for each skill
- **SkillGap**: Represents detected gaps in current capabilities

### Skill Types

1. **Template-Based Skills**: Generated from predefined templates for common patterns
2. **LLM-Generated Skills**: Created by Claude for novel or complex scenarios
3. **Hybrid Skills**: Combination of template structure with LLM customization

## Quick Start

### 1. Basic Usage

```python
from claude_subagent.adaptive_skills import AdaptiveSkillManager

# Initialize the manager
manager = AdaptiveSkillManager(skills_dir="my_skills")

# Analyze and adapt to new patterns
test_data = [
    {"input": "New card format: 4242-4242-4242-4242"},
    {"input": "European style: 4242 4242 4242 4242"}
]

expected_outputs = [
    [{"raw": "4242-4242-4242-4242", "start": 17, "end": 36}],
    [{"raw": "4242 4242 4242 4242", "start": 14, "end": 33}]
]

new_skills = manager.analyze_and_adapt(test_data, expected_outputs)
print(f"Generated {len(new_skills)} new skills")
```

### 2. Using the Adaptive API

```bash
# Start the adaptive subagent
python -m claude_subagent.adaptive_app

# Train new skills
curl -X POST http://localhost:5000/train \
  -H "Content-Type: application/json" \
  -d '{
    "examples": [
      {
        "input": "Card: 4242-4242-4242-4242",
        "expected_detections": [
          {"raw": "4242-4242-4242-4242", "start": 6, "end": 25}
        ]
      }
    ],
    "description": "Hyphen-separated credit cards"
  }'

# Use enhanced detection
curl -X POST http://localhost:5000/scan-adaptive \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Multiple cards: 4111111111111111 and 4242-4242-4242-4242",
    "use_all_skills": true
  }'
```

### 3. Running Examples

```bash
# Run the example usage script
python claude_subagent/adaptive_skills/example_usage.py

# Run tests
python -m pytest tests/test_adaptive_skills.py -v
```

## API Endpoints

### Detection Endpoints

- `POST /scan` - Original credit card detection
- `POST /scan-adaptive` - Enhanced detection with all adaptive skills

### Training Endpoints

- `POST /train` - Generate new skills from examples
- `POST /analyze-gaps` - Identify detection gaps without creating skills

### Management Endpoints

- `GET /health` - System health and skill status
- `GET /skills` - List all adaptive skills with metadata
- `GET /skill-performance` - Detailed performance metrics
- `POST /feedback` - Submit feedback to improve skills

## Skill Development

### Creating Custom Templates

```python
from claude_subagent.adaptive_skills import SkillTemplate

class CustomDetectionTemplate(SkillTemplate):
    def generate_code(self, parameters):
        pattern = parameters.get('pattern', r'custom_pattern')
        return f'''
def detect(text):
    import re
    pattern = re.compile(r'{pattern}')
    return [{{"raw": m.group(0), "start": m.start(), "end": m.end()}}
            for m in pattern.finditer(text)]
'''

    def get_test_cases(self, parameters):
        return [
            {"input": "test with custom pattern", "expected_count": 1}
        ]
```

### Manual Gap Creation

```python
from claude_subagent.adaptive_skills import SkillGap

gap = SkillGap(
    pattern="masked_cards",
    description="Detection of masked credit card numbers",
    examples=["****-****-****-4242", "Card ending in 1234"],
    expected_output=[{"raw": "****-****-****-4242", "type": "masked"}],
    severity=0.8
)

skill = manager.generate_skill_for_gap(gap)
if manager.test_and_deploy_skill(skill):
    print(f"Deployed new skill: {skill.name}")
```

## Performance Tracking

The system automatically tracks:

- **True Positives**: Correct detections
- **False Positives**: Incorrect detections (false alarms)
- **False Negatives**: Missed detections
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1 Score**: 2 × (Precision × Recall) / (Precision + Recall)

### Feedback Integration

```bash
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Card: 4242424242424242",
    "skill_name": "detect_credit_card_1234",
    "feedback_type": "false_negative",
    "expected_detections": [
      {"raw": "4242424242424242", "start": 6, "end": 22}
    ]
  }'
```

## Configuration

### Environment Variables

- `CLAUDE_API_KEY`: API key for LLM-powered skill generation
- `CLAUDE_API_ENDPOINT`: Custom Claude API endpoint
- `SUBAGENT_PORT`: Port for the adaptive subagent (default: 5000)
- `PRESIDIO_ANALYZER_URL`: Presidio analyzer service URL
- `PRESIDIO_ANONYMIZER_URL`: Presidio anonymizer service URL

### Skill Directory Structure

```
adaptive_skills_generated/
├── detect_credit_card_1234.py
├── detect_custom_pattern_5678.py
└── detect_masked_cards_9012.py
```

## Best Practices

### 1. Quality Training Data

Provide clear, diverse examples when training new skills:

```json
{
  "examples": [
    {
      "input": "Visa: 4111111111111111",
      "expected_detections": [
        {"raw": "4111111111111111", "start": 6, "end": 22, "valid": true}
      ]
    }
  ]
}
```

### 2. Regular Performance Monitoring

Check skill performance regularly:

```python
for skill_name in manager.list_skills():
    perf = manager.get_skill_performance(skill_name)
    if perf.f1_score < 0.8:
        print(f"Skill {skill_name} needs improvement (F1: {perf.f1_score:.3f})")
```

### 3. Incremental Improvement

Start with template-based skills, then use LLM generation for complex cases:

```python
# Try template first
if simple_pattern:
    skill = template.generate_code(params)
# Fall back to LLM for complex cases
else:
    skill = llm_generator.generate_skill(gap, context)
```

### 4. Validation and Testing

Always validate generated skills before deployment:

```python
if manager.validate_skill_syntax(skill.code):
    if manager.run_skill_tests(skill):
        manager.deploy_skill(skill)
    else:
        print("Skill failed tests")
else:
    print("Skill has syntax errors")
```

## Troubleshooting

### Common Issues

1. **Skill Generation Fails**
   - Check Claude API key is set
   - Verify network connectivity
   - Review example data quality

2. **Poor Performance**
   - Provide more diverse training examples
   - Check for overlapping patterns
   - Consider skill merging or deduplication

3. **Memory Issues**
   - Limit number of loaded skills
   - Implement skill pruning based on performance
   - Use skill caching strategies

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

Planned improvements to the adaptive skill system:

1. **Skill Merging**: Automatically combine similar skills
2. **Pattern Clustering**: Group related detection patterns
3. **Active Learning**: Request human feedback for uncertain cases
4. **Skill Versioning**: Track skill evolution and rollback capabilities
5. **Distributed Learning**: Share improvements across multiple instances

## Contributing

To contribute new skill templates or improvements:

1. Fork the repository
2. Create a new branch for your feature
3. Add tests for new functionality
4. Submit a pull request with documentation

For questions or issues, please open an issue in the project repository.