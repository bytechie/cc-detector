#!/usr/bin/env python3
"""
Simple Credit Card Detection Example

This example demonstrates basic credit card detection functionality.
It shows how to use the core detection system to find potential
credit card numbers in text.

Usage:
    python simple_detection.py

Features:
- Basic credit card detection
- Luhn algorithm validation
- Multiple format support (spaces, dashes, continuous)
- Detailed detection results
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from skills.core.detect_credit_cards import detect

def demonstrate_basic_detection():
    """Demonstrate basic credit card detection capabilities."""

    print("=" * 60)
    print("🔍 Credit Card Detection - Basic Example")
    print("=" * 60)

    # Test data with various formats
    test_cases = [
        {
            "name": "Continuous Number",
            "text": "My Visa card number is 4111111111111111 for payments."
        },
        {
            "name": "Space-Separated",
            "text": "Card: 4111 1111 1111 1111 expires 12/25"
        },
        {
            "name": "Dash-Separated",
            "text": "Payment method: 4111-1111-1111-1111 (Visa)"
        },
        {
            "name": "Multiple Cards",
            "text": "Primary: 4111111111111111, Backup: 5555555555554444"
        },
        {
            "name": "Mixed Valid/Invalid",
            "text": "Valid: 4111111111111111, Invalid: 4111111111111112"
        },
        {
            "name": "Real-world Example",
            "text": """
            Order #12345
            Customer: John Doe
            Payment: Visa ending in 1111 (4111111111111111)
            Amount: $156.78
            Authorization: 123456
            """
        }
    ]

    total_detections = 0
    total_valid = 0

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        print(f"Input: {test_case['text']}")

        # Perform detection
        detections = detect(test_case['text'])

        print(f"\n🔍 Results:")
        if detections:
            for j, detection in enumerate(detections, 1):
                print(f"  {j}. Card: {detection['number']}")
                print(f"     Raw:   '{detection['raw']}'")
                print(f"     Valid: {'✅ Yes' if detection['valid'] else '❌ No'}")
                print(f"     Position: {detection['start']}-{detection['end']}")

                total_detections += 1
                if detection['valid']:
                    total_valid += 1
        else:
            print("  No credit card numbers detected.")

    print(f"\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total test cases: {len(test_cases)}")
    print(f"Total detections: {total_detections}")
    print(f"Valid credit cards: {total_valid}")
    print(f"Invalid numbers: {total_detections - total_valid}")

def interactive_detection():
    """Allow user to test their own text."""

    print("\n" + "=" * 60)
    print("🎮 Interactive Detection")
    print("=" * 60)
    print("Enter your own text to scan for credit card numbers.")
    print("Type 'quit' or 'exit' to end the session.\n")

    while True:
        try:
            text = input("📝 Enter text to scan: ").strip()

            if text.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if not text:
                print("⚠️  Please enter some text.")
                continue

            # Detect credit cards
            detections = detect(text)

            if detections:
                print(f"\n🔍 Found {len(detections)} potential credit card numbers:")
                for i, detection in enumerate(detections, 1):
                    status = "✅ Valid" if detection['valid'] else "❌ Invalid"
                    print(f"  {i}. {detection['raw']} ({status})")
            else:
                print("✅ No credit card numbers detected.")

            print("-" * 40)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main example function."""
    try:
        # Run demonstration with predefined test cases
        demonstrate_basic_detection()

        # Run interactive session
        interactive_detection()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the correct directory.")
        print("The skills module should be available in the parent directory.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()