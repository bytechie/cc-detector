#!/usr/bin/env python3
"""
Integration Demo: Credit Card Detector with Claude Skills & n8n
This demo shows how to use the detector in various integration scenarios.
"""

import json
import time
import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.claude_skills.claude_skills_example import CreditCardDetectorSkill

def demo_claude_skills():
    """Demonstrate Claude Skills integration"""
    print("🤖 Claude Skills Integration Demo")
    print("=" * 50)

    # Initialize the skill
    skill = CreditCardDetectorSkill()

    # Test cases
    test_cases = [
        {
            "name": "Simple Credit Card Detection",
            "text": "My Visa card number is 4111111111111111"
        },
        {
            "name": "Multiple Cards",
            "text": "Customer has Visa 4111111111111111, MasterCard 5555555555554444, and Amex 378282246310005"
        },
        {
            "name": "Formated Card Numbers",
            "text": "Card: 4111-1111-1111-1111 or 4111 1111 1111 1111"
        },
        {
            "name": "No Credit Cards",
            "text": "This is a regular text without any payment information."
        },
        {
            "name": "Real-world Example",
            "text": """
            Dear Customer,

            Your order #12345 has been processed.
            Please update your payment information.
            Current card on file: ****-****-****-1111
            New card: 4111111111111111 (expires 12/25)

            Thank you for your business!
            """
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * len(test_case['name']))
        print(f"Input: {test_case['text'][:100]}{'...' if len(test_case['text']) > 100 else ''}")

        # Basic detection
        start_time = time.time()
        result = skill.detect_credit_cards(test_case['text'])
        detection_time = time.time() - start_time

        # Show results
        print(f"Cards found: {len(result['detections'])}")
        if result['detections']:
            for detection in result['detections']:
                print(f"  - {detection['number']} (Valid: {detection['valid']})")
        print(f"Redacted: {result['redacted'][:80]}{'...' if len(result['redacted']) > 80 else ''}")
        print(f"Processing time: {detection_time:.4f}s")

        # Comprehensive analysis
        analysis = skill.analyze_text_security(test_case['text'])
        security = analysis['security_analysis']
        print(f"Risk Level: {security['risk_level']} (Score: {security['security_score']}/100)")

def demo_batch_processing():
    """Demonstrate batch processing capabilities"""
    print("\n\n📦 Batch Processing Demo")
    print("=" * 30)

    skill = CreditCardDetectorSkill()

    # Simulate processing multiple documents
    documents = [
        "Payment received for order #1001 using Visa 4111111111111111",
        "Refund processed to MasterCard 5555555555554444",
        "Invoice #2002 paid with Amex 378282246310005",
        "Regular business communication",
        "Customer support ticket with card details: 4111111111111111"
    ]

    print(f"Processing {len(documents)} documents...")

    start_time = time.time()
    results = []

    for doc in documents:
        result = skill.analyze_text_security(doc)
        results.append({
            "text": doc,
            "cards_found": len(result['detections']),
            "risk_level": result['security_analysis']['risk_level']
        })

    total_time = time.time() - start_time

    # Summary
    high_risk_docs = [r for r in results if r['risk_level'] == 'HIGH']
    medium_risk_docs = [r for r in results if r['risk_level'] == 'MEDIUM']
    low_risk_docs = [r for r in results if r['risk_level'] == 'LOW']

    print(f"\nProcessing Summary:")
    print(f"Total documents: {len(documents)}")
    print(f"Total time: {total_time:.3f}s")
    print(f"Average time per document: {total_time/len(documents):.3f}s")
    print(f"High risk documents: {len(high_risk_docs)}")
    print(f"Medium risk documents: {len(medium_risk_docs)}")
    print(f"Low risk documents: {len(low_risk_docs)}")

def demo_n8n_workflow_simulation():
    """Simulate an n8n workflow"""
    print("\n\n🔄 n8n Workflow Simulation")
    print("=" * 35)

    skill = CreditCardDetectorSkill()

    # Simulate different workflow steps
    print("1. Input: Customer review data")
    input_data = {
        "customer_id": "cust_123",
        "review_text": "Great service! Used my Visa 4111111111111111 for payment.",
        "rating": 5,
        "timestamp": "2025-01-15T10:30:00Z"
    }

    print(f"   Processing review for customer {input_data['customer_id']}")

    # Step 2: Scan for sensitive data
    print("2. Scanning for sensitive information...")
    scan_result = skill.analyze_text_security(input_data['review_text'])

    if scan_result['detections']:
        print("   ⚠️  Credit card detected!")
        print(f"   Risk level: {scan_result['security_analysis']['risk_level']}")

        # Step 3: Decision branch
        if scan_result['security_analysis']['risk_level'] == 'HIGH':
            print("3. Decision: Route to security team for review")
            action = "SECURITY_REVIEW"
        else:
            print("3. Decision: Process with redacted data")
            action = "PROCESS_REDACTED"

        # Step 4: Prepare output
        output_data = {
            "customer_id": input_data['customer_id'],
            "original_review": input_data['review_text'],
            "redacted_review": scan_result['redacted'],
            "rating": input_data['rating'],
            "action": action,
            "security_analysis": scan_result['security_analysis']
        }
    else:
        print("   ✅ No sensitive data detected")
        output_data = input_data

    print("4. Output data prepared:")
    print(f"   Action: {output_data.get('action', 'NORMAL_PROCESSING')}")
    print(f"   Review safe to process: {not scan_result['detections']}")

def demo_api_endpoints():
    """Show how to use API endpoints directly"""
    print("\n\n🌐 Direct API Usage Demo")
    print("=" * 30)

    import requests

    # Health check
    try:
        health = requests.get("http://localhost:5000/health")
        if health.status_code == 200:
            print("✅ Credit Card Detector API is running")
            health_data = health.json()
            print(f"   Mode: {health_data.get('mode')}")
            print(f"   Status: {health_data.get('status')}")
        else:
            print("❌ Credit Card Detector API is not responding")
            return
    except:
        print("❌ Cannot connect to Credit Card Detector API")
        print("   Make sure it's running with: ./start.sh start basic")
        return

    # API call example
    test_text = "API test with card 4111111111111111"

    print(f"\nTesting API with: {test_text}")

    try:
        response = requests.post(
            "http://localhost:5000/scan",
            json={"text": test_text},
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ API call successful")
            print(f"   Cards detected: {len(result['detections'])}")
            print(f"   Redacted text: {result['redacted']}")
        else:
            print(f"❌ API call failed with status {response.status_code}")

    except Exception as e:
        print(f"❌ API call error: {e}")

def main():
    """Run all demos"""
    print("🎯 Credit Card Detector Integration Demo")
    print("=" * 50)
    print("This demo shows how to integrate with Claude skills and n8n workflows.")
    print("Make sure the Credit Card Detector is running on localhost:5000")
    print("Start with: ./start.sh start basic")

    # Run demos
    demo_claude_skills()
    demo_batch_processing()
    demo_n8n_workflow_simulation()
    demo_api_endpoints()

    print("\n\n🎉 Demo Complete!")
    print("=" * 20)
    print("Check out the integration guide for more details:")
    print("docs/INTEGRATION_GUIDE.md")

if __name__ == "__main__":
    main()