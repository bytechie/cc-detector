"""
Claude Skills Registry - Centralized skill management

This module provides a unified interface to all credit card detection skills
organized by category for better maintainability and discoverability.
"""

# Core skills - these are the main credit card detection functions
try:
    from src.core.detect_credit_cards import detect as detect_credit_cards
    from src.core.detect_credit_cards_presidio import detect as detect_credit_cards_presidio
    from src.core.redact_credit_cards import redact as redact_credit_cards
    from src.core.redact_credit_cards_presidio import redact as redact_credit_cards_presidio
except ImportError as e:
    print(f"Warning: Could not import core skills: {e}")
    # Set fallback None values
    detect_credit_cards = None
    detect_credit_cards_presidio = None
    redact_credit_cards = None
    redact_credit_cards_presidio = None

# Advanced skills - these require additional dependencies
try:
    from .adaptive.example_usage import main as adaptive_example
except ImportError:
    adaptive_example = None

try:
    from src.integration.skill_seekers_integration import example_main as skill_seekers_example
except ImportError:
    skill_seekers_example = None

# Skill Registry
class SkillRegistry:
    """Registry for managing and discovering available skills."""

    # Core credit card detection skills
    CORE_SKILLS = {
        'detect_credit_cards': {
            'module': 'skills.core.detect_credit_cards',
            'description': 'Basic credit card number detection using regex patterns',
            'function': 'detect_credit_cards'
        },
        'detect_credit_cards_presidio': {
            'module': 'skills.core.detect_credit_cards_presidio',
            'description': 'Advanced detection using Microsoft Presidio framework',
            'function': 'detect_credit_cards'
        },
        'redact_credit_cards': {
            'module': 'skills.core.redact_credit_cards',
            'description': 'Redact detected credit card numbers from text',
            'function': 'redact_credit_cards'
        },
        'redact_credit_cards_presidio': {
            'module': 'skills.core.redact_credit_cards_presidio',
            'description': 'Advanced redaction using Microsoft Presidio framework',
            'function': 'redact_credit_cards'
        }
    }

    # Adaptive and learning skills
    ADAPTIVE_SKILLS = {
        'adaptive_skills': {
            'module': 'skills.adaptive.example_usage',
            'description': 'Adaptive learning and optimization capabilities',
            'function': 'main'
        }
    }

    # Integration with external systems
    INTEGRATION_SKILLS = {
        'skill_seekers_integration': {
            'module': 'skills.integration.skill_seekers_integration.example_integration',
            'description': 'Skill Seekers Integration - External skill discovery and management platform',
            'function': 'main'
        }
    }

    @classmethod
    def get_all_skills(cls):
        """Get all available skills."""
        all_skills = {}
        all_skills.update(cls.CORE_SKILLS)
        all_skills.update(cls.ADAPTIVE_SKILLS)
        all_skills.update(cls.INTEGRATION_SKILLS)
        return all_skills

    @classmethod
    def get_skills_by_category(cls, category):
        """Get skills by category."""
        category_map = {
            'core': cls.CORE_SKILLS,
            'adaptive': cls.ADAPTIVE_SKILLS,
            'integration': cls.INTEGRATION_SKILLS
        }
        return category_map.get(category, {})

    @classmethod
    def list_categories(cls):
        """List all available skill categories."""
        return ['core', 'adaptive', 'integration']

# Export main classes and functions
__all__ = [
    'SkillRegistry',
    # Core skills
    'detect_credit_cards',
    'detect_credit_cards_presidio',
    'redact_credit_cards',
    'redact_credit_cards_presidio',
    # Advanced skills
    'adaptive_example',
    'skill_seekers_example'
]

# Version info
__version__ = '1.0.0'
__description__ = 'Claude Skills Registry - Organized credit card detection capabilities'