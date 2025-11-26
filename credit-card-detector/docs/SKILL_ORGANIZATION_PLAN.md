# 🗂️ Claude Skills Organization Plan

## Current Issues
- Duplicate skill directories in multiple locations
- Empty directories causing confusion
- Inconsistent naming conventions
- Skills scattered across different locations

## Recommended Directory Structure

```
credit-card-detector/
├── skills/                           # 🎯 Main skills directory
│   ├── core/                        # Core credit card detection skills
│   │   ├── __init__.py
│   │   ├── detect_credit_cards.py
│   │   ├── detect_credit_cards_presidio.py
│   │   ├── redact_credit_cards.py
│   │   └── redact_credit_cards_presidio.py
│   ├── adaptive/                    # Advanced adaptive skills
│   │   ├── __init__.py
│   │   └── adaptive_skills.py
│   ├── integration/                 # Integration with external systems
│   │   ├── __init__.py
│   │   └── skill_seekers_integration.py
│   ├── security/                    # Security-focused skills
│   │   ├── __init__.py
│   │   └── security_skills.py
│   └── generated/                   # Auto-generated skills
│       ├── __init__.py
│       └── README.md
├── claude_subagent/
│   └── main.py                      # Main orchestrator
└── docs/
    ├── SKILLS_REFERENCE.md          # Skills documentation
    └── SKILL_DEVELOPMENT.md         # Guide for creating skills
```

## Migration Steps

### Phase 1: Cleanup Empty Directories
```bash
# Remove empty duplicate directories
rmdir manual_skills/ generated_skills/ integration_skills/ security_skills/
```

### Phase 2: Consolidate Skills
```bash
# Move all skills to unified structure
mkdir -p skills/{core,adaptive,integration,security,generated}
mv claude_subagent/skills/* skills/core/
mv claude_subagent/adaptive_skills/* skills/adaptive/
mv claude_subagent/skill_seekers_integration/* skills/integration/
```

### Phase 3: Update Imports
```python
# Old imports
from claude_subagent.skills.detect_credit_cards import detect_credit_cards
from claude_subagent.adaptive_skills import adaptive_skills

# New imports
from skills.core.detect_credit_cards import detect_credit_cards
from skills.adaptive.adaptive_skills import adaptive_skills
```

### Phase 4: Create Skill Registry
```python
# skills/registry.py
class SkillRegistry:
    CORE_SKILLS = [
        'detect_credit_cards',
        'detect_credit_cards_presidio',
        'redact_credit_cards',
        'redact_credit_cards_presidio'
    ]

    ADAPTIVE_SKILLS = [
        'adaptive_skills'
    ]

    INTEGRATION_SKILLS = [
        'skill_seekers_integration'
    ]
```

## Benefits
✅ Clean, organized structure
✅ Clear separation of concerns
✅ Easy to find and maintain skills
✅ Simplified imports
✅ Better for new contributors
✅ Scalable for future skills

## Implementation Priority
1. **High**: Remove empty directories
2. **High**: Consolidate existing skills
3. **Medium**: Update imports and documentation
4. **Low**: Create registry and advanced features