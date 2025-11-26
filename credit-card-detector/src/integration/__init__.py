"""
Integration Skills Module

This module provides integration capabilities with external systems and services.
It contains specialized integrations for various platforms and frameworks.

## Structure:
- skill_seekers_integration: Integration with Skill Seekers platform
"""

# Import Skill Seekers Integration
try:
    from .skill_seekers_integration import main as skill_seekers_main
    from .skill_seekers_integration.example_integration import (
        SkillSeekersIntegration,
        ConflictResolutionEngine,
        PerformanceMonitor
    )
    skill_seekers_available = True
except ImportError as e:
    print(f"Warning: Skill Seekers Integration not available: {e}")
    skill_seekers_main = None
    skill_seekers_available = False

# Export main integration components
__all__ = [
    'skill_seekers_main',
    'skill_seekers_available',
]

# Add specific classes if available
if skill_seekers_available:
    __all__.extend([
        'SkillSeekersIntegration',
        'ConflictResolutionEngine',
        'PerformanceMonitor'
    ])

# Version info
__version__ = '1.0.0'
__description__ = 'Integration Skills - External system integrations'