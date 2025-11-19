"""
Skill Seekers Integration

This module provides integration with the Skill Seekers platform for discovering,
importing, and managing external skills to enhance the credit card detection system.

Main Components:
- SkillSeekersIntegration: Main integration class
- ConflictResolutionEngine: Handles skill conflicts
- SkillDiscoveryEngine: Discovers skills from external sources
"""

# Import main integration components with better error handling
SKILL_SEEKERS_AVAILABLE = False

# Import all components from example_integration and main
try:
    from .example_integration import (
        SkillSeekersIntegration,
        ConflictResolutionEngine,
        SkillDiscoveryEngine,
        ExternalSkillSource,
        ImportedSkill,
        SkillConflict
    )
    from .main import main as example_main
    SKILL_SEEKERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Skill Seekers Integration components not available: {e}")
    # Create placeholder classes
    SkillSeekersIntegration = None
    ConflictResolutionEngine = None
    SkillDiscoveryEngine = None
    ExternalSkillSource = None
    ImportedSkill = None
    SkillConflict = None
    example_main = None

# Export main classes
__all__ = [
    'SkillSeekersIntegration',
    'ConflictResolutionEngine',
    'SkillDiscoveryEngine',
    'ExternalSkillSource',
    'ImportedSkill',
    'SkillConflict',
    'example_main',
    'SKILL_SEEKERS_AVAILABLE'
]

# Version and metadata
__version__ = '1.0.0'
__description__ = 'Skill Seekers Integration - External skill discovery and management'