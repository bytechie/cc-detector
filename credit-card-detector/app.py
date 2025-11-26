#!/usr/bin/env python3
"""
Unified Credit Card Detector Application

This is a single, configurable Flask application that replaces the previous
multiple app files. It supports different modes and can be configured for
various use cases.

Modes:
- basic: Simple detection and redaction
- metrics: Adds Prometheus metrics monitoring
- adaptive: Includes adaptive skill system
- resource_aware: Optimizes based on available resources
- full: All features enabled

Usage:
    python app.py [--mode MODE] [--port PORT] [--config CONFIG]

Examples:
    python app.py --mode basic
    python app.py --mode metrics --port 5000
    python app.py --mode adaptive --config config/production.yaml
"""

import os
import sys
import time
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, g

# Import skills and utilities
from skills.core import detect_credit_cards, redact_credit_cards

# Optional imports (will be handled gracefully if not available)
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from skills.adaptive import AdaptiveSkillManager, SkillGap
    ADAPTIVE_AVAILABLE = True
except ImportError:
    ADAPTIVE_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class CreditCardDetectorApp:
    """Unified Credit Card Detector Application."""

    def __init__(self, mode: str = "basic", config: Optional[Dict[str, Any]] = None):
        """Initialize the application with specified mode."""
        self.mode = mode
        self.config = config or {}
        self.app = Flask(__name__)
        self.adaptive_manager = None
        self.metrics = None

        # Configure logging
        self._setup_logging()

        # Initialize based on mode
        self._initialize_mode()

        # Setup routes
        self._setup_routes()

    def _setup_logging(self):
        """Setup application logging."""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_mode(self):
        """Initialize features based on the selected mode."""
        self.logger.info(f"Initializing application in '{self.mode}' mode")

        # Initialize metrics if mode requires it
        if self.mode in ['metrics', 'full'] and PROMETHEUS_AVAILABLE:
            self._initialize_metrics()

        # Initialize adaptive skills if mode requires it
        if self.mode in ['adaptive', 'full'] and ADAPTIVE_AVAILABLE:
            self._initialize_adaptive_skills()

        # Initialize resource monitoring if mode requires it
        if self.mode in ['resource_aware', 'full'] and PSUTIL_AVAILABLE:
            self._initialize_resource_monitoring()

    def _initialize_metrics(self):
        """Initialize Prometheus metrics."""
        self.metrics = {
            'REQUEST_COUNT': Counter(
                'credit_card_detector_requests_total',
                'Total requests to credit card detector',
                ['method', 'endpoint', 'status']
            ),
            'SCAN_REQUESTS': Counter(
                'credit_card_scan_requests_total',
                'Total credit card scan requests',
                ['has_detections']
            ),
            'REQUEST_DURATION': Histogram(
                'credit_card_detector_request_duration_seconds',
                'Request duration in seconds',
                ['method', 'endpoint']
            ),
            'SCAN_DURATION': Histogram(
                'credit_card_scan_duration_seconds',
                'Credit card scan duration in seconds'
            ),
            'DETECTIONS_TOTAL': Counter(
                'credit_card_detections_total',
                'Total credit cards detected',
                ['valid_luhn']
            ),
            'CARDS_IN_TEXT': Histogram(
                'credit_cards_found_per_scan',
                'Number of credit cards found per scan'
            ),
            'ACTIVE_CONNECTIONS': Gauge(
                'credit_card_detector_active_connections',
                'Number of active connections'
            ),
            'LATEST_SCAN_TIMESTAMP': Gauge(
                'credit_card_detector_latest_scan_timestamp',
                'Timestamp of latest scan'
            )
        }

        # Setup request tracking
        self.app.before_request(self._before_request)
        self.app.after_request(self._after_request)

        self.logger.info("Prometheus metrics initialized")

    def _initialize_adaptive_skills(self):
        """Initialize adaptive skills system."""
        skills_dir = self.config.get('adaptive', {}).get('skills_dir', 'adaptive_skills_generated')
        self.adaptive_manager = AdaptiveSkillManager(skills_dir=skills_dir)
        self.logger.info(f"Adaptive skills initialized with directory: {skills_dir}")

    def _initialize_resource_monitoring(self):
        """Initialize resource monitoring."""
        self.resource_monitoring = True
        self.logger.info("Resource monitoring enabled")

    def _before_request(self):
        """Called before each request for metrics tracking."""
        if self.metrics:
            g.start_time = time.time()
            self.metrics['ACTIVE_CONNECTIONS'].inc()

    def _after_request(self, response):
        """Called after each request for metrics tracking."""
        if self.metrics and hasattr(g, 'start_time'):
            request_duration = time.time() - g.start_time
            self.metrics['REQUEST_DURATION'].labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown'
            ).observe(request_duration)
            self.metrics['REQUEST_COUNT'].labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=response.status_code
            ).inc()
            self.metrics['ACTIVE_CONNECTIONS'].dec()
        return response

    def _setup_routes(self):
        """Setup Flask routes based on mode."""
        # Basic routes (always available)
        self.app.add_url_rule('/', 'index', self.index, methods=['GET'])
        self.app.add_url_rule('/health', 'health', self.health, methods=['GET'])
        self.app.add_url_rule('/scan', 'scan', self.scan, methods=['POST'])

        # Metrics routes
        if self.mode in ['metrics', 'full'] and PROMETHEUS_AVAILABLE:
            self.app.add_url_rule('/metrics', 'metrics', self.metrics_endpoint, methods=['GET'])

        # Adaptive skills routes
        if self.mode in ['adaptive', 'full'] and ADAPTIVE_AVAILABLE:
            self.app.add_url_rule('/scan-adaptive', 'scan_adaptive', self.scan_adaptive, methods=['POST'])
            self.app.add_url_rule('/train', 'train', self.train, methods=['POST'])
            self.app.add_url_rule('/skills', 'skills', self.skills, methods=['GET'])
            self.app.add_url_rule('/skill-performance', 'skill_performance', self.skill_performance, methods=['GET'])

        # Resource-aware routes
        if self.mode in ['resource_aware', 'full'] and PSUTIL_AVAILABLE:
            self.app.add_url_rule('/resources', 'resources', self.resources, methods=['GET'])

    def _check_presidio_service(self, url: str, service_name: str) -> dict:
        """Check if a Presidio service is healthy."""
        try:
            import requests
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                return {"name": service_name, "status": "healthy", "url": url}
            else:
                return {"name": service_name, "status": "unhealthy", "url": url, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"name": service_name, "status": "unreachable", "url": url, "error": str(e)}

    def index(self):
        """Root endpoint with service information."""
        info = {
            "service": "Credit Card Detector",
            "mode": self.mode,
            "version": "3.0.0-unified",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "/health": "Health check",
                "/scan": "Credit card detection (POST)"
            }
        }

        # Add mode-specific endpoints
        if self.mode in ['metrics', 'full']:
            info["endpoints"]["/metrics"] = "Prometheus metrics"

        if self.mode in ['adaptive', 'full']:
            info["endpoints"].update({
                "/scan-adaptive": "Adaptive detection (POST)",
                "/train": "Train new skills (POST)",
                "/skills": "List adaptive skills",
                "/skill-performance": "Skill performance metrics"
            })

        if self.mode in ['resource_aware', 'full']:
            info["endpoints"]["/resources"] = "Resource usage information"

        return jsonify(info)

    def health(self):
        """Health check with dependency status."""
        health_status = {
            "status": "ok",
            "service": f"claude-subagent-{self.mode}",
            "mode": self.mode,
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {}
        }

        # Check Presidio services
        analyzer_url = os.environ.get("PRESIDIO_ANALYZER_URL", "http://localhost:3000")
        anonymizer_url = os.environ.get("PRESIDIO_ANONYMIZER_URL", "http://localhost:3001")

        health_status["dependencies"]["analyzer"] = self._check_presidio_service(analyzer_url, "presidio-analyzer")
        health_status["dependencies"]["anonymizer"] = self._check_presidio_service(anonymizer_url, "presidio-anonymizer")

        # Add mode-specific health information
        if self.mode in ['adaptive', 'full'] and self.adaptive_manager:
            health_status["adaptive_skills"] = {
                "total_skills": len(self.adaptive_manager.list_skills()),
                "skill_names": self.adaptive_manager.list_skills()
            }

        # Determine overall health
        unhealthy_deps = [dep for dep in health_status["dependencies"].values()
                          if dep["status"] not in ["healthy", "unreachable"]]

        if unhealthy_deps:
            health_status["status"] = "degraded"
            health_status["message"] = f"Some dependencies are unhealthy: {[dep['name'] for dep in unhealthy_deps]}"

        return jsonify(health_status)

    def scan(self):
        """Basic credit card detection endpoint."""
        start_time = time.time()

        try:
            data = request.get_json(force=True)
            text = data.get("text", "")

            # Perform detection
            detections = detect_credit_cards.detect(text)
            scan_duration = time.time() - start_time

            # Update metrics if available
            if self.metrics:
                self.metrics['SCAN_DURATION'].observe(scan_duration)
                self.metrics['CARDS_IN_TEXT'].observe(len(detections))
                self.metrics['LATEST_SCAN_TIMESTAMP'].set(time.time())

                # Track detection counts
                valid_cards = sum(1 for d in detections if d['valid'])
                invalid_cards = len(detections) - valid_cards

                if valid_cards > 0:
                    self.metrics['DETECTIONS_TOTAL'].labels(valid_luhn='true').inc(valid_cards)
                if invalid_cards > 0:
                    self.metrics['DETECTIONS_TOTAL'].labels(valid_luhn='false').inc(invalid_cards)

                self.metrics['SCAN_REQUESTS'].labels(has_detections='true' if detections else 'false').inc()

            # Perform redaction
            redacted = redact_credit_cards.redact(text, detections)

            response_data = {
                "detections": detections,
                "redacted": redacted,
                "scan_duration_seconds": scan_duration
            }

            # Add mode-specific information
            if self.mode in ['resource_aware', 'full'] and hasattr(self, 'resource_monitoring'):
                response_data["resource_usage"] = self._get_resource_usage()

            return jsonify(response_data)

        except Exception as e:
            if self.metrics:
                self.metrics['SCAN_REQUESTS'].labels(has_detections='error').inc()
            return jsonify({"error": str(e)}), 500

    def scan_adaptive(self):
        """Adaptive credit card detection endpoint."""
        if not self.adaptive_manager:
            return jsonify({"error": "Adaptive skills not available in current mode"}), 400

        try:
            data = request.get_json(force=True)
            text = data.get("text", "")

            # Use adaptive skills for detection
            detections = self.adaptive_manager.detect_with_skills(text)
            redacted = redact_credit_cards.redact(text, detections)

            return jsonify({
                "detections": detections,
                "redacted": redacted,
                "adaptive_mode": True
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def train(self):
        """Train new adaptive skills."""
        if not self.adaptive_manager:
            return jsonify({"error": "Adaptive skills not available in current mode"}), 400

        try:
            data = request.get_json(force=True)

            # Extract training data
            examples = data.get("examples", [])
            expected_outputs = data.get("expected_outputs", [])

            if len(examples) != len(expected_outputs):
                return jsonify({"error": "Examples and expected outputs must have same length"}), 400

            # Identify skill gaps and generate new skills
            gaps = self.adaptive_manager.identify_skill_gaps(examples, expected_outputs)
            generated_skills = []

            for gap in gaps:
                skill = self.adaptive_manager.generate_skill_for_gap(gap)
                if skill and self.adaptive_manager.test_and_deploy_skill(skill):
                    generated_skills.append(skill.name)

            return jsonify({
                "identified_gaps": len(gaps),
                "generated_skills": generated_skills,
                "total_skills": len(self.adaptive_manager.list_skills())
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def skills(self):
        """List available adaptive skills."""
        if not self.adaptive_manager:
            return jsonify({"error": "Adaptive skills not available in current mode"}), 400

        try:
            skills = self.adaptive_manager.list_skills()
            skill_info = {}

            for skill_name in skills:
                performance = self.adaptive_manager.get_skill_performance(skill_name)
                skill_info[skill_name] = {
                    "available": True,
                    "performance": performance.to_dict() if performance else None
                }

            return jsonify({
                "total_skills": len(skills),
                "skills": skill_info
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def skill_performance(self):
        """Get performance metrics for adaptive skills."""
        if not self.adaptive_manager:
            return jsonify({"error": "Adaptive skills not available in current mode"}), 400

        try:
            skills = self.adaptive_manager.list_skills()
            performance_data = {}

            for skill_name in skills:
                performance = self.adaptive_manager.get_skill_performance(skill_name)
                if performance:
                    performance_data[skill_name] = performance.to_dict()

            return jsonify({
                "total_skills": len(skills),
                "skill_performance": performance_data
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def metrics_endpoint(self):
        """Prometheus metrics endpoint."""
        if not self.metrics:
            return jsonify({"error": "Metrics not available in current mode"}), 400

        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

    def resources(self):
        """Resource usage information."""
        if not PSUTIL_AVAILABLE:
            return jsonify({"error": "Resource monitoring not available"}), 400

        return jsonify(self._get_resource_usage())

    def _get_resource_usage(self) -> dict:
        """Get current resource usage."""
        if not PSUTIL_AVAILABLE:
            return {}

        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk usage
            disk = psutil.disk_usage('/')

            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "core_count": psutil.cpu_count()
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent,
                    "used_gb": round(memory.used / (1024**3), 2)
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2),
                    "used_gb": round(disk.used / (1024**3), 2)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application."""
        self.logger.info(f"Starting Credit Card Detector in '{self.mode}' mode on port {port}")

        # Print startup information
        print(f"\n🚀 Credit Card Detector - Unified Application")
        print(f"📋 Mode: {self.mode}")
        print(f"🌐 Server: http://{host}:{port}")
        print(f"🔍 Health: http://{host}:{port}/health")

        if self.mode in ['metrics', 'full']:
            print(f"📊 Metrics: http://{host}:{port}/metrics")

        print(f"\n💡 Available endpoints: http://{host}:{port}/")
        print(f"📚 Documentation: Check examples/ directory for usage examples\n")

        self.app.run(host=host, port=port, debug=debug)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML or JSON file."""
    try:
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                import yaml
                return yaml.safe_load(f)
            elif config_path.endswith('.json'):
                return json.load(f)
            else:
                raise ValueError("Config file must be YAML or JSON")
    except Exception as e:
        print(f"Warning: Could not load config file {config_path}: {e}")
        return {}


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Unified Credit Card Detector Application')
    parser.add_argument('--mode', choices=['basic', 'metrics', 'adaptive', 'resource_aware', 'full'],
                       default='basic', help='Application mode (default: basic)')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    # Load configuration
    config = {}
    if args.config:
        config = load_config(args.config)

    # Create and run application
    app = CreditCardDetectorApp(mode=args.mode, config=config)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()