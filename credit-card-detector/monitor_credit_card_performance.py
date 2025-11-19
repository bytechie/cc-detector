#!/usr/bin/env python3
"""
Monitor Credit Card Detection Performance

This script demonstrates how to monitor the credit card detection system
using both direct metrics and Prometheus queries.
"""

import requests
import time
import json
from datetime import datetime

# Configuration
PROMETHEUS_URL = "http://localhost:9090"
DETECTION_API_URL = "http://localhost:5000/scan"

def query_prometheus(query):
    """Query Prometheus for metrics."""
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Prometheus query failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error querying Prometheus: {e}")
        return None

def display_prometheus_metrics():
    """Display key monitoring metrics from Prometheus."""
    print("🔍 Prometheus Metrics Dashboard")
    print("=" * 50)

    queries = [
        ("up", "Service Status"),
        ("prometheus_tsdb_head_samples_appended_total", "Total Samples Collected"),
        ("rate(prometheus_http_requests_total[5m])", "Prometheus Request Rate"),
    ]

    for query, description in queries:
        result = query_prometheus(query)
        if result and result.get("data", {}).get("result"):
            print(f"\n📊 {description}")
            for metric in result["data"]["result"]:
                value = metric.get("value", ["0", "0"])[1]
                labels = metric.get("metric", {})
                print(f"   {labels}: {value}")
        else:
            print(f"\n❌ {description}: No data available")

def test_credit_card_detection_performance():
    """Test credit card detection performance if API is available."""
    print(f"\n🎯 Testing Credit Card Detection Performance")
    print("=" * 50)

    test_data = [
        "Customer payment: Visa 4111111111111111",
        "Multiple cards: MC 5555555555554444, Amex 378282246310005",
        "No cards here: just regular text",
        "Invalid card: 4111111111111112 should fail Luhn",
    ]

    for i, text in enumerate(test_data, 1):
        print(f"\n🧪 Test {i}: {text[:30]}...")

        try:
            start_time = time.time()
            response = requests.post(DETECTION_API_URL,
                                   json={"text": text},
                                   timeout=5)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                detections = data.get("detections", [])
                valid_cards = sum(1 for d in detections if d.get("valid", False))

                print(f"   ✅ Response time: {duration:.3f}s")
                print(f"   📋 Detections: {len(detections)} ({valid_cards} valid)")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:50]}")

        except requests.exceptions.ConnectionError:
            print("   ❌ Connection refused - API not running")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")

def show_monitoring_tips():
    """Show tips for monitoring the system."""
    print(f"\n💡 Monitoring Guide")
    print("=" * 50)

    print("""
🎯 Key Performance Indicators to Monitor:

1. RESPONSE TIME:
   - Query: histogram_quantile(0.95, credit_card_detector_request_duration_seconds_bucket)
   - Target: < 100ms for 95th percentile

2. THROUGHPUT:
   - Query: rate(credit_card_detector_requests_total[5m])
   - Monitor: Requests per second

3. DETECTION ACCURACY:
   - Query: rate(credit_card_detections_total[5m])
   - Track: Valid vs Invalid card detections

4. ERROR RATE:
   - Query: rate(credit_card_scan_requests_total{has_detections="error"}[5m])
   - Target: < 1% error rate

📈 Grafana Dashboard Setup:
1. Go to http://localhost:3002
2. Import dashboard: monitoring/grafana/dashboards/credit-card-dashboard.json
3. Set Prometheus as data source
4. Create alerts for threshold breaches

🔧 Prometheus Queries:
- Open http://localhost:9090
- Try queries like:
  * up{job="credit-card-detector"}
  * rate(credit_card_scan_requests_total[5m])
  * histogram_quantile(0.95, credit_card_scan_duration_seconds_bucket)
""")

def check_infrastructure_health():
    """Check health of monitoring infrastructure."""
    print(f"\n🏥 Infrastructure Health Check")
    print("=" * 50)

    services = [
        ("Prometheus", "http://localhost:9090/api/v1/status/config"),
        ("Grafana", "http://localhost:3002/api/health"),
        ("Presidio Analyzer", "http://localhost:3000/health"),
        ("Presidio Anonymizer", "http://localhost:3001/health"),
    ]

    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ Healthy" if response.status_code == 200 else f"⚠️ HTTP {response.status_code}"
            print(f"   {name}: {status}")
        except requests.exceptions.ConnectionError:
            print(f"   {name}: ❌ Connection refused")
        except Exception as e:
            print(f"   {name}: ❌ {str(e)[:30]}")

def main():
    """Main monitoring demonstration."""
    print("🔎 Credit Card Detection System Monitoring")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check infrastructure
    check_infrastructure_health()

    # Display Prometheus metrics
    display_prometheus_metrics()

    # Test detection performance
    test_credit_card_detection_performance()

    # Show monitoring tips
    show_monitoring_tips()

    print(f"\n🎉 Monitoring Summary")
    print("=" * 50)
    print("✅ Prometheus: http://localhost:9090")
    print("✅ Grafana: http://localhost:3002")
    print("📊 Enhanced metrics available when main app is running")
    print("📋 Dashboard ready for import in Grafana")

if __name__ == "__main__":
    main()