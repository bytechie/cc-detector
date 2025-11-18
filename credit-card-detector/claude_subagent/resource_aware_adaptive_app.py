"""Resource-Aware Adaptive Subagent

This Flask app integrates resource management with the adaptive skills system
to provide intelligent credit card detection that adapts to resource constraints.

Key Features:
- Real-time resource monitoring and constraint detection
- Adaptive processing strategies based on resource availability
- Intelligent skill selection and prioritization
- Dynamic optimization of batch sizes and concurrency
- Performance prediction and resource-aware scheduling
- Automatic adaptation to resource constraints
"""

import os
import requests
import json
import asyncio
import psutil
from datetime import datetime
from flask import Flask, request, jsonify
from claude_subagent.skills import detect_credit_cards, redact_credit_cards
from claude_subagent.adaptive_skills import AdaptiveSkillManager
from claude_subagent.skill_seekers_integration import SkillSeekersIntegration
from claude_subagent.resource_management import (
    ResourceConstraints, ResourceType, ConstraintLevel, OptimizationStrategy,
    AdaptiveProcessingEngine, ResourceMonitor, ResourceOptimizer
)

app = Flask(__name__)

# Initialize core systems with resource awareness
constraints = ResourceConstraints(
    max_cpu_percent=75.0,
    max_memory_percent=80.0,
    max_batch_size=500,
    max_concurrent_tasks=4
)

adaptive_manager = AdaptiveSkillManager(skills_dir="resource_aware_skills")
skill_seekers_integration = SkillSeekersIntegration(adaptive_manager)
processing_engine = AdaptiveProcessingEngine(constraints, adaptive_manager)


def _check_presidio_service(url: str, service_name: str) -> dict:
    """Check if a Presidio service is healthy."""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            return {"name": service_name, "status": "healthy", "url": url}
        else:
            return {"name": service_name, "status": "unhealthy", "url": url, "error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"name": service_name, "status": "unreachable", "url": url, "error": str(e)}


@app.route("/health", methods=["GET"])
def health():
    """Comprehensive health check with resource awareness."""
    # Get current resource metrics
    current_metrics = processing_engine.resource_monitor.get_current_metrics()
    performance_stats = processing_engine.get_performance_stats()

    health_status = {
        "status": "ok",
        "service": "resource-aware-claude-subagent",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {},
        "adaptive_skills": {
            "total_skills": len(adaptive_manager.list_skills()),
            "skill_names": adaptive_manager.list_skills()
        },
        "resource_management": {
            "constraints": constraints.__dict__,
            "current_strategy": processing_engine.current_strategy.value,
            "constraint_level": constraints.get_constraint_level(current_metrics).value if current_metrics else "unknown",
            "is_processing": processing_engine.is_processing
        }
    }

    # Add current metrics if available
    if current_metrics:
        health_status["current_resources"] = current_metrics.to_dict()

    # Add performance stats if available
    if performance_stats:
        health_status["performance_stats"] = performance_stats

    # Check Presidio dependencies
    analyzer_url = os.environ.get("PRESIDIO_ANALYZER_URL", "http://localhost:3000")
    health_status["dependencies"]["analyzer"] = _check_presidio_service(analyzer_url, "presidio-analyzer")

    anonymizer_url = os.environ.get("PRESIDIO_ANONYMIZER_URL", "http://localhost:3001")
    health_status["dependencies"]["anonymizer"] = _check_presidio_service(anonymizer_url, "presidio-anonymizer")

    # Determine overall health considering resources
    unhealthy_deps = [dep for dep in health_status["dependencies"].values()
                      if dep["status"] not in ["healthy", "unreachable"]]

    # Check resource constraints
    if current_metrics:
        constraint_level = constraints.get_constraint_level(current_metrics)
        if constraint_level in [ConstraintLevel.HIGH, ConstraintLevel.CRITICAL]:
            health_status["status"] = "resource_constrained"
            health_status["message"] = f"System under {constraint_level.value} resource constraints"
        elif unhealthy_deps:
            health_status["status"] = "degraded"
            health_status["message"] = f"Some dependencies are unhealthy: {[dep['name'] for dep in unhealthy_deps]}"

    return jsonify(health_status)


@app.route("/scan", methods=["POST"])
def scan():
    """Original scan endpoint using fixed credit card detection."""
    data = request.get_json(force=True)
    text = data.get("text", "")
    detections = detect_credit_cards.detect(text)
    redacted = redact_credit_cards.redact(text, detections)
    return jsonify({"detections": detections, "redacted": redacted})


@app.route("/scan-resource-aware", methods=["POST"])
async def scan_resource_aware():
    """Resource-aware enhanced scan endpoint."""
    data = request.get_json(force=True)
    text = data.get("text", "")
    texts = data.get("texts", [text])  # Support multiple texts
    use_optimization = data.get("use_optimization", True)
    resource_constraints = data.get("resource_constraints", {})

    # Apply custom constraints if provided
    if resource_constraints:
        for key, value in resource_constraints.items():
            if hasattr(constraints, key):
                setattr(constraints, key, value)

    if use_optimization and len(texts) > 1:
        # Use resource-aware processing for multiple texts
        try:
            # Define processing function
            async def process_single_text(input_text):
                # Start with base detection
                base_detections = detect_credit_cards.detect(input_text)

                # Apply adaptive skills if available
                all_detections = base_detections.copy()
                for skill_name in adaptive_manager.list_skills():
                    try:
                        skill = adaptive_manager.skill_registry[skill_name]
                        skill_detections = adaptive_manager._execute_skill(skill, input_text)
                        all_detections.extend(skill_detections)
                    except Exception as e:
                        print(f"Error in skill {skill_name}: {e}")

                # Deduplicate
                unique_detections = []
                seen_positions = set()
                for detection in all_detections:
                    pos_key = (detection.get("start", 0), detection.get("end", 0))
                    if pos_key not in seen_positions:
                        seen_positions.add(pos_key)
                        unique_detections.append(detection)

                redacted = redact_credit_cards.redact(input_text, unique_detections)
                return {
                    "text": input_text,
                    "detections": unique_detections,
                    "redacted": redacted,
                    "detection_count": len(unique_detections)
                }

            # Process with resource awareness
            results, performance_info = await processing_engine.process_with_constraints(
                texts,
                process_single_text
            )

            # Combine results
            total_detections = sum(r.get("detection_count", 0) for r in results if r)

            return jsonify({
                "results": results,
                "total_texts_processed": len(results),
                "total_detections": total_detections,
                "performance": performance_info,
                "resource_optimization": {
                    "enabled": True,
                    "strategy_used": performance_info.get("strategy", "unknown"),
                    "constraint_level": constraints.get_constraint_level(
                        processing_engine.resource_monitor.get_current_metrics()
                    ).value if processing_engine.resource_monitor.get_current_metrics() else "unknown"
                }
            })

        except Exception as e:
            print(f"Resource-aware processing error: {e}")
            # Fall back to simple processing
            pass

    # Fallback to simple processing
    if len(texts) == 1:
        text = texts[0]
        detections = detect_credit_cards.detect(text)
        redacted = redact_credit_cards.redact(text, detections)
        return jsonify({
            "results": [{
                "text": text,
                "detections": detections,
                "redacted": redacted,
                "detection_count": len(detections)
            }],
            "total_texts_processed": 1,
            "total_detections": len(detections),
            "resource_optimization": {"enabled": False}
        })
    else:
        # Process multiple texts simply
        results = []
        total_detections = 0

        for text in texts:
            try:
                detections = detect_credit_cards.detect(text)
                redacted = redact_credit_cards.redact(text, detections)
                results.append({
                    "text": text,
                    "detections": detections,
                    "redacted": redacted,
                    "detection_count": len(detections)
                })
                total_detections += len(detections)
            except Exception as e:
                results.append({
                    "text": text,
                    "detections": [],
                    "redacted": text,
                    "detection_count": 0,
                    "error": str(e)
                })

        return jsonify({
            "results": results,
            "total_texts_processed": len(results),
            "total_detections": total_detections,
            "resource_optimization": {"enabled": False}
        })


@app.route("/resource-monitor", methods=["GET"])
def resource_monitor():
    """Get current resource metrics and monitoring info."""
    current_metrics = processing_engine.resource_monitor.get_current_metrics()
    average_metrics = processing_engine.resource_monitor.get_average_metrics(duration_minutes=5.0)

    return jsonify({
        "current": current_metrics.to_dict() if current_metrics else None,
        "average_5min": average_metrics.to_dict() if average_metrics else None,
        "monitoring_active": processing_engine.resource_monitor.is_monitoring,
        "history_size": len(processing_engine.resource_monitor.metrics_history),
        "constraint_level": constraints.get_constraint_level(current_metrics).value if current_metrics else "unknown"
    })


@app.route("/resource-constraints", methods=["GET", "POST"])
def manage_resource_constraints():
    """Get or update resource constraints."""
    if request.method == "GET":
        """Get current resource constraints."""
        current_metrics = processing_engine.resource_monitor.get_current_metrics()
        current_level = constraints.get_constraint_level(current_metrics).value if current_metrics else "unknown"

        return jsonify({
            "constraints": constraints.__dict__,
            "current_constraint_level": current_level,
            "recommendations": processing_engine.resource_optimizer.get_optimization_recommendations(current_metrics) if current_metrics else []
        })

    else:  # POST
        """Update resource constraints."""
        data = request.get_json(force=True)

        try:
            # Update constraints
            for key, value in data.items():
                if hasattr(constraints, key):
                    setattr(constraints, key, value)

            # Update the processor's constraints
            processing_engine.constraints = constraints
            processing_engine.resource_optimizer = ResourceOptimizer(constraints)

            return jsonify({
                "message": "Resource constraints updated successfully",
                "new_constraints": constraints.__dict__
            })

        except Exception as e:
            return jsonify({"error": f"Failed to update constraints: {str(e)}"}), 500


@app.route("/optimization-strategies", methods=["GET", "POST"])
def manage_optimization_strategies():
    """Manage optimization strategies."""
    if request.method == "GET":
        """Get available optimization strategies and their performance."""
        return jsonify({
            "available_strategies": [s.value for s in OptimizationStrategy],
            "current_strategy": processing_engine.current_strategy.value,
            "strategy_performance": processing_engine.resource_optimizer.strategy_performance,
            "performance_history": {
                strategy.value: [asdict(r) for r in results]
                for strategy, results in processing_engine.resource_optimizer.performance_history.items()
            }
        })

    else:  # POST
        """Manually set optimization strategy."""
        data = request.get_json(force=True)
        strategy_name = data.get("strategy")

        try:
            strategy = OptimizationStrategy(strategy_name)
            processing_engine.current_strategy = strategy

            return jsonify({
                "message": f"Optimization strategy set to {strategy_name}",
                "current_strategy": strategy.value
            })

        except ValueError:
            return jsonify({
                "error": f"Invalid strategy: {strategy_name}. Available strategies: {[s.value for s in OptimizationStrategy]}"
            }), 400


@app.route("/performance-stats", methods=["GET"])
def performance_stats():
    """Get detailed performance statistics."""
    stats = processing_engine.get_performance_stats()

    # Add system performance info
    system_info = {
        "cpu_count": psutil.cpu_count(),
        "memory_total_gb": psutil.virtual_memory().total / (1024**3),
        "disk_usage_percent": psutil.disk_usage('/').percent,
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
    }

    return jsonify({
        "processing_performance": stats,
        "system_info": system_info,
        "adaptive_skills_performance": {
            skill_name: {
                "f1_score": perf.f1_score,
                "precision": perf.precision,
                "recall": perf.recall,
                "last_updated": perf.last_updated
            }
            for skill_name, perf in adaptive_manager.performance_metrics.items()
        }
    })


@app.route("/benchmark-processing", methods=["POST"])
async def benchmark_processing():
    """Benchmark different processing strategies with current data."""
    data = request.get_json(force=True)
    texts = data.get("texts", [])
    iterations = data.get("iterations", 3)

    if not texts:
        return jsonify({"error": "No texts provided for benchmarking"}), 400

    # Create a sample processing function
    async def sample_processing(text):
        base_detections = detect_credit_cards.detect(text)
        return {"detections": base_detections, "count": len(base_detections)}

    benchmark_results = {}

    # Test each strategy
    for strategy in OptimizationStrategy:
        strategy_results = []

        for iteration in range(iterations):
            try:
                start_time = time.time()

                # Force strategy selection
                original_strategy = processing_engine.current_strategy
                processing_engine.current_strategy = strategy

                results, performance_info = await processing_engine.process_with_constraints(
                    texts,
                    sample_processing
                )

                end_time = time.time()
                processing_time = end_time - start_time

                strategy_results.append({
                    "iteration": iteration + 1,
                    "processing_time": processing_time,
                    "throughput": len(texts) / processing_time,
                    "actual_strategy": performance_info.get("strategy"),
                    "success_count": sum(1 for r in results if r and not isinstance(r, Exception))
                })

                processing_engine.current_strategy = original_strategy

            except Exception as e:
                strategy_results.append({
                    "iteration": iteration + 1,
                    "error": str(e),
                    "processing_time": float('inf'),
                    "throughput": 0,
                    "success_count": 0
                })

        # Calculate statistics for this strategy
        successful_results = [r for r in strategy_results if "error" not in r]

        if successful_results:
            benchmark_results[strategy.value] = {
                "avg_processing_time": sum(r["processing_time"] for r in successful_results) / len(successful_results),
                "avg_throughput": sum(r["throughput"] for r in successful_results) / len(successful_results),
                "min_processing_time": min(r["processing_time"] for r in successful_results),
                "max_processing_time": max(r["processing_time"] for r in successful_results),
                "success_rate": len(successful_results) / iterations,
                "iterations": strategy_results
            }
        else:
            benchmark_results[strategy.value] = {
                "success_rate": 0,
                "iterations": strategy_results
            }

    return jsonify({
        "benchmark_config": {
            "text_count": len(texts),
            "iterations": iterations,
            "total_iterations": len(OptimizationStrategy) * iterations
        },
        "results": benchmark_results,
        "recommendation": _get_benchmark_recommendation(benchmark_results)
    })


@app.route("/simulate-resource-constraints", methods=["POST"])
async def simulate_resource_constraints():
    """Simulate different resource constraint scenarios."""
    data = request.get_json(force=True)
    scenarios = data.get("scenarios", [])
    texts = data.get("texts", [])

    if not texts:
        return jsonify({"error": "No texts provided for simulation"}), 400

    # Default scenarios if none provided
    if not scenarios:
        scenarios = [
            {"name": "unconstrained", "max_cpu_percent": 100, "max_memory_percent": 100, "max_concurrent_tasks": 8},
            {"name": "moderate", "max_cpu_percent": 70, "max_memory_percent": 70, "max_concurrent_tasks": 4},
            {"name": "constrained", "max_cpu_percent": 50, "max_memory_percent": 50, "max_concurrent_tasks": 2},
            {"name": "critical", "max_cpu_percent": 30, "max_memory_percent": 30, "max_concurrent_tasks": 1}
        ]

    simulation_results = {}
    original_constraints = ResourceConstraints(
        max_cpu_percent=constraints.max_cpu_percent,
        max_memory_percent=constraints.max_memory_percent,
        max_concurrent_tasks=constraints.max_concurrent_tasks
    )

    async def process_text_sample(text):
        return {"processed": True, "length": len(text)}

    for scenario in scenarios:
        try:
            # Apply scenario constraints
            scenario_constraints = ResourceConstraints(
                max_cpu_percent=scenario.get("max_cpu_percent", 80),
                max_memory_percent=scenario.get("max_memory_percent", 80),
                max_concurrent_tasks=scenario.get("max_concurrent_tasks", 4)
            )

            # Update processor constraints temporarily
            processing_engine.constraints = scenario_constraints
            processing_engine.resource_optimizer = ResourceOptimizer(scenario_constraints)

            start_time = time.time()

            results, performance_info = await processing_engine.process_with_constraints(
                texts,
                process_text_sample
            )

            end_time = time.time()

            # Get resource usage during processing
            current_metrics = processing_engine.resource_monitor.get_current_metrics()
            constraint_level = scenario_constraints.get_constraint_level(current_metrics).value if current_metrics else "unknown"

            simulation_results[scenario["name"]] = {
                "constraints": scenario_constraints.__dict__,
                "processing_time": end_time - start_time,
                "throughput": len(texts) / (end_time - start_time),
                "strategy_used": performance_info.get("strategy"),
                "constraint_level": constraint_level,
                "success_count": len([r for r in results if r and not isinstance(r, Exception)]),
                "performance_info": performance_info
            }

        except Exception as e:
            simulation_results[scenario["name"]] = {
                "error": str(e),
                "success_count": 0
            }

    # Restore original constraints
    processing_engine.constraints = original_constraints
    processing_engine.resource_optimizer = ResourceOptimizer(original_constraints)

    return jsonify({
        "simulation_config": {
            "text_count": len(texts),
            "scenarios_tested": len(scenarios)
        },
        "results": simulation_results,
        "analysis": _analyze_simulation_results(simulation_results)
    })


def _get_benchmark_recommendation(benchmark_results):
    """Get optimization recommendation based on benchmark results."""
    if not benchmark_results:
        return "No successful benchmark results"

    # Find best performing strategy
    best_strategy = None
    best_throughput = 0
    best_success_rate = 0

    for strategy_name, results in benchmark_results.items():
        if results.get("success_rate", 0) > 0.5:  # At least 50% success rate
            throughput = results.get("avg_throughput", 0)
            success_rate = results.get("success_rate", 0)

            # Prioritize success rate, then throughput
            if success_rate > best_success_rate or (success_rate == best_success_rate and throughput > best_throughput):
                best_strategy = strategy_name
                best_throughput = throughput
                best_success_rate = success_rate

    if best_strategy:
        return f"Recommended strategy: {best_strategy} (throughput: {best_throughput:.2f} texts/sec, success rate: {best_success_rate:.1%})"
    else:
        return "No strategy achieved acceptable success rate - check system resources"


def _analyze_simulation_results(results):
    """Analyze simulation results and provide insights."""
    analysis = {
        "best_performance": None,
        "worst_performance": None,
        "resource_efficiency": {},
        "recommendations": []
    }

    successful_results = {k: v for k, v in results.items() if v.get("success_count", 0) > 0 and "error" not in v}

    if successful_results:
        # Find best and worst performing
        best_scenario = max(successful_results.items(), key=lambda x: x[1].get("throughput", 0))
        worst_scenario = min(successful_results.items(), key=lambda x: x[1].get("throughput", 0))

        analysis["best_performance"] = {
            "scenario": best_scenario[0],
            "throughput": best_scenario[1].get("throughput", 0),
            "strategy": best_scenario[1].get("strategy_used")
        }

        analysis["worst_performance"] = {
            "scenario": worst_scenario[0],
            "throughput": worst_scenario[1].get("throughput", 0),
            "strategy": worst_scenario[1].get("strategy_used")
        }

        # Resource efficiency analysis
        for scenario_name, result in successful_results.items():
            constraints = result.get("constraints", {})
            cpu_limit = constraints.get("max_cpu_percent", 100)
            throughput = result.get("throughput", 0)

            if cpu_limit > 0:
                efficiency = throughput / cpu_limit
                analysis["resource_efficiency"][scenario_name] = efficiency

        # Generate recommendations
        best_throughput = analysis["best_performance"]["throughput"]
        worst_throughput = analysis["worst_performance"]["throughput"]

        if best_throughput > worst_throughput * 2:
            analysis["recommendations"].append(
                f"Significant performance difference detected. Consider using {analysis['best_performance']['scenario']} scenario settings."
            )

        # Check strategy adaptation
        strategies_used = set(result.get("strategy_used") for result in successful_results.values())
        if len(strategies_used) > 1:
            analysis["recommendations"].append(
                "System successfully adapted different optimization strategies based on resource constraints."
            )

    return analysis


if __name__ == "__main__":
    import os
    port = int(os.environ.get("SUBAGENT_PORT", 5000))

    print(f"Starting Resource-Aware Adaptive Subagent on port {port}")
    print("\n=== Resource-Aware Features ===")
    print("Detection:")
    print("  POST /scan - Original credit card detection")
    print("  POST /scan-resource-aware - Resource-aware enhanced detection")
    print("\nResource Management:")
    print("  GET /resource-monitor - Real-time resource monitoring")
    print("  GET/POST /resource-constraints - Manage resource constraints")
    print("  GET/POST /optimization-strategies - Manage optimization strategies")
    print("  GET /performance-stats - Detailed performance statistics")
    print("\nBenchmarking & Analysis:")
    print("  POST /benchmark-processing - Benchmark different strategies")
    print("  POST /simulate-resource-constraints - Simulate constraint scenarios")
    print("  GET /health - Comprehensive health with resource info")
    print("\nStarting server...")

    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    finally:
        # Cleanup resources on shutdown
        processing_engine.cleanup()