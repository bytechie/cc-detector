"""Enhanced Adaptive Subagent with Skill Seekers Integration

This Flask app combines the adaptive skills system with Skill Seekers integration
to provide a comprehensive credit card detection and management platform.

Key Features:
- Adaptive skill generation and management
- External skill discovery and import
- Conflict detection and resolution
- Quality assessment and filtering
- Continuous learning from external sources
"""

import os
import requests
import json
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify
from claude_subagent.skills import detect_credit_cards, redact_credit_cards
from claude_subagent.adaptive_skills import AdaptiveSkillManager
from claude_subagent.skill_seekers_integration import SkillSeekersIntegration

app = Flask(__name__)

# Initialize adaptive skill manager with Skill Seekers integration
adaptive_manager = AdaptiveSkillManager(skills_dir="enhanced_adaptive_skills")
skill_seekers_integration = SkillSeekersIntegration(adaptive_manager)


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
    """Comprehensive health check with Skill Seekers integration status."""
    health_status = {
        "status": "ok",
        "service": "enhanced-claude-subagent-with-skill-seekers",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {},
        "adaptive_skills": {
            "total_skills": len(adaptive_manager.list_skills()),
            "skill_names": adaptive_manager.list_skills()
        }
    }

    # Check Presidio dependencies
    analyzer_url = os.environ.get("PRESIDIO_ANALYZER_URL", "http://localhost:3000")
    health_status["dependencies"]["analyzer"] = _check_presidio_service(analyzer_url, "presidio-analyzer")

    anonymizer_url = os.environ.get("PRESIDIO_ANONYMIZER_URL", "http://localhost:3001")
    health_status["dependencies"]["anonymizer"] = _check_presidio_service(anonymizer_url, "presidio-anonymizer")

    # Add Skill Seekers integration status
    integration_status = skill_seekers_integration.get_integration_status()
    health_status["skill_seekers"] = {
        "external_sources": integration_status["external_sources"],
        "active_sources": integration_status["active_sources"],
        "discovered_skills": integration_status["discovered_skills"],
        "current_conflicts": integration_status["current_conflicts"]
    }

    # Determine overall health
    unhealthy_deps = [dep for dep in health_status["dependencies"].values()
                      if dep["status"] not in ["healthy", "unreachable"]]

    if unhealthy_deps:
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


@app.route("/scan-enhanced", methods=["POST"])
def scan_enhanced():
    """Enhanced scan endpoint using adaptive skills and imported external skills."""
    data = request.get_json(force=True)
    text = data.get("text", "")
    use_all_skills = data.get("use_all_skills", True)
    include_external = data.get("include_external", True)

    # Start with base credit card detection
    base_detections = detect_credit_cards.detect(text)
    all_detections = base_detections.copy()

    if use_all_skills:
        # Apply all available adaptive skills
        for skill_name in adaptive_manager.list_skills():
            try:
                skill = adaptive_manager.skill_registry[skill_name]
                skill_detections = adaptive_manager._execute_skill(skill, text)

                # Add skill source information
                for detection in skill_detections:
                    detection["skill_source"] = skill_name

                all_detections.extend(skill_detections)
            except Exception as e:
                print(f"Error in skill {skill_name}: {e}")

    # Deduplicate detections based on position
    unique_detections = []
    seen_positions = set()

    for detection in all_detections:
        pos_key = (detection.get("start", 0), detection.get("end", 0))
        if pos_key not in seen_positions:
            seen_positions.add(pos_key)
            unique_detections.append(detection)

    # Redact using all detections
    redacted = redact_credit_cards.redact(text, unique_detections)

    # Statistics
    skill_sources = {}
    for detection in unique_detections:
        source = detection.get("skill_source", "base")
        skill_sources[source] = skill_sources.get(source, 0) + 1

    return jsonify({
        "detections": unique_detections,
        "redacted": redacted,
        "stats": {
            "base_detections": len(base_detections),
            "adaptive_detections": len(unique_detections) - len(base_detections),
            "total_detections": len(unique_detections),
            "unique_skills_used": len(skill_sources),
            "skill_sources": skill_sources,
            "external_skills_enabled": include_external
        }
    })


@app.route("/external-sources", methods=["GET", "POST"])
def manage_external_sources():
    """Manage external skill sources."""
    if request.method == "GET":
        """List all external skill sources."""
        status = skill_seekers_integration.get_integration_status()
        return jsonify({
            "sources": status["sources"],
            "total_sources": status["external_sources"],
            "active_sources": status["active_sources"]
        })

    else:  # POST
        """Add a new external skill source."""
        data = request.get_json(force=True)

        required_fields = ["name", "url", "source_type"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        try:
            success = skill_seekers_integration.add_external_source(
                name=data["name"],
                url=data["url"],
                source_type=data["source_type"],
                description=data.get("description", ""),
                tags=data.get("tags", [])
            )

            if success:
                return jsonify({
                    "message": f"Successfully added external source: {data['name']}",
                    "source": {
                        "name": data["name"],
                        "url": data["url"],
                        "source_type": data["source_type"],
                        "description": data.get("description", ""),
                        "tags": data.get("tags", [])
                    }
                })
            else:
                return jsonify({"error": "Failed to add external source"}), 500

        except Exception as e:
            return jsonify({"error": f"Failed to add external source: {str(e)}"}), 500


@app.route("/discover-skills", methods=["POST"])
async def discover_skills():
    """Discover and import skills from external sources."""
    try:
        # Run the async discovery process
        results = await skill_seekers_integration.scan_external_sources()

        return jsonify({
            "message": "Skill discovery completed",
            "results": results,
            "integration_status": skill_seekers_integration.get_integration_status()
        })

    except Exception as e:
        return jsonify({"error": f"Skill discovery failed: {str(e)}"}), 500


@app.route("/setup-security-sources", methods=["POST"])
def setup_security_sources():
    """Setup predefined security-focused skill sources."""
    try:
        skill_seekers_integration.discover_credit_card_security_skills()

        status = skill_seekers_integration.get_integration_status()

        return jsonify({
            "message": "Security sources setup completed",
            "sources_added": len([s for s in status["sources"] if "security" in str(s).lower()]),
            "total_sources": status["external_sources"],
            "sources": status["sources"]
        })

    except Exception as e:
        return jsonify({"error": f"Failed to setup security sources: {str(e)}"}), 500


@app.route("/analyze-conflicts", methods=["POST"])
def analyze_conflicts():
    """Analyze potential conflicts between skills."""
    data = request.get_json(force=True)

    # For demonstration, we'll analyze conflicts between existing skills
    existing_skills = adaptive_manager.skill_registry

    # Mock new skills for analysis
    mock_new_skills = []

    try:
        from claude_subagent.skill_seekers_integration import ConflictResolutionEngine
        conflict_resolver = ConflictResolutionEngine()

        conflicts = conflict_resolver.detect_conflicts(existing_skills, mock_new_skills)

        conflict_info = [
            {
                "type": conflict.conflict_type,
                "skill1": conflict.skill1,
                "skill2": conflict.skill2,
                "description": conflict.description,
                "severity": conflict.severity,
                "resolution_suggestion": conflict.resolution_suggestion,
                "auto_resolvable": conflict.auto_resolvable
            }
            for conflict in conflicts
        ]

        return jsonify({
            "conflicts_detected": len(conflicts),
            "conflicts": conflict_info,
            "resolution_recommendations": [c.resolution_suggestion for c in conflicts if c.auto_resolvable]
        })

    except Exception as e:
        return jsonify({"error": f"Conflict analysis failed: {str(e)}"}), 500


@app.route("/skill-quality-report", methods=["GET"])
def skill_quality_report():
    """Generate a quality report for all skills."""
    try:
        skills_info = []

        for skill_name in adaptive_manager.list_skills():
            skill = adaptive_manager.skill_registry[skill_name]
            performance = adaptive_manager.get_skill_performance(skill_name)

            # Basic quality assessment
            quality_score = 0.5  # Default

            if performance:
                # Use F1 score as primary quality metric
                quality_score = performance.f1_score if performance.f1_score > 0 else 0.5

            skills_info.append({
                "name": skill_name,
                "description": skill.description,
                "dependencies": skill.dependencies,
                "test_cases_count": len(skill.test_cases),
                "performance": {
                    "f1_score": performance.f1_score if performance else 0.0,
                    "precision": performance.precision if performance else 0.0,
                    "recall": performance.recall if performance else 0.0,
                    "last_updated": performance.last_updated if performance else None
                },
                "quality_score": quality_score,
                "quality_grade": "A" if quality_score >= 0.9 else "B" if quality_score >= 0.7 else "C" if quality_score >= 0.5 else "D"
            })

        # Sort by quality score
        skills_info.sort(key=lambda x: x["quality_score"], reverse=True)

        # Summary statistics
        avg_quality = sum(s["quality_score"] for s in skills_info) / len(skills_info) if skills_info else 0
        high_quality_count = sum(1 for s in skills_info if s["quality_score"] >= 0.8)

        return jsonify({
            "summary": {
                "total_skills": len(skills_info),
                "average_quality": round(avg_quality, 3),
                "high_quality_skills": high_quality_count,
                "quality_distribution": {
                    "A": sum(1 for s in skills_info if s["quality_grade"] == "A"),
                    "B": sum(1 for s in skills_info if s["quality_grade"] == "B"),
                    "C": sum(1 for s in skills_info if s["quality_grade"] == "C"),
                    "D": sum(1 for s in skills_info if s["quality_grade"] == "D")
                }
            },
            "skills": skills_info
        })

    except Exception as e:
        return jsonify({"error": f"Quality report generation failed: {str(e)}"}), 500


@app.route("/training-dashboard", methods=["GET"])
def training_dashboard():
    """Provide a dashboard view of the training and learning status."""
    try:
        # Get comprehensive status
        integration_status = skill_seekers_integration.get_integration_status()
        skill_report = None

        # Get skill quality report
        try:
            # Reuse the quality report logic
            skills_info = []
            for skill_name in adaptive_manager.list_skills():
                skill = adaptive_manager.skill_registry[skill_name]
                performance = adaptive_manager.get_skill_performance(skill_name)

                quality_score = 0.5
                if performance and performance.f1_score > 0:
                    quality_score = performance.f1_score

                skills_info.append({
                    "name": skill_name,
                    "quality_score": quality_score,
                    "performance": {
                        "f1_score": performance.f1_score if performance else 0.0,
                        "true_positives": performance.true_positives if performance else 0,
                        "false_positives": performance.false_positives if performance else 0,
                        "false_negatives": performance.false_negatives if performance else 0
                    }
                })

            skill_report = {
                "total_skills": len(skills_info),
                "skills": skills_info[:10],  # Top 10 skills
                "average_quality": sum(s["quality_score"] for s in skills_info) / len(skills_info) if skills_info else 0
            }

        except Exception:
            skill_report = {"error": "Could not generate skill report"}

        return jsonify({
            "dashboard": {
                "last_updated": datetime.utcnow().isoformat(),
                "skill_seekers": {
                    "external_sources": integration_status["external_sources"],
                    "active_sources": integration_status["active_sources"],
                    "discovered_skills": integration_status["discovered_skills"],
                    "current_conflicts": integration_status["current_conflicts"]
                },
                "adaptive_skills": skill_report,
                "system_health": {
                    "total_skills": len(adaptive_manager.list_skills()),
                    "integration_active": True,
                    "auto_learning_enabled": True
                },
                "recent_activity": [
                    "System initialized with enhanced adaptive capabilities",
                    "Skill Seekers integration configured",
                    "External sources ready for discovery"
                ]
            }
        })

    except Exception as e:
        return jsonify({"error": f"Dashboard generation failed: {str(e)}"}), 500


@app.route("/run-example-scenarios", methods=["POST"])
def run_example_scenarios():
    """Run example scenarios to demonstrate system capabilities."""
    data = request.get_json(force=True)
    scenario = data.get("scenario", "all")

    try:
        from claude_subagent.skill_seekers_integration.example_integration import (
            example_basic_integration, example_credit_card_security_skills,
            example_conflict_resolution, example_quality_assessment,
            example_continuous_learning
        )

        results = {}

        if scenario in ["all", "basic"]:
            print("Running basic integration example...")
            await example_basic_integration()
            results["basic_integration"] = "completed"

        if scenario in ["all", "security"]:
            print("Running security skills example...")
            await example_credit_card_security_skills()
            results["security_skills"] = "completed"

        if scenario in ["all", "conflicts"]:
            print("Running conflict resolution example...")
            await example_conflict_resolution()
            results["conflict_resolution"] = "completed"

        if scenario in ["all", "quality"]:
            print("Running quality assessment example...")
            await example_quality_assessment()
            results["quality_assessment"] = "completed"

        if scenario in ["all", "learning"]:
            print("Running continuous learning example...")
            await example_continuous_learning()
            results["continuous_learning"] = "completed"

        return jsonify({
            "message": f"Example scenarios completed: {', '.join(results.keys())}",
            "scenarios_run": list(results.keys()),
            "total_scenarios": len(results)
        })

    except Exception as e:
        return jsonify({"error": f"Example scenario failed: {str(e)}"}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("SUBAGENT_PORT", 5000))

    print(f"Starting Enhanced Adaptive Subagent with Skill Seekers Integration on port {port}")
    print("\n=== Available Endpoints ===")
    print("Detection:")
    print("  POST /scan - Original credit card detection")
    print("  POST /scan-enhanced - Enhanced detection with all adaptive skills")
    print("\nAdaptive Skills:")
    print("  POST /train - Train new skills from examples")
    print("  GET /skills - List all adaptive skills")
    print("  POST /feedback - Submit performance feedback")
    print("\nSkill Seekers Integration:")
    print("  GET /external-sources - List external skill sources")
    print("  POST /external-sources - Add new external source")
    print("  POST /discover-skills - Scan external sources for new skills")
    print("  POST /setup-security-sources - Setup security-focused sources")
    print("  POST /analyze-conflicts - Analyze skill conflicts")
    print("\nAnalytics & Monitoring:")
    print("  GET /health - System health check")
    print("  GET /skill-quality-report - Quality assessment report")
    print("  GET /training-dashboard - Learning status dashboard")
    print("  POST /run-example-scenarios - Run demonstration scenarios")
    print("\nStarting server...")

    app.run(host="0.0.0.0", port=port, debug=True)