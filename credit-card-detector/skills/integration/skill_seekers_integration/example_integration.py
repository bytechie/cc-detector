"""
Example Usage of Skill Seekers Integration with Adaptive Skills

This example demonstrates how to use the integrated system to discover,
import, and manage skills from external sources for enhanced credit card detection.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from skills.adaptive.example_usage import AdaptiveSkillManager
except ImportError:
    try:
        from claude_subagent.adaptive_skills import AdaptiveSkillManager
    except ImportError:
        AdaptiveSkillManager = None
# Import SkillSeekersIntegration - handle circular import by using the class directly
try:
    from . import SkillSeekersIntegration
except ImportError:
    # For circular import cases, define locally if needed
    SkillSeekersIntegration = None


async def example_basic_integration():
    """Basic example of setting up and using the integration"""
    print("=== Basic Skill Seekers Integration Example ===\n")

    # Initialize adaptive manager
    adaptive_manager = AdaptiveSkillManager(skills_dir="integration_skills")

    # Initialize integration
    integration = SkillSeekersIntegration(adaptive_manager)

    # Add external sources
    print("1. Adding external skill sources...")

    # Add OWASP documentation source
    integration.add_external_source(
        name="OWASP_Credit_Card",
        url="https://cheatsheetseries.owasp.org/cheatsheets/Credit_Card_Cheat_Sheet.html",
        source_type="documentation",
        description="OWASP Credit Card Security Guidelines",
        tags=["security", "credit_card", "owasp"]
    )

    # Add Python regex documentation
    integration.add_external_source(
        name="Python_Regex",
        url="https://docs.python.org/3/library/re.html",
        source_type="documentation",
        description="Python Regular Expression Documentation",
        tags=["python", "regex", "pattern_matching"]
    )

    # Get integration status
    status = integration.get_integration_status()
    print(f"Added {status['external_sources']} external sources")
    print(f"Active sources: {status['active_sources']}")
    print()

    # Scan external sources for skills
    print("2. Scanning external sources for skills...")

    # Note: This would normally scan the actual URLs, but for demo purposes
    # we'll show the structure
    scan_results = {
        'scanned_sources': 2,
        'discovered_skills': 0,
        'imported_skills': 0,
        'conflicts_detected': 0,
        'conflicts_resolved': 0,
        'errors': []
    }

    print(f"Scanned {scan_results['scanned_sources']} sources")
    print(f"Discovered {scan_results['discovered_skills']} new skills")
    print(f"Imported {scan_results['imported_skills']} skills")

    if scan_results['errors']:
        print("Errors encountered:")
        for error in scan_results['errors']:
            print(f"  - {error}")
    print()

    # Show final status
    final_status = integration.get_integration_status()
    print("3. Final integration status:")
    print(json.dumps(final_status, indent=2))


async def example_credit_card_security_skills():
    """Example: Discover security-focused credit card skills"""
    print("\n=== Credit Card Security Skills Discovery ===\n")

    # Initialize integration
    adaptive_manager = AdaptiveSkillManager(skills_dir="security_skills")
    integration = SkillSeekersIntegration(adaptive_manager)

    # Add predefined security sources
    print("1. Adding credit card security sources...")
    integration.discover_credit_card_security_skills()

    status = integration.get_integration_status()
    print(f"Added {len(status['sources'])} security-focused sources:")
    for source in status['sources']:
        print(f"  - {source['name']}: {source['description']}")
        print(f"    Tags: {', '.join(['security', 'credit_card'])}")  # Simplified for demo
    print()

    # Simulate skill discovery with mock data
    print("2. Simulating skill discovery...")

    # Mock discovered skills
    mock_discovered_skills = [
        {
            "name": "pci_dss_validation",
            "description": "Validates credit card numbers according to PCI DSS standards",
            "source": "PCI_DSS_Docs",
            "quality_score": 0.9
        },
        {
            "name": "luhn_checksum_enhanced",
            "description": "Enhanced Luhn algorithm validation with better error handling",
            "source": "OWASP_Cheat_Sheet",
            "quality_score": 0.85
        },
        {
            "name": "card_brand_detection",
            "description": "Detects credit card brand (Visa, MasterCard, Amex) from number patterns",
            "source": "OWASP_Cheat_Sheet",
            "quality_score": 0.8
        }
    ]

    print(f"Would discover {len(mock_discovered_skills)} security skills:")
    for skill in mock_discovered_skills:
        print(f"  - {skill['name']}: {skill['description']}")
        print(f"    Quality: {skill['quality_score']}, Source: {skill['source']}")
    print()

    # Show how skills would enhance detection
    print("3. Enhanced detection capabilities:")
    test_text = "Credit cards: 4111111111111111 (Visa), 5500000000000004 (MasterCard), 378282246310005 (Amex)"
    print(f"Input: {test_text}")
    print("Enhanced detection would provide:")
    print("  - Basic detection: Card numbers and validity")
    print("  - Brand identification: Visa, MasterCard, Amex")
    print("  - PCI DSS compliance checking")
    print("  - Enhanced validation with better error handling")


async def example_conflict_resolution():
    """Example: Demonstrate conflict detection and resolution"""
    print("\n=== Conflict Detection and Resolution Example ===\n")

    adaptive_manager = AdaptiveSkillManager(skills_dir="conflict_demo")
    integration = SkillSeekersIntegration(adaptive_manager)

    # Create some existing skills first
    existing_skill_code = '''
def detect(text):
    """Basic credit card detection"""
    import re
    pattern = r'\\b(?:\\d[ -]?){13,16}\\d\\b'
    return [{"raw": m.group(0), "start": m.start(), "end": m.end()}
            for m in re.finditer(pattern, text)]
'''

    # Mock adding existing skill
    print("1. Existing skills in system:")
    print("  - detect_credit_card_basic: Basic credit card detection")
    print()

    # Simulate discovering a conflicting skill
    print("2. New skill discovered from external source:")
    print("  - detect_credit_card: Enhanced credit card detection with Luhn validation")
    print("  - Conflict: Name collision with existing skill")
    print()

    # Show conflict resolution
    print("3. Conflict resolution process:")
    print("  - Detected name collision")
    print("  - Auto-resolvable: Yes")
    print("  - Resolution: Rename new skill to 'detect_credit_card_20250117'")
    print("  - Status: ✅ Resolved automatically")
    print()

    # Show functionality overlap detection
    print("4. Functionality overlap analysis:")
    print("  - Comparing patterns: ['detect', 'find', 're']")
    print("  - Pattern similarity: 0.85")
    print("  - Conflict severity: 0.85 (high)")
    print("  - Resolution: Choose higher quality skill")
    print("  - Status: ⚠️ Requires manual review")


async def example_quality_assessment():
    """Example: Skill quality assessment and filtering"""
    print("\n=== Skill Quality Assessment Example ===\n")

    # Mock skills with different quality levels
    skills = [
        {
            "name": "high_quality_skill",
            "description": "Well-documented skill with comprehensive tests",
            "metrics": {
                "code_complexity": 0.8,
                "documentation_quality": 0.9,
                "example_coverage": 0.8,
                "error_handling": 0.9,
                "overall_quality": 0.85
            }
        },
        {
            "name": "medium_quality_skill",
            "description": "Functional skill with minimal documentation",
            "metrics": {
                "code_complexity": 0.6,
                "documentation_quality": 0.4,
                "example_coverage": 0.5,
                "error_handling": 0.6,
                "overall_quality": 0.55
            }
        },
        {
            "name": "low_quality_skill",
            "description": "Basic skill with no documentation or error handling",
            "metrics": {
                "code_complexity": 0.3,
                "documentation_quality": 0.1,
                "example_coverage": 0.0,
                "error_handling": 0.2,
                "overall_quality": 0.15
            }
        }
    ]

    quality_threshold = 0.6

    print("1. Discovered skills quality assessment:")
    for skill in skills:
        quality = skill["metrics"]["overall_quality"]
        status = "✅ Pass" if quality >= quality_threshold else "❌ Fail"
        print(f"  - {skill['name']}: {quality:.2f} {status}")
        print(f"    Description: {skill['description']}")
        print(f"    Documentation: {skill['metrics']['documentation_quality']:.2f}")
        print(f"    Error handling: {skill['metrics']['error_handling']:.2f}")
        print()

    print(f"2. Quality filtering (threshold: {quality_threshold}):")
    high_quality_skills = [s for s in skills if s["metrics"]["overall_quality"] >= quality_threshold]
    print(f"  Skills passing quality filter: {len(high_quality_skills)}/{len(skills)}")
    print("  Imported skills:")
    for skill in high_quality_skills:
        print(f"    - {skill['name']}")
    print()

    print("3. Quality improvement suggestions:")
    for skill in skills:
        if skill["metrics"]["overall_quality"] < quality_threshold:
            print(f"  - {skill['name']}:")
            if skill["metrics"]["documentation_quality"] < 0.5:
                print("    • Add comprehensive docstrings")
            if skill["metrics"]["example_coverage"] < 0.5:
                print("    • Include more usage examples")
            if skill["metrics"]["error_handling"] < 0.5:
                print("    • Add proper error handling")


async def example_continuous_learning():
    """Example: Continuous learning from external sources"""
    print("\n=== Continuous Learning Example ===\n")

    adaptive_manager = AdaptiveSkillManager(skills_dir="continuous_learning")
    integration = SkillSeekersIntegration(adaptive_manager)

    print("1. Setting up continuous learning pipeline:")
    print("  - External sources configured:")

    # Add diverse sources for continuous learning
    sources = [
        ("Security Blogs", "https://blog.sucuri.net/", "security", ["malware", "security", "threats"]),
        ("OWASP Updates", "https://owasp.org/", "documentation", ["security", "owasp", "vulnerabilities"]),
        ("Pattern Matching", "https://www.regular-expressions.info/", "documentation", ["regex", "patterns"]),
        ("Fraud Detection", "https://www.fraud-detection.net/", "documentation", ["fraud", "detection", "ml"])
    ]

    for name, url, source_type, tags in sources:
        integration.add_external_source(name, url, source_type, tags)
        print(f"    • {name}: {url}")

    print()
    print("2. Learning schedule:")
    print("  - Scan frequency: Every 24 hours")
    print("  - Quality threshold: 0.6")
    print("  - Max conflicts per scan: 5")
    print("  - Auto-import: Enabled")
    print()

    print("3. Simulated learning progression:")

    # Simulate multiple learning cycles
    for cycle in range(1, 4):
        print(f"  Cycle {cycle}:")
        print(f"    - Discovered {cycle * 2} new skills")
        print(f"    - Quality threshold passed: {cycle + 1}")
        print(f"    - Conflicts resolved: {cycle}")
        print(f"    - Total skills in system: {len(adaptive_manager.list_skills()) + cycle * 2}")

    print()
    print("4. Benefits of continuous learning:")
    print("  ✅ Always up-to-date with latest security patterns")
    print("  ✅ Automatic discovery of new detection techniques")
    print("  ✅ Continuous improvement of detection accuracy")
    print("  ✅ Reduced manual maintenance overhead")
    print("  ✅ Adaptation to emerging threats")


async def main():
    """Run all examples"""
    print("Skill Seekers + Adaptive Skills Integration Examples\n")
    print("=" * 60)

    try:
        await example_basic_integration()
    except Exception as e:
        print(f"Basic integration example failed: {e}")

    print("\n" + "=" * 60)

    try:
        await example_credit_card_security_skills()
    except Exception as e:
        print(f"Security skills example failed: {e}")

    print("\n" + "=" * 60)

    try:
        await example_conflict_resolution()
    except Exception as e:
        print(f"Conflict resolution example failed: {e}")

    print("\n" + "=" * 60)

    try:
        await example_quality_assessment()
    except Exception as e:
        print(f"Quality assessment example failed: {e}")

    print("\n" + "=" * 60)

    try:
        await example_continuous_learning()
    except Exception as e:
        print(f"Continuous learning example failed: {e}")

    print("\n" + "=" * 60)
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())