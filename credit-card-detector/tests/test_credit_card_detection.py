#!/usr/bin/env python3
"""
Test script for credit card detection using various test data patterns.
Based on standard credit card test numbers and patterns.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from skills.core import detect_credit_cards, redact_credit_cards

# Test data based on standard credit card testing patterns
# These are commonly used test numbers that pass Luhn validation
TEST_DATA = [
    # Valid test numbers (pass Luhn check)
    {
        "name": "Visa Test Numbers",
        "text": """
        John Doe's payment information:
        Visa card: 4111111111111111
        Another Visa: 4012888888881881
        Payment due: $45.67
        Reference: VISA-4222222222222
        """
    },
    {
        "name": "Mastercard Test Numbers",
        "text": """
        Jane Smith's order details:
        Mastercard: 5555555555554444
        Alternative MC: 5105105105105100
        World Mastercard: 2223000048400011
        """
    },
    {
        "name": "American Express Test Numbers",
        "text": """
        Business account details:
        Amex card: 378282246310005
        Another Amex: 371449635398431
        Corporate card: 378734493671000
        """
    },
    {
        "name": "Discover Test Numbers",
        "text": """
        Subscription payment:
        Discover: 6011111111111117
        Alternative: 6011000990139424
        """
    },
    {
        "name": "Mixed Card Types",
        "text": """
        Customer payment methods:
        Primary Visa: 4111111111111111 expires 12/25
        Backup Mastercard: 5555555555554444 expires 09/24
        Business Amex: 378282246310005 expires 03/26
        Emergency Discover: 6011111111111117 expires 07/25
        Contact: john.doe@email.com, Phone: 555-123-4567
        """
    },
    {
        "name": "Realistic Transaction Data",
        "text": """
        Order #12345 - Customer: Sarah Johnson
        Billing Address: 123 Main St, New York, NY 10001
        Payment Method: Visa ending in 4242 (4111111111111111)
        Amount: $156.78
        Authorization Code: 123456
        Transaction ID: TXN-789456123
        Email: sarah.johnson@email.com
        """
    },
    {
        "name": "Edge Cases and Invalid Numbers",
        "text": """
        Test various formats and invalid numbers:
        Valid: 4111111111111111
        Invalid (fails Luhn): 4111111111111112
        Too short: 411111111111
        Too long: 41111111111111111111
        With spaces: 4111 1111 1111 1111
        With dashes: 4111-1111-1111-1111
        Mixed: 4111 1111-1111 1111
        """
    },
    {
        "name": "International Formats",
        "text": """
        European customer data:
        Name: Pierre Dubois
        Address: 15 Rue de la Paix, 75002 Paris, France
        Phone: +33 1 42 96 12 34
        Payment: Carte Bleu 4111111111111111
        Email: pierre.dubois@email.fr
        Order total: €125.50
        """
    }
]

def run_detection_test():
    """Run credit card detection on test data."""
    print("=" * 80)
    print("CREDIT CARD DETECTION TEST SUITE")
    print("=" * 80)

    total_detections = 0
    total_valid_cards = 0

    for i, test_case in enumerate(TEST_DATA, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 60)
        print("Input Text:")
        print(test_case['text'])

        # Run detection
        detections = detect_credit_cards.detect(test_case['text'])

        print(f"\n🔍 Detections Found: {len(detections)}")

        case_valid_cards = 0
        for detection in detections:
            print(f"  • Card: {detection['number']}")
            print(f"    Valid (Luhn): {'✅ Yes' if detection['valid'] else '❌ No'}")
            print(f"    Raw format: '{detection['raw']}'")
            print(f"    Position: {detection['start']}-{detection['end']}")
            if detection['valid']:
                case_valid_cards += 1
                total_valid_cards += 1

        total_detections += len(detections)

        # Run redaction
        redacted = redact_credit_cards.redact(test_case['text'], detections)
        print(f"\n🔒 Redacted Text:")
        print(redacted)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total test cases: {len(TEST_DATA)}")
    print(f"Total potential card numbers detected: {total_detections}")
    print(f"Total valid credit cards (pass Luhn): {total_valid_cards}")
    print(f"Invalid numbers (fail Luhn): {total_detections - total_valid_cards}")

    # Test individual detection
    print("\n" + "=" * 80)
    print("INDIVIDUAL CARD VALIDATION TESTS")
    print("=" * 80)

    test_cards = [
        ("4111111111111111", "Visa Test", True),
        ("5555555555554444", "Mastercard Test", True),
        ("378282246310005", "Amex Test", True),
        ("6011111111111117", "Discover Test", True),
        ("4111111111111112", "Invalid Luhn", False),
        ("1234567890123456", "Random Invalid", False),
    ]

    print("Testing individual card numbers:")
    for card_num, description, expected in test_cards:
        is_valid = detect_credit_cards.is_valid_luhn(card_num)
        status = "✅ PASS" if is_valid == expected else "❌ FAIL"
        print(f"  {status} {card_num} ({description}) - Valid: {is_valid}")

if __name__ == "__main__":
    run_detection_test()