#!/usr/bin/env python3
"""
Basic API Integration Examples for Credit Card Detector
Shows how to use the REST API for credit card detection.
"""

import requests
import json
from typing import Dict, Any, List
import time

class CreditCardAPIClient:
    """Simple API client for Credit Card Detector"""

    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "unreachable"}

    def scan_text(self, text: str) -> Dict[str, Any]:
        """Scan text for credit cards"""
        try:
            response = self.session.post(
                f"{self.base_url}/scan",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "detections": [],
                "redacted": text
            }

    def batch_scan(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Scan multiple texts"""
        results = []
        for text in texts:
            result = self.scan_text(text)
            results.append(result)
        return results

# Usage examples
def example_basic_scan():
    """Example 1: Basic text scanning"""
    print("=== Example 1: Basic Text Scanning ===")

    client = CreditCardAPIClient()

    # Check health first
    health = client.health_check()
    if health.get("status") != "ok":
        print(f"❌ API not healthy: {health}")
        return

    print("✅ API is healthy")

    # Test with credit card
    test_text = "My Visa card number is 4111111111111111"
    result = client.scan_text(test_text)

    print(f"Input: {test_text}")
    print(f"Cards found: {len(result['detections'])}")
    print(f"Redacted: {result['redacted']}")
    print()

def example_batch_processing():
    """Example 2: Batch processing"""
    print("=== Example 2: Batch Processing ===")

    client = CreditCardAPIClient()

    texts = [
        "No sensitive data here",
        "Card: 4111111111111111",
        "Multiple cards: 4111111111111111 and 5555555555554444",
        "Safe business communication"
    ]

    start_time = time.time()
    results = client.batch_scan(texts)
    processing_time = time.time() - start_time

    print(f"Processed {len(texts)} texts in {processing_time:.3f}s")

    for i, (text, result) in enumerate(zip(texts, results)):
        cards_found = len(result['detections'])
        status = "⚠️ CARDS" if cards_found > 0 else "✅ SAFE"
        print(f"  Text {i+1}: {status} ({cards_found} cards)")

    print()

def example_error_handling():
    """Example 3: Error handling"""
    print("=== Example 3: Error Handling ===")

    # Test with invalid URL
    client = CreditCardAPIClient(base_url="http://localhost:9999")

    health = client.health_check()
    if "error" in health:
        print(f"❌ Expected error: {health['error']}")

    # Test with timeout
    client = CreditCardAPIClient(timeout=0.001)
    result = client.scan_text("Test text")

    if "error" in result:
        print(f"❌ Expected timeout error: {result['error']}")

    print()

def main():
    """Run all examples"""
    print("🌐 Credit Card Detector API Integration Examples")
    print("=" * 55)
    print("Make sure the detector is running: ./start.sh start basic")
    print()

    example_basic_scan()
    example_batch_processing()
    example_error_handling()

    print("🎉 API examples completed!")
    print("Check the API documentation for more advanced usage.")

if __name__ == "__main__":
    main()