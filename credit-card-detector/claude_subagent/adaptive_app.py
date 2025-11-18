"""Enhanced Claude Subagent Flask app with Adaptive Skills.

Endpoints:
- POST /scan -> accepts JSON {"text": "..."} and returns JSON {detections, redacted}
- POST /scan-adaptive -> uses adaptive skill system for enhanced detection
- POST /train -> trains new skills based on provided examples
- GET /health -> returns health status with dependency checks
- GET /skills -> lists available adaptive skills
- GET /skill-performance -> shows performance metrics for adaptive skills
"""
import os
import requests
import json
from datetime import datetime
from flask import Flask, request, jsonify
from claude_subagent.skills import detect_credit_cards, redact_credit_cards
from claude_subagent.adaptive_skills import AdaptiveSkillManager, SkillGap

app = Flask(__name__)

# Initialize adaptive skill manager
adaptive_manager = AdaptiveSkillManager(skills_dir="adaptive_skills_generated")


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
    """Health check with dependency status and adaptive skills info."""
    health_status = {
        "status": "ok",
        "service": "claude-subagent-adaptive",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {},
        "adaptive_skills": {
            "total_skills": len(adaptive_manager.list_skills()),
            "skill_names": adaptive_manager.list_skills()
        }
    }

    # Check Presidio Analyzer (optional dependency)
    analyzer_url = os.environ.get("PRESIDIO_ANALYZER_URL", "http://localhost:3000")
    health_status["dependencies"]["analyzer"] = _check_presidio_service(analyzer_url, "presidio-analyzer")

    # Check Presidio Anonymizer (optional dependency)
    anonymizer_url = os.environ.get("PRESIDIO_ANONYMIZER_URL", "http://localhost:3001")
    health_status["dependencies"]["anonymizer"] = _check_presidio_service(anonymizer_url, "presidio-anonymizer")

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


@app.route("/scan-adaptive", methods=["POST"])
def scan_adaptive():
    """Enhanced scan endpoint using adaptive skill system."""
    data = request.get_json(force=True)
    text = data.get("text", "")
    use_all_skills = data.get("use_all_skills", True)

    # Start with base credit card detection
    base_detections = detect_credit_cards.detect(text)

    if use_all_skills:
        # Apply all available adaptive skills
        adaptive_detections = []

        for skill_name in adaptive_manager.list_skills():
            try:
                skill = adaptive_manager.skill_registry[skill_name]
                skill_detections = adaptive_manager._execute_skill(skill, text)

                # Add skill source information
                for detection in skill_detections:
                    detection["skill_source"] = skill_name

                adaptive_detections.extend(skill_detections)
            except Exception as e:
                # Log error but continue with other skills
                print(f"Error in skill {skill_name}: {e}")

        # Combine and deduplicate detections
        all_detections = base_detections + adaptive_detections

        # Simple deduplication based on position
        unique_detections = []
        seen_positions = set()

        for detection in all_detections:
            pos_key = (detection.get("start", 0), detection.get("end", 0))
            if pos_key not in seen_positions:
                seen_positions.add(pos_key)
                unique_detections.append(detection)
    else:
        unique_detections = base_detections

    # Redact using all detections
    redacted = redact_credit_cards.redact(text, unique_detections)

    return jsonify({
        "detections": unique_detections,
        "redacted": redacted,
        "stats": {
            "base_detections": len(base_detections),
            "adaptive_detections": len(unique_detections) - len(base_detections),
            "total_detections": len(unique_detections),
            "skills_used": adaptive_manager.list_skills() if use_all_skills else []
        }
    })


@app.route("/train", methods=["POST"])
def train_skills():
    """Train new adaptive skills based on provided examples."""
    data = request.get_json(force=True)

    # Expected format:
    # {
    #   "examples": [
    #     {"input": "text with patterns", "expected_detections": [...]},
    #     ...
    #   ],
    #   "description": "Optional description of what to detect"
    # }

    examples = data.get("examples", [])
    description = data.get("description", "User-provided training data")

    if not examples:
        return jsonify({"error": "No examples provided"}), 400

    # Prepare test data and expected outputs
    test_data = []
    expected_outputs = []

    for example in examples:
        test_data.append({"input": example["input"]})
        expected_outputs.append(example.get("expected_detections", []))

    try:
        # Generate new skills to address gaps
        new_skills = adaptive_manager.analyze_and_adapt(test_data, expected_outputs)

        return jsonify({
            "message": f"Generated {len(new_skills)} new skills",
            "new_skills": [
                {
                    "name": skill.name,
                    "description": skill.description,
                    "test_cases_count": len(skill.test_cases)
                }
                for skill in new_skills
            ],
            "total_skills": len(adaptive_manager.list_skills())
        })

    except Exception as e:
        return jsonify({"error": f"Training failed: {str(e)}"}), 500


@app.route("/skills", methods=["GET"])
def list_skills():
    """List all available adaptive skills."""
    skills_info = []

    for skill_name in adaptive_manager.list_skills():
        skill = adaptive_manager.skill_registry[skill_name]
        performance = adaptive_manager.get_skill_performance(skill_name)

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
            }
        })

    return jsonify({
        "total_skills": len(skills_info),
        "skills": skills_info
    })


@app.route("/skill-performance", methods=["GET"])
def skill_performance():
    """Get detailed performance metrics for all skills."""
    performance_data = {}

    for skill_name in adaptive_manager.list_skills():
        perf = adaptive_manager.get_skill_performance(skill_name)
        if perf:
            performance_data[skill_name] = {
                "true_positives": perf.true_positives,
                "false_positives": perf.false_positives,
                "false_negatives": perf.false_negatives,
                "accuracy": perf.accuracy,
                "precision": perf.precision,
                "recall": perf.recall,
                "f1_score": perf.f1_score,
                "last_updated": perf.last_updated
            }

    return jsonify({
        "skills_performance": performance_data,
        "total_skills": len(performance_data)
    })


@app.route("/feedback", methods=["POST"])
def submit_feedback():
    """Submit feedback to improve skill performance."""
    data = request.get_json(force=True)

    # Expected format:
    # {
    #   "input_text": "the original text",
    #   "skill_name": "name of the skill",
    #   "detections": [...],  # What the skill found
    #   "expected_detections": [...],  # What should have been found
    #   "feedback_type": "false_positive" | "false_negative" | "correct"
    # }

    input_text = data.get("input_text", "")
    skill_name = data.get("skill_name", "")
    feedback_type = data.get("feedback_type", "")
    expected_detections = data.get("expected_detections", [])

    if not all([input_text, skill_name, feedback_type]):
        return jsonify({"error": "Missing required fields"}), 400

    # Calculate TP/FP/FN based on feedback
    tp, fp, fn = 0, 0, 0

    if feedback_type == "correct":
        tp = 1
    elif feedback_type == "false_positive":
        fp = 1
    elif feedback_type == "false_negative":
        fn = 1

    # Update skill performance
    try:
        adaptive_manager.update_skill_performance(skill_name, tp, fp, fn)

        return jsonify({
            "message": "Feedback recorded",
            "skill_name": skill_name,
            "updated_metrics": adaptive_manager.get_skill_performance(skill_name).__dict__
        })

    except Exception as e:
        return jsonify({"error": f"Failed to record feedback: {str(e)}"}), 500


@app.route("/analyze-gaps", methods=["POST"])
def analyze_gaps():
    """Analyze current skill gaps without creating new skills."""
    data = request.get_json(force=True)

    examples = data.get("examples", [])

    if not examples:
        return jsonify({"error": "No examples provided"}), 400

    # Prepare test data
    test_data = [{"input": example["input"]} for example in examples]
    expected_outputs = [example.get("expected_detections", []) for example in examples]

    try:
        # Identify gaps without generating skills
        gaps = adaptive_manager.identify_skill_gaps(test_data, expected_outputs)

        gap_info = [
            {
                "pattern": gap.pattern,
                "description": gap.description,
                "examples": gap.examples,
                "severity": gap.severity,
                "frequency": gap.frequency
            }
            for gap in gaps
        ]

        return jsonify({
            "gaps_found": len(gap_info),
            "gaps": gap_info,
            "current_skills": adaptive_manager.list_skills()
        })

    except Exception as e:
        return jsonify({"error": f"Gap analysis failed: {str(e)}"}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("SUBAGENT_PORT", 5000))
    print(f"Starting adaptive subagent on port {port}")
    print("Available endpoints:")
    print("  POST /scan - Original credit card detection")
    print("  POST /scan-adaptive - Enhanced detection with adaptive skills")
    print("  POST /train - Train new skills from examples")
    print("  GET /health - Health check and system status")
    print("  GET /skills - List all adaptive skills")
    print("  GET /skill-performance - Performance metrics")
    print("  POST /feedback - Submit performance feedback")
    print("  POST /analyze-gaps - Analyze detection gaps")
    app.run(host="0.0.0.0", port=port)