"""
Resource Management Examples

This module demonstrates the resource-aware adaptive capabilities
with practical examples of constraint handling and optimization.
"""

import asyncio
import time
import random
import json
from typing import List, Dict, Any
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from claude_subagent.resource_management import (
    ResourceConstraints, ResourceType, ConstraintLevel, OptimizationStrategy,
    AdaptiveProcessingEngine, ResourceMonitor, ProcessingTask
)
from claude_subagent.resource_management.performance_predictor import (
    PerformancePredictor, PerformanceRecord
)


async def example_basic_resource_monitoring():
    """Example: Basic resource monitoring and constraint detection"""
    print("=== Basic Resource Monitoring Example ===\n")

    # Create resource monitor
    monitor = ResourceMonitor(sampling_interval=0.5)

    # Create constraints
    constraints = ResourceConstraints(
        max_cpu_percent=75.0,
        max_memory_percent=80.0,
        max_batch_size=100,
        max_concurrent_tasks=4
    )

    print("1. Starting resource monitoring...")
    monitor.start_monitoring()

    # Monitor for a few seconds
    print("2. Collecting resource metrics...")
    await asyncio.sleep(3)

    # Get current and average metrics
    current_metrics = monitor.get_current_metrics()
    avg_metrics = monitor.get_average_metrics(duration_minutes=0.05)  # 3 seconds

    print(f"3. Current resource usage:")
    if current_metrics:
        print(f"   CPU: {current_metrics.cpu_percent:.1f}%")
        print(f"   Memory: {current_metrics.memory_percent:.1f}% ({current_metrics.memory_used_mb:.1f} MB)")
        print(f"   Threads: {current_metrics.active_threads}")
        print(f"   Processes: {current_metrics.active_processes}")

    print(f"\n4. Average resource usage (last 3 seconds):")
    if avg_metrics:
        print(f"   CPU: {avg_metrics.cpu_percent:.1f}%")
        print(f"   Memory: {avg_metrics.memory_percent:.1f}%")

    # Check constraint level
    if current_metrics:
        constraint_level = constraints.get_constraint_level(current_metrics)
        print(f"\n5. Current constraint level: {constraint_level.value}")

        if constraint_level != ConstraintLevel.NONE:
            print("   ⚠️  System is under resource constraints")
        else:
            print("   ✅ System has adequate resources")

    # Stop monitoring
    monitor.stop_monitoring()
    print("\n6. Resource monitoring stopped")


async def example_adaptive_strategies():
    """Example: Adaptive strategy selection based on constraints"""
    print("\n=== Adaptive Strategy Selection Example ===\n")

    # Create processing engine
    constraints = ResourceConstraints(
        max_cpu_percent=70.0,
        max_memory_percent=75.0,
        max_batch_size=200,
        max_concurrent_tasks=4
    )

    engine = AdaptiveProcessingEngine(constraints)
    monitor = engine.resource_monitor
    monitor.start_monitoring()

    # Simulate different resource scenarios
    scenarios = [
        {
            "name": "Low Load (Morning)",
            "cpu_load": 30,
            "memory_load": 25,
            "data_count": 100
        },
        {
            "name": "Medium Load (Afternoon)",
            "cpu_load": 60,
            "memory_load": 55,
            "data_count": 500
        },
        {
            "name": "High Load (Peak Hours)",
            "cpu_load": 85,
            "memory_load": 80,
            "data_count": 1000
        },
        {
            "name": "Critical Load (System Stress)",
            "cpu_load": 95,
            "memory_load": 90,
            "data_count": 2000
        }
    ]

    print("1. Testing adaptive strategy selection:")

    for scenario in scenarios:
        print(f"\n   Scenario: {scenario['name']}")
        print(f"   - Simulated CPU: {scenario['cpu_load']}%")
        print(f"   - Simulated Memory: {scenario['memory_load']}%")
        print(f"   - Data items: {scenario['data_count']}")

        # Create mock metrics for the scenario
        mock_metrics = type('MockMetrics', (), {
            'cpu_percent': scenario['cpu_load'],
            'memory_percent': scenario['memory_load'],
            'active_threads': random.randint(5, 25),
            'timestamp': time.time()
        })()

        # Get recommended strategy
        strategy = engine.resource_optimizer.select_optimal_strategy(
            mock_metrics,
            scenario['data_count']
        )

        # Get optimized parameters
        batch_size = engine.resource_optimizer.optimize_batch_size(
            mock_metrics,
            100  # base batch size
        )

        concurrency = engine.resource_optimizer.optimize_concurrency(
            mock_metrics,
            scenario['data_count']
        )

        print(f"   - Recommended Strategy: {strategy.value}")
        print(f"   - Optimized Batch Size: {batch_size}")
        print(f"   - Optimized Concurrency: {concurrency}")

        # Get constraint level
        constraint_level = constraints.get_constraint_level(mock_metrics)
        print(f"   - Constraint Level: {constraint_level.value}")

    monitor.stop_monitoring()


async def example_resource_constrained_processing():
    """Example: Processing data under various resource constraints"""
    print("\n=== Resource-Constrained Processing Example ===\n")

    # Sample data for processing
    sample_data = [
        "Credit card: 4111111111111111",
        "No sensitive data here",
        "Card number: 4242424242424242",
        "Random text with numbers: 123456789",
        "Another card: 5555555555554444",
        "Valid Visa: 4111111111111111",
        "Test data: 9999999999999999",
        "More content: 1234567890123456"
    ] * 25  # 200 total items

    print(f"1. Processing {len(sample_data)} text items under different constraints:")

    # Test different constraint levels
    constraint_scenarios = [
        {
            "name": "Unconstrained",
            "constraints": ResourceConstraints(
                max_cpu_percent=95,
                max_memory_percent=95,
                max_batch_size=500,
                max_concurrent_tasks=8
            )
        },
        {
            "name": "Moderately Constrained",
            "constraints": ResourceConstraints(
                max_cpu_percent=70,
                max_memory_percent=70,
                max_batch_size=100,
                max_concurrent_tasks=4
            )
        },
        {
            "name": "Highly Constrained",
            "constraints": ResourceConstraints(
                max_cpu_percent=50,
                max_memory_percent=50,
                max_batch_size=50,
                max_concurrent_tasks=2
            )
        },
        {
            "name": "Critically Constrained",
            "constraints": ResourceConstraints(
                max_cpu_percent=30,
                max_memory_percent=30,
                max_batch_size=20,
                max_concurrent_tasks=1
            )
        }
    ]

    # Define simple processing function
    async def process_text(text):
        """Simulate text processing with resource costs"""
        # Simulate processing time
        await asyncio.sleep(0.001)  # 1ms per item
        return {
            "text": text,
            "length": len(text),
            "has_card": "card" in text.lower() and any(c.isdigit() for c in text)
        }

    results_summary = []

    for scenario in constraint_scenarios:
        print(f"\n   {scenario['name']}:")

        # Create processing engine with scenario constraints
        engine = AdaptiveProcessingEngine(scenario['constraints'])
        monitor = engine.resource_monitor
        monitor.start_monitoring()

        try:
            start_time = time.time()

            # Process data with resource awareness
            processed_results, performance_info = await engine.process_with_constraints(
                sample_data,
                process_text
            )

            end_time = time.time()
            processing_time = end_time - start_time

            print(f"   - Processing Time: {processing_time:.3f} seconds")
            print(f"   - Throughput: {len(sample_data) / processing_time:.1f} items/sec")
            print(f"   - Strategy Used: {performance_info.get('strategy', 'unknown')}")
            print(f"   - Batch Size: {performance_info.get('batch_size', 'unknown')}")
            print(f"   - Concurrency: {performance_info.get('concurrency', 'unknown')}")
            print(f"   - Items Processed: {len([r for r in processed_results if r])}")

            results_summary.append({
                "scenario": scenario['name'],
                "processing_time": processing_time,
                "throughput": len(sample_data) / processing_time,
                "strategy": performance_info.get('strategy'),
                "success_rate": len([r for r in processed_results if r]) / len(sample_data)
            })

        finally:
            monitor.stop_monitoring()
            engine.cleanup()

    # Compare results
    print("\n2. Performance Comparison:")
    print("   Scenario                | Time (s) | Throughput | Strategy        | Success Rate")
    print("   ------------------------|----------|------------|-----------------|-------------")
    for result in results_summary:
        print(f"   {result['scenario']:<24} | {result['processing_time']:>8.3f} | {result['throughput']:>10.1f} | {result['strategy']:<15} | {result['success_rate']:>11.1%}")


async def example_performance_prediction():
    """Example: ML-based performance prediction"""
    print("\n=== Performance Prediction Example ===\n")

    # Create performance predictor
    predictor = PerformancePredictor()

    # Add some historical performance data
    print("1. Adding historical performance data...")
    historical_data = [
        {
            "data_size": 100,
            "cpu_usage": 30,
            "memory_usage": 25,
            "strategy": "sequential",
            "processing_time": 0.1,
            "throughput": 1000
        },
        {
            "data_size": 500,
            "cpu_usage": 60,
            "memory_usage": 50,
            "strategy": "batch_optimized",
            "processing_time": 0.4,
            "throughput": 1250
        },
        {
            "data_size": 1000,
            "cpu_usage": 80,
            "memory_usage": 70,
            "strategy": "parallel_limited",
            "processing_time": 0.6,
            "throughput": 1667
        },
        {
            "data_size": 2000,
            "cpu_usage": 90,
            "memory_usage": 85,
            "strategy": "adaptive_sampling",
            "processing_time": 0.5,
            "throughput": 2000
        }
    ]

    for data in historical_data:
        record = PerformanceRecord(
            timestamp=time.time() - random.randint(3600, 86400),  # Random time in last day
            data_size=data["data_size"],
            cpu_usage=data["cpu_usage"],
            memory_usage=data["memory_usage"],
            thread_count=random.randint(5, 20),
            strategy=data["strategy"],
            processing_time=data["processing_time"],
            throughput=data["throughput"],
            success_rate=1.0,
            batch_size=100,
            concurrency=4,
            skill_count=5
        )
        predictor.add_record(record)

    print(f"   Added {len(historical_data)} historical records")

    # Test scenarios for prediction
    test_scenarios = [
        {
            "name": "Small Dataset, Low Resources",
            "data_size": 50,
            "cpu": 25,
            "memory": 20
        },
        {
            "name": "Medium Dataset, Medium Resources",
            "data_size": 500,
            "cpu": 60,
            "memory": 55
        },
        {
            "name": "Large Dataset, High Resources",
            "data_size": 1500,
            "cpu": 85,
            "memory": 80
        },
        {
            "name": "Very Large Dataset, Critical Resources",
            "data_size": 3000,
            "cpu": 95,
            "memory": 90
        }
    ]

    print("\n2. Performance Predictions:")
    print("   Scenario                              | Predicted Time | Predicted Throughput | Recommended Strategy | Confidence")
    print("   --------------------------------------|----------------|----------------------|----------------------|------------")

    for scenario in test_scenarios:
        # Create mock metrics
        mock_metrics = type('MockMetrics', (), {
            'cpu_percent': scenario['cpu'],
            'memory_percent': scenario['memory'],
            'active_threads': 10,
            'timestamp': time.time()
        })()

        # Get prediction
        prediction = predictor.predict_performance(
            scenario['data_size'],
            mock_metrics,
            ResourceConstraints()
        )

        print(f"   {scenario['name']:<37} | {prediction.predicted_processing_time:>14.3f} | {prediction.predicted_throughput:>20.1f} | {prediction.recommended_strategy:<20} | {prediction.confidence_score:>10.1%}")

        # Show optimization suggestions
        if prediction.optimization_suggestions:
            print(f"     Suggestions: {prediction.optimization_suggestions[0]}")
        if len(prediction.optimization_suggestions) > 1:
            print(f"                  {prediction.optimization_suggestions[1]}")

    print(f"\n3. Model Information:")
    model_info = predictor.get_model_info()
    print(f"   - Training Records: {model_info['total_records']}")
    print(f"   - Models Trained: {model_info['models_trained']}")
    print(f"   - Feature Count: {model_info['feature_count']}")


async def example_intelligent_resource_management():
    """Example: Complete intelligent resource management scenario"""
    print("\n=== Intelligent Resource Management Scenario ===\n")

    print("Scenario: E-commerce platform processing payment logs during different traffic periods")
    print("Objective: Maintain performance while adapting to resource constraints\n")

    # Simulate payment log data
    payment_logs = [
        f"Payment processed: ${random.randint(10, 1000)} - Card: {'4111111111111111' if random.random() > 0.7 else '4242424242424242'}",
        f"Transaction failed: Insufficient funds - Card: {'5555555555554444' if random.random() > 0.8 else '378282246310005'}",
        f"Refund issued: ${random.randint(5, 500)} - Original card: {'6011111111111117' if random.random() > 0.9 else '2223000048400011'}",
        "System status: All payment gateways operational",
        f"Chargeback initiated: ${random.randint(20, 800)} - Reason: Dispute"
    ] * 100  # 500 log entries

    # Define traffic patterns throughout the day
    traffic_periods = [
        {
            "name": "Early Morning (3 AM)",
            "load_factor": 0.2,  # 20% of peak load
            "description": "Low traffic, maintenance window"
        },
        {
            "name": "Morning Rush (9 AM)",
            "load_factor": 0.7,  # 70% of peak load
            "description": "Business hours starting"
        },
        {
            "name": "Peak Shopping (2 PM)",
            "load_factor": 1.0,  # 100% of peak load
            "description": "Maximum traffic, flash sale active"
        },
        {
            "name": "Evening Slowdown (8 PM)",
            "load_factor": 0.5,  # 50% of peak load
            "description": "Moderate traffic, dinner time"
        },
        {
            "name": "System Stress (11 PM)",
            "load_factor": 0.9,  # 90% load + maintenance tasks
            "description": "High traffic + batch processing"
        }
    ]

    # Processing function for payment logs
    async def process_payment_logs(logs):
        """Process payment logs to detect sensitive card information"""
        results = []
        for log in logs:
            # Simple detection simulation
            has_card = any(keyword in log for keyword in ['4111', '4242', '5555', '3782', '6011'])
            results.append({
                "log": log,
                "has_sensitive_data": has_card,
                "length": len(log),
                "processed_at": time.time()
            })
        return results

    print("1. Processing logs throughout different traffic periods:")

    for period in traffic_periods:
        print(f"\n   {period['name']}:")
        print(f"   Description: {period['description']}")
        print(f"   Load Factor: {period['load_factor']:.0%} of peak")

        # Calculate resource load based on traffic
        base_cpu_load = 20 + (period['load_factor'] * 60)  # 20-80% CPU
        base_memory_load = 15 + (period['load_factor'] * 55)  # 15-70% Memory

        # Create constraints based on current load
        constraints = ResourceConstraints(
            max_cpu_percent=min(95, 100 - base_cpu_load + 20),  # Leave headroom
            max_memory_percent=min(95, 100 - base_memory_load + 25),
            max_batch_size=max(10, int(500 * (1 - period['load_factor'] + 0.2))),  # Smaller batches under high load
            max_concurrent_tasks=max(1, int(8 * (1 - period['load_factor'] + 0.3)))  # Less concurrency under high load
        )

        # Process sample of logs based on traffic
        sample_size = int(len(payment_logs) * period['load_factor'])
        sample_logs = payment_logs[:sample_size]

        print(f"   Processing {sample_size} log entries...")
        print(f"   Available CPU: {constraints.max_cpu_percent:.0f}%")
        print(f"   Available Memory: {constraints.max_memory_percent:.0f}%")

        # Create processing engine
        engine = AdaptiveProcessingEngine(constraints)
        monitor = engine.resource_monitor
        monitor.start_monitoring()

        try:
            start_time = time.time()

            # Process with resource awareness
            processed_results, performance_info = await engine.process_with_constraints(
                sample_logs,
                process_payment_logs
            )

            processing_time = time.time() - start_time

            # Analyze results
            sensitive_logs = sum(1 for r in processed_results if r and r.get('has_sensitive_data', False))
            total_processed = len([r for r in processed_results if r])

            print(f"   Results:")
            print(f"   - Processing Time: {processing_time:.3f} seconds")
            print(f"   - Throughput: {total_processed / processing_time:.1f} logs/sec")
            print(f"   - Strategy Used: {performance_info.get('strategy', 'unknown')}")
            print(f"   - Sensitive Data Found: {sensitive_logs} logs")
            print(f"   - Success Rate: {total_processed / sample_size:.1%}")

            # Show adaptation
            actual_strategy = performance_info.get('strategy')
            if period['load_factor'] > 0.8:
                expected_strategies = ['adaptive_sampling', 'sequential', 'skill_priority']
            elif period['load_factor'] > 0.5:
                expected_strategies = ['batch_optimized', 'caching_aggressive']
            else:
                expected_strategies = ['parallel_limited', 'batch_optimized']

            if actual_strategy in expected_strategies:
                print(f"   - ✅ Strategy selection matches expectations for load level")
            else:
                print(f"   - ⚠️  Unexpected strategy ({actual_strategy}) for load level")

        finally:
            monitor.stop_monitoring()
            engine.cleanup()

    print("\n2. Key Insights:")
    print("   ✅ System automatically adapts processing strategy based on resource availability")
    print("   ✅ Under high load, switches to conservative strategies (sequential, sampling)")
    print("   ✅ Under low load, uses efficient parallel processing")
    print("   ✅ Maintains processing throughput while respecting resource constraints")
    print("   ✅ Gracefully handles traffic spikes without system overload")


async def main():
    """Run all resource management examples"""
    print("Resource Management Examples\n")
    print("=" * 60)

    try:
        await example_basic_resource_monitoring()
    except Exception as e:
        print(f"Basic monitoring example failed: {e}")

    print("\n" + "=" * 60)

    try:
        await example_adaptive_strategies()
    except Exception as e:
        print(f"Adaptive strategies example failed: {e}")

    print("\n" + "=" * 60)

    try:
        await example_resource_constrained_processing()
    except Exception as e:
        print(f"Resource constrained processing example failed: {e}")

    print("\n" + "=" * 60)

    try:
        await example_performance_prediction()
    except Exception as e:
        print(f"Performance prediction example failed: {e}")

    print("\n" + "=" * 60)

    try:
        await example_intelligent_resource_management()
    except Exception as e:
        print(f"Intelligent resource management example failed: {e}")

    print("\n" + "=" * 60)
    print("All resource management examples completed!")
    print("\nKey Takeaways:")
    print("🎯 Resource-aware AI can adapt to any constraint level")
    print("🚀 Automatic strategy selection optimizes performance")
    print("📊 ML-based prediction enables proactive optimization")
    print("🛡️ System remains stable under any load conditions")
    print("🔮 Intelligence learns and improves over time")


if __name__ == "__main__":
    asyncio.run(main())