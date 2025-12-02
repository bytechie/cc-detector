#!/usr/bin/env python3
"""
Basic Credit Card Redaction Example

This example demonstrates how to redact credit card numbers from text
using the detection and redaction system together.

Usage:
    python basic_redaction.py

Features:
- Credit card detection
- Safe redaction with [REDACTED] placeholders
- Preservation of original text structure
- Multiple redaction modes
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from skills.core.detect_credit_cards import detect
from skills.core.redact_credit_cards import redact

def demonstrate_basic_redaction():
    """Demonstrate basic credit card redaction capabilities."""

    print("=" * 60)
    print("🔒 Credit Card Redaction - Basic Example")
    print("=" * 60)

    # Test data with various formats and scenarios
    test_cases = [
        {
            "name": "Single Card",
            "text": "My payment method is Visa 4111111111111111"
        },
        {
            "name": "Multiple Cards",
            "text": "Payment options: Visa 4111111111111111 or Mastercard 5555555555554444"
        },
        {
            "name": "Formatted Cards",
            "text": "Card numbers: 4111-1111-1111-1111 and 4111 1111 1111 1111"
        },
        {
            "name": "Log Entry",
            "text": "2024-01-15 10:30:45 [INFO] Payment processed for card 4111111111111111, amount $156.78"
        },
        {
            "name": "Customer Data",
            "text": """
            Customer Profile:
            Name: John Doe
            Email: john.doe@example.com
            Phone: 555-123-4567
            Payment: Visa 4111111111111111 (expires 12/25)
            """
        },
        {
            "name": "Transaction Log",
            "text": """
            TXN ID: 123456789
            Timestamp: 2024-01-15T10:30:45Z
            Amount: $156.78
            Card: 4111-1111-1111-1111
            Status: APPROVED
            Auth Code: 123456
            """
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 50)

        original_text = test_case['text']
        print(f"Original:")
        print(f"  {original_text}")

        # Detect credit cards
        detections = detect(original_text)
        print(f"\n🔍 Detections: {len(detections)} found")
        for j, detection in enumerate(detections, 1):
            status = "✅ Valid" if detection['valid'] else "❌ Invalid"
            print(f"  {j}. '{detection['raw']}' ({status})")

        # Redact credit cards
        redacted_text = redact(original_text, detections)
        print(f"\n🔒 Redacted:")
        print(f"  {redacted_text}")

        # Show redaction statistics
        cards_redacted = len([d for d in detections if d['valid']])
        print(f"\n📊 Stats: {cards_redacted}/{len(detections)} cards redacted")

def demonstrate_redaction_modes():
    """Demonstrate different redaction modes."""

    print("\n" + "=" * 60)
    print("🎨 Redaction Modes Example")
    print("=" * 60)

    text = "Payment methods: Visa 4111111111111111 and Amex 378282246310005"
    detections = detect(text)

    print(f"Original text: {text}")
    print(f"Detections: {len(detections)} cards found\n")

    # Demonstrate different redaction approaches
    redaction_modes = [
        {
            "name": "Standard Redaction",
            "mode": "redact",
            "description": "Uses [REDACTED] placeholder"
        },
        {
            "name": "Masked Redaction",
            "mode": "mask",
            "description": "Shows only last 4 digits"
        },
        {
            "name": "Hash Redaction",
            "mode": "hash",
            "description": "Replaces with hash placeholder"
        }
    ]

    for mode_info in redaction_modes:
        print(f"🎨 {mode_info['name']}:")
        print(f"   Description: {mode_info['description']}")
        try:
            redacted = redact(text, detections, mode=mode_info['mode'])
            print(f"   Result: {redacted}")
        except Exception as e:
            print(f"   Result: Mode not available - {e}")
        print()

def batch_redaction_example():
    """Demonstrate batch processing of multiple texts."""

    print("📦 Batch Redaction Example")
    print("-" * 30)

    # Simulate log entries
    log_entries = [
        "2024-01-15 10:30:45 User123 paid with 4111111111111111",
        "2024-01-15 10:31:22 User456 payment 5555555555554444 failed",
        "2024-01-15 10:32:15 User789 charged 378282246310005 successfully",
        "2024-01-15 10:33:01 User234 used card 4111111111111111 for $25.50",
        "2024-01-15 10:33:45 User567 payment with 6011111111111117 approved"
    ]

    print(f"Processing {len(log_entries)} log entries...\n")

    for i, log_entry in enumerate(log_entries, 1):
        detections = detect(log_entry)
        if detections:
            redacted = redact(log_entry, detections)
            print(f"{i:2d}. Original: {log_entry}")
            print(f"    Redacted: {redacted}")
            print(f"    Cards found: {len(detections)}")
        else:
            print(f"{i:2d}. No cards: {log_entry}")
        print()

    print("✅ Batch processing complete!")

def main():
    """Main example function."""
    try:
        # Demonstrate basic redaction
        demonstrate_basic_redaction()

        # Demonstrate different redaction modes
        demonstrate_redaction_modes()

        # Demonstrate batch processing
        batch_redaction_example()

        print("\n" + "=" * 60)
        print("🎉 Redaction Examples Complete!")
        print("=" * 60)
        print("\n💡 Key Takeaways:")
        print("• Always detect before redacting to ensure safety")
        print("• Redaction preserves text structure and readability")
        print("• Different redaction modes for different use cases")
        print("• Batch processing is efficient for multiple texts")
        print("• Only valid credit cards should typically be redacted")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the correct directory.")
        print("The skills module should be available in the parent directory.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()