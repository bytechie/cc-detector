#!/usr/bin/env python3
"""
Load Testing Script for Credit Card Detection with Metrics
Generates realistic traffic to populate Grafana dashboard
"""

import requests
import time
import random
import threading
import json
from concurrent.futures import ThreadPoolExecutor
import statistics

# Test data for realistic load generation
TEST_SCENARIOS = [
    {
        "name": "Single Visa Card",
        "text": "Customer payment: Visa 4111111111111111 expires 12/25",
        "expected_detections": 1
    },
    {
        "name": "Multiple Cards",
        "text": "Payment methods: Visa 4111111111111111, Mastercard 5555555555554444, Amex 378282246310005",
        "expected_detections": 3
    },
    {
        "name": "No Cards",
        "text": "Regular transaction: Customer bought items for $45.67 using cash.",
        "expected_detections": 0
    },
    {
        "name": "International Format",
        "text": "European client: Payment with Carte Bleu 4111111111111111 for €125.50",
        "expected_detections": 1
    },
    {
        "name": "Mixed Format Cards",
        "text": "Card details: 4111-1111-1111-1111, 4242 4242 4242 4242, and 5555555555554444",
        "expected_detections": 3
    },
    {
        "name": "Invalid Card",
        "text": "Test invalid card: 4111111111111112 (should fail Luhn)",
        "expected_detections": 1
    },
    {
        "name": "Long Text with Card",
        "text": "Order #12345 - Customer: Sarah Johnson, Billing Address: 123 Main St, Payment: Visa ending in 4242 (4111111111111111), Amount: $156.78",
        "expected_detections": 1
    },
    {
        "name": "Business Transaction",
        "text": "Corporate expense: MC 5555555555554444 for office supplies, reference: BUS-001",
        "expected_detections": 1
    }
]

BASE_URL = "http://localhost:5000"

def make_scan_request(scenario):
    """Make a single scan request and return metrics."""
    try:
        start_time = time.time()

        response = requests.post(
            f"{BASE_URL}/scan",
            json={"text": scenario["text"]},
            timeout=10
        )

        end_time = time.time()
        response_time = end_time - start_time

        if response.status_code == 200:
            data = response.json()
            detections = len(data.get("detections", []))
            metrics = data.get("metrics", {})

            return {
                "success": True,
                "response_time": response_time,
                "detections": detections,
                "expected_detections": scenario["expected_detections"],
                "scan_duration": metrics.get("scan_duration_seconds", 0),
                "valid_cards": metrics.get("valid_cards", 0),
                "invalid_cards": metrics.get("invalid_cards", 0),
                "scenario": scenario["name"]
            }
        else:
            return {
                "success": False,
                "response_time": response_time,
                "status_code": response.status_code,
                "scenario": scenario["name"]
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "scenario": scenario["name"]
        }

def simulate_user_session(user_id, requests_per_session=10, delay_range=(1, 3)):
    """Simulate a user making multiple requests over time."""
    session_results = []

    for i in range(requests_per_session):
        # Random scenario selection
        scenario = random.choice(TEST_SCENARIOS)

        result = make_scan_request(scenario)
        result["user_id"] = user_id
        result["request_number"] = i + 1
        session_results.append(result)

        # Random delay between requests
        delay = random.uniform(*delay_range)
        time.sleep(delay)

    return session_results

def generate_burst_load(concurrent_users=5, requests_per_user=20):
    """Generate burst load with multiple concurrent users."""
    print(f"🚀 Generating burst load: {concurrent_users} users, {requests_per_user} requests each")

    all_results = []

    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        # Submit user sessions
        futures = [
            executor.submit(simulate_user_session, user_id, requests_per_user, (0.1, 0.5))
            for user_id in range(1, concurrent_users + 1)
        ]

        # Collect results
        for future in futures:
            try:
                user_results = future.result(timeout=60)
                all_results.extend(user_results)
            except Exception as e:
                print(f"❌ User session failed: {e}")

    return all_results

def generate_sustained_load(duration_seconds=60, target_rps=2):
    """Generate sustained load for a specific duration."""
    print(f"⏱️ Generating sustained load: {target_rps} RPS for {duration_seconds} seconds")

    results = []
    start_time = time.time()
    end_time = start_time + duration_seconds

    request_count = 0

    while time.time() < end_time:
        scenario = random.choice(TEST_SCENARIOS)
        result = make_scan_request(scenario)
        result["timestamp"] = time.time()
        results.append(result)

        request_count += 1

        # Calculate delay to maintain target RPS
        elapsed = time.time() - start_time
        expected_requests = elapsed * target_rps

        if request_count > expected_requests:
            # Slow down
            delay = 0.1
        else:
            # Speed up or maintain pace
            delay = max(0, (1.0 / target_rps) - 0.01)

        time.sleep(delay)

    return results

def analyze_results(results):
    """Analyze load test results and print summary."""
    if not results:
        print("❌ No results to analyze")
        return

    successful_requests = [r for r in results if r.get("success", False)]
    failed_requests = [r for r in results if not r.get("success", False)]

    print("\n📊 Load Test Results Summary")
    print("=" * 50)
    print(f"Total requests: {len(results)}")
    print(f"Successful: {len(successful_requests)} ({len(successful_requests)/len(results):.1%})")
    print(f"Failed: {len(failed_requests)} ({len(failed_requests)/len(results):.1%})")

    if successful_requests:
        response_times = [r["response_time"] for r in successful_requests]
        detections = [r["detections"] for r in successful_requests if "detections" in r]

        print(f"\n⏱️ Response Time Statistics:")
        print(f"  Average: {statistics.mean(response_times):.3f}s")
        print(f"  Median: {statistics.median(response_times):.3f}s")
        print(f"  95th percentile: {statistics.quantiles(response_times, n=20)[18]:.3f}s")
        print(f"  99th percentile: {statistics.quantiles(response_times, n=100)[98]:.3f}s")
        print(f"  Min: {min(response_times):.3f}s")
        print(f"  Max: {max(response_times):.3f}s")

        if detections:
            print(f"\n🎯 Detection Statistics:")
            print(f"  Total detections: {sum(detections)}")
            print(f"  Average per request: {statistics.mean(detections):.1f}")
            print(f"  Max in single request: {max(detections)}")

        # Scenario analysis
        scenario_counts = {}
        for r in successful_requests:
            scenario = r.get("scenario", "Unknown")
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1

        print(f"\n📋 Scenarios Tested:")
        for scenario, count in sorted(scenario_counts.items()):
            print(f"  {scenario}: {count} requests")

def main():
    """Main load testing function."""
    print("🔥 Credit Card Detection Load Testing with Metrics")
    print("=" * 60)

    # Check if service is available
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Service is healthy and ready for load testing")
        else:
            print(f"⚠️ Service health check returned {response.status_code}")
    except Exception as e:
        print(f"❌ Service not available: {e}")
        return

    # Phase 1: Burst load
    print("\n🎯 Phase 1: Burst Load Testing")
    burst_results = generate_burst_load(concurrent_users=3, requests_per_user=10)

    # Wait a moment between phases
    time.sleep(2)

    # Phase 2: Sustained load
    print("\n⏱️ Phase 2: Sustained Load Testing")
    sustained_results = generate_sustained_load(duration_seconds=30, target_rps=3)

    # Combine all results
    all_results = burst_results + sustained_results

    # Analyze results
    analyze_results(all_results)

    # Check final metrics
    print(f"\n📈 Final Metrics Check")
    print("=" * 30)
    try:
        metrics_response = requests.get(f"{BASE_URL}/metrics")
        if metrics_response.status_code == 200:
            metrics_text = metrics_response.text
            scan_requests = sum(1 for line in metrics_text.split('\n')
                              if line.startswith('credit_card_scan_requests_total'))
            print(f"✅ Metrics endpoint accessible")
            print(f"📊 Scan request metrics found: {scan_requests}")
        else:
            print(f"⚠️ Metrics endpoint returned {metrics_response.status_code}")
    except Exception as e:
        print(f"❌ Error checking metrics: {e}")

    print(f"\n🎉 Load testing completed!")
    print(f"📊 Check Grafana dashboard: http://localhost:3002")
    print(f"🔍 Check Prometheus: http://localhost:9090")

if __name__ == "__main__":
    main()