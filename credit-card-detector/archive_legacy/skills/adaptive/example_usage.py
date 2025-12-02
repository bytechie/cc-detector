"""
Example usage of the Adaptive Skill System

This module demonstrates how to use the adaptive skill system to automatically
generate and deploy new detection skills based on performance gaps.
"""

import json
from pathlib import Path
import sys

# Add the parent directory to the path so we can import the adaptive skills
sys.path.insert(0, str(Path(__file__).parent.parent))

from adaptive_skills import AdaptiveSkillManager, SkillGap, GeneratedSkill


def example_basic_usage():
    """Basic example of using the adaptive skill manager"""
    print("=== Basic Adaptive Skill System Usage ===\n")

    # Initialize the skill manager
    manager = AdaptiveSkillManager(skills_dir="generated_skills")

    # Create test data where existing skills might fail
    test_data = [
        {
            "input": "New credit card format: 4242-4242-4242-4242",
            "description": "Hyphen-separated card number"
        },
        {
            "input": "European format: 4242 4242 4242 4242",
            "description": "Space-separated card number"
        },
        {
            "input": "No sensitive data here",
            "description": "Clean text"
        },
        {
            "input": "Amex card: 378282246310005",
            "description": "15-digit American Express"
        }
    ]

    # Expected outputs for the test data
    expected_outputs = [
        [  # For the first test case
            {
                "start": 25,
                "end": 44,
                "raw": "4242-4242-4242-4242",
                "number": "4242424242424242",
                "valid": True
            }
        ],
        [  # For the second test case
            {
                "start": 18,
                "end": 37,
                "raw": "4242 4242 4242 4242",
                "number": "4242424242424242",
                "valid": True
            }
        ],
        [],  # No detections for clean text
        [  # For Amex card
            {
                "start": 11,
                "end": 26,
                "raw": "378282246310005",
                "number": "378282246310005",
                "valid": True
            }
        ]
    ]

    print("1. Analyzing current skill performance...")

    # Analyze and adapt
    new_skills = manager.analyze_and_adapt(test_data, expected_outputs)

    print(f"Generated {len(new_skills)} new skills to address performance gaps")

    # List all available skills
    available_skills = manager.list_skills()
    print(f"Available skills: {available_skills}")

    # Test the improved system
    print("\n2. Testing improved detection capabilities:")
    for i, test_case in enumerate(test_data):
        detections = []

        # Run all available skills
        for skill_name in available_skills:
            skill = manager.skill_registry[skill_name]
            skill_detections = manager._execute_skill(skill, test_case["input"])
            detections.extend(skill_detections)

        print(f"Test {i + 1}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        print(f"Detections: {len(detections)}")
        for detection in detections:
            print(f"  - Found: {detection['raw']} (valid: {detection.get('valid', 'N/A')})")
        print()


def example_manual_gap_creation():
    """Example of manually creating skills for specific gaps"""
    print("=== Manual Gap Creation Example ===\n")

    manager = AdaptiveSkillManager(skills_dir="manual_skills")

    # Create a specific gap we want to address
    gap = SkillGap(
        pattern="masked_credit_cards",
        description="Detection of masked/partially visible credit card numbers",
        examples=[
            "Card ending in 4242: ****-****-****-4242",
            "Last 4 digits: ****1234",
            "Partial card: 4242-xxxx-xxxx-4242"
        ],
        expected_output=[
            {"raw": "****-****-****-4242", "type": "masked", "last4": "4242"},
            {"raw": "****1234", "type": "masked", "last4": "1234"},
            {"raw": "4242-xxxx-xxxx-4242", "type": "partial", "pattern": "4242...4242"}
        ],
        severity=0.8,
        frequency=5
    )

    print("1. Generating skill for masked credit card detection...")

    # Generate a skill for this gap
    new_skill = manager.generate_skill_for_gap(gap)

    if new_skill:
        print(f"Generated skill: {new_skill.name}")
        print(f"Description: {new_skill.description}")

        # Test the skill
        if manager.test_and_deploy_skill(new_skill):
            print("✓ Skill successfully deployed!")

            # Test it on the examples
            print("\n2. Testing the new skill:")
            for example in gap.examples:
                detections = manager._execute_skill(new_skill, example)
                print(f"Input: {example}")
                print(f"Detections: {len(detections)}")
                for detection in detections:
                    print(f"  - {detection}")
                print()
        else:
            print("✗ Skill failed validation tests")
    else:
        print("✗ Failed to generate skill for the gap")


def example_performance_tracking():
    """Example of tracking skill performance over time"""
    print("=== Performance Tracking Example ===\n")

    manager = AdaptiveSkillManager(skills_dir="performance_demo")

    # Simulate some performance data
    skill_name = "detect_credit_card_1234"

    if skill_name in manager.skill_registry:
        print(f"Tracking performance for {skill_name}")

        # Simulate multiple rounds of performance updates
        rounds = [
            {"tp": 8, "fp": 2, "fn": 1},  # Good performance
            {"tp": 15, "fp": 3, "fn": 2},  # Improving
            {"tp": 25, "fp": 5, "fn": 3},  # Still improving
        ]

        for i, round_data in enumerate(rounds, 1):
            manager.update_skill_performance(skill_name, **round_data)
            perf = manager.get_skill_performance(skill_name)

            print(f"\nRound {i}:")
            print(f"  True Positives: {perf.true_positives}")
            print(f"  False Positives: {perf.false_positives}")
            print(f"  False Negatives: {perf.false_negatives}")
            print(f"  Precision: {perf.precision:.3f}")
            print(f"  Recall: {perf.recall:.3f}")
            print(f"  F1 Score: {perf.f1_score:.3f}")
    else:
        print(f"Skill {skill_name} not found. Available skills: {manager.list_skills()}")


def example_skill_comparison():
    """Example of comparing different skills for the same task"""
    print("=== Skill Comparison Example ===\n")

    manager = AdaptiveSkillManager(skills_dir="comparison_demo")

    # Test input
    test_text = "Multiple cards: 4111111111111111, 4242-4242-4242-4242, and 378282246310005"

    print(f"Testing input: {test_text}\n")

    # Compare all available skills
    skill_results = {}

    for skill_name in manager.list_skills():
        skill = manager.skill_registry[skill_name]
        detections = manager._execute_skill(skill, test_text)
        skill_results[skill_name] = detections

        print(f"{skill_name}:")
        print(f"  Detections: {len(detections)}")
        for detection in detections:
            print(f"    - {detection.get('raw', 'N/A')} (valid: {detection.get('valid', 'N/A')})")
        print()

    # Find the best performing skill
    best_skill = manager.get_best_skill_for_pattern("credit card detection")
    print(f"Best performing skill for credit card patterns: {best_skill}")


if __name__ == "__main__":
    print("Adaptive Skill System Examples\n")
    print("=" * 50)

    # Run all examples
    try:
        example_basic_usage()
    except Exception as e:
        print(f"Basic usage example failed: {e}")

    print("\n" + "=" * 50)

    try:
        example_manual_gap_creation()
    except Exception as e:
        print(f"Manual gap creation example failed: {e}")

    print("\n" + "=" * 50)

    try:
        example_performance_tracking()
    except Exception as e:
        print(f"Performance tracking example failed: {e}")

    print("\n" + "=" * 50)

    try:
        example_skill_comparison()
    except Exception as e:
        print(f"Skill comparison example failed: {e}")